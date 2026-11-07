#!/usr/bin/env python3
import pathlib,sys,json,hashlib,subprocess,re,shutil,tarfile
work,evidence,ndk=map(pathlib.Path,sys.argv[1:4]);baseline=json.load(open(evidence/'original-source-manifest.json'));modified=[]
for entry in baseline:
 f=work/entry['path']
 if 'symlink'in entry:
  if not f.is_symlink()or str(f.readlink())!=entry['symlink']:modified.append(entry['path'])
 elif not f.is_file()or f.is_symlink()or not f.resolve().is_relative_to(work.resolve())or hashlib.file_digest(open(f,'rb'),'sha256').hexdigest()!=entry['sha256']:modified.append(entry['path'])
(evidence/'source-drift.json').write_text(json.dumps({'checkedFiles':len(baseline),'modifiedOriginalFiles':modified},indent=2)+'\n');assert not modified,modified
binary=work/'out/Release/node';assert binary.is_file()and not binary.is_symlink();assert binary.resolve().is_relative_to(work.resolve())
readelf=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf';text=subprocess.check_output([str(readelf),'-h','-l','-d',str(binary)],text=True);(evidence/'node-elf.txt').write_text(text)
assert re.search(r'Machine:\s+AArch64',text)and'/system/bin/linker64'in text;assert 'libc.so.6'not in text and'ld-linux'not in text
needed=re.findall(r'\(NEEDED\).*?\[([^\]]+)\]',text);allowed={'libc.so','libm.so','libdl.so','liblog.so','libandroid.so','libz.so','libc++_shared.so'};assert set(needed)<=allowed,needed
runtime=evidence/'runtime';runtime.mkdir();shutil.copyfile(binary,runtime/'node');(runtime/'node').chmod(0o755);shutil.copyfile(work/'LICENSE',runtime/'LICENSE.node')
if'libc++_shared.so'in needed:
 lib=ndk/'toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so';assert lib.is_file();(runtime/'lib').mkdir();shutil.copyfile(lib,runtime/'lib/libc++_shared.so')
 notices=[f for f in ndk.rglob('NOTICE')if f.is_file()and len(f.relative_to(ndk).parts)<=5]
 for i,f in enumerate(notices):shutil.copyfile(f,runtime/('NOTICE.ndk.'+str(i)))
(evidence/'runtime-build.json').write_text(json.dumps({'version':'22.21.1','sourceArchiveSha256':'487d73fd4db00dc2420d659a8221b181a7937fbc5bc73f31c30b1680ad6ded6a','target':'aarch64-linux-android','nativeAPI':26,'needed':needed,'binaryBytes':binary.stat().st_size,'binarySha256':hashlib.file_digest(open(binary,'rb'),'sha256').hexdigest(),'runtimeBuild':'passed','AndroidExecution':'not_run','originalPluginProbe':'not_run','ordinaryAPK':'not_run','sourceOriginalFilesUnchanged':True},indent=2)+'\n')
with tarfile.open(evidence/'node22-android-arm64.tar.gz','w:gz')as t:t.add(runtime,arcname='node22-android-arm64')
print((evidence/'runtime-build.json').read_text())
