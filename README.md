# dsh-grok-search-android

Unofficial Android adaptation feasibility experiments for [dsh-grok-search](https://github.com/Lain-in-coding/dsh-grok-search). Preserve the original Rust search backend and JavaScript orchestration rather than replacing the project with a different search system.

## Current scope

The first manual workflow cross-compiles the original backend for Android/bionic `aarch64-linux-android`, using native API 26 as an experimental compiler setting. This is **not** an APK minSdk decision. No UI, account system, hosted search server, or real paid search request is added.

Pinned plugin reference: `df34daebaf3ea28e1da764f5257a8084c1944b21`. Pinned backend: GrokSearch-rs `v0.1.26`, commit `be5fe87db22939de9405a7e9c70b1e43f7151214`. Upstream release CI injects tag version 0.1.26 into source manifests; this experiment records and restricts that version-only change.

## Separate acceptance results

| Acceptance | Verified status |
|---|---|
| Android backend compilation | Passed — Actions run #5; AArch64 / Android linker |
| Backend launch on an Android device | Passed in Android 16 Shizuku shell (not APK sandbox) |
| MCP handshake and tools discovery | Passed locally over stdio; 5 tools discovered |
| Original plugin orchestration under an Android adapter | Original core mock execution passed in Android/bionic shell; APK host not yet tested |
| Mock success/fallback/failure/timeout/cancellation | Passed in selected unchanged upstream suites on Android/bionic Node24.22.2 |
| Real search with an approved request budget | Not run |
| Target Android AI client integration | Not run |
| Ordinary distributable APK | Not run |

## Build experiment

Run the manual **Android backend compile experiment** workflow. Rust 1.90.0 and NDK 27.3.13750724 are fixed. The exact preinstalled NDK is checked from source.properties; sdkmanager is not assumed to be on PATH. Dependencies are vendored and checked before compiling in a no-network, clean-environment Linux sandbox. The GitHub-hosted runner is a **cross-compilation host**, not an Android runtime. No PAT or repository secret is supplied to build scripts.

Artifacts retain build logs, version-only diff, lock/provenance records, execution traces, ELF metadata, hashes and (only if produced) the Android binary. Failure artifacts remain available. Consult the actual run conclusion; workflow presence alone is not success. Artifacts retain the backend MIT license; dependency notice completeness still needs a redistribution review.

## Recorded results

See [verification evidence and limits](docs/VERIFICATION.md), [local MCP smoke script](tests/android-mcp-smoke.sh), and [UI reference notes](docs/UI_REFERENCE.md). A working backend is not a completed Android adaptation of the original plugin. The original ESM orchestration, Android host adapter, approved real search, target AI client and ordinary APK distribution remain unverified.

## Android original-core milestone

The original plugin MCP module now handshakes with the original Rust backend on the actual Android phone. Five unchanged upstream test files pass **113/113 on Android/bionic Node24.22.2** (not the earlier Alpine/musl baseline). Original core payload hashes match before and after execution. This is a Shizuku shell experiment using a signed-repository Node runtime payload; no Termux App or APK was installed.

See [Android original-core results](docs/C4-ANDROID-RESULTS.md) and [machine-readable evidence](docs/evidence/original-core-android-turn12.json). Real searches, target-client integration and ordinary APK packaging/execution remain unverified. The earlier Node22 source-build run timed out after 65 minutes; it did not produce the runtime used here.
