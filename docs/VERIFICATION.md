# Android local backend verification

## Conclusion

The original Rust backend was cross-compiled for Android/bionic, launched on an actual Android device, and completed a local stdio MCP initialization and tool discovery exchange. **This does not complete the dsh-grok-search Android adaptation.** The original plugin orchestration has not yet run through an Android host adapter.

## Fixed inputs

- Plugin reference: `df34daebaf3ea28e1da764f5257a8084c1944b21`.
- Backend: GrokSearch-rs tag `v0.1.26`, commit `be5fe87db22939de9405a7e9c70b1e43f7151214`.
- Successful experiment commit: `bf82a34b4399ccba9953b7ba5a69b95b179691cb`.
- GitHub Actions run: `42344734516` (#5), conclusion `success`.
- Rust 1.90.0; NDK r27d / 27.3.13750724; `aarch64-linux-android`; native API 26; no HTTP feature. Native API is not an APK minSdk choice.
- Root-package version injection only, following the upstream release workflow; registry dependency versions/checksums remain locked.

## Separate acceptance results

| Item | Status | Evidence / limit |
|---|---|---|
| Backend Android cross-compilation | passed | Successful compile, sandbox audit and ELF checks in run #5 |
| Android native CLI startup | passed | Android 16 / API 36 / arm64-v8a, Shizuku shell UID2000; `grok-search-rs 0.1.26`; not ordinary APK sandbox |
| MCP initialization | passed | Negotiated 2025-06-18; server identity/version matched |
| MCP tool discovery | passed | web_search, get_sources, web_fetch, web_map, doctor |
| Original plugin Android orchestration | not_run | Need Android-compatible JS runtime and minimal host seam, preserving upstream ESM |
| Original orchestration mock cases | not_run | Main success, fallback, all failures, timeout and cancellation remain pending |
| Real search | not_run | No tools/call sent, no real API credential used |
| Target Android AI client | not_run | Client not selected; generic compatibility not claimed |
| Ordinary distributable APK | not_run | No APK built or installed |

## Artifact identity

- Artifact ID: `13562982656`; archive bytes: `2484349`.
- Archive SHA-256: `cd63cf8290c35d129f24dba60cdd5b8d9823c60abe0164ee48b892e2a1f6f3b4`, independently matched GitHub digest.
- Native binary bytes: `3570808`.
- Binary SHA-256: `8e5696d97f8eef4aded6f48fa2be52543cba417570566044bbd0087ec6dac838`.
- ELF64 little-endian AArch64; interpreter `/system/bin/linker64`; PT_LOAD alignment 0x4000. No glibc loader or libc.so.6 linked.

## Actual device test

The binary was copied to a fresh shell-owned `/data/local/tmp` directory and checked against the build hash before use. Version startup had a 10-second limit. The MCP smoke script used an empty isolated HOME/config location, synthetic handshake-only configuration and a loopback-discard endpoint. It sent exactly:

1. initialize
2. notifications/initialized
3. tools/list

Both JSON-RPC responses were parsed independently. stderr was empty; the test child was waited/reaped and a separate PID check found it absent. No search, doctor or other tool call was sent. These results prove local Android shell/backend behavior, not Android app process privileges, service lifetime, AI client acceptance or actual paid search.

Named FIFO creation was denied by Android before any backend launch. The failed directory was preserved. A standard anonymous mksh coprocess pipe was independently tested and used instead, without changing SELinux, storage permissions or device settings.

The script is intended for `/system/bin/sh` (Android mksh), not Bash. Place the verified binary as `grok-search-rs` in your own fresh test directory, then run:

```sh
timeout -k 2 25 /system/bin/sh tests/android-mcp-smoke.sh /data/local/tmp/YOUR_INDEPENDENT_TEST_DIR
```

Do not call this an ordinary APK integration test. Do not use a real key for this handshake-only smoke test.

## Failed experiments retained

| Run | Result | Actual reason / change |
|---|---|---|
| 42343416462 (#1) | failed before compile | sdkmanager absent from PATH; switched to exact verified preinstalled NDK |
| 42343653856 (#2) | failed before Cargo | unprivileged namespace loopback initialization denied; trusted root namespace setup followed by nonroot zero-capability entry |
| 42343939380 (#3) | failed during early compile | sandbox tmpfs permissions blocked rustc temporary files; fixed only tmpfs mode and added write preflight |
| 42344251650 (#4) | compilation passed, audit failed | exact Rust LLD, GCC13 collect2 and NDK wrapper bash paths missing from the audit list; original 1774 traces reviewed and replayed, arbitrary bash still rejected |
| 42344734516 (#5) | passed | compile, external observer audit, Android ELF checks and artifact upload all succeeded |

Each run corresponded to a distinct committed correction; there were no duplicate dispatches of the same commit. Failed logs/artifacts were not cleaned. None of these CI harness failures were presented as proof that the upstream backend could not support Android.

## Remaining boundary

The next most valuable experiment is a minimal Android-compatible runtime/host for the original JS orchestration. It must preserve routed-search, source-chain, source-adapters, search-executor and result mapping, and verify cancellation semantics rather than merely embedding a browser engine. No full DSH port, replacement search system, remote MCP middleman, full UI or account system has been introduced.

Backend license notice is included in third_party/GrokSearch-rs.LICENSE; full dependency redistribution notices still require a separate audit before distributing a product.
