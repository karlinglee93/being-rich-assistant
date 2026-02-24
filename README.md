# Being Rich Assistant API (MVP)

Simple FastAPI MVP for real stock data and basic price analytics.

## Features

- Get latest stock price by ticker
- Get historical OHLC data by date range
- Compute simple analytics (SMA, daily return, annualized volatility)

## Tech Stack

- FastAPI
- ib_insync (Interactive Brokers API)
- pandas / numpy
- pytest

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run API:

```bash
uvicorn app.main:app --reload
```

Open docs:

- http://127.0.0.1:8000/docs

## Endpoints

- `GET /health`
- `GET /api/v1/market/price?ticker=AAPL`
- `GET /api/v1/market/history?ticker=AAPL&start_date=2026-01-01&end_date=2026-01-10`
- `GET /api/v1/analytics/summary?ticker=AAPL&start_date=2026-01-01&end_date=2026-01-10&sma_window=5`

## Notes

- Market data is fetched on demand (no DB/cache in this MVP).
- Data source is `Interactive Brokers (IBKR) API` via `ib_insync`. Requires TWS (Trader Workstation) or IB Gateway to be running locally.
- Ensure your IBKR_HOST and IBKR_PORT settings match your TWS/Gateway configuration (.env file).

## Run Tests

```bash
pytest -q
```

## GitHub MCP Setup

This project includes a VS Code MCP server config at `.vscode/mcp.json` for GitHub.

### 1) Create a GitHub Personal Access Token

- Go to GitHub settings and create a token with the minimum scopes you need.
- Typical MVP scopes: `repo` and `read:org`.

### 2) Export token in your shell

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
```

You can also place it in your local environment management flow based on `.env.example`.

For this workspace, a local helper is included:

```bash
cp .env.local.example .env.local
# edit .env.local and set GITHUB_PERSONAL_ACCESS_TOKEN
source scripts/load_github_mcp_token.zsh
```

`.env.local` is gitignored to keep your token out of version control.

### 3) Ensure Node.js is available

The MCP config runs:

```bash
npx -y @modelcontextprotocol/server-github
```

Install Node.js if `npx` is not available.

### 4) Start using MCP in VS Code

- Open this workspace in VS Code.
- The GitHub MCP server will be available from the workspace MCP configuration.
