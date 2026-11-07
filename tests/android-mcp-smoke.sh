#!/system/bin/sh
set -eu
D="$1"
test -x "$D/grok-search-rs"
R=$(mktemp -d "$D/mcp-anon.XXXXXXXX")
printf 'MCP_TEST_DIR=%s\n' "$R"
mkdir "$R/home" "$R/tmp"
pid=''
cleanup() {
  trap - EXIT HUP INT TERM
  if [ -n "$pid" ]; then
    kill -TERM "$pid" 2>/dev/null || true
    for n in 1 2 3 4 5 6 7 8 9 10; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.1
    done
    kill -KILL "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT HUP INT TERM
env -i PATH=/system/bin:/system/xbin HOME="$R/home" TMPDIR="$R/tmp" \
  GROK_SEARCH_CONFIG="$R/no-config.toml" \
  GROK_SEARCH_AUTH_MODE=api_key \
  GROK_SEARCH_API_KEY=handshake-only-synthetic-not-a-real-key \
  GROK_SEARCH_URL=http://127.0.0.1:9 GROK_SEARCH_MODEL=offline-handshake \
  GROK_SEARCH_TIMEOUT_SECONDS=5 \
  "$D/grok-search-rs" 2> "$R/stderr.txt" |&
pid=$!
printf 'BACKEND_PID=%s\n' "$pid"
request='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"android-local-port-probe","version":"0.1.0"}}}'
printf '%s\n' "$request" > "$R/requests.jsonl"
print -r -p -- "$request"
IFS= read -r -p -t 8 response || { printf 'INITIALIZE_READ_FAILED\n'; cat "$R/stderr.txt"; exit 1; }
printf '%s\n' "$response" > "$R/responses.jsonl"
printf 'INITIALIZE_RESPONSE=%s\n' "$response"
request='{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'
printf '%s\n' "$request" >> "$R/requests.jsonl"
print -r -p -- "$request"
request='{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
printf '%s\n' "$request" >> "$R/requests.jsonl"
print -r -p -- "$request"
IFS= read -r -p -t 8 response || { printf 'TOOLS_READ_FAILED\n'; cat "$R/stderr.txt"; exit 1; }
printf '%s\n' "$response" >> "$R/responses.jsonl"
printf 'TOOLS_RESPONSE=%s\n' "$response"
cleanup
pid=''
printf 'PROCESS_REAPED=true\n'
printf 'NO_TOOL_CALLS_SENT=true\n'
printf 'MCP_TRANSCRIPT=%s\n' "$R/responses.jsonl"
