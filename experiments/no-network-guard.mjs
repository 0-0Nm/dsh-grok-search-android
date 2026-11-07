import fs from 'node:fs';
import http from 'node:http';
import https from 'node:https';
import net from 'node:net';
import { syncBuiltinESMExports } from 'node:module';
const counts = {fetchDenied:0,httpDenied:0,tcpDenied:0,platform:process.platform,node:process.version};
globalThis.fetch = async () => { counts.fetchDenied++; throw new Error('Baseline test forbids real network fetch'); };
for (const mod of [http, https]) {
  mod.request = mod.get = () => { counts.httpDenied++; throw new Error('Baseline test forbids real HTTP requests'); };
}
net.Socket.prototype.connect = function() { counts.tcpDenied++; throw new Error('Baseline test forbids real socket connections'); };
syncBuiltinESMExports();
process.on('exit', () => {
  if (process.env.LAB_EVIDENCE_DIR) fs.writeFileSync(`${process.env.LAB_EVIDENCE_DIR}/network-guard-${process.pid}.json`, JSON.stringify(counts)+'\n', {flag:'wx'});
});
