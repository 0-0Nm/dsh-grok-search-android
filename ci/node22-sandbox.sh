#!/usr/bin/env bash
set -euo pipefail
WORK=$(realpath "$1"); NDK=$(realpath "$2"); CI=$(realpath "$3"); JOBS="$4"
test -x "$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang++"
# Privileged setup is restricted to namespaces; no downloaded source runs as root.
sudo /usr/bin/bwrap \
 --unshare-net --unshare-pid --unshare-ipc --unshare-uts --die-with-parent --new-session \
 --cap-drop ALL --cap-add CAP_SETUID --cap-add CAP_SETGID --cap-add CAP_SETPCAP --clearenv \
 --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/sbin /sbin --symlink usr/lib /lib --symlink usr/lib64 /lib64 \
 --dir /etc --ro-bind /etc/ld.so.cache /etc/ld.so.cache --ro-bind /etc/alternatives /etc/alternatives \
 --proc /proc --dev /dev --tmpfs /tmp --chmod 1777 /tmp \
 --ro-bind "$NDK" /ndk --ro-bind "$CI" /ci --bind "$WORK" /work --chdir /work \
 --setenv PATH /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin:/usr/bin:/bin \
 --setenv HOME /tmp --setenv TMPDIR /tmp --setenv LANG C.UTF-8 --setenv PYTHONDONTWRITEBYTECODE 1 \
 --setenv CC /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang \
 --setenv CXX /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang++ \
 --setenv CC_target /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang \
 --setenv CXX_target /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android26-clang++ \
 --setenv AR /ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-ar \
 --setenv CC_host /usr/bin/gcc --setenv CXX_host /usr/bin/g++ --setenv AR_host /usr/bin/ar \
 --setenv GYP_CROSSCOMPILE 1 \
 --setenv GYP_DEFINES 'target_arch=arm64 v8_target_arch=arm64 android_target_arch=arm64 host_arch=x64 host_os=linux OS=android android_ndk_path=/ndk' \
 --setenv LDFLAGS '-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384' \
 /usr/bin/setpriv --reuid "$(id -u)" --regid "$(id -g)" --clear-groups \
 --inh-caps=-all --ambient-caps=-all --bounding-set=-all --no-new-privs \
 /usr/bin/python3 /ci/node22-entry.py "$(id -u)" "$(id -g)" "$JOBS"
