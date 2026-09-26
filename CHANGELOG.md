# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-27

### Added

- Retrieval-first RAG pipeline using LangChain retrieval and persistent Chroma storage.
- Local Sentence Transformers embeddings with no external embedding API requirement.
- Reviewed canonical Q&A responses for LLM-free public chat.
- Optional, explicitly enabled generative mode with retrieval fallback.
- FastAPI search, chat, health, and compiled-frontend serving.
- React, Vite, and TypeScript web interface.
- Physically separate public and internal Chroma collections with API-key-protected internal search.
- Retrieval evaluation dataset, metrics runner, and documented baseline.
- Idempotent knowledge ingestion and public knowledge validation tooling.
- PM2 and Nginx deployment examples and production runbook.
- Public-release privacy controls and optional archive audit utility.

[Unreleased]: https://github.com/hussnainsheikh/vidzy-rag/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hussnainsheikh/vidzy-rag/releases/tag/v0.1.0
