# Contributing to Vidzy RAG

Thank you for helping improve Vidzy RAG. Keep changes focused, tested, and safe for a public repository.

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

cd web
npm ci
cd ..
```

The first backend test or indexing run downloads the configured Sentence Transformers model. External LLM credentials are not needed for the default retrieval mode.

## Development

Run the backend from the repository root:

```bash
source .venv/bin/activate
uvicorn api.app.main:app --host 127.0.0.1 --port 8100 --reload
```

Run the frontend development server separately:

```bash
cd web
npm run dev
```

Python code should remain typed, small, and explicit about public/private scope. TypeScript should pass the configured compiler and ESLint rules. Avoid unrelated formatting or dependency changes.

## Tests and validation

Before opening a pull request, run:

```bash
source .venv/bin/activate
pytest
node scripts/knowledge/validate-knowledge.mjs

cd web
npm run typecheck
npm run lint
npm run build
npm audit --audit-level=high
```

Tests must work from a public clone without private knowledge, production secrets, paid APIs, or an external LLM key.

## Knowledge contributions and privacy

Public knowledge must be reviewed product information suitable for publication. Preserve the public/private collection boundary in loaders, retrieval, tests, and documentation.

Never commit:

- `knowledge/internal/`;
- a production `.env` or any credential;
- proprietary organization knowledge, customer data, or private implementation findings;
- Chroma runtime data, downloaded models, or model/tool caches;
- mixed-scope facts or private provenance registries.

If a change could expose internal results through public chat, treat it as security-sensitive and follow [SECURITY.md](SECURITY.md).

## Pull requests

- Explain the user-visible purpose and scope.
- Link relevant issues without disclosing security-sensitive details.
- Add or update tests and documentation where behavior changes.
- Include validation results and note any deliberate omissions.
- Keep commits reviewable and avoid generated runtime artifacts.
- Confirm that `git ls-files knowledge/internal` returns no output.

By contributing, you agree that your contribution is licensed under the repository's Apache-2.0 license.
