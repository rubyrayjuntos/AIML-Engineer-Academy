#!/usr/bin/env bash
# Optional Promptfoo track — not used by default CI / Cloud Agents.
set -euo pipefail

if [[ "${ACADEMY_PROMPTFOO:-}" != "1" ]]; then
  echo "Refusing to run: set ACADEMY_PROMPTFOO=1 to opt into Promptfoo." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/promptfoo"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found — install Node.js to run Promptfoo." >&2
  exit 1
fi

exec npx --yes promptfoo@0.103.3 eval -c promptfooconfig.yaml "$@"
