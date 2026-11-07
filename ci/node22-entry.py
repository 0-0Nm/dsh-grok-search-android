#!/usr/bin/env python3
import os,sys,pathlib,json,subprocess,tempfile
uid,gid,jobs=map(int,sys.argv[1:4]);assert uid!=0 and os.geteuid()==uid and os.getegid()==gid
s=dict(x.split(':',1)for x in pathlib.Path('/proc/self/status').read_text().splitlines()if ':'in x)
for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']:assert int(s[k].strip(),16)==0,k
assert s['NoNewPrivs'].strip()=='1';assert not pathlib.Path('/home/runner').exists()
for path in ['/usr','/ndk','/ci']:
 entries=[x.split()for x in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()if x.split()[4]==path];assert entries and'ro'in entries[-1][5].split(','),path
probe=pathlib.Path(tempfile.mkdtemp(dir='/tmp'));(probe/'check').write_text('isolated temporary write check\n')
print('RUNTIME_SANDBOX='+json.dumps({'uid':uid,'gid':gid,'capabilitiesZero':True,'noNewPrivs':True,'network':'isolated namespace','hostHomeMounted':False,'jobs':jobs}),flush=True)
# Same cross-target compiler and GYP settings as the reviewed official Android entry.
subprocess.run(['/usr/bin/python3','configure.py','--dest-cpu=arm64','--dest-os=android','--cross-compiling','--openssl-no-asm','--with-intl=full-icu','--download=none','--without-npm','--without-corepack'],cwd='/work',check=True)
subprocess.run(['/usr/bin/make','-j'+str(jobs)],cwd='/work',check=True)
