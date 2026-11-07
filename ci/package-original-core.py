#!/usr/bin/env python3
import pathlib,sys,subprocess,json,shutil,hashlib,tarfile,re
source,out,probe=map(pathlib.Path,sys.argv[1:4]);assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='df34daebaf3ea28e1da764f5257a8084c1944b21'
out.mkdir(parents=True,exist_ok=True);bundle=out/'original-core';bundle.mkdir();up=bundle/'upstream';up.mkdir();shutil.copytree(source/'src/core',up/'src/core');shutil.copyfile(source/'src/provider.mjs',up/'src/provider.mjs');shutil.copytree(source/'node_modules',up/'node_modules',symlinks=True)
for name in ['package.json','package-lock.json','LICENSE']:shutil.copyfile(source/name,up/name)
selected=['provider-core.test.mjs','provider-mcp.test.mjs','routed-search.test.mjs','source-adapters.test.mjs','source-chain.test.mjs'];(up/'test').mkdir()
for name in selected:shutil.copyfile(source/'test'/name,up/'test'/name)
shutil.copytree(source/'fixtures/mcp',up/'fixtures/mcp')
fixtures=set()
for name in selected:
 text=(source/'test'/name).read_text()
 for rel in re.findall(r"new URL\(['\"](\.\./fixtures/[^'\"]+)['\"],\s*import\.meta\.url\)",text):
  candidate=(source/'test'/rel).resolve();base=source.resolve();assert candidate.is_relative_to(base/'fixtures')and candidate.is_file(),rel
  relative=candidate.relative_to(base);destination=up/relative;destination.parent.mkdir(parents=True,exist_ok=True)
  if destination.exists():assert destination.read_bytes()==candidate.read_bytes()
  else:shutil.copyfile(candidate,destination)
  fixtures.add(str(relative))
shutil.copyfile(probe,bundle/'probe-original.mjs')
files=[]
for f in sorted(bundle.rglob('*')):
 if f.is_file()and not f.is_symlink():files.append({'path':str(f.relative_to(bundle)),'sha256':hashlib.file_digest(open(f,'rb'),'sha256').hexdigest()})
manifest={'upstreamCommit':'df34daebaf3ea28e1da764f5257a8084c1944b21','originalSourceChanges':False,'dependencyInstall':'npm ci --ignore-scripts --legacy-peer-deps --omit=dev; original lock retained','nodeRequirement':'>=22.0.0','selectedOriginalTests':selected,'fixtureFiles':sorted(fixtures),'files':files,'runtimeProbe':'not_run','testsOnAndroid':'not_run','ordinaryAPK':'not_run'}
(bundle/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(out/'original-core-experiment.tar.gz','w:gz')as t:t.add(bundle,arcname='original-core')
print(json.dumps({'originalFilesPreserved':True,'bundleFiles':len(files),'selectedOriginalTests':selected,'AndroidExecution':'not_run'}))
