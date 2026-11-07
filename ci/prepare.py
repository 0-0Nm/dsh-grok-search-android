#!/usr/bin/env python3
import argparse, pathlib, subprocess, hashlib, json, tomllib, difflib, re
ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('evidence');args=ap.parse_args()
p=pathlib.Path(args.source).resolve();out=pathlib.Path(args.evidence).resolve();out.mkdir(parents=True,exist_ok=True)
commit=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
assert commit=='be5fe87db22939de9405a7e9c70b1e43f7151214',commit
before={n:(p/n).read_text()for n in ['Cargo.toml','Cargo.lock']}
assert hashlib.sha256((p/'Cargo.lock').read_bytes()).hexdigest()=='5741e2738ff1408fe0a5c1c107a32ff8f9e6b7d0a216f67d8cfda48855f37a77'
assert not (p/'build.rs').exists(),'Unexpected upstream root build script'
manifest,n=re.subn(r'(?m)^version = "0\.1\.25"$','version = "0.1.26"',before['Cargo.toml'],count=1);assert n==1
lock,n=re.subn(r'(\[\[package\]\]\nname = "grok-search-rs"\nversion = ")0\.1\.25("\n)',r'\g<1>0.1.26\2',before['Cargo.lock'],count=1);assert n==1
old=tomllib.loads(before['Cargo.lock']);new=tomllib.loads(lock)
assert [x for x in old['package']if x['name']!='grok-search-rs']==[x for x in new['package']if x['name']!='grok-search-rs']
mold=tomllib.loads(before['Cargo.toml']);mnew=tomllib.loads(manifest);mold['package']['version']='0.1.26';assert mold==mnew
for name,text in [('Cargo.toml',manifest),('Cargo.lock',lock)]: (p/name).write_text(text)
(out/'version-only.patch').write_text(''.join(''.join(difflib.unified_diff(before[n].splitlines(True),(p/n).read_text().splitlines(True),fromfile='upstream/'+n,tofile='experiment/'+n))for n in before))
provenance={'upstream_commit':commit,'tag':'v0.1.26','source_version_before':'0.1.25','version_injected':'0.1.26','rust':'1.90.0','ndk':'27.3.13750724','native_api':26,'target':'aarch64-linux-android','features':'default (no http feature)','original_lock_sha256':hashlib.sha256(before['Cargo.lock'].encode()).hexdigest(),'experiment_lock_sha256':hashlib.sha256(lock.encode()).hexdigest(),'acceptance':'cross-compile only; no Android execution or plugin integration'}
(out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps(provenance))
