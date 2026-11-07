#!/usr/bin/env python3
import pathlib,sys,json,tomllib,hashlib
vendor=pathlib.Path(sys.argv[1]);audit=json.load(open(sys.argv[2]));out=pathlib.Path(sys.argv[3])
expected={(x['name'],x['version']):x for x in audit['packages']};seen=set();builds=[]
for p in sorted(vendor.iterdir()):
 if not p.is_dir():continue
 assert not p.is_symlink()
 manifest=tomllib.loads((p/'Cargo.toml').read_text());pkg=manifest['package'];key=(pkg['name'],pkg['version']);assert key in expected,key;assert key not in seen;seen.add(key)
 spec=expected[key];checks=json.load(open(p/'.cargo-checksum.json'));assert checks['package']==spec['checksum'],key
 for name,sha in checks['files'].items():
  f=p/name;assert f.resolve().is_relative_to(p.resolve());assert not f.is_symlink();assert hashlib.sha256(f.read_bytes()).hexdigest()==sha,(key,name)
 assert not (p/'.git').exists()
 build=pkg.get('build', 'build.rs' if (p/'build.rs').is_file()else False)
 if build:
  assert spec['build'] and spec['build']['path']==build,(key,build)
  assert hashlib.sha256((p/build).read_bytes()).hexdigest()==spec['build']['sha256'],key;builds.append({'name':key[0],'version':key[1],'entry':build})
 else:assert spec['build'] is None,key
assert seen==set(expected),('missing',sorted(set(expected)-seen))
result={'registry_packages':len(seen),'build_entries':len(builds),'checksums_and_scripts':'passed','builds':builds}
(out/'vendor-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'registry_packages':len(seen),'build_entries':len(builds),'status':'passed'}))
