import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
const [rootArg, expectedManifest, expectedVersion] = process.argv.slice(2);
assert.equal(process.platform,'android'); assert.equal(process.arch,'arm64');
assert.equal(process.version,expectedVersion); assert(Number(process.versions.node.split('.')[0])>=22);
const root=fs.realpathSync(rootArg); const bytes=fs.readFileSync(path.join(root,'manifest.json'));
assert.equal(createHash('sha256').update(bytes).digest('hex'),expectedManifest);
const manifest=JSON.parse(bytes);assert.equal('v'+manifest.nodeVersion,expectedVersion);
for(const entry of manifest.files){
 const f=path.resolve(root,entry.path);assert(f.startsWith(root+path.sep));assert(!fs.lstatSync(f).isSymbolicLink());
 assert.equal(createHash('sha256').update(fs.readFileSync(f)).digest('hex'),entry.sha256,entry.path);
}
assert.equal(createHash('sha256').update('abc').digest('hex'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
assert.equal(Buffer.from('中文🙂').toString('utf8'),'中文🙂');
assert.equal(typeof fetch,'function');assert.equal(typeof AbortSignal.any,'function');assert.equal(typeof AbortSignal.timeout,'function');
assert.equal(Intl.getCanonicalLocales('zh-CN')[0],'zh-CN');
const tmp=fs.mkdtempSync(path.join(process.env.TMPDIR,'native-node-smoke-'));
fs.writeFileSync(path.join(tmp,'own-file.txt'),'isolated file check\n',{flag:'wx'});
assert.equal(fs.readFileSync(path.join(tmp,'own-file.txt'),'utf8'),'isolated file check\n');
const child=spawnSync('/system/bin/echo',['native-child-ok'],{env:{PATH:'/system/bin'},encoding:'utf8',timeout:3000});
assert.equal(child.status,0);assert.equal(child.stdout.trim(),'native-child-ok');
const result={platform:process.platform,arch:process.arch,nodeVersion:process.version,uid:process.getuid(),manifestFilesVerified:manifest.files.length,
 crypto:'passed',unicode:'passed',fetchAvailable:true,fetchInvoked:false,abortAPIs:'passed',filesystem:'passed',childProcess:'passed',
 origin:manifest.origin,originalPluginExecution:'not_run',ordinaryAPK:'not_run',probeId:randomUUID(),temporaryDirectory:tmp};
console.log(JSON.stringify(result));
