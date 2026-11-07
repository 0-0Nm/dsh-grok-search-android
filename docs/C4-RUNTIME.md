# C4: original JS runtime / host experiment

Status: pending, not an Android App or completed plugin adaptation.

The plugin declares Node >=22 and uses fs, crypto, child_process, ESM and the pinned MCP client. The inspected nodejs-mobile main/release remains Node18.20.4, so it is not silently substituted.

Candidate: official Node v22.21.1, tag commit 6ac4ab19ad02803f03b54501193397563e99988e. The official source tar.xz is fixed to SHA256 487d73fd4db00dc2420d659a8221b181a7937fbc5bc73f31c30b1680ad6ded6a. Upstream BUILDING.md explicitly does not support Android, despite retaining an Android build entry; compilation and execution therefore require experiments.

Reviewed build entry: android-configure/android_configure.py, configure/configure.py, Makefile, tools/gyp_node.py, common.gypi, node.gyp and current V8 trap-handler guard. No stale optional Android patch is applied preemptively. Dependencies are bundled in the release source, downloads are disabled during configure/build, and npm/corepack are excluded from the resulting runtime.

A separate writable build copy is inside a clean no-network namespace; host HOME/credentials are absent, toolchain/system mounts are read-only, and the actual build runs nonroot with all capabilities zero. Original source hashes are independently checked afterward. This is not an exhaustive supply-chain safety proof.

The standard public-repository Ubuntu24.04 runner is used, not a larger runner. Native API26 and NDK27.3.13750724 are fixed. Build concurrency is bounded by available memory/CPUs (maximum4); the build has a 65-minute process limit and the job75-minute limit. The project does not install Termux, SDKs, APKs or toolchains on the phone.

A second independent job packages the pinned original JS core, original tests and lockfile-resolved npm dependencies with lifecycle scripts disabled and peer-host installation suppressed. It does not import the DSH bundle/main entry or ship the full DSH host.

The first phone probe will execute the original mcp-search.mjs::probeMcpHandshake, including its real SDK, child process and stdio transport against the verified original Rust binary. This is stronger than a new handwritten JSON-RPC client, but is still not proof of full routed-search behavior, real search, an AI client or an ordinary APK.

Next, the selected original routed/provider/source tests may be run on Android with isolated configuration and synthetic fixtures, preserving the distinction between mock cases and real searches. No real API credentials or paid searches are part of this workflow.

UI and Elanor references remain a later phase; this experiment does not select a UI stack or add product/account features.
