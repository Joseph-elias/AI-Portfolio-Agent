# Local-RAG

Repository: https://github.com/Joseph-elias/Local-RAG

Local-RAG is a production-oriented local RAG app where users upload PDFs and chat with source-cited answers.
It uses local Chroma persistence and OpenAI-based embeddings/chat generation.

Technical highlights:
- PDF ingestion with chunking and metadata
- Citation-ready retrieval (filename + page signals)
- FastAPI backend and web frontend integration
- Session-aware chat memory

This project is relevant for recruiter-facing AI assistants and enterprise document QA use cases.