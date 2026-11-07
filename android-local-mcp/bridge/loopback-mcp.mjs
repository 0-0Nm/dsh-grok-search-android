import http from 'node:http';
import { timingSafeEqual, createHash } from 'node:crypto';
const VERSIONS = new Set(['2025-06-18', '2025-11-25']);
const TOOL = Object.freeze({name:'web_search',description:'Search using the original dsh-grok-search routing core on this Android device. External provider APIs require separate configuration and permission.',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1,maxLength:4096},maxResults:{type:'integer',minimum:1,maximum:20}},required:['query'],additionalProperties:false}});
const idOK = x => (typeof x==='string'&&x.length>0&&x.length<=128)||(typeof x==='number'&&Number.isSafeInteger(x));
const digest = value => createHash('sha256').update(value).digest();
export async function startLoopbackMcp({token,search,allowSearch=false,port=0,budgetMs=120000}={}) {
 if(typeof token!=='string'||!/^[A-Za-z0-9_-]{43,128}$/.test(token))throw new TypeError('A private random local access token is required');
 if(typeof search!=='function')throw new TypeError('Original search adapter required');
 if(!Number.isSafeInteger(port)||port<0||port>65535||!Number.isSafeInteger(budgetMs)||budgetMs<50||budgetMs>120000)throw new TypeError('Invalid endpoint bounds');
 const expected=digest('Bearer '+token);const active=new Map();const sockets=new Set();let closing=false;let requestsInWindow=0;let windowStart=Date.now();let actualPort;
 const reply=(res,status,body)=>{if(res.destroyed||res.writableEnded)return;const bytes=body===undefined?'':JSON.stringify(body);res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(bytes);};
 const error=(res,id,code,message)=>reply(res,200,{jsonrpc:'2.0',id,error:{code,message}});
 const server=http.createServer(async(req,res)=>{
  try {
   if(closing){reply(res,503);return;}
   if(req.url!=='/mcp'){reply(res,404);return;}
   if(req.headers.host!==`127.0.0.1:${actualPort}`||req.headers.origin!==undefined){reply(res,403);return;}
   const auth=req.headers.authorization;
   if(typeof auth!=='string'||auth.length>256||!timingSafeEqual(digest(auth),expected)){res.setHeader('WWW-Authenticate','Bearer realm="local-android-mcp"');reply(res,401);return;}
   if(req.method!=='POST'){res.setHeader('Allow','POST');reply(res,405);return;}
   if(Date.now()-windowStart>=1000){windowStart=Date.now();requestsInWindow=0;}
   if(++requestsInWindow>40){reply(res,429);return;}
   if(!(req.headers['content-type']??'').toLowerCase().split(';')[0].trim().includes('application/json')){reply(res,415);return;}
   const accept=(req.headers.accept??'').toLowerCase();
   if(!accept.includes('application/json')||!accept.includes('text/event-stream')){reply(res,406);return;}
   const protocol=req.headers['mcp-protocol-version'];if(protocol!==undefined&&!VERSIONS.has(protocol)){reply(res,400);return;}
   let bytes=0;const chunks=[];
   for await(const chunk of req){bytes+=chunk.length;if(bytes>65536){reply(res,413);req.resume();return;}chunks.push(chunk);}
   let msg;
   try {msg=JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{reply(res,400,{jsonrpc:'2.0',id:null,error:{code:-32700,message:'Parse error'}});return;}
   if(!msg||Array.isArray(msg)||typeof msg!=='object'||msg.jsonrpc!=='2.0'||typeof msg.method!=='string'){reply(res,400,{jsonrpc:'2.0',id:null,error:{code:-32600,message:'Invalid request'}});return;}
   const notification=!Object.hasOwn(msg,'id');
   if(notification){
    if(msg.method==='notifications/cancelled'&&idOK(msg.params?.requestId))active.get(JSON.stringify(msg.params.requestId))?.abort(new Error('CALLER_CANCELLED'));
    reply(res,202);return;
   }
   if(!idOK(msg.id)){error(res,null,-32600,'Invalid request ID');return;}
   const id=msg.id;
   if(msg.method==='initialize'){
    const requested=msg.params?.protocolVersion;
    reply(res,200,{jsonrpc:'2.0',id,result:{protocolVersion:VERSIONS.has(requested)?requested:'2025-06-18',capabilities:{tools:{}},serverInfo:{name:'dsh-grok-search-android',version:'0.1-local-bridge'}}});return;
   }
   if(msg.method==='ping'){reply(res,200,{jsonrpc:'2.0',id,result:{}});return;}
   if(msg.method==='tools/list'){reply(res,200,{jsonrpc:'2.0',id,result:{tools:[TOOL]}});return;}
   if(msg.method!=='tools/call'){error(res,id,-32601,'Method not found');return;}
   const args=msg.params?.arguments;
   if(msg.params?.name!=='web_search'||!args||typeof args!=='object'||Array.isArray(args)||typeof args.query!=='string'||!args.query.trim()||args.query.length>4096||Object.keys(args).some(k=>!['query','maxResults'].includes(k))||(args.maxResults!==undefined&&(!Number.isSafeInteger(args.maxResults)||args.maxResults<1||args.maxResults>20))){error(res,id,-32602,'Invalid web_search arguments');return;}
   if(!allowSearch){reply(res,200,{jsonrpc:'2.0',id,result:{isError:true,content:[{type:'text',text:'SEARCH_DISABLED: real search has not been enabled for this experiment.'}]}});return;}
   const key=JSON.stringify(id);
   if(active.size>=8){reply(res,429);return;}
   if(active.has(key)){error(res,id,-32600,'Duplicate active request ID');return;}
   const controller=new AbortController();active.set(key,controller);const timer=setTimeout(()=>controller.abort(new Error('REQUEST_TIMEOUT')),budgetMs);
   const closed=()=>{if(!res.writableEnded)controller.abort(new Error('CLIENT_DISCONNECTED'));};res.once('close',closed);
   try {
    const result=await search({query:args.query,maxResults:args.maxResults??5},controller.signal);controller.signal.throwIfAborted();
    reply(res,200,{jsonrpc:'2.0',id,result:{content:[{type:'text',text:JSON.stringify(result)}]}});
   }catch(e){
    const code=controller.signal.aborted?'SEARCH_CANCELLED_OR_TIMEOUT':typeof e?.code==='string'&&/^[A-Z0-9_]{1,64}$/.test(e.code)?e.code:'SEARCH_FAILED';
    reply(res,200,{jsonrpc:'2.0',id,result:{isError:true,content:[{type:'text',text:code}]}});
   }finally{clearTimeout(timer);res.removeListener('close',closed);active.delete(key);}
  }catch{if(!res.headersSent)reply(res,400);else res.destroy();}
 });
 server.maxHeadersCount=32;server.maxConnections=32;server.headersTimeout=5000;server.requestTimeout=10000;server.keepAliveTimeout=1000;
 server.on('connection',socket=>{sockets.add(socket);socket.on('close',()=>sockets.delete(socket));});
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',()=>{server.removeListener('error',reject);resolve();});});actualPort=server.address().port;
 return {url:`http://127.0.0.1:${actualPort}/mcp`,address:server.address(),get activeRequests(){return active.size;},async close(){closing=true;for(const c of active.values())c.abort(new Error('SERVER_STOPPING'));for(const socket of sockets)socket.destroy();await new Promise(resolve=>server.close(resolve));}};
}
