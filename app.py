import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from config import UPLOAD_ROOT, VECTOR_ROOT
from database.mongodb import init_db, save_chat, get_recent_chats
from rag.document_loader import extract_document
from rag.vector_store import build_index, load_index, search_index
from rag.qa import generate_answer
from rag.catalog import load_universities

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024

os.makedirs(UPLOAD_ROOT, exist_ok=True)
os.makedirs(VECTOR_ROOT, exist_ok=True)

try:
    init_db()
    DB_OK = True
    print("MongoDB connected successfully")
except Exception as exc:
    DB_OK = False
    print("MongoDB warning:", exc)

UNIVERSITIES = load_universities()

def university_id(value):
    value = value.strip().lower()

    for u in UNIVERSITIES:
        if u["id"].lower() == value:
            return u["id"]

        if u["name"].lower() == value:
            return u["id"]

    raise ValueError("Unknown university")


def get_university(uid):
    for u in UNIVERSITIES:
        if u["id"] == uid:
            return u

    return None


def seed_indexes():
    print("Checking university documents...")

    for u in UNIVERSITIES:
        folder = os.path.join(UPLOAD_ROOT, u["id"])

        if not os.path.isdir(folder):
            continue

        index_path = os.path.join(
            VECTOR_ROOT,
            u["id"],
            "index.faiss"
        )

        metadata_path = os.path.join(
            VECTOR_ROOT,
            u["id"],
            "metadata.json"
        )

        if os.path.exists(index_path) and os.path.exists(metadata_path):
            print(f"Index exists: {u['name']}")
            continue

        found_document = False

        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)

            if not os.path.isfile(path):
                continue

            extension = filename.rsplit(".", 1)[-1].lower()

            if extension not in {"pdf", "docx", "txt"}:
                print(
                    f"Indexing skipped: {path} -> Unsupported document type"
                )
                continue

            found_document = True

            try:
                text, pages = extract_document(path)

                if not text.strip():
                    print(
                        f"Indexing skipped: {path} -> No readable text"
                    )
                    continue

                build_index(
                    u["id"],
                    text,
                    filename,
                    pages,
                    u
                )

                print(
                    f"Indexed successfully: {u['name']} -> {filename}"
                )

            except Exception as exc:
                print(
                    f"Indexing skipped: {path} -> {exc}"
                )

        if not found_document:
            print(
                f"No documents found for {u['name']}"
            )


seed_indexes()


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/universities")
def universities():

    ap_count = sum(
        1 for u in UNIVERSITIES
        if u.get("state") == "Andhra Pradesh"
    )

    telangana_count = sum(
        1 for u in UNIVERSITIES
        if u.get("state") == "Telangana"
    )

    return jsonify({
        "total_universities": len(UNIVERSITIES),
        "states": {
            "Andhra Pradesh": ap_count,
            "Telangana": telangana_count
        },
        "universities": [
            {
                "id": u["id"],
                "name": u["name"],
                "short_name": u.get("short_name", ""),
                "city": u.get("city", ""),
                "type": u.get(
                    "type",
                    "University"
                ),
                "official_url": u.get(
                    "official_url",
                    ""
                ),
                "state": u.get(
                    "state",
                    ""
                )
            }
            for u in UNIVERSITIES
        ]
    })


@app.get("/api/status")
def status():

    indexed = []

    for u in UNIVERSITIES:

        index_path = os.path.join(
            VECTOR_ROOT,
            u["id"],
            "index.faiss"
        )

        metadata_path = os.path.join(
            VECTOR_ROOT,
            u["id"],
            "metadata.json"
        )

        if (
            os.path.exists(index_path)
            and os.path.exists(metadata_path)
        ):
            indexed.append(u["id"])

    return jsonify({
        "mongodb": DB_OK,
        "total_universities": len(UNIVERSITIES),
        "indexed_count": len(indexed),
        "indexed_universities": indexed
    })


@app.post("/api/upload")
def upload():

    university = request.form.get(
        "university",
        ""
    ).strip()

    file = request.files.get("file")

    if (
        not university
        or not file
        or not file.filename
    ):
        return jsonify({
            "error": "University and file are required"
        }), 400

    try:
        uid = university_id(university)

    except ValueError:
        return jsonify({
            "error": "Select a university from the list"
        }), 400

    extension = (
        file.filename
        .rsplit(".", 1)[-1]
        .lower()
    )

    if extension not in {
        "pdf",
        "docx",
        "txt"
    }:
        return jsonify({
            "error": (
                "Only PDF, DOCX and TXT "
                "files are supported"
            )
        }), 400

    filename = secure_filename(
        file.filename
    )

    if not filename:
        return jsonify({
            "error": "Invalid filename"
        }), 400

    folder = os.path.join(
        UPLOAD_ROOT,
        uid
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    path = os.path.join(
        folder,
        filename
    )

    try:
        file.save(path)

        text, pages = extract_document(
            path
        )

        if not text.strip():
            return jsonify({
                "error": (
                    "No readable text "
                    "found in the document"
                )
            }), 400

        u = get_university(uid)

        build_index(
            uid,
            text,
            filename,
            pages,
            u
        )

        return jsonify({
            "message": (
                f"{filename} indexed for "
                f"{u['name']}"
            ),
            "university": u["name"]
        })

    except Exception as exc:

        print(
            "Upload/indexing error:",
            repr(exc)
        )

        return jsonify({
            "error": (
                "Document indexing failed"
            ),
            "details": str(exc)
        }), 500


@app.post("/api/chat")
def chat():

    data = request.get_json(
        silent=True
    ) or {}

    university = data.get(
        "university",
        ""
    ).strip()

    question = data.get(
        "question",
        ""
    ).strip()

    if not university or not question:

        return jsonify({
            "error": (
                "University and question "
                "are required"
            )
        }), 400

    try:
        uid = university_id(
            university
        )

    except ValueError:

        return jsonify({
            "error": "Unknown university"
        }), 400

    index, metadata = load_index(
        uid
    )

    if index is None:

        return jsonify({
            "error": (
                "No documents have been "
                "indexed for this university yet."
            )
        }), 404

    try:

        results = search_index(
            index,
            metadata,
            question,
            top_k=6
        )

    except Exception as exc:

        print(
            "RAG search error:",
            repr(exc)
        )

        return jsonify({
            "error": (
                "RAG search failed"
            ),
            "details": str(exc)
        }), 500

    if not results:

        return jsonify({
            "error": (
                "No relevant source material "
                "was found in the indexed documents."
            )
        }), 404

    u = get_university(uid)

    try:

        answer = generate_answer(
            question,
            results,
            u
        )

    except Exception as exc:

        print(
            "Chat/Gemini error:",
            repr(exc)
        )

        return jsonify({
            "error": (
                "The AI service could not "
                "generate an answer."
            ),
            "details": str(exc)
        }), 502

    if DB_OK:

        try:

            save_chat(
                u["name"],
                question,
                answer
            )

        except Exception as exc:

            print(
                "MongoDB save warning:",
                repr(exc)
            )

    sources = []

    for r in results:

        sources.append({
            "title": r.get(
                "title",
                r.get("file", "Document")
            ),
            "file": r.get(
                "file",
                ""
            ),
            "page": r.get(
                "page"
            ),
            "source_url": r.get(
                "source_url"
            ),
            "score": round(
                float(
                    r.get(
                        "score",
                        0
                    )
                ),
                3
            )
        })

    return jsonify({
        "answer": answer,
        "sources": sources
    })


@app.get("/api/history")
def history():

    if not DB_OK:

        return jsonify({
            "chats": []
        })

    try:

        return jsonify({
            "chats": get_recent_chats(20)
        })

    except Exception as exc:

        print(
            "History error:",
            repr(exc)
        )

        return jsonify({
            "chats": []
        })


if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )