# Security policy

## Supported versions

Security fixes are applied to the latest release and the current `main` branch. Older releases may not receive patches.

## Reporting a vulnerability

Do not disclose suspected vulnerabilities, private knowledge, credentials, or exploit details in a public GitHub issue, discussion, or pull request.

Use GitHub's private vulnerability reporting feature from the repository's **Security** tab when it is available. If it is not available, contact the repository owner through an established private channel and share only enough information to arrange a secure report. This repository does not publish a dedicated security email address.

Include the affected version, impact, reproduction steps, and any suggested mitigation. Allow maintainers reasonable time to investigate and coordinate a fix before public disclosure.

## Secrets and internal access

- Keep `.env` files and production credentials out of Git.
- Generate a unique `INTERNAL_API_KEY` for each environment, store it server-side, and never expose it to browser code or logs.
- Rotate any key that may have been disclosed.
- Do not enable optional generative mode merely by provisioning an API key; activation must remain explicit.
- Do not include customer data, proprietary documents, or security findings in public examples or reports.

## Private knowledge boundary

Private documents belong only in the ignored `knowledge/internal/` area or another approved private source. Public and private documents are indexed into separate Chroma collections. Public `/api/chat` is expected to retrieve only from `vidzy_public`; access to internal or combined search requires the server-side internal API key.

Changes affecting ingestion scope, collection selection, metadata filtering, authorization, proxy behavior, or logging require focused security review.

## Deployment assumptions

The provided deployment configuration assumes TLS termination and rate limiting at Nginx, one Uvicorn worker bound to localhost, protected environment files, restricted filesystem permissions, and a persistent Chroma directory outside the web root. Operators remain responsible for host hardening, dependency updates, backups, monitoring, key rotation, and access control.
