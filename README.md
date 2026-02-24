# Being Rich Assistant API (MVP)

Simple FastAPI MVP for real stock data and basic price analytics.

## Features

- Get latest stock price by ticker
- Get historical OHLC data by date range
- Compute simple analytics (SMA, daily return, annualized volatility)

## Tech Stack

- FastAPI
- Interactive Brokers REST API (token-based)
- requests / pandas / numpy
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
- Data source is `Interactive Brokers REST API` using token-based authentication.
- No local services required - pure HTTP API calls.
- Requires valid IBKR API credentials configured in `.env`.

## Setup IBKR API Credentials

1. **Create `.env.local` from `.env.example`**:
   ```bash
   cp .env.example .env.local
   ```

2. **Get IBKR API credentials**:
   - Visit [IBKR API Dashboard](https://www.interactivebrokers.com/en/trading/ibkr-apis.php)
   - Generate API Key and Secret
   - Note your Account ID (e.g., `U12345678`)

3. **Add credentials to `.env.local`** (never commit this file):
   ```env
   # .env.local
   IBKR_API_KEY=your_api_key_here
   IBKR_API_SECRET=your_api_secret_here
   IBKR_ACCOUNT_ID=your_account_id_here
   ```

4. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Note: `.env.local` is gitignored and not committed to version control.

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
