import fs from 'node:fs';
import path from 'node:path';
import { startLoopbackMcp } from './loopback-mcp.mjs';
import { createOriginalSearch } from './original-search.mjs';
const [coreRoot,backend,configPath,tokenFile,portArg='0']=process.argv.slice(2);
if(!tokenFile||!path.isAbsolute(tokenFile))throw new Error('Explicit private local access-token file required');
const st=fs.lstatSync(tokenFile);if(!st.isFile()||st.isSymbolicLink()||(st.mode&0o077)!==0||st.size>256)throw new Error('Local access-token file must be private and regular');
const token=fs.readFileSync(tokenFile,'utf8').trim();
const original=await createOriginalSearch({coreRoot,backend,configPath});
// This experiment never enables external searches. Later enablement needs a safe configuration entry and a request budget.
const server=await startLoopbackMcp({token,search:original.search,allowSearch:false,port:Number(portArg)});
console.log(JSON.stringify({event:'ready',url:server.url,searchEnabled:false,adapter:'original createGrokProvider + createSourceRouter + createRoutedSearch',credentialsLogged:false}));
let stopping=false;
async function close(){if(stopping)return;stopping=true;await server.close();await original.close();}
process.once('SIGTERM',()=>close().then(()=>process.exit(0),()=>process.exit(1)));
process.once('SIGINT',()=>close().then(()=>process.exit(0),()=>process.exit(1)));
