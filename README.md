# Being Rich Assistant API (MVP)

Simple FastAPI MVP for real stock data and basic price analytics.

## Features

- Get latest stock price by ticker
- Get historical OHLC data by date range
- Compute simple analytics (SMA, daily return, annualized volatility)

## Tech Stack

- FastAPI
- Alpha Vantage REST API
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
- Data source is `Alpha Vantage REST API`.
- Uses free-tier Alpha Vantage endpoints (`GLOBAL_QUOTE`, `TIME_SERIES_DAILY` with `outputsize=compact`).
- Historical queries are limited to the compact window (roughly last 100 trading days).
- No local services required - pure HTTP API calls.
- Requires a valid Alpha Vantage API key configured in `.env.local`.

## Environment Configuration

### File Structure
- **`.env`** - Public configuration (safe to commit)
   - Contains default values for `APP_NAME`, `APP_VERSION`, `ALPHA_VANTAGE_BASE_URL`
   - Can include `FRONTEND_ORIGINS` for browser CORS allowlist
  - Never contains secrets
  
- **`.env.local`** - Local secrets (gitignored, never committed)
   - Contains your actual Alpha Vantage API key
  - Contains GitHub personal access token (if using MCP)
  - Copy from `.env.local.example` and fill in your values

### Setup Alpha Vantage API Credentials

1. **Create `.env.local` from `.env.local.example`**:
   ```bash
   cp .env.local.example .env.local
   ```

2. **Get an Alpha Vantage API key**:
   - Visit [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key)
   - Generate your free API key

3. **Edit `.env.local`** (never commit this file):
   ```env
   ALPHA_VANTAGE_API_KEY=your_actual_api_key
   ALPHA_VANTAGE_VERIFY_SSL=true
   ALPHA_VANTAGE_ALLOW_INSECURE_SSL_FALLBACK=true
   FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token  # optional
   ```

4. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```
   
   The app automatically loads variables from both `.env` and `.env.local` with `.env.local` taking precedence.

   If your local Python environment cannot validate TLS certificates, keep
   `ALPHA_VANTAGE_ALLOW_INSECURE_SSL_FALLBACK=true` (default) or set
   `ALPHA_VANTAGE_VERIFY_SSL=false` to force insecure HTTPS for local development.

## UI Client (Next.js)

The workspace includes a Next.js client in `../being-rich-assistant-client`.

Run the client:

```bash
cd ../being-rich-assistant-client
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000" > .env.local
npm run dev
```

Then open http://localhost:3000.

## Load Environment Variables in Shell

For GitHub MCP, shell scripts, or manual commands that need credentials:

```bash
source scripts/setup_env.zsh
```

This loads `GITHUB_PERSONAL_ACCESS_TOKEN` and Alpha Vantage credentials into your current shell.

**When to use:**
- ✅ Before using GitHub MCP in VS Code
- ✅ Before running shell scripts with credentials  
- ✅ Before manual curl/API calls
- ❌ NOT needed for running the FastAPI app (automatic)

## Run Tests

```bash
pytest -q
```

## GitHub MCP Setup

This project includes a VS Code MCP server config at `.vscode/mcp.json` for GitHub.

### 1) Create a GitHub Personal Access Token

- Go to GitHub settings and create a token with the minimum scopes you need.
- Typical MVP scopes: `repo` and `read:org`.

### 2) Load credentials in your shell

For this workspace, use the environment setup helper:

```bash
cp .env.local.example .env.local
# edit .env.local and set GITHUB_PERSONAL_ACCESS_TOKEN
source scripts/setup_env.zsh
```

This loads your GitHub token and Alpha Vantage credentials from `.env.local` into the shell (gitignored for security).

### 3) Ensure Node.js is available

The MCP config runs:

```bash
npx -y @modelcontextprotocol/server-github
```

Install Node.js if `npx` is not available.

### 4) Start using MCP in VS Code

- Open this workspace in VS Code.
- The GitHub MCP server will be available from the workspace MCP configuration.
