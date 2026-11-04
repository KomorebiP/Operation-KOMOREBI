import {createCompiler} from './lean-wasm/index.js?v=HEAVY_VERSION_HERE';
import {CHECKPOINT, validateCapsule, sha256, textHash} from './lean-wasm/checkpoint-codec.js';
import {A_SOURCES, B_SOURCES, CONSUMER_GOOD, CONSUMER_FALSE, moduleSource} from './lean-wasm/fixture.js';

const button=document.querySelector('#run'),stop=document.querySelector('#stop'),status=document.querySelector('#status'),output=document.querySelector('#log');
let compiler=null,abort=null,generation=0,busy=false,retiring=Promise.resolve(),releasePause=null;
const write=text=>{output.textContent+=text+'\n';};
const records=[],workerStats=[];
const NativeWorker=globalThis.Worker;let startingLabel='unknown';
globalThis.Worker=class extends NativeWorker{
  constructor(...args){super(...args);this.probeStats={label:startingLabel,compileCalls:0,reservations:[]};workerStats.push(this.probeStats);
    this.addEventListener('message',({data})=>{
      if(data?.type!=='memory')return;
      const event={requestedMiB:data.mb,failed:!!data.failed};
      if(!data.failed)Object.assign(event,{initialPages:data.initialPages,maximumPages:data.maximumPages,
        initialMiB:data.initialPages/16,maximumMiB:data.maximumPages/16,declared:data.declared});
      this.probeStats.reservations.push(event);write(this.probeStats.label+' reservation: '+JSON.stringify(event));
    });}
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
  if(graph.version!=='HEAVY_VERSION_HERE'||graph.config.scope!==CHECKPOINT.scope)throw Error('Probe graph policy changed');
  const root=new URL('../../',location.href);
  for(const file of graph.files){
    active(ticket);const res=await fetch(new URL(file.path,root),{cache:'no-cache'});
    if(!res.ok)throw Error('Graph asset unavailable: '+file.path);
    const bytes=new Uint8Array(await res.arrayBuffer());
    if(bytes.length!==file.size||await sha256(bytes)!==file.sha256)throw Error('Graph asset changed: '+file.path);
  }
  const raw=new Uint8Array(await (await fetch(new URL('engine/SOURCE.json',location.href),{cache:'no-cache'})).arrayBuffer());
  if(await sha256(raw)!==CHECKPOINT.engineSourceSha)throw Error('Engine identity changed');
  for(const [i,row] of A_SOURCES.entries()){
    if(await textHash(row.source)!==CHECKPOINT.modules[i].sourceSha||await textHash(moduleSource(row.source,row.module))!==CHECKPOINT.modules[i].wrappedSha)throw Error('Exact fixture changed: '+row.module);
  }
  write('Pinned graph checked: '+graph.files.length+' assets; three exact original producers and pinned original consumers.');
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
  records.push({control:label,result:'PASS',compileMs:result.compileMs,diagnostics:result.diagnostics});
}
async function rejectPreflight(capsule,session,label,pattern){
  let rejected=false;
  try{await validateCapsule(capsule,session);}catch(error){
    if(!pattern.test(String(error.message||error)))throw error;
    rejected=true;write(label+' rejected before receiver startup: '+String(error.message||error));
  }
  if(!rejected)throw Error(label+' unexpectedly validated');
  records.push({control:label,result:'REJECTED',scope:'Codec preflight; no receiver worker or source execution'});
}
async function run(){
  if(busy)return;busy=true;button.disabled=true;stop.disabled=false;output.textContent='';records.length=0;workerStats.length=0;
  const falseTarget=document.querySelector('#false-target').checked;document.querySelector('#false-target').disabled=true;
  abort=new AbortController();const ticket=++generation,start=performance.now();status.textContent='Preparing three-module probe';
  try{
    await proxy();active(ticket);await pins(ticket);active(ticket);
    const nonce=new Uint8Array(16);crypto.getRandomValues(nonce);
    const session={workspace:CHECKPOINT.workspace,generation:ticket,run:Array.from(nonce,b=>b.toString(16).padStart(2,'0')).join(''),boundary:CHECKPOINT.boundary};
    const a=await startCompiler(ticket,'A three producers');
    for(const row of A_SOURCES){
      const result=await a.run(moduleSource(row.source,row.module),undefined,{syntaxSource:row.source,mainModule:row.module,checkpointModule:row.module});
      active(ticket);clean(result,'Original '+row.module);
    }
    const capsule=await a.exportCheckpoint(session);active(ticket);await validateCapsule(capsule,session);
    if(capsule.parts.length!==15)throw Error('Expected exactly fifteen emitted parts');
    const bytes=capsule.parts.reduce((n,p)=>n+p.size,0);
    write('Exported '+capsule.parts.length+' owned parts / '+bytes+' bytes; identity '+capsule.identity);
    records.push({control:'export',result:'PASS',parts:capsule.parts.map(({module,suffix,size,sha256})=>({module,suffix,size,sha256})),identity:capsule.identity});
    const valid=structuredClone(capsule),corrupt=structuredClone(capsule),missing=structuredClone(capsule);
    corrupt.parts[0].bytes[0]^=1;missing.parts.splice(7,1);
    await retire(a);active(ticket);
    await rejectPreflight(corrupt,session,'Corrupt artifact',/artifact checksum mismatch/);
    await rejectPreflight(missing,session,'Missing middle-module artifact',/exactly fifteen probe parts/);
    active(ticket);
    if(document.querySelector('#pause').checked){
      status.textContent='Paused after export; no consumer worker started';
      document.querySelector('#continue').disabled=false;
      await new Promise(resolve=>{releasePause=resolve;});releasePause=null;
      document.querySelector('#continue').disabled=true;active(ticket);
    }
    const b=await startCompiler(ticket,'B fresh receiver');
    const installed=await b.installCheckpoint(valid,session);active(ticket);write('Installed: '+JSON.stringify(installed));
    records.push({control:'fresh-receiver-import',result:'PASS',parts:installed.parts,bytes:installed.bytes});
    for(const row of B_SOURCES){
      const result=await b.run(moduleSource(row.source,row.module),undefined,{syntaxSource:row.source,mainModule:row.module});
      active(ticket);clean(result,'Original '+row.module);
    }
    const target=await b.run(falseTarget?CONSUMER_FALSE:CONSUMER_GOOD);active(ticket);
    if(falseTarget){
      const badText=target.diagnostics.map(d=>d.text).join('\n');
      if(target.exitCode===0||!target.errors.length||!/1 = 2/.test(badText)||!/rfl/.test(badText))throw Error('False edited target did not report expected mathematical error: '+JSON.stringify(target));
      write('False edited Conventions correctly rejected: '+badText);
      records.push({control:'false-edited-Conventions',result:'REJECTED',compileMs:target.compileMs,diagnostics:target.diagnostics});
    }else clean(target,'Original Conventions');
    if(workerStats.length!==2||workerStats[0].compileCalls!==3||workerStats[1].compileCalls!==3)throw Error('Unexpected worker/source count: '+JSON.stringify(workerStats));
    await retire(b);active(ticket);status.textContent=falseTarget?'PASS false edited Conventions target rejected':'PASS original Conventions terminal target';
    write(JSON.stringify({result:'PASS',scenario:falseTarget?'false-edited-target':'original-target',scope:CHECKPOINT.scope,records,workerStats,seconds:(performance.now()-start)/1000},null,2));
  }catch(error){
    if(ticket===generation){status.textContent='FAIL: '+String(error.message||error);write('No complete control success. No retry.');}
    write('Terminal: '+String(error.message||error));
    write(JSON.stringify({result:'FAIL',scenario:falseTarget?'false-edited-target':'original-target',scope:CHECKPOINT.scope,records,workerStats,seconds:(performance.now()-start)/1000},null,2));
  }finally{
    abort?.abort();await retire(compiler);abort=null;busy=false;button.disabled=false;stop.disabled=true;document.querySelector('#false-target').disabled=false;
    write('Elapsed '+((performance.now()-start)/1000).toFixed(2)+'s');
  }
}
document.querySelector('#continue').onclick=()=>releasePause?.();
button.onclick=run;
stop.onclick=()=>{generation++;releasePause?.();document.querySelector('#continue').disabled=true;abort?.abort();compiler?.dispose();status.textContent='Stopped without a successful control result';};
