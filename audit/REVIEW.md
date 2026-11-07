# Dependency build review

197 registry archives (39,605,058 compressed bytes) matched the upstream lock checksums. 45 build entry points and selected local helper/probe code were read before permitting an isolated build. Highest declared MSRV: 1.87.0; 31 packages omit an MSRV. Rust 1.90.0 meets declared minimums, but compilation is not yet proven.

Conditional approval only: fixed upstream revision and package hashes; no credentials or host HOME mounted; clean environment; read-only source/vendor/toolchains; only temporary build/output storage writable; OS-isolated networking plus Cargo frozen/offline; process and network-call evidence retained. No unrestricted execution approval.

ring/cc compile native assembly and C. Nondefault generation paths, including RING_PREGENERATE_ASM, are not enabled. libc probes emcc even for other targets; a missing emcc is not a reason to install it. Probe crates may invoke rustc and remove their own OUT_DIR/probe files.

Not exhaustively audited: proc macros, all C/ASM/Rust code, prebuilt objects, and nondefault build branches. Passing this experiment is not a supply-chain safety guarantee, device execution test, or whole-plugin adaptation.

Execution tracing uses an outer root observer; protected raw logs are never mounted inside the sandbox. A path allowlist does not prove code authenticity at writable build-output paths. execveat, incomplete required records, unknown successful executions and attempted Internet connections fail the experiment. On a failed compile, trace auditing still runs; ELF acceptance remains success-only.
