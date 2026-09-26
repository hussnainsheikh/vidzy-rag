# Vidzy RAG knowledge

This directory is the content boundary for retrieval. Files committed under `public/` and `metadata/questions.jsonl` contain the reviewed, user-facing knowledge used by the public chatbot.

## Public and private scopes

- `public/` contains product documentation that is safe to publish and index for public retrieval.
- `metadata/questions.jsonl` contains reviewed public questions and canonical answers.
- `internal/` is a Git-ignored local area for proprietary organizational documents. Teams may add their own private Markdown here for development or production without publishing it to GitHub.
- `metadata/facts.jsonl` and `metadata/sources.jsonl` are ignored because the local Phase 1 copies mix scopes and include private provenance. They must not be force-added.

The ingestion process writes public and private documents to physically separate Chroma collections: `vidzy_public` and `vidzy_internal`. The public chatbot retrieves only from `vidzy_public`. Internal and combined search scopes require the configured internal API key; adding private documents does not make them available to public chat.

Keep private inputs available through a secure, out-of-band deployment process. Do not place credentials, customer data, security findings, private source locations, or implementation provenance in public knowledge files.

## Validation

From the repository root, run:

```bash
node scripts/knowledge/validate-knowledge.mjs
```

The validator checks JSONL structure, identifiers, references, duplicate content, and common secret patterns. A public checkout can operate without the ignored private metadata files; a trusted local checkout can additionally validate and index those files when present.
