#!/usr/bin/env zsh

load_github_mcp_token() {
  emulate -L zsh
  set -euo pipefail

  local ROOT_DIR LOCAL_ENV_FILE
  ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  LOCAL_ENV_FILE="$ROOT_DIR/.env.local"

  if [[ ! -f "$LOCAL_ENV_FILE" ]]; then
    echo "Missing $LOCAL_ENV_FILE"
    echo "Create it from .env.local.example and set GITHUB_PERSONAL_ACCESS_TOKEN."
    return 1
  fi

  set -a
  source "$LOCAL_ENV_FILE"
  set +a

  if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
    echo "GITHUB_PERSONAL_ACCESS_TOKEN is not set in $LOCAL_ENV_FILE"
    return 1
  fi

  # export to parent shell when sourced
  export GITHUB_PERSONAL_ACCESS_TOKEN

  echo "GitHub MCP token loaded from $LOCAL_ENV_FILE"
}

load_github_mcp_token "$@"