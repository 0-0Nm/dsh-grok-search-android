#!/usr/bin/env python3
import pathlib,sys,re,json,hashlib,subprocess,shutil
out=pathlib.Path(sys.argv[1]);evidence=pathlib.Path(sys.argv[2]);ndk=pathlib.Path(sys.argv[3])
binary=out/'target/aarch64-linux-android/release/grok-search-rs';assert binary.is_file()
reader=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'
r=subprocess.run([str(reader),'-h','-l','-d',str(binary)],capture_output=True,text=True,check=True);(evidence/'elf.txt').write_text(r.stdout)
assert re.search(r'Machine:\s+AArch64',r.stdout)
assert '/system/bin/linker64'in r.stdout,'Not Android dynamic loader'
assert 'libc.so.6'not in r.stdout and 'ld-linux'not in r.stdout,'Unexpected glibc artifact'
shutil.copyfile(binary,evidence/'grok-search-rs-android-arm64')
sha=hashlib.sha256(binary.read_bytes()).hexdigest();(evidence/'SHA256SUMS').write_text(sha+'  grok-search-rs-android-arm64\n')
result={'backendCompilation':'passed','elfArchitecture':'AArch64','interpreter':'/system/bin/linker64','binarySha256':sha,'backendAndroidLaunch':'not_run','mcpHandshake':'not_run','pluginOrchestration':'not_run','realSearch':'not_run','clientIntegration':'not_run','apkDistribution':'not_run'}
(evidence/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
