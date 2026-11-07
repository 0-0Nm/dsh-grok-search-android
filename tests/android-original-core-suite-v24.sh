#!/system/bin/sh
set -eu
test "$#" -eq 4 || { printf 'usage: suite RUNTIME CORE C4_TEST_DIR NODE_SHA\n'; exit 2; }
RUNTIME="$1"; CORE="$2"; CASE="$3"; NODE_SHA="$4"
for path in "$RUNTIME" "$CORE" "$CASE"; do
 case "$path" in /*) ;; *) exit 2;; esac
 case "$path" in *[!A-Za-z0-9_./-]*) exit 2;; esac
done
test "${#NODE_SHA}" -eq 64; case "$NODE_SHA" in *[!a-f0-9]*) exit 2;; esac
ACTUAL=$(sha256sum "$RUNTIME/node"); test "${ACTUAL%% *}" = "$NODE_SHA"
test "$(cat "$CASE/probe-exit.txt")" = 0
test -x "$CASE/node-fixture-launcher"; test -f "$CORE/no-network-guard.mjs"
OUT=$(mktemp -d "$CASE/suite.XXXXXXXX"); mkdir "$OUT/home" "$OUT/tmp"
printf 'C4_SUITE_DIR=%s\n' "$OUT"
cd "$CORE/upstream"
set +e
timeout -k 3 45 env -i PATH="$RUNTIME:/system/bin:/system/xbin" HOME="$OUT/home" TMPDIR="$OUT/tmp" LD_LIBRARY_PATH="$RUNTIME/lib" OPENSSL_CONF="$RUNTIME/openssl-empty.cnf" SSL_CERT_FILE="$RUNTIME/ca-certificates.pem" \
 DSH_TEST_NODE="$CASE/node-fixture-launcher" LAB_EVIDENCE_DIR="$OUT" \
 "$RUNTIME/node" --import "$CORE/no-network-guard.mjs" --test --test-concurrency=1 \
 test/provider-core.test.mjs test/provider-mcp.test.mjs test/routed-search.test.mjs test/source-adapters.test.mjs test/source-chain.test.mjs \
 > "$OUT/test.log" 2>&1
RC=$?
set -e
printf '%s\n' "$RC" > "$OUT/exit-code.txt"
printf 'C4_SUITE_EXIT=%s\n' "$RC"
tail -30 "$OUT/test.log"
exit "$RC"
