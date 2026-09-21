import os
import json
import faiss
from rag.chunker import chunk_text
from rag.embeddings import encode
from config import VECTOR_ROOT

def _paths(uid):
    folder = os.path.join(VECTOR_ROOT, uid)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "index.faiss"), os.path.join(folder, "metadata.json")

def build_index(uid, text, filename, pages, university):
    index_path, metadata_path = _paths(uid)
    chunks = []

    for item in pages:
        for chunk in chunk_text(item["text"]):
            chunks.append({
                "text": chunk,
                "file": filename,
                "page": item.get("page"),
                "title": filename,
                "source_url": university.get("official_url", ""),
                "university": university["name"]
            })

    if not chunks:
        raise ValueError("No text chunks were created")

    vectors = encode([x["text"] for x in chunks]).astype("float32")

    if os.path.exists(index_path) and os.path.exists(metadata_path):
        index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        index.add(vectors)
        metadata.extend(chunks)
    else:
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        metadata = chunks

    faiss.write_index(index, index_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def load_index(uid):
    index_path, metadata_path = _paths(uid)
    if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
        return None, None
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

def search_index(index, metadata, question, top_k=6):
    q = encode([question]).astype("float32")
    k = min(top_k, index.ntotal)
    scores, ids = index.search(q, k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        item = dict(metadata[int(idx)])
        item["score"] = float(score)
        results.append(item)
    return results
