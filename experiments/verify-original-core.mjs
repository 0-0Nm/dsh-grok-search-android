import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
const [coreArg, expectedManifest] = process.argv.slice(2);
assert(coreArg && /^[a-f0-9]{64}$/.test(expectedManifest));
assert.equal(process.platform, 'android'); assert.equal(process.arch, 'arm64');
assert.equal(process.version, 'v22.21.1');
const core = fs.realpathSync(coreArg);
const bytes = fs.readFileSync(path.join(core, 'manifest.json'));
assert.equal(createHash('sha256').update(bytes).digest('hex'), expectedManifest);
const manifest = JSON.parse(bytes);
assert.equal(manifest.upstreamCommit, 'df34daebaf3ea28e1da764f5257a8084c1944b21');
assert.equal(manifest.originalSourceChanges, false);
let checked = 0;
for (const item of manifest.files) {
  const file = path.resolve(core, item.path);
  assert(file.startsWith(core + path.sep));
  assert(!fs.lstatSync(file).isSymbolicLink() && fs.statSync(file).isFile());
  assert(fs.realpathSync(file).startsWith(core + path.sep));
  assert.equal(createHash('sha256').update(fs.readFileSync(file)).digest('hex'), item.sha256, item.path);
  checked++;
}
assert(fs.existsSync(path.join(core, 'upstream/fixtures/internal-candidate/mcp-sources.mjs')));
console.log(JSON.stringify({platform:process.platform,arch:process.arch,nodeVersion:process.version,
  upstreamCommit:manifest.upstreamCommit,manifestSha256:expectedManifest,filesChecked:checked,
  businessSourceChanged:false,ordinaryAPK:'not_run'}));
