# Building a knowledge base

Vidzy RAG ships with a small, reviewed public product corpus, but the ingestion pipeline is designed to work with another product's knowledge. The important work happens before LangChain or Chroma: source claims must be extracted, verified, classified, and written as reliable canonical material.

## Lifecycle

```text
Source material
  → knowledge extraction
  → evidence validation
  → public/private classification
  → canonical documentation
  → canonical Q&A
  → validation
  → LangChain ingestion
  → local embeddings
  → Chroma collections
```

### 1. Gather source material

Useful sources can include application source code, product and API documentation, FAQs, help-center articles, user guides, architecture documentation, and manually reviewed facts from subject-matter experts. Prefer current primary sources and record enough provenance privately for reviewers to re-check each claim.

### 2. Extract and validate facts

A developer or AI coding agent can inspect a product codebase and derive evidence-backed product facts. This is a valid way to discover implemented behavior, constraints, and terminology, but generated claims are candidates—not truth. Verify each claim against the implementation or another authoritative source before exposing it publicly.

Resolve conflicts and remove stale, ambiguous, sensitive, or unsupported claims. Never copy secrets, customer data, private endpoints, security findings, or proprietary implementation paths into public material.

### 3. Classify public and private knowledge

Decide whether each verified claim is appropriate for customers or only for authorized operators and developers. Classification happens before ingestion:

```text
knowledge/
├── public/                  # reviewed Markdown tracked by Git
├── internal/                # proprietary Markdown, local and Git-ignored
└── metadata/
    └── questions.jsonl      # reviewed public canonical Q&A
```

Local mixed-scope fact and provenance registries may support review, but they are intentionally ignored when they contain private records or source locations. Organizations should manage those inputs through their approved private storage and deployment process.

### 4. Write canonical documentation

Convert verified public facts into short Markdown organized by user intent and stable headings. Describe product behavior, not private implementation evidence. Keep one topic per section so the heading-aware loader can create focused chunks.

Private operational or architectural documentation can be placed under the ignored `knowledge/internal/` directory. It remains available for authorized local or production indexing without entering the public Git repository.

### 5. Add canonical questions

`knowledge/metadata/questions.jsonl` contains one JSON object per reviewed public answer. For example, based on the included public Vidzy knowledge:

```json
{"id":"faq-timed-cta","scope":"public","question":"Can Vidzy show calls-to-action during video playback?","aliases":["Can a CTA appear while the video is playing?"],"answer":"Yes. A reusable CTA can appear at its default playback time or at a timestamp overridden for a specific assigned video.","category":"cta","status":"verified","source_fact_ids":["cta-timed-display","cta-per-video-timestamp"],"tags":["cta","video-player","timing"]}
```

Canonical Q&A makes retrieval-only chat possible. A question and its alternative phrasings are embedded for semantic matching; when confidence is sufficient, the API returns the reviewed canonical answer directly. No LLM is required to compose or reinterpret the claim.

### 6. Validate, ingest, and index

Run validation before indexing:

```bash
node scripts/knowledge/validate-knowledge.mjs
python -m api.app.ingestion.index
```

LangChain documents are created from the reviewed Markdown and JSONL inputs. The configured local Sentence Transformers model produces embeddings, and Chroma stores them in physically separate collections:

- `vidzy_public` for public Markdown and canonical Q&A;
- `vidzy_internal` for locally supplied private documents and metadata.

The public chat service selects only `vidzy_public`. Internal and combined search scopes are separate, authenticated API operations.

## Use your own product knowledge

1. Review or remove the sample files under `knowledge/public/`.
2. Add public Markdown for your product using clear headings and publishable language.
3. Add reviewed canonical Q&A objects to `knowledge/metadata/questions.jsonl`.
4. Optionally add proprietary Markdown under the ignored `knowledge/internal/` directory.
5. Update evaluation cases to reflect your supported questions.
6. Validate, index, run the tests, and inspect retrieval results before deployment.

Keep schema fields used by the loader unless you update ingestion and tests together. Product names in application copy can be adapted separately from the retrieval architecture.

## Keep knowledge current

Treat knowledge as versioned product content. When the underlying product changes:

1. identify affected claims and canonical answers;
2. verify the new behavior against authoritative evidence;
3. update public and private documents in their correct scopes;
4. update evaluation cases;
5. run validation and tests;
6. reindex Chroma using the idempotent indexing command;
7. review changed counts and representative retrieval results before promotion.

Reindexing replaces the contents of each collection, preventing stale or duplicate chunks from accumulating. Coordinate it with the running API as described in the deployment runbook.
