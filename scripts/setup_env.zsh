#!/usr/bin/env zsh
# Setup environment variables from .env and .env.local
# 
# USAGE: source scripts/setup_env.zsh
#
# When to use:
# - Before using GitHub MCP (VS Code integration)
# - Before running shell scripts that need credentials
# - Before using curls/API calls that need auth tokens
#
# Does NOT need to be called for FastAPI app (it auto-loads .env files)

setup_env() {
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

  # Check and export Alpha Vantage credentials (optional but recommended)
  if [[ -n "${ALPHA_VANTAGE_API_KEY:-}" ]]; then
    export ALPHA_VANTAGE_API_KEY
    loaded_vars+=("✓ Alpha Vantage API credentials")
  elif [[ -n "${ALPHA_VANTAGE_BASE_URL:-}" ]]; then
    echo "⚠️  Warning: Missing ALPHA_VANTAGE_API_KEY in $LOCAL_ENV_FILE"
    echo "   Please set ALPHA_VANTAGE_API_KEY"
  fi

  if [[ ${#loaded_vars[@]} -eq 0 ]]; then
    echo "⚠️  No credentials found in $LOCAL_ENV_FILE"
    echo "   Update it with GITHUB_PERSONAL_ACCESS_TOKEN and/or Alpha Vantage credentials"
    return 1
  fi

  # Show what was loaded
  echo "🔐 Environment variables loaded from $LOCAL_ENV_FILE"
  for var in "${loaded_vars[@]}"; do
    echo "   $var"
  done

  return 0
}

setup_env "$@"