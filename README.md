# AI Engineer Academy (Neural Academy)

Interactive training platform for modern AI/ML engineers: curriculum UI, architecture simulators, and evidence-backed Python labs.

## Stack

- **Web app:** React 19 + Vite 6 SPA served by Express (`server.ts`) on port `3000`
- **AI Mentor:** xAI Grok via `XAI_API_KEY` (optional; curriculum fallback without a key)
- **Labs:** `labs/module-1` … `labs/module-5` (isolated per-lab virtualenvs)

## Field atlas (positioning page)

Standalone static page in [`atlas/`](./atlas/): who this is for, what is inside, what not to expect, and a filterable map of CPU-proved vs survey vs optional-live vs thin topics.

```bash
npm run dev   # then http://localhost:3000/atlas/
```

Or open `atlas/index.html` without the applet. This is a shared learning-space pitch, not a paid product page. The in-app certificate remains a local keepsake.

## Quick start (web)

```bash
cp .env.example .env   # set XAI_API_KEY for live mentor replies
npm install
npm run dev            # http://localhost:3000
```

Useful scripts:

| Command | Purpose |
| --- | --- |
| `npm run lint` | Typecheck SPA + `server.ts` |
| `npm test` | Vitest unit tests (certificate, quiz lock, progress parse) |
| `npm run build` | Production Vite + server bundle |
| `npm run dev` | Express + Vite middleware (development) |

## Labs

Each lab has its own `requirements.txt`. Use a dedicated venv (dependencies conflict across labs):

```bash
cd labs/module-1-foundations
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

See each lab `README.md` for validation/evidence commands. Cloud-agent notes live in [`AGENTS.md`](./AGENTS.md).

## Certificate unlock (local progress)

Stored in browser `localStorage`. Requires:

1. All modules marked complete
2. Lab evidence confirmed for every module
3. Module quizzes **or** the program quiz at ≥60%

## License / status

Private training applet. The in-app certificate is a learning keepsake, not a vendor-accredited credential.
