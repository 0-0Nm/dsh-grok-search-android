import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, isAbsolute } from 'node:path';
import { tmpdir } from 'node:os';
import { randomUUID } from 'node:crypto';
import { probeMcpHandshake } from './upstream/src/core/mcp-search.mjs';
assert.equal(process.platform, 'android', 'This probe must run with the Android/bionic runtime, not Linux glibc/musl');
assert(Number(process.versions.node.split('.')[0]) >= 22);
assert.equal(typeof fetch, 'function');
assert.equal(typeof AbortSignal.any, 'function');
assert.equal(typeof AbortSignal.timeout, 'function');
const executable = process.argv[2];
assert(executable && isAbsolute(executable), 'Pass the verified original Grok Android backend absolute path');
const work = mkdtempSync(join(tmpdir(), 'original-plugin-probe-'));
mkdirSync(join(work, 'home'));
mkdirSync(join(work, 'tmp'));
const result = await probeMcpHandshake({
  executable,
  configPath: join(work, 'no-config.toml'),
  envOverrides: {
    HOME: join(work, 'home'), TMPDIR: join(work, 'tmp'),
    GROK_SEARCH_AUTH_MODE: 'api_key',
    GROK_SEARCH_API_KEY: 'handshake-only-synthetic-not-a-real-key',
    GROK_SEARCH_URL: 'http://127.0.0.1:9',
    GROK_SEARCH_MODEL: 'offline-handshake',
  },
  signal: AbortSignal.timeout(12000),
});
assert.equal(result.version, '0.1.26');
assert.equal(result.toolsDeclared, true);
assert.equal(result.exited, true);
const receipt = { platform: process.platform, arch: process.arch, nodeVersion: process.version,
  originalPluginCommit: 'df34daebaf3ea28e1da764f5257a8084c1944b21',
  originalModule: 'src/core/mcp-search.mjs::probeMcpHandshake',
  result, realSearch: 'not_run', originalRoutedSearchSuite: 'not_run', ordinaryAPK: 'not_run',
  probeId: randomUUID(), work };
writeFileSync(join(work, 'result.json'), JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(receipt));
