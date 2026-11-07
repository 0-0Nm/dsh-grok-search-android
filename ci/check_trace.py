#!/usr/bin/env python3
# Run by the trusted outer observer, not by build scripts.
import pathlib,sys,re,json
tracedir=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);traces=list(tracedir.glob('exec.trace.*'))
assert traces,'Missing external observer traces'
executed=[];violations=[];events=0
for f in traces:
 text=f.read_text(errors='strict')
 assert text.strip(),('Empty trace',f.name)
 for line in text.splitlines():
  relevant=any(x in line for x in ['execve(', 'execveat(', 'connect(', '<... execve', '<... execveat', '<... connect'])
  if not relevant:continue
  events+=1
  if '<unfinished ...>'in line or 'resumed>'in line:
   violations.append({'type':'unparsed_event','trace':f.name,'line':line});continue
  if not re.search(r'= (?:-?\d+|\?)',line):
   violations.append({'type':'missing_syscall_result','trace':f.name,'line':line});continue
  if 'connect('in line:
   if 'sa_family=AF_INET'in line:violations.append({'type':'network_attempt','trace':f.name,'line':line})
   continue
  if 'execveat('in line:
   if not re.search(r'= -1\b',line):violations.append({'type':'execveat_not_permitted','trace':f.name,'line':line})
   continue
  # Failed PATH candidates execute nothing; record successful execve paths only.
  if re.search(r'= -1\b',line):continue
  match=re.search(r'execve\("([^"\\\n]+)",',line)
  if not match or not re.search(r'= 0\s*$',line):
   violations.append({'type':'unparsed_exec','trace':f.name,'line':line});continue
  path=match[1];executed.append(path)
  allowed=(path in ['/usr/bin/bwrap','/usr/bin/setpriv','/usr/bin/python3','/toolchain/bin/cargo','/toolchain/bin/rustc','/toolchain/bin/rustdoc','/usr/bin/cc','/usr/bin/gcc','/usr/bin/ld','/usr/bin/as','/usr/bin/ld.bfd','/bin/cc','/bin/gcc','/usr/bin/dirname','/bin/dirname']or path.startswith('/ndk/toolchains/llvm/prebuilt/linux-x86_64/bin/')or re.fullmatch(r'/usr/lib/gcc/x86_64-linux-gnu/\d+/[^/]+',path)or re.fullmatch(r'/build/target/(?:release|aarch64-linux-android/release)/build/[A-Za-z0-9_.-]+/build-script-(?:build|main)',path))
  if not allowed:violations.append({'type':'unapproved_exec','path':path,'trace':f.name})
if '/usr/bin/bwrap'not in executed or '/toolchain/bin/cargo'not in executed:
 violations.append({'type':'missing_required_exec'})
result={'traceFiles':len(traces),'relevantEvents':events,'executedPaths':sorted(set(executed)),'violations':violations,'observer':'host root-owned trace directory not mounted in sandbox','scope':'execution PATH audit, not proof of compiled code authenticity; read-only/no-network/clean-env isolation is the containment boundary'}
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not violations,violations
