#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
destination="${1:-}"

if [[ -z "$destination" ]]; then
  echo "Optional archive audit utility." >&2
  echo "Usage: scripts/create-public-release.sh /absolute/output-directory" >&2
  exit 2
fi
if [[ "$destination" != /* || "$destination" == "/" ]]; then
  echo "Destination must be an absolute, non-root path." >&2
  exit 2
fi
if [[ -e "$destination" ]]; then
  echo "Destination already exists; refusing to overwrite it." >&2
  exit 2
fi

mkdir -p "$destination"
git -C "$repository_root" archive --format=tar HEAD | tar -xf - -C "$destination"

if find "$destination/knowledge" -path '*/internal/*' -o -name 'facts.jsonl' -o -name 'sources.jsonl' | grep -q .; then
  echo "Private knowledge unexpectedly appeared in release output." >&2
  exit 1
fi

echo "Public release audit archive created at $destination"
