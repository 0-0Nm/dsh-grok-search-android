# C4/C5 Android original-core experiment

## Result

The original plugin MCP transport and selected search-orchestration suites executed successfully on the actual Android phone, using Android/bionic Node24.22.2. This is not the earlier Linux/musl baseline and is not an ordinary APK acceptance result.

- Device: V2463A, Android16/API36, arm64-v8a, Shizuku UID2000.
- Runtime: Node24.22.2 extracted from signed Termux repository packages; no Termux App or package installation scripts used. This is an independent temporary CLI runtime and 9 dependency libraries.
- Original plugin: df34daebaf3ea28e1da764f5257a8084c1944b21.
- Original Rust backend: be5fe87db22939de9405a7e9c70b1e43f7151214; binary reports 0.1.26.
- 1197 original-core payload files verified before and after tests; original business modules and tests not edited.

## Independent results

| Item | Result |
|---|---|
| Runtime Android platform/ABI, fs, crypto, Unicode, Intl, abort APIs, child process | passed |
| Original mcp-search.mjs::probeMcpHandshake with real SDK and Rust backend | passed: version 0.1.26, toolsDeclared=true, exited=true |
| provider-core.test.mjs | included in 113/113 passed |
| provider-mcp.test.mjs | included in 113/113 passed |
| routed-search.test.mjs | included in 113/113 passed |
| source-adapters.test.mjs | included in 113/113 passed |
| source-chain.test.mjs | included in 113/113 passed |
| Mock primary success, failure fallback, all sources fail, total timeout, caller cancellation | passed in original suites; exact case names in JSON receipt |
| Real external search | not_run |
| Target Android AI client integration | not_run |
| Ordinary distributable APK/App sandbox | not_run |
| UI | not implemented |

The original SDK probe launches the verified Rust backend and confirms shutdown. The original tests use offline stdio fixtures and injected mock responses; no paid or real search was sent. Five suite-process network guards report platform=android and zero intercepted network attempts. The guard intercepts application APIs; it is not OS-level network isolation or a formal network trace.

## Runtime configuration and recorded failure

The first suite launcher omitted OPENSSL_CONF; Node attempted the package's original /data/data/com.termux/... path and exited 13 before starting tests. A separate v24 launcher supplies the existing local openssl-empty.cnf and CA path, as the successful native runtime probe already did. No system permissions, SELinux setting, original business code or test assertions were changed. The old launcher and failure directory remain preserved.

The original source filters inherited LD_LIBRARY_PATH. This behavior was not weakened. Upstream's DSH_TEST_NODE test override points to a lab fixture launcher which restores only the relocated Node's library/config paths for test fixtures. The actual original Rust backend does not depend on that wrapper.

Node22's earlier source compilation run 42349282972 timed out at the 65-minute budget; Node24 is a different signed-prebuilt CLI experiment, not a falsely claimed successful Node22 build.

## Reproduction boundary

Use the recorded SHA256 identities in the JSON receipt and an independent shell-owned test directory. Reuse the original upstream test files, the validated flattened core payload and the unchanged Rust binary. Node24 startup requires LD_LIBRARY_PATH pointing to the bundled lib directory and OPENSSL_CONF pointing to its local configuration. The v24 test launcher and verifier are included in tests/ and experiments/. Tests are bounded to 45 seconds; the external wrapper must allow their cleanup margin.

The exact pinned upstream core is used; DSH bundle/UI/services were not fully ported. A production Android host interface, app-private configuration, runtime packaging, App UID execution restrictions, lifecycle/foreground requirements, DNS/TLS with a real API and redistribution notices still require investigation. Root/Shizuku is a current test context, not an approved final product requirement.

## Next

Validate a minimal ordinary APK packaging and runtime-start path without adding a full UI or account system. APK installation/launch will require separate explicit consent before changing device state. A real paid search and target-client integration are separate later acceptance items.
