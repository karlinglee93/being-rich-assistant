#!/usr/bin/env zsh

load_local_env_vars() {
  emulate -L zsh
  set -euo pipefail

  # Best effort to find the project root
  # This works when called from project root or when sourced from scripts/
  local ROOT_DIR LOCAL_ENV_FILE
  
  if [[ -f ".env.local" ]]; then
    # Already in project root
    ROOT_DIR="."
  elif [[ -f "../.env.local" ]]; then
    # In scripts directory
    ROOT_DIR=".."
  else
    # Fallback: try to find git root or use current directory
    ROOT_DIR="${(%):-/}"
  fi
  
  ROOT_DIR="$(cd "$ROOT_DIR" && pwd)"
  LOCAL_ENV_FILE="$ROOT_DIR/.env.local"

  if [[ ! -f "$LOCAL_ENV_FILE" ]]; then
    echo "❌ Missing $LOCAL_ENV_FILE"
    echo "📝 Create it from .env.local.example and configure your credentials."
    return 1
  fi

  set -a
  source "$LOCAL_ENV_FILE"
  set +a

  # Track what was loaded
  local loaded_vars=()

  # Check and export GitHub token (optional)
  if [[ -n "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
    export GITHUB_PERSONAL_ACCESS_TOKEN
    loaded_vars+=("✓ GitHub MCP token")
  fi

  # Check and export IBKR credentials (optional but recommended)
  if [[ -n "${IBKR_API_KEY:-}" && -n "${IBKR_API_SECRET:-}" && -n "${IBKR_ACCOUNT_ID:-}" ]]; then
    export IBKR_API_KEY
    export IBKR_API_SECRET
    export IBKR_ACCOUNT_ID
    loaded_vars+=("✓ IBKR API credentials")
  elif [[ -n "${IBKR_API_KEY:-}" || -n "${IBKR_API_SECRET:-}" || -n "${IBKR_ACCOUNT_ID:-}" ]]; then
    echo "⚠️  Warning: Incomplete IBKR credentials in $LOCAL_ENV_FILE"
    echo "   Please set IBKR_API_KEY, IBKR_API_SECRET, and IBKR_ACCOUNT_ID"
  fi

  if [[ ${#loaded_vars[@]} -eq 0 ]]; then
    echo "⚠️  No credentials found in $LOCAL_ENV_FILE"
    echo "   Update it with GITHUB_PERSONAL_ACCESS_TOKEN and/or IBKR credentials"
    return 1
  fi

  # Show what was loaded
  echo "🔐 Environment variables loaded from $LOCAL_ENV_FILE"
  for var in "${loaded_vars[@]}"; do
    echo "   $var"
  done

  return 0
}

load_local_env_vars "$@"