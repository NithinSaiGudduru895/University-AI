# AP + Telangana University AI — Official-Source RAG Assistant

A resume-ready multi-university RAG application for Andhra Pradesh universities.

## Stack

- Python + Flask
- Gemini API
- RAG
- Sentence Transformers embeddings
- FAISS vector search
- MongoDB
- PDF/DOCX/TXT ingestion
- Responsive glassmorphism frontend

## University catalog

The project includes a catalog of AP universities and official website links. The catalog is based primarily on AP state-university listings and APSCHE university participation lists. The application does NOT invent institutional policy documents.

## Real-document workflow

1. Create the Python 3.12 environment.
2. Install requirements.
3. Configure `.env`.
4. Run MongoDB locally.
5. Run `python scripts/collect_official_docs.py`.
6. Review the downloaded files under `uploads/<university_id>/`.
7. Start `python app.py`.
8. On first startup, documents are embedded and indexed into separate FAISS stores.

Some university websites block automated crawling. If a university blocks the collector, download authorized documents manually from its official website and put them in the matching `uploads/<university_id>/` folder.

## Important

The source collector is intentionally restricted to the official domain in `data/universities.json`. Do not treat search-engine snippets, coaching sites, blogs, or Wikipedia as official university policy.

Before putting this project on a resume, keep a small set of high-quality, current documents for each university and retain their source URLs.

## Windows setup

Use Python 3.12:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create `.env` from `.env.example`.

Start MongoDB, then:

```powershell
python scripts/collect_official_docs.py
python app.py
```

Open:

http://127.0.0.1:5000

## MongoDB

Default:

```text
mongodb://localhost:27017
```

Database:

```text
ap_university_ai
```

## Gemini

Put your API key in `.env`:

```env
GEMINI_API_KEY=YOUR_ACTUAL_KEY
```

Never commit `.env` to GitHub.

## RAG flow

```text
Official university documents
        ↓
PDF/DOCX/TXT extraction
        ↓
Chunking
        ↓
Sentence Transformer embeddings
        ↓
University-specific FAISS index
        ↓
Semantic retrieval
        ↓
Gemini LLM
        ↓
Answer + source documents + page
```


## Expanded coverage

The catalog now supports Andhra Pradesh and Telangana university knowledge bases with separate vector indexes per university, official-source metadata, Gemini RAG answers, MongoDB chat history, and document upload/collection workflows.
