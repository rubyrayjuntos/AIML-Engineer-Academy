# AI Engineer Academy

Interactive AI/ML engineering training platform. Two parts live in this repo:

- Root web app: React 19 + Vite 6 SPA served by an Express server (`server.ts`) that also proxies Gemini and code-simulation endpoints.
- `labs/module-1..5`: standalone Python exercises, each with its own `requirements.txt` and `pytest` suite (validated by the `.github/workflows/*-lab.yml` CI jobs).

## Cursor Cloud specific instructions

### Web app (root)
- Run in development with `npm run dev` (runs `tsx server.ts`, Express + Vite middleware) and listens on `http://0.0.0.0:3000`. There is no separate Vite port — the Express server serves the SPA.
- Lint is `npm run lint` (`tsc --noEmit`); build is `npm run build` (Vite + esbuild bundle of the server). The esbuild `import.meta` warning during build is benign — dev mode uses `tsx`, not the bundled `dist/server.cjs`.
- `GEMINI_API_KEY` is optional. Without it, `/api/ai/chat` returns high-quality canned "curriculum engine" fallback answers, so the AI Mentor and full UI work end-to-end with no secret. Set `GEMINI_API_KEY` (see `.env.example`) only to exercise real Gemini calls. Check `curl -s localhost:3000/api/health` to see `hasGeminiKey`.

### Python labs
- Each lab is isolated in its own virtualenv at `labs/module-*/.venv` because their dependencies conflict across labs (e.g. `mcp` in module-3 needs a newer `starlette` than `fastapi` in module-4). Do NOT install all lab requirements into one shared environment.
- Run a lab's tests with its own venv, e.g. `cd labs/module-1-foundations && ./.venv/bin/python -m pytest -q`.
- Some CI jobs also run scripts: module-1 `python -m app.pipeline`; module-4 `python -m app.benchmark`/`python -m app.evidence` (write to `artifacts/`, which is gitignored). Run these via the lab's `./.venv/bin/python`.
- System package `python3.12-venv` is required to create the venvs; it is installed into the VM image during environment setup (not in the update script).
