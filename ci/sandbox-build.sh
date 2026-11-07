#!/usr/bin/env bash
set -euo pipefail
SOURCE=$(realpath "$1"); VENDOR=$(realpath "$2"); OUTPUT=$(realpath "$3"); TOOLCHAIN=$(realpath "$4"); NDK=$(realpath "$5"); TRACE_DIR=$(realpath -m "$6")
for directory in "$SOURCE" "$VENDOR" "$OUTPUT" "$TOOLCHAIN" "$NDK"; do test -d "$directory"; done
test -x /usr/bin/bwrap; test -x /usr/bin/strace
test -x "$TOOLCHAIN/bin/cargo"; test -x "$TOOLCHAIN/bin/rustc"
test -x "$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang"
mkdir -p "$OUTPUT/cargo-home" "$OUTPUT/target"
# Root observer and namespace setup remain outside dependency execution.
# Only trusted setpriv retains SETUID/SETGID/SETPCAP until it drops UID and all caps.
sudo install -d -o root -g root -m 0700 "$TRACE_DIR"
# All host HOME/config/SSH/runner credentials are absent. Only these mounts exist.
# Network, PID, IPC and UTS namespaces are isolated; source and tools are read-only.
sudo /usr/bin/strace -ff -s 4096 -e trace=execve,execveat,connect -o "$TRACE_DIR/exec.trace" \
 /usr/bin/bwrap \
 --unshare-net --unshare-pid --unshare-ipc --unshare-uts --die-with-parent --new-session \
 --cap-drop ALL --cap-add CAP_SETUID --cap-add CAP_SETGID --cap-add CAP_SETPCAP --clearenv \
 --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/sbin /sbin \
 --symlink usr/lib /lib --symlink usr/lib64 /lib64 \
 --dir /etc --ro-bind /etc/ld.so.cache /etc/ld.so.cache --ro-bind /etc/alternatives /etc/alternatives \
 --proc /proc --dev /dev --tmpfs /tmp \
 --ro-bind "$SOURCE" /source --ro-bind "$VENDOR" /vendor \
 --ro-bind "$TOOLCHAIN" /toolchain --ro-bind "$NDK" /ndk --bind "$OUTPUT" /build \
 --ro-bind "$(dirname "$(realpath "$0")")/sandbox-entry.py" /entry.py \
 --chdir /source \
 --setenv PATH /toolchain/bin:/ndk/toolchains/llvm/prebuilt/linux-x86_64/bin:/usr/bin:/bin \
 --setenv HOME /tmp --setenv TMPDIR /tmp --setenv LANG C.UTF-8 \
 --setenv CARGO_HOME /build/cargo-home --setenv CARGO_TARGET_DIR /build/target \
 --setenv RUSTC /toolchain/bin/rustc --setenv RUSTDOC /toolchain/bin/rustdoc \
 --setenv CARGO_BUILD_JOBS 2 --setenv CARGO_INCREMENTAL 0 \
 --setenv CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang \
 --setenv CC_aarch64_linux_android /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang \
 --setenv AR_aarch64_linux_android /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-ar \
 --setenv RUSTFLAGS '-C link-arg=-Wl,-z,max-page-size=16384 -C link-arg=-Wl,-z,common-page-size=16384' \
 /usr/bin/setpriv --reuid "$(id -u)" --regid "$(id -g)" --clear-groups \
 --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs \
 /usr/bin/python3 /entry.py "$(id -u)" "$(id -g)"
