# Android local MCP connection experiment

Purpose: add a thin loopback transport/host seam without rewriting the original search core. Target client selected by user: current L3Hub. Read-only fork source at tree cf60ab8d3ed5894eb710f7bccdebaacfbe0d4fdd includes StreamableHTTPServer and custom headers; installed-client interoperability is not yet verified.

## Implemented

- 127.0.0.1-only stateless MCP HTTP POST/JSON endpoint; GET streaming intentionally unsupported (405).
- Locally generated bearer access token, private storage, no token in startup output or logs.
- Strict Host check, reject any Origin, bounded bodies/connections/in-flight requests; input validation and cancellation propagation.
- Original provider, source router, routed-search and release barrier assembled from pinned upstream core. External searches are disabled in the experiment entry point, regardless of any request.
- Android test APK v2 adds start/stop and local-token copy buttons. INTERNET permission is needed for loopback sockets. No service/background lifetime guarantee; Activity-scoped experiment only.

## Executed verification

The 9 transport tests passed both on existing Alpine/Linux and Android/bionic shell Node24.22.2. On Android, the original pinned MCP client SDK 2.4.0 connected to the endpoint, initialized, discovered web_search and received SEARCH_DISABLED. Original search was invoked zero times. These are not yet the installed L3Hub connection or AppUID HTTP tests.

## APK

Package org.dsh.androidprobe versionCode 2, targetSDK 36/minSDK 26. The v2 APK was built, signed and checked; it is not installed yet. Updating the existing test App, starting the local endpoint, and adding an isolated L3Hub test configuration require explicit user approval. No real paid search is authorized by this experiment.

The server exposes the original plugin's search tool only; it does not claim to expose every Rust backend tool. This is an experimental protocol subset, not blanket MCP compliance or production authentication certification. Local token headers are not OAuth.

## Source and reproduction

Original core stays at df34daebaf3ea28e1da764f5257a8084c1944b21; original Rust backend stays at be5fe87db22939de9405a7e9c70b1e43f7151214. Original business source is unchanged. Runtime/binary assets are not checked into Git. android/build.py records actual local source paths and requires the verified payload prepared in preceding experiments; it is not a turnkey build from this directory alone. Do not execute downloaded installers or supply secrets in build logs.

Do not present this as a complete MCP product: secure search configuration, real-provider validation under a request budget, installed-client interoperation, background lifecycle, release signing and complete redistribution notices remain pending.
