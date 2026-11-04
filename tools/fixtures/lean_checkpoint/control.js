import {createCompiler} from './lean-wasm/index.js?v=20261104-checkpoint-probe1';
import {CHECKPOINT, validateCapsule, sha256, textHash} from './lean-wasm/checkpoint-codec.js';
import {MODULE, SOURCE, CONSUMER_GOOD, CONSUMER_FALSE, moduleSource} from './lean-wasm/fixture.js';

const button=document.querySelector('#run'),stop=document.querySelector('#stop'),status=document.querySelector('#status'),output=document.querySelector('#log');
let compiler=null,abort=null,generation=0,busy=false,retiring=Promise.resolve(),releasePause=null;
const write=text=>{output.textContent+=text+'\n';};
const records=[];
const NativeWorker=globalThis.Worker,workerStats=[];let startingLabel='unknown';
globalThis.Worker=class extends NativeWorker{
  constructor(...args){super(...args);this.probeStats={label:startingLabel,compileCalls:0};workerStats.push(this.probeStats);}
  postMessage(message,...args){if(message?.type==='compile')this.probeStats.compileCalls++;return super.postMessage(message,...args);}
};
const active=ticket=>{if(ticket!==generation)throw Error('Stopped; no further source or worker is scheduled.');};
async function retire(current){
  if(!current)return;
  retiring=Promise.all([retiring,current.dispose()]).then(()=>{});
  await retiring;
  write('Closed: '+JSON.stringify(await current.closed));
  if(compiler===current)compiler=null;
}
async function proxy(){
  await navigator.serviceWorker.register(new URL('sw.js',location.href),{scope:new URL('./',location.href).pathname});
  await navigator.serviceWorker.ready;
  if(!navigator.serviceWorker.controller)await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Asset proxy setup timed out')),20000);
    navigator.serviceWorker.addEventListener('controllerchange',()=>{clearTimeout(timer);resolve();},{once:true});
  });
}
async function pins(ticket){
  const response=await fetch(new URL('checkpoint-graph.json',location.href),{cache:'no-cache'});
  if(!response.ok)throw Error('Probe graph record unavailable');
  const graph=await response.json();
  if(graph.version!=='20261104-checkpoint-probe1'||graph.config.scope!==CHECKPOINT.scope)throw Error('Probe graph policy changed');
  const root=new URL('../../',location.href);
  for(const file of graph.files){
    active(ticket);const res=await fetch(new URL(file.path,root),{cache:'no-cache'});
    if(!res.ok)throw Error('Graph asset unavailable: '+file.path);
    const bytes=new Uint8Array(await res.arrayBuffer());
    if(bytes.length!==file.size||await sha256(bytes)!==file.sha256)throw Error('Graph asset changed: '+file.path);
  }
  const raw=new Uint8Array(await (await fetch(new URL('engine/SOURCE.json',location.href),{cache:'no-cache'})).arrayBuffer());
  if(await sha256(raw)!==CHECKPOINT.engineSourceSha)throw Error('Engine identity changed');
  if(await textHash(SOURCE)!==CHECKPOINT.modules[0].sourceSha||await textHash(moduleSource(SOURCE,MODULE))!==CHECKPOINT.modules[0].wrappedSha)throw Error('Exact probe fixture changed');
  write('Pinned graph checked: '+graph.files.length+' assets; source '+CHECKPOINT.modules[0].sourceSha);
}
async function startCompiler(ticket,label){
  await retiring;active(ticket);startingLabel=label;write('Starting '+label);
  const current=await createCompiler({baseUrl:new URL('engine/',location.href).href,syntaxCheck:'frontend',signal:abort.signal,
    onProgress:m=>{if(ticket===generation)status.textContent=label+': '+m;},onStatus:m=>{if(ticket===generation)write(label+': '+m);}});
  if(ticket!==generation){await retire(current);active(ticket);}
  compiler=current;return current;
}
function clean(result,label){
  if(result.exitCode!==0||result.errors.length)throw Error(label+' did not pass cleanly: '+JSON.stringify(result));
  write(label+' PASS '+result.compileMs+'ms');
}
function copy(capsule){return structuredClone(capsule);}
async function rejectedInstall(ticket,label,capsule,session,expression){
  const current=await startCompiler(ticket,label),stats=workerStats.at(-1);let expected=false;
  try{await current.installCheckpoint(capsule,session);}catch(error){
    if(!expression.test(String(error.message||error)))throw error;
    expected=true;write(label+' rejected before consumer source: '+String(error.message||error));
  }
  if(!expected)throw Error(label+' unexpectedly installed; no consumer was executed');
  if(stats.compileCalls!==0)throw Error(label+' unexpectedly sent a source compile');
  records.push({control:label,result:'REJECTED',measuredCompileCalls:stats.compileCalls});
  await retire(current);active(ticket);
}
async function run(){
  if(busy)return;busy=true;button.disabled=true;stop.disabled=false;output.textContent='';records.length=0;workerStats.length=0;
  abort=new AbortController();const ticket=++generation,start=performance.now();status.textContent='Preparing fixed probe control';
  try{
    await proxy();active(ticket);await pins(ticket);active(ticket);
    const nonce=new Uint8Array(16);crypto.getRandomValues(nonce);
    const session={workspace:CHECKPOINT.workspace,generation:ticket,run:Array.from(nonce,b=>b.toString(16).padStart(2,'0')).join(''),boundary:1};
    const a=await startCompiler(ticket,'A export');
    const result=await a.run(moduleSource(SOURCE,MODULE),undefined,{syntaxSource:SOURCE,mainModule:MODULE,checkpointModule:MODULE});
    active(ticket);clean(result,'Original Compression');
    const capsule=await a.exportCheckpoint(session);active(ticket);await validateCapsule(capsule,session);
    if(capsule.parts.length!==5)throw Error('Expected exactly five emitted parts');
    const bytes=capsule.parts.reduce((n,p)=>n+p.size,0);
    write('Exported '+capsule.parts.length+' owned parts / '+bytes+' bytes; identity '+capsule.identity);
    records.push({control:'export',result:'PASS',parts:capsule.parts.map(({module,suffix,size,sha256})=>({module,suffix,size,sha256})),identity:capsule.identity});
    const valid=copy(capsule),corrupt=copy(capsule),missing=copy(capsule);
    if(!corrupt.parts[0].bytes.length)throw Error('Cannot test corruption of an empty first part');
    corrupt.parts[0].bytes[0]^=1;missing.parts.pop();
    await retire(a);active(ticket);
    if(document.querySelector('#pause').checked){
      status.textContent='Paused after export; no consumer worker started';
      document.querySelector('#continue').disabled=false;
      await new Promise(resolve=>{releasePause=resolve;});releasePause=null;
      document.querySelector('#continue').disabled=true;active(ticket);
    }
    const b=await startCompiler(ticket,'B valid import');
    const installed=await b.installCheckpoint(valid,session);active(ticket);write('Installed: '+JSON.stringify(installed));
    const good=await b.run(CONSUMER_GOOD);active(ticket);clean(good,'Original Recovery');
    const bad=await b.run(CONSUMER_FALSE);active(ticket);
    const badText=bad.diagnostics.map(d=>d.text).join('\n');
    if(bad.exitCode===0||!bad.errors.length||!bad.diagnostics.length||!/1 = 2/.test(badText)||!/rfl/.test(badText))throw Error('False Recovery did not report the expected mathematical error: '+JSON.stringify(bad));
    write('False Recovery correctly rejected: '+bad.diagnostics.map(d=>d.text).join('\n'));
    records.push({control:'fresh-import-and-consumers',result:'PASS',recoveryCompileMs:good.compileMs,falseProofRejected:true});
    await retire(b);active(ticket);
    await rejectedInstall(ticket,'C corrupt',corrupt,session,/artifact checksum mismatch/);
    await rejectedInstall(ticket,'D missing',missing,session,/exactly five probe parts/);
    active(ticket);status.textContent='PASS Proof Path five-part export/import and negative controls';
    write(JSON.stringify({result:'PASS',scope:CHECKPOINT.scope,records,workerStats,seconds:(performance.now()-start)/1000},null,2));
  }catch(error){
    if(ticket===generation){status.textContent='FAIL: '+String(error.message||error);write('No complete control success. No retry.');}
    write('Terminal: '+String(error.message||error));
  }finally{
    abort?.abort();await retire(compiler);abort=null;busy=false;button.disabled=false;stop.disabled=true;
    write('Elapsed '+((performance.now()-start)/1000).toFixed(2)+'s');
  }
}
document.querySelector('#continue').onclick=()=>releasePause?.();
button.onclick=run;
stop.onclick=()=>{generation++;releasePause?.();document.querySelector('#continue').disabled=true;abort?.abort();compiler?.dispose();status.textContent='Stopped without a successful control result';};
