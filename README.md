# dsh-grok-search-android

Unofficial Android adaptation feasibility experiments for [dsh-grok-search](https://github.com/Lain-in-coding/dsh-grok-search). Preserve the original Rust search backend and JavaScript orchestration rather than replacing the project with a different search system.

## Current scope

The first manual workflow cross-compiles the original backend for Android/bionic `aarch64-linux-android`, using native API 26 as an experimental compiler setting. This is **not** an APK minSdk decision. No UI, account system, hosted search server, or real paid search request is added.

Pinned plugin reference: `df34daebaf3ea28e1da764f5257a8084c1944b21`. Pinned backend: GrokSearch-rs `v0.1.26`, commit `be5fe87db22939de9405a7e9c70b1e43f7151214`. Upstream release CI injects tag version 0.1.26 into source manifests; this experiment records and restricts that version-only change.

## Separate acceptance results

| Acceptance | Status before the first run |
|---|---|
| Android backend compilation | Not yet verified |
| Backend launch on an Android device | Not run |
| MCP handshake and tools discovery | Not run |
| Original plugin orchestration under an Android adapter | Not run |
| Mock success/fallback/failure/timeout/cancellation | Not run |
| Real search with an approved request budget | Not run |
| Target Android AI client integration | Not run |
| Ordinary distributable APK | Not run |

## Build experiment

Run the manual **Android backend compile experiment** workflow. Rust 1.90.0 and NDK 27.3.13750724 are fixed. The exact preinstalled NDK is checked from source.properties; sdkmanager is not assumed to be on PATH. Dependencies are vendored and checked before compiling in a no-network, clean-environment Linux sandbox. The GitHub-hosted runner is a **cross-compilation host**, not an Android runtime. No PAT or repository secret is supplied to build scripts.

Artifacts retain build logs, version-only diff, lock/provenance records, execution traces, ELF metadata, hashes and (only if produced) the Android binary. Failure artifacts remain available. Consult the actual run conclusion; workflow presence alone is not success. Artifacts retain the backend MIT license; dependency notice completeness still needs a redistribution review.
