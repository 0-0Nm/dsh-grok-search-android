#!/usr/bin/env python3
import pathlib,sys,tarfile,hashlib,json,shutil,stat
archive,original,build,evidence=map(pathlib.Path,sys.argv[1:5]);evidence.mkdir(parents=True,exist_ok=True)
expected='487d73fd4db00dc2420d659a8221b181a7937fbc5bc73f31c30b1680ad6ded6a'
h=hashlib.file_digest(open(archive,'rb'),'sha256').hexdigest();assert h==expected
original.mkdir(exist_ok=False)
with tarfile.open(archive)as t:
 for m in t.getmembers():
  n=pathlib.PurePosixPath(m.name);assert not n.is_absolute()and'..'not in n.parts
  assert n.parts[0]=='node-v22.21.1'
 t.extractall(original,filter='data')
source=original/'node-v22.21.1';assert '#define NODE_MAJOR_VERSION 22'in(source/'src/node_version.h').read_text();assert '#define NODE_MINOR_VERSION 21'in(source/'src/node_version.h').read_text();assert '#define NODE_PATCH_VERSION 1'in(source/'src/node_version.h').read_text()
manifest=[]
for f in sorted(source.rglob('*')):
 if f.is_symlink():manifest.append({'path':str(f.relative_to(source)),'symlink':str(f.readlink())})
 elif f.is_file():manifest.append({'path':str(f.relative_to(source)),'sha256':hashlib.file_digest(open(f,'rb'),'sha256').hexdigest()})
(evidence/'original-source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copytree(source,build,symlinks=True)
(evidence/'source.json').write_text(json.dumps({'release':'v22.21.1','gitReference':'6ac4ab19ad02803f03b54501193397563e99988e','archiveSha256':h,'originalFiles':len(manifest),'platform':'aarch64-linux-android','nativeAPI':26,'ndk':'27.3.13750724','changes':'no runtime source patch; generated build files allowed only in independent copy'},indent=2)+'\n')
print(json.dumps({'sourceHashMatched':True,'originalFiles':len(manifest),'independentBuildCopy':str(build)}))
