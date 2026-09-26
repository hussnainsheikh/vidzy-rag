# Vidzy RAG Production Deployment Runbook

Target: `https://rag.vidzyplayer.com`

This runbook prepares a deployment but does not authorize or perform one. It creates a separate Nginx virtual host and a separate PM2 application named `vidzy-rag`. Never change, restart, or proxy through the existing Vidzy NestJS backend.

## Required values

Replace these placeholders before running commands:

| Placeholder | Meaning |
| --- | --- |
| `<RAG_USER>` | Linux account that owns the existing PM2 daemon and will run RAG |
| `<RAG_GROUP>` | Primary group for that account |
| `<RAG_REPOSITORY_URL>` | Reviewed Git repository URL containing the committed Phase 2 application |
| `<RAG_RELEASE_REF>` | Immutable reviewed commit SHA or release tag |
| `<RAG_SSH_HOST>` | SSH destination used to transfer private knowledge, such as `user@server` |
| `<SERVER_PUBLIC_IP>` | Existing Vidzy server public IPv4 address |
| `<EXISTING_VIDZY_HEALTH_URL>` | A known safe URL used to prove the existing product still works |

The current working tree must be reviewed and committed before deployment. Do not deploy an uncommitted local directory.

## 1. Prerequisite checks

Run read-only checks on the server first:

```bash
cat /etc/os-release
uname -m
nproc
free -h
swapon --show
df -h / /opt /var/lib
nginx -v
sudo nginx -t
pm2 --version
pm2 list
python3 --version
node --version
npm --version
sudo ss -ltnp | grep -E ':(80|443|8100)\b' || true
```

Requirements:

- one available local port, `127.0.0.1:8100`;
- at least 2 GB swap before deployment;
- enough headroom above the observed ~429 MiB loaded RAG RSS;
- Python 3.12 recommended and tested; Python must be at least 3.10;
- Node 22 recommended and tested; Node must be at least 18.18;
- `git`, Python venv support, compiler basics, Node/npm, PM2, Nginx, `curl`, `jq`, `rsync`, and `openssl`;
- the shell account running `pm2 list` must be the owner of the existing PM2 daemon. Do not accidentally create a second root PM2 daemon with `sudo pm2`.

If swap is missing, stop and have the server administrator add and persist a 2 GB swap file before continuing. Recheck `swapon --show` and `free -h` afterward.

## 2. DNS setup

At the authoritative DNS provider, create:

```text
Type: A
Host: rag
Value: <SERVER_PUBLIC_IP>
```

Verify from more than one resolver before requesting a certificate:

```bash
dig +short rag.vidzyplayer.com A
dig @1.1.1.1 +short rag.vidzyplayer.com A
dig @8.8.8.8 +short rag.vidzyplayer.com A
```

Every result must equal `<SERVER_PUBLIC_IP>`. At the time this runbook was prepared, the hostname returned no public A record, so DNS is currently a deployment blocker.

## 3. Server directories

After setting the real values in the shell:

```bash
export RAG_USER='<RAG_USER>'
export RAG_GROUP='<RAG_GROUP>'

sudo install -d -o "$RAG_USER" -g "$RAG_GROUP" -m 0750 /opt/vidzy-rag
sudo install -d -o "$RAG_USER" -g "$RAG_GROUP" -m 0750 /var/lib/vidzy-rag
sudo install -d -o "$RAG_USER" -g "$RAG_GROUP" -m 0750 /var/lib/vidzy-rag/chroma
sudo install -d -o "$RAG_USER" -g "$RAG_GROUP" -m 0750 /var/lib/vidzy-rag/huggingface
```

Do not place Chroma under the Git checkout. Nginx must never serve `/var/lib/vidzy-rag`.

## 4. Repository deployment and private knowledge

As `<RAG_USER>`:

```bash
cd /opt/vidzy-rag
git clone '<RAG_REPOSITORY_URL>' .
git fetch --tags --prune
git checkout --detach '<RAG_RELEASE_REF>'
git status --short
```

`git status --short` must be empty at this point.

The public repository intentionally excludes `knowledge/internal/`, `knowledge/metadata/facts.jsonl`, and `knowledge/metadata/sources.jsonl`. A production internal collection cannot be built without the approved private inputs. Transfer them separately from the trusted development workstation—never commit them to a public remote:

```bash
rsync -az --delete --chmod=D750,F640 knowledge/internal/ '<RAG_SSH_HOST>:/opt/vidzy-rag/knowledge/internal/'
rsync -az --chmod=F640 knowledge/metadata/facts.jsonl knowledge/metadata/sources.jsonl '<RAG_SSH_HOST>:/opt/vidzy-rag/knowledge/metadata/'
```

On the server, correct and verify ownership without printing contents:

```bash
sudo chown -R "$RAG_USER:$RAG_GROUP" /opt/vidzy-rag/knowledge/internal /opt/vidzy-rag/knowledge/metadata
find /opt/vidzy-rag/knowledge/internal -type d -exec chmod 0750 {} \;
find /opt/vidzy-rag/knowledge/internal -type f -exec chmod 0640 {} \;
chmod 0640 /opt/vidzy-rag/knowledge/metadata/facts.jsonl /opt/vidzy-rag/knowledge/metadata/sources.jsonl
```

Do not put `/opt/vidzy-rag` directly under any Nginx `root` or `alias`.

## 5. Python environment

Use the tested Python 3.12 interpreter supplied by the server administrator:

```bash
cd /opt/vidzy-rag
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip check
```

Do not install Python packages globally and do not install `requirements-generative.txt` for this deployment.

## 6. Frontend build

```bash
cd /opt/vidzy-rag/web
npm ci
npm audit --audit-level=high
npm run typecheck
npm run lint
npm run build
test -s dist/index.html
cd /opt/vidzy-rag
```

There is no Node process in production. FastAPI serves `web/dist`.

## 7. Production environment

Create `/opt/vidzy-rag/.env` from `deploy/.env.production.example`. Generate the internal API key on the server and insert it without sending it through chat, Git, or frontend configuration:

```bash
cd /opt/vidzy-rag
cp deploy/.env.production.example .env
openssl rand -hex 32
editor .env
chmod 0600 .env
chown "$RAG_USER:$RAG_GROUP" .env
stat -c '%a %U %G %n' .env
```

The resulting file must contain:

- `APP_ENV=production`
- `CHROMA_PATH=/var/lib/vidzy-rag/chroma`
- `KNOWLEDGE_PATH=/opt/vidzy-rag/knowledge`
- `STATIC_DIR=/opt/vidzy-rag/web/dist`
- `RAG_RESPONSE_MODE=retrieval`
- a unique nonempty `INTERNAL_API_KEY`
- an empty `OPENAI_API_KEY`
- `CORS_ORIGINS=https://rag.vidzyplayer.com`

Do not reuse a development value. Generate a completely new production key for each environment and rotate any value that may have been disclosed.

Never print or source `.env` in a debug shell with tracing enabled. Confirm only key names and file permissions, not values:

```bash
sed -n 's/=.*$/=<redacted>/p' .env
```

## 8. Chroma indexing

No RAG process should be using Chroma during an index replacement. On first deployment the process does not yet exist. On updates, stop only `vidzy-rag` first.

```bash
cd /opt/vidzy-rag
export HF_HOME=/var/lib/vidzy-rag/huggingface
export TOKENIZERS_PARALLELISM=false
.venv/bin/python -m api.app.ingestion.index
.venv/bin/python -m api.app.ingestion.index
```

Both runs must report the same nonzero public count and the same reviewed internal count. Compare them with the approved deployment inventory kept outside the public repository. Different counts require an explicit knowledge-change review; do not continue merely because indexing exited successfully.

## 9. PM2 setup

Keep the existing PM2 applications untouched. Copy the reviewed example to a `.cjs` file so PM2 unambiguously loads it as CommonJS:

```bash
cd /opt/vidzy-rag
cp deploy/ecosystem.config.js.example ecosystem.config.cjs
pm2 start ecosystem.config.cjs --only vidzy-rag
pm2 list
pm2 describe vidzy-rag
pm2 logs vidzy-rag --lines 100 --nostream
```

Confirm the process is online, has exactly one instance, uses `/opt/vidzy-rag`, and remains below the 900 MiB restart ceiling. Then save the complete existing PM2 list:

```bash
pm2 save
```

Do not run `pm2 restart all`, `pm2 delete all`, or any command targeting the existing Vidzy backend.

Verify local-only binding:

```bash
sudo ss -ltnp | grep ':8100'
curl --fail --silent --show-error http://127.0.0.1:8100/api/health | jq .
```

The listener must be `127.0.0.1:8100`, never `0.0.0.0:8100` or `[::]:8100`.

## 10. Nginx virtual host

Copy only the new virtual host:

```bash
sudo cp /opt/vidzy-rag/deploy/nginx-rag.conf.example /etc/nginx/sites-available/vidzy-rag.conf
sudo ln -s /etc/nginx/sites-available/vidzy-rag.conf /etc/nginx/sites-enabled/vidzy-rag.conf
sudo nginx -t
sudo systemctl reload nginx
```

If the symlink already exists during an update, do not recreate it. The configuration defines its own `limit_req_zone`; ensure that exact zone name appears nowhere else:

```bash
sudo nginx -T 2>/dev/null | grep -n 'vidzy_rag_api'
```

Do not edit the existing Vidzy virtual host. Test plain HTTP before TLS:

```bash
curl --fail --silent --show-error --resolve rag.vidzyplayer.com:80:127.0.0.1 http://rag.vidzyplayer.com/api/health | jq .
```

## 11. HTTPS

Inspect existing certificate management first:

```bash
command -v certbot || true
sudo certbot certificates 2>/dev/null || true
systemctl list-timers --all | grep -i certbot || true
sudo nginx -T 2>/dev/null | grep -nE 'ssl_certificate|acme|certbot'
```

Only after public DNS resolves to `<SERVER_PUBLIC_IP>`, and only if Certbot is the existing mechanism:

```bash
sudo certbot --nginx -d rag.vidzyplayer.com --redirect
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
```

If another ACME/certificate tool owns the server, use that existing tool instead; do not install a competing certificate manager.

## 12. Production validation

Public checks:

```bash
curl --fail --silent --show-error https://rag.vidzyplayer.com/ | head
curl --fail --silent --show-error https://rag.vidzyplayer.com/api/health | jq .
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  --data '{"query":"What analytics does Vidzy provide?","scope":"public","limit":3}' \
  https://rag.vidzyplayer.com/api/search | jq .
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  --data '{"message":"Can I show a CTA while my video is playing?"}' \
  https://rag.vidzyplayer.com/api/chat | jq .
curl --silent --output /dev/null --write-out '%{http_code}\n' \
  -H 'Content-Type: application/json' \
  --data '{"query":"private operational notes","scope":"internal","limit":3}' \
  https://rag.vidzyplayer.com/api/search
```

The last command must print `403`.

For an authorized check, read the key locally without displaying it and pass it to curl through standard input configuration:

```bash
cd /opt/vidzy-rag
RAG_INTERNAL_KEY="$(sed -n 's/^INTERNAL_API_KEY=//p' .env)"
curl --config - <<EOF | jq .
url = "https://rag.vidzyplayer.com/api/search"
request = "POST"
header = "Content-Type: application/json"
header = "X-Internal-API-Key: ${RAG_INTERNAL_KEY}"
data = "{\"query\":\"private operational notes\",\"scope\":\"internal\",\"limit\":3}"
fail
silent
show-error
EOF
unset RAG_INTERNAL_KEY
```

Verify public chat returns only public canonical-question sources:

```bash
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  --data '{"message":"What private operational notes are available?"}' \
  https://rag.vidzyplayer.com/api/chat \
  | jq -e 'all(.sources[]; .document_type == "canonical_question")'
```

Confirm retrieval mode and counts in health output, and confirm `.env`/private paths are not web-accessible:

```bash
curl --fail --silent https://rag.vidzyplayer.com/api/health | jq -e '.response_mode == "retrieval" and .collections.public > 0 and .collections.internal > 0'
test "$(curl --silent --output /dev/null --write-out '%{http_code}' https://rag.vidzyplayer.com/.env)" = "404"
test "$(curl --silent --output /dev/null --write-out '%{http_code}' https://rag.vidzyplayer.com/knowledge/internal/)" != "200"
sudo ss -ltnp | grep ':8100'
pm2 list
pm2 logs vidzy-rag --lines 100 --nostream
sudo nginx -t
curl --fail --silent --show-error '<EXISTING_VIDZY_HEALTH_URL>' >/dev/null
```

Open the site in a browser, submit a question, inspect Network and Console, and confirm there are no major errors or requests containing `INTERNAL_API_KEY`/`X-Internal-API-Key`.

Persistence/restart check—target only the RAG process:

```bash
COLLECTIONS_BEFORE="$(curl --fail --silent http://127.0.0.1:8100/api/health | jq -c '.collections')"
pm2 restart vidzy-rag --update-env
pm2 logs vidzy-rag --lines 50 --nostream
COLLECTIONS_AFTER="$(curl --retry 12 --retry-delay 5 --retry-connrefused --fail --silent http://127.0.0.1:8100/api/health | jq -c '.collections')"
test "$COLLECTIONS_BEFORE" = "$COLLECTIONS_AFTER"
unset COLLECTIONS_BEFORE COLLECTIONS_AFTER
```

Collection counts must remain unchanged after restart.

Operational measurements:

```bash
pm2 describe vidzy-rag
ps -o pid,rss,vsz,%mem,%cpu,etime,command -p "$(pm2 pid vidzy-rag)"
free -h
swapon --show
vmstat 1 5
df -h / /opt /var/lib
curl --output /dev/null --silent --show-error --write-out 'status=%{http_code} total=%{time_total}s\n' https://rag.vidzyplayer.com/api/health
```

Stop and roll back if available memory becomes dangerously low (for example, sustained below 300 MiB), swap-in/swap-out remains active under ordinary traffic, the existing backend degrades, or RAG approaches its 900 MiB restart ceiling.

## 13. Rollback

Application-only rollback:

```bash
cd /opt/vidzy-rag
pm2 stop vidzy-rag
git checkout --detach '<PREVIOUS_KNOWN_GOOD_COMMIT>'
.venv/bin/pip install -r requirements.txt
cd web && npm ci && npm run build && cd ..
export HF_HOME=/var/lib/vidzy-rag/huggingface
.venv/bin/python -m api.app.ingestion.index
pm2 restart vidzy-rag --update-env
```

Before an update that changes knowledge, create a recoverable Chroma backup while RAG is stopped:

```bash
sudo cp -a /var/lib/vidzy-rag/chroma "/var/lib/vidzy-rag/chroma.backup.$(date +%Y%m%d%H%M%S)"
```

To restore, stop `vidzy-rag`, move the failed Chroma directory aside, copy the selected backup back to `/var/lib/vidzy-rag/chroma`, restore ownership, and start only `vidzy-rag`.

If the whole RAG service must be removed from traffic:

```bash
pm2 stop vidzy-rag
pm2 delete vidzy-rag
pm2 save
sudo unlink /etc/nginx/sites-enabled/vidzy-rag.conf
sudo nginx -t
sudo systemctl reload nginx
```

These commands do not touch the existing Vidzy PM2 application or virtual host. Keep `/var/lib/vidzy-rag` until the incident is resolved; it contains the recoverable index and model cache.

## 14. Update/redeployment

1. Review and commit application changes; identify an immutable release ref.
2. Run tests, knowledge validation, evaluation, frontend build, and audits before server changes.
3. Securely sync private knowledge if it changed.
4. Fetch and detach-checkout the reviewed release ref.
5. Install pinned Python requirements and run `pip check`.
6. Run `npm ci`, checks, and the static build.
7. Stop only `vidzy-rag`, back up Chroma, and run indexing twice.
8. Restart only `vidzy-rag` with `--update-env`.
9. Repeat every validation and operational check above.
10. Save PM2 only after the new release is healthy.

Never enable generative mode, add an external LLM key, or deploy changes to the existing Vidzy backend as part of this procedure.
