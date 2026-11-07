import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { randomBytes } from 'node:crypto';
import { startLoopbackMcp } from './bridge/loopback-mcp.mjs';
import { createOriginalSearch } from './bridge/original-search.mjs';
const [coreRoot,backend,work]=process.argv.slice(2);
assert.equal(process.platform,'android');
const original=await createOriginalSearch({coreRoot,backend,configPath:path.join(work,'no-config.toml')});
const token=randomBytes(32).toString('base64url');let calls=0;
const server=await startLoopbackMcp({token,allowSearch:false,search:async(...args)=>{calls++;return original.search(...args);}});
const sdk=await import(pathToFileURL(path.join(coreRoot,'upstream/node_modules/@modelcontextprotocol/client/dist/index.mjs')).href);
assert.equal(typeof sdk.StreamableHTTPClientTransport,'function');
const client=new sdk.Client({name:'android-original-sdk-local-http-check',version:'1'},{capabilities:{},versionNegotiation:{mode:'legacy'}});
const transport=new sdk.StreamableHTTPClientTransport(new URL(server.url),{requestInit:{headers:{Authorization:'Bearer '+token}}});
try{
 await client.connect(transport,{signal:AbortSignal.timeout(5000)});
 const listed=await client.listTools({}, {signal:AbortSignal.timeout(5000)});
 assert.deepEqual(listed.tools.map(t=>t.name),['web_search']);
 const disabled=await client.callTool({name:'web_search',arguments:{query:'local-handshake-budget-check-not-sent-upstream'}},undefined,{signal:AbortSignal.timeout(5000)});
 assert.equal(disabled.isError,true);assert.match(disabled.content[0].text,/SEARCH_DISABLED/);assert.equal(calls,0);
 const result={platform:process.platform,node:process.version,clientSDK:'@modelcontextprotocol/client2.4.0',transport:'StreamableHTTP',initialize:'passed',toolsDiscovery:'passed',tools:listed.tools.map(t=>t.name),searchDisabled:'passed',originalSearchInvocations:calls,originalFactoryAssembly:'passed',serverAddress:server.address.address,tokenLogged:false,realSearch:'not_run',L3HubInstalledClient:'not_run',AppUIDHTTPIntegration:'not_run'};
 fs.writeFileSync(path.join(work,'sdk-result.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{await client.close();await server.close();await original.close();}
