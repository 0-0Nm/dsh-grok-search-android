#!/usr/bin/env python3
from pathlib import Path
import subprocess,zipfile,hashlib,json,sys
p=Path(__file__).resolve().parent; w=p/'build';w.mkdir(exist_ok=False);sdk=Path('/root/toolbox/sdk/android-sdk');bt=sdk/'build-tools/36.0.0';platform=sdk/'platforms/android-36/android.jar';runtime=Path('/root/toolbox/workspace/dsh-android-audit-cdPUAz3v/C4-prebuilt-review-nazgqvsm/runtime');backend=Path('/storage/emulated/0/Download/dsh-android-audit-cdPUAz3v/backend-run5/grok-search-rs-android-arm64');logs=[]
def run(name,cmd):
 r=subprocess.run([str(x)for x in cmd],capture_output=True,text=True);(w/(name+'.log')).write_text(r.stdout+r.stderr);logs.append({'stage':name,'exitCode':r.returncode});print(name,r.returncode,flush=True)
 if r.returncode:print((r.stdout+r.stderr)[-6000:]);raise SystemExit(r.returncode)
(w/'classes').mkdir();(w/'dex').mkdir();(w/'gen').mkdir()
run('link',[bt/'aapt2','link','-I',platform,'--manifest',p/'AndroidManifest.xml','--java',w/'gen','-A',p/'assets','-o',w/'resources.apk','--min-sdk-version','26','--target-sdk-version','36'])
run('javac',['javac','-source','8','-target','8','-classpath',platform,'-d',w/'classes',*list((p/'src').rglob('*.java'))])
run('d8',[bt/'d8','--lib',platform,'--min-api','26','--output',w/'dex',*list((w/'classes').rglob('*.class'))])
assert hashlib.file_digest(open(runtime/'node','rb'),'sha256').hexdigest()=='d578386032936914bee48b47f4370cff4a2e66740a1266964ab6b9d25a64c23b'
assert hashlib.file_digest(open(backend,'rb'),'sha256').hexdigest()=='8e5696d97f8eef4aded6f48fa2be52543cba417570566044bbd0087ec6dac838'
with zipfile.ZipFile(w/'unsigned.apk','w')as out:
 with zipfile.ZipFile(w/'resources.apk')as src:
  for item in src.infolist():out.writestr(item,src.read(item.filename))
 out.write(w/'dex/classes.dex','classes.dex',compress_type=zipfile.ZIP_STORED)
 for src,name in [(runtime/'node','libnode_exec.so'),(backend,'libgrok_exec.so')]:out.write(src,'lib/arm64-v8a/'+name,compress_type=zipfile.ZIP_DEFLATED)
run('align',[bt/'zipalign','-f','4',w/'unsigned.apk',w/'aligned.apk'])
run('sign',[bt/'apksigner','sign','--ks','/root/toolbox/keys/debug.keystore','--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',w/'dsh-core-probe.apk',w/'aligned.apk'])
run('signature',[bt/'apksigner','verify','--verbose',w/'dsh-core-probe.apk'])
run('manifest',[bt/'aapt2','dump','badging',w/'dsh-core-probe.apk'])
run('alignment',[bt/'zipalign','-c','4',w/'dsh-core-probe.apk'])
f=w/'dsh-core-probe.apk';receipt={'apk':str(f),'bytes':f.stat().st_size,'sha256':hashlib.file_digest(open(f,'rb'),'sha256').hexdigest(),'package':'org.dsh.androidprobe','targetSDK':36,'minSDK':26,'INTERNET_permission':True,'versionCode':2,'searchEnabled':False,'buildChecks':logs,'installed':False,'launched':False,'AppUID_execution':'not_run','scope':'loopback authenticated MCP connection experiment; search disabled, L3Hub not yet connected'};(w/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
