# C4 phone-side continuation harness

Status: deployment prepared; the original JS has **not** yet executed on the Android/bionic Node candidate. Backend C1-C3 remain separate passed results.

## Prepared and checked

- Original business sources and tests remain unchanged at plugin commit df34daebaf3ea28e1da764f5257a8084c1944b21.
- A symlink-free deployment projection retains all original file bytes. The sole npm .bin/node-which link is materialized from its package target, not replaced with new logic. The original archives remain preserved.
- Two verification adapters are added outside upstream/: a manifest verifier and the previously tested no-network guard.
- Archive SHA256: e635a9f7bb12d555e150e00137c5572d2320e0b2bd98bded7cfb7c90b41ea3dc.
- Manifest SHA256: 7075e705cd3a42279be0f3eb36aa9fc58d85247cf3c7e4509c983511099ee5a9.
- 1197 manifest files verified before deployment; 1198 regular files including the manifest and zero symlinks observed after actual Android extraction.
- Actual /system/bin/sh syntax checks passed. Adapter JS syntax also parsed under the existing Linux/Alpine Node runtime; that parsing is not Android execution.

## Preserve the original environment boundary

Original src/core/mcp-search.mjs intentionally does not inherit LD_LIBRARY_PATH in SYSTEM_ENV. Do not weaken this whitelist for testing. If the native Node executable needs its bundled libc++ library, Node-based fixture children need the same controlled local library path.

The probe creates a dedicated node-fixture-launcher, which restores only the verified runtime's own lib/ and execs that runtime. The original test/provider-mcp.test.mjs:14 already accepts DSH_TEST_NODE as a fixture-runtime override. This is test setup, not a replacement MCP client or modified search implementation. Real Rust-backend calls still use its verified original binary.

## Acceptance order

1. Independently verify the native Node artifact/source identity, its Android ELF and runtime dependency hashes before executing it. No runtime hash is invented or accepted from an unverified file.
2. tests/android-original-core-probe.sh checks the supplied runtime hash, original backend hash and manifest hash before any Node invocation. The read-only verification adapter then hashes every manifest file and requires Android/arm64/Node22.21.1.
3. The unchanged original probeMcpHandshake is invoked against the actual Rust backend using only synthetic handshake configuration. No tools/call is sent by this probe.
4. Only after a successful probe, tests/android-original-core-suite.sh runs the five selected unchanged upstream test files with independent HOME/TMP, bounded execution and no real network. This is the planned Android counterpart to the 113-test Linux/musl baseline.
5. Independently parse result files and process cleanup evidence; neither script presence nor deployment counts as a pass.

Both scripts require explicit absolute ASCII test paths and actual public SHA256 values. They do not ask for real API credentials. The phone source deployment is under a new shell-owned /data/local/tmp project directory; no APK, Termux installation, SDK, global environment or device setting is changed. This does not prove ordinary APK sandbox behavior or distribution.
