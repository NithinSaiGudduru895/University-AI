# University coverage

This build combines:
- 18 Andhra Pradesh state universities from the Andhra Pradesh government state-university list.
- 17 Telangana state-university entries from the Telangana Education Policy 2026 table.
- 3 Telangana central universities.
- 3 Telangana deemed universities.
- 5 Telangana private universities.

The catalog keeps the university type explicit. Newer Telangana institutions can be added without changing the RAG architecture.

## Official-document rule

Only documents from each university's official domain should be indexed as authoritative knowledge.
The collector script is intentionally conservative: it crawls within the configured official domain and downloads PDF/DOC/DOCX/TXT files it discovers.

Some university sites use JavaScript, anti-bot protection, or portal redirects. In those cases, place the official files manually in:
uploads/<university_id>/

Then run the application; the existing indexing logic will build the university-specific FAISS index.
