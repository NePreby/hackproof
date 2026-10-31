<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hackmeridian-light.png">
  <img src="assets/hackmeridian-dark.png" alt="HackMeridian" width="200">
</picture>

# HackProof

HackMeridian 2026 submissions, rebuilt from Stellar testnet and linked to their GitHub repos by exact matches. Browse the projects, check each match on Stellar Expert and GitHub, download the data, or ask the chat.

Each project has an evidence tier. `verified` means an exact repo to chain match with activity in the window. `likely` (shown as "Code only") means a Stellar dependency and at least 5 commits in the window, in a repo created or updated for the event. The window is set in `config/hackmeridian-2026.yaml`.

## Layout

- `apps/web`: React, Vite and shadcn/ui
- `apps/api`: FastAPI, asyncpg and Postgres, managed with uv
- `apps/api/src/hackproof/chat/system-prompt.md`: the chat prompts
- `config/integrations.yaml`: the Stellar integration partners and how each is detected, by package in any language or by API host in code

## Run

```sh
cp .env.example .env
docker compose up -d db
pnpm install
pnpm dev:api
pnpm dev:web
```

The web app is on `localhost:5173` and proxies `/api` to port 8000. Set `ANTHROPIC_API_KEY` to enable the chat.

## Data

Run from `apps/api`. `discover` and `scan` need `HACKPROOF_GITHUB_TOKEN`.

```sh
uv run hackproof sync
uv run hackproof discover
uv run hackproof scan
uv run hackproof reconcile
uv run hackproof export
```

Published schemas for data exports and public API models are indexed in [`apps/web/public/schema/index.json`](apps/web/public/schema/index.json) (`https://hackproof.vercel.app/schema/index.json`).

## Checks

```sh
cd apps/api && uv run ruff check . && uv run ruff format --check . && uv run pytest
pnpm lint && pnpm format:check && pnpm build
```
