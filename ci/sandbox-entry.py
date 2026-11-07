#!/usr/bin/env python3
# Trusted boundary check, mounted read-only and executed before any crate code.
import os,sys,pathlib,json
uid,gid=map(int,sys.argv[1:3]);assert uid!=0 and os.geteuid()==uid and os.getegid()==gid
status=dict(line.split(':',1)for line in pathlib.Path('/proc/self/status').read_text().splitlines()if ':'in line)
for key in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']:assert int(status[key].strip(),16)==0,(key,status[key])
assert status['NoNewPrivs'].strip()=='1'
for directory in ['/source','/vendor','/toolchain','/ndk']:
 matches=[line.split()for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()if line.split()[4]==directory]
 assert matches and 'ro'in matches[-1][5].split(','),directory
assert not pathlib.Path('/home/runner').exists(),'Host HOME unexpectedly visible'
record={'uid':uid,'gid':gid,'allCapabilitiesZero':True,'noNewPrivs':True,'readonlyMounts':['/source','/vendor','/toolchain','/ndk'],'hostHomeMounted':False}
pathlib.Path('/build/sandbox-entry.json').write_text(json.dumps(record,indent=2)+'\n');print('SANDBOX_ENTRY='+json.dumps(record),flush=True)
os.execv('/toolchain/bin/cargo',['/toolchain/bin/cargo','build','--release','--frozen','--offline','--target','aarch64-linux-android','--bin','grok-search-rs'])
