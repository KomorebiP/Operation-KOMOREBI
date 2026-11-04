import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {resolve,sep} from 'node:path';
import vm from 'node:vm';
Object.defineProperty(globalThis,'crypto',{value:webcrypto,configurable:true});
if (!process.argv[2]) throw Error('Pass the generated probe directory.');
const base=resolve(process.argv[2],'assets/lean-wasm')+sep;
const load=name=>import(pathToFileURL(base+name));
const codec=await load('checkpoint-codec.js');
const {CHECKPOINT,expectedParts,sha256,validateCapsule,assertLengths,MAX_PART,MAX_TOTAL}=codec;
const fixture=await load('fixture.js');
const {createCompiler}=await load('compiler.js');
const session={workspace:CHECKPOINT.workspace,generation:1,run:'a'.repeat(32),boundary:1};
const identity='b'.repeat(64);
const receipts=CHECKPOINT.modules.map(entry=>({...entry,nonce:'1'.repeat(32)}));
async function capsuleFor(receiptsOverride=receipts,sessionOverride=session){
  const parts=[];
  for(const [i,entry] of expectedParts().entries()){
    const bytes=new Uint8Array([i,i+1]);
    parts.push({...entry,size:bytes.length,sha256:await sha256(bytes),bytes});
  }
  return {schema:1,scope:CHECKPOINT.scope,session:sessionOverride,identity,receipts:receiptsOverride,parts};
}
const capsule=await capsuleFor();let checks=0;
assert.equal(await validateCapsule(capsule,session,identity),10);checks++;
async function rejects(change,pattern){const bad=structuredClone(capsule);change(bad);await assert.rejects(validateCapsule(bad,session,identity),pattern);checks++;}
await rejects(c=>{c.parts[0].bytes[0]^=1;},/checksum/);
await rejects(c=>{c.parts[0].sha256='c'.repeat(64);},/checksum/);
await rejects(c=>{c.parts[0].size++;},/own its exact byte buffer/);
await rejects(c=>{c.parts.pop();},/exactly five/);
await rejects(c=>{c.parts.push(c.parts[0]);},/exactly five/);
await rejects(c=>{c.parts[1].suffix=c.parts[0].suffix;},/identity/);
await rejects(c=>{c.parts[0].module='../CheckpointTiny.Pure42';},/identity/);
await rejects(c=>{c.parts[0].path='/lib/lean/arbitrary';},/fields/);
await rejects(c=>{c.parts[0].suffix='.olean.deps';},/identity/);
await rejects(c=>{c.receipts[0].sourceSha='c'.repeat(64);},/receipt/);
await rejects(c=>{c.receipts[0].wrappedSha='c'.repeat(64);},/receipt/);
await rejects(c=>{c.receipts[0].nonce='';},/receipt/);
await rejects(c=>{c.session.run='d'.repeat(32);},/stale/);
await rejects(c=>{c.session.generation++;},/stale/);
await rejects(c=>{c.session.boundary=3;},/boundary/);
await rejects(c=>{c.scope='conventions-original-a3-v2';},/identity/);
await rejects(c=>{c.identity='d'.repeat(64);},/identity/);
await rejects(c=>{c.parts[0].size=MAX_PART+1;},/budget/);
await rejects(c=>{c.parts[0].bytes=new Uint8Array(new SharedArrayBuffer(2));},/own its exact byte buffer/);
await rejects(c=>{c.parts[0].bytes=new Uint8Array(new ArrayBuffer(4),1,2);},/own its exact byte buffer/);
await rejects(c=>{c.parts[1].bytes=c.parts[0].bytes;},/own its exact byte buffer/);
const lengths=expectedParts().map(entry=>({...entry,size:0}));
for(let i=0;i<4;i++)lengths[i].size=MAX_PART;
assert.equal(assertLengths(lengths),MAX_TOTAL);checks++;
lengths[4].size=1;assert.throws(()=>assertLengths(lengths),/total byte budget/);checks++;

// Protocol tests only: the fake worker never executes Lean. Actual proof and
// five-part filesystem import acceptance remain required in the browser.
let behavior='complete';const workers=[];
class FakeWorker{
  constructor(){this.messages=[];workers.push(this);}
  send(data){this.onmessage?.({data});}
  postMessage(message){this.messages.push(message);queueMicrotask(async()=>{
    if(message.type==='start')this.send({type:'ready'});
    if(message.type==='dispose')this.send({type:'disposed',id:message.id,cleanup:{threadShutdownRequested:true}});
    if(message.type==='reset')this.send({type:'reset_done',id:message.id});
    if(message.type==='load_modules')this.send({type:'modules_loaded',id:message.id,results:message.roots.map(root=>({root,files:1}))});
    if(message.type==='load_layer')this.send({type:'layer_loaded',id:message.id,label:message.label,ok:true,files:1});
    if(message.type==='compile'){
      const nonce=message.code.match(/__KOMOREBI_FRONTEND_STARTED_([0-9a-f]{32})__/)[1];
      for(const phase of behavior==='missing-completion'?['STARTED']:['STARTED','COMPLETED']){
        this.send({type:'stdout',data:JSON.stringify({severity:'information',data:`__KOMOREBI_FRONTEND_${phase}_${nonce}__`})});
      }
      if(behavior==='warning')this.send({type:'stdout',data:JSON.stringify({severity:'warning',data:'CONTROL_WARNING'})});
      if(behavior==='error')this.send({type:'stdout',data:JSON.stringify({severity:'error',data:'CONTROL_REPORTED_ERROR'})});
      this.send({type:'result',id:message.id,success:true});
    }
    if(message.type==='checkpoint_export')this.send({type:'checkpoint_exported',id:message.id,capsule:await capsuleFor(message.receipts,message.session)});
    if(message.type==='checkpoint_install')this.send({type:'checkpoint_installed',id:message.id,parts:5,bytes:10,identity});
  });}
  terminate(){this.terminated=true;}
}
globalThis.Worker=FakeWorker;
globalThis.fetch=async()=>new Response('',{status:404});
const compiler=signal=>createCompiler({baseUrl:'https://example.test/engine/',syntaxCheck:'frontend',signal});
const run=compiler=>compiler.run(fixture.moduleSource(fixture.SOURCE,fixture.MODULE),undefined,
  {syntaxSource:fixture.SOURCE,mainModule:fixture.MODULE,checkpointModule:fixture.MODULE});
const never=await compiler();
await assert.rejects(never.exportCheckpoint(session,receipts),/exact completed probe source/);checks++;
assert.equal(workers.at(-1).messages.filter(m=>m.type==='checkpoint_export').length,0);checks++;
await never.dispose();
for(const failure of ['error','missing-completion','warning']){
  behavior=failure;const current=await compiler();
  if(failure==='error')assert.notEqual((await run(current)).exitCode,0);
  else if(failure==='warning'){const result=await run(current);assert.equal(result.exitCode,0);assert.match(result.errors.join(' '),/CONTROL_WARNING/);}
  else await assert.rejects(run(current),/did not complete/);
  await assert.rejects(current.exportCheckpoint(session),/exact completed probe source/);checks++;
  assert.equal(workers.at(-1).messages.filter(m=>m.type==='checkpoint_export').length,0);checks++;
  await current.dispose();
}
behavior='complete';const a=await compiler();
await assert.rejects(a.run(fixture.moduleSource(fixture.SOURCE+'\n',fixture.MODULE),undefined,
  {syntaxSource:fixture.SOURCE+'\n',mainModule:fixture.MODULE,checkpointModule:fixture.MODULE}),/allowlisted/);checks++;
assert.equal(workers.at(-1).messages.filter(m=>m.type==='compile').length,0);checks++;
assert.equal((await run(a)).exitCode,0);await assert.rejects(run(a),/executes once/);checks++;assert.equal(workers.at(-1).messages.filter(m=>m.type==='compile').length,1);checks++;const issued=await a.exportCheckpoint(session);checks++;
await a.dispose();await a.closed;
const forged=structuredClone(issued);forged.parts[0].bytes[0]^=1;forged.parts[0].sha256=await sha256(forged.parts[0].bytes);
assert.equal(await validateCapsule(forged,session),10);checks++;
const b=await compiler();await assert.rejects(b.installCheckpoint(forged,session),/privately issued artifact provenance/);checks++;
assert.equal(workers.at(-1).messages.filter(m=>m.type==='checkpoint_install'||m.type==='compile').length,0);checks++;
await b.closed;
const c=await compiler(),racer=await compiler(),racingWorkers=workers.slice(-2);
const racing=await Promise.allSettled([c.installCheckpoint(structuredClone(issued),session),racer.installCheckpoint(structuredClone(issued),session)]);
assert.equal(racing.filter(r=>r.status==='fulfilled').length,1);checks++;
assert.equal(racing.filter(r=>r.status==='rejected'&&/privately issued/.test(r.reason.message)).length,1);checks++;
assert.equal(racingWorkers.flatMap(w=>w.messages).filter(m=>m.type==='checkpoint_install').length,1);checks++;
await c.dispose();await racer.dispose();await Promise.all([c.closed,racer.closed]);
const d=await compiler();await assert.rejects(d.installCheckpoint(structuredClone(issued),session),/privately issued artifact provenance/);checks++;
assert.equal(workers.at(-1).messages.filter(m=>m.type==='checkpoint_install'||m.type==='compile').length,0);checks++;
await d.closed;
const session2={...session,run:'e'.repeat(32)},a2=await compiler();
await run(a2);const issued2=await a2.exportCheckpoint(session2);await a2.dispose();await a2.closed;
const receiver=await compiler(),receiverWorker=workers.at(-1),mutable=structuredClone(issued2),mutableSession=structuredClone(session2);
const installing=receiver.installCheckpoint(mutable,mutableSession);
mutable.parts[0].bytes[0]^=1;mutable.parts[0].sha256='f'.repeat(64);mutableSession.run='f'.repeat(32);mutable.scope='mutated';
assert.equal((await installing).parts,5);checks++;
const posted=receiverWorker.messages.find(m=>m.type==='checkpoint_install');
assert.equal(posted.capsule.parts[0].bytes[0],issued2.parts[0].bytes[0]);checks++;
assert.equal(posted.session.run,session2.run);assert.equal(posted.capsule.scope,CHECKPOINT.scope);checks++;
await receiver.dispose();await receiver.closed;

// An aborted originating run cannot authorize a later receiver, even after
// its compiler was normally closed to hand off the artifacts.
const originAbort=new AbortController(),origin=await compiler(originAbort.signal);
await run(origin);const revoked=await origin.exportCheckpoint({...session,run:'2'.repeat(32)});
await origin.dispose();originAbort.abort();const late=await compiler();
await assert.rejects(late.installCheckpoint(revoked,{...session,run:'2'.repeat(32)}),/live privately issued/);checks++;
assert.equal(workers.at(-1).messages.filter(m=>m.type==='checkpoint_install'||m.type==='compile').length,0);checks++;
await late.closed;
const beforeCompile=await compiler();
await assert.rejects(beforeCompile.run(fixture.CONSUMER_GOOD+'\n'),/allowlisted/);checks++;
for(const syntaxCheck of ['auto','full','off']) {
  await assert.rejects(beforeCompile.run(fixture.CONSUMER_GOOD,undefined,{syntaxCheck}),/completed frontend/);checks++;
}
assert.equal(workers.at(-1).messages.filter(m=>m.type==='compile').length,0);checks++;
await beforeCompile.dispose();
for(let i=0;i<5;i++)await rejects(c=>{c.parts.splice(i,1);},/exactly five/);

// Exercise the generated real worker's checkpoint RPC and filesystem transaction.
// Its native compiler and build measurement are mocked here, not Lean's proof result.
const workerSource=await readFile(base+'worker.js','utf8');
function transaction({writeFailure=0,renameFailure=0,corruptStage=false,collision=false,exporting=false,oversize=false}={}) {
  const files=new Map(),directories=new Set(['/','/workspace','/lib','/lib/lean']),messages=[];
  let writes=0,renames=0,reads=0,nativeCompiles=0,bootFetches=0;
  const path=part=>codec.artifactPath(part.module,part.suffix);
  if(exporting)for(const part of capsule.parts)files.set(path(part),part.bytes);
  if(collision)files.set(path(capsule.parts[0]),new Uint8Array([1]));
  const FS={
    analyzePath:name=>({exists:files.has(name)||directories.has(name)}),
    mkdir:name=>directories.add(name),
    lstat:name=>({mode:0x8000,size:oversize?MAX_PART+1:files.get(name).length}),
    isFile:mode=>mode===0x8000,
    readFile:name=>{reads++;return files.get(name);},
    writeFile(name,data){
      writes++;if(writes===writeFailure)throw Error('Injected stage write failure');
      const copy=Uint8Array.from(data);if(corruptStage)copy[0]^=1;files.set(name,copy);
    },
    rename(from,to){
      renames++;if(renames===renameFailure)throw Error('Injected rename failure');
      files.set(to,files.get(from));files.delete(from);
    }
  };
  const self={postMessage:(message,transfers)=>messages.push({message,transfers}),__LEAN_WASM_CONFIG__:{}};
  const context=vm.createContext({self,location:{search:''},URLSearchParams,URL,Uint8Array,ArrayBuffer,crypto:webcrypto,
    setTimeout,clearTimeout,TextEncoder,TextDecoder,performance,codecInjected:codec,identityInjected:identity,
    fetch(){bootFetches++;throw Error('Unexpected boot after terminal failure');},
    compileCountInjected:exporting?1:0,Module:{FS,_lean_wasm_compile(){nativeCompiles++;throw Error('No native compile in this control');}}});
  const inspect=vm.runInContext(workerSource+`
    moduleReady=true;checkpointCompileCount=compileCountInjected;
    checkpointCodecPromise=Promise.resolve(codecInjected);
    checkpointIdentity=async()=>identityInjected;
    ({ready:()=>moduleReady,committed:()=>checkpointCommitted});`,context);
  return {files,messages,inspect,dispatch:data=>self.onmessage({data}),
    get writes(){return writes;},get renames(){return renames;},get reads(){return reads;},get nativeCompiles(){return nativeCompiles;},get bootFetches(){return bootFetches;}};
}
const install={type:'checkpoint_install',id:1,session,capsule};
const validTransaction=transaction();await validTransaction.dispatch(install);
assert.equal(validTransaction.messages.at(-1).message.type,'checkpoint_installed');checks++;
assert.equal(validTransaction.inspect.committed(),true);assert.equal(validTransaction.renames,5);checks++;
for(const part of capsule.parts)assert.deepEqual(validTransaction.files.get(codec.artifactPath(part.module,part.suffix)),part.bytes);checks++;
await validTransaction.dispatch(install);
assert.equal(validTransaction.inspect.ready(),false);assert.equal(validTransaction.renames,5);checks++;
for(const fault of [{writeFailure:3},{renameFailure:3},{corruptStage:true},{collision:true}]) {
  const tx=transaction(fault);await tx.dispatch(install);
  assert.equal(tx.messages.at(-1).message.type,'checkpoint_error');assert.equal(tx.inspect.ready(),false);checks++;
  assert.ok(!tx.messages.some(row=>row.message.type==='checkpoint_installed'));checks++;
  await tx.dispatch({type:'compile',id:2,code:fixture.CONSUMER_GOOD});
  assert.equal(tx.messages.at(-1).message.success,false);assert.equal(tx.nativeCompiles,0);checks++;
  const written=tx.writes;await tx.dispatch(install);assert.equal(tx.writes,written);checks++;
  await tx.dispatch({type:'start'});assert.equal(tx.bootFetches,0);assert.match(tx.messages.at(-1).message.data,/invalidated/);checks++;
}
const overlapping=transaction();const inflight=overlapping.dispatch(install);
await overlapping.dispatch({type:'reset',id:3});await inflight;
assert.equal(overlapping.inspect.ready(),false);assert.equal(overlapping.writes,0);checks++;
assert.ok(overlapping.messages.some(row=>/overlapped/.test(row.message.data||'')));checks++;
const oversized=transaction({exporting:true,oversize:true});
await oversized.dispatch({type:'checkpoint_export',id:4,session,receipts});
assert.equal(oversized.messages.at(-1).message.type,'checkpoint_error');assert.equal(oversized.reads,0);checks++;
const owned=transaction({exporting:true});await owned.dispatch({type:'checkpoint_export',id:5,session,receipts});
const exported=owned.messages.at(-1);assert.equal(exported.message.type,'checkpoint_exported');assert.equal(exported.transfers.length,5);checks++;
for(const part of exported.message.capsule.parts) {
  assert.equal(part.bytes.buffer.byteLength,part.size);
  assert.notEqual(part.bytes,owned.files.get(codec.artifactPath(part.module,part.suffix)));
}
checks++;

const graph=JSON.parse(await readFile(base+'../../lean/browser/checkpoint-graph.json','utf8'));
for(const record of graph.files){
  const bytes=await readFile(base+'../../'+record.path);
  assert.equal(bytes.length,record.size);assert.equal(await sha256(bytes),record.sha256);
}
console.log(JSON.stringify({result:'PASS',checks,graphAssets:graph.files.length,
  scope:'Codec, receipt-issuance and worker filesystem controls only. No actual Lean/import success claimed.'}));
