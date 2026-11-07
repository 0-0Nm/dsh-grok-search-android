import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
export async function createOriginalSearch({coreRoot,backend,configPath,budgetMs=120000}) {
 for(const p of [coreRoot,backend,configPath])if(typeof p!=='string'||!path.isAbsolute(p))throw new TypeError('Explicit app-private absolute paths required');
 const base=fs.realpathSync(coreRoot);if(!fs.statSync(backend).isFile())throw new TypeError('Original backend binary missing');
 const read=async rel=>import(pathToFileURL(path.join(base,'upstream/src',rel)).href);
 const [{createGrokProvider},{createSourceRouter},{createRoutedSearch},{createReleaseBarrier},{createSharedConfigStore}]=await Promise.all([read('provider.mjs'),read('core/source-adapters.mjs'),read('core/routed-search.mjs'),read('core/release-transaction.mjs'),read('core/shared-config.mjs')]);
 const store=createSharedConfigStore({path:configPath,env:()=>({})});const getConfig=()=>store.readEffective();
 const preferences={snapshot:()=>({value:{grokEnabled:true,githubEnabled:true}})};
 const provider=createGrokProvider({configuration:{executable:backend,configPath,budgetMs,envOverrides:{HOME:path.dirname(configPath),TMPDIR:process.env.TMPDIR??path.dirname(configPath)}}});
 const sourceRouter=createSourceRouter({getConfig,getPreferences:()=>preferences.snapshot()});
 const routed=createRoutedSearch({grok:provider.provider,sourceRouter,preferences,releaseBarrier:createReleaseBarrier(),getConfig,budgetMs});
 return {search:(request,signal)=>routed.search(request,signal,'search'),async close(){const outcomes=await Promise.allSettled([routed.dispose(),provider.dispose()]);for(const x of outcomes)if(x.status==='rejected')throw x.reason;}};
}
