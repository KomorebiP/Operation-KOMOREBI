import test from 'node:test';
import assert from 'node:assert/strict';
globalThis.document={querySelector:()=>null};
const {moduleSource,outcome,withCompatibility,mapDiagnostic}=await import('../website/assets/lean-browser.js');
const {createCompiler}=await import('../website/assets/lean-wasm/compiler.js');

test('only a completed clean check receives the clean state',()=>{
  assert.equal(outcome({exitCode:0,errors:[]}),'passed');
  assert.equal(outcome({exitCode:0,errors:['warning: declaration uses sorry']}),'warning');
  assert.equal(outcome({exitCode:1,errors:[]}),'failed');
  assert.equal(outcome(undefined),'failed');
});
test('module export wrapper keeps the original proof body and names the real import',()=>{
  const original='import Mathlib.Data.Set.Function\n\nnamespace ProofPath\ntheorem t : True := by trivial\nend ProofPath\n';
  const wrapped=moduleSource(original,'ProofPath.Compression');
  assert.ok(wrapped.includes(original.slice(original.indexOf('\n')+1)));
  assert.ok(wrapped.includes('setMainModule `ProofPath.Compression'));
  assert.ok(wrapped.includes('@[expose] public section'));
  assert.ok(wrapped.includes('/lib/lean/ProofPath/Compression.olean'));
  assert.throws(()=>moduleSource(original,'../bad'));
  assert.throws(()=>moduleSource('namespace Changed','ProofPath.Compression'));
});
test('compatibility is explicit and diagnostics point to the original proof',()=>{
  const source='import A\n\nexample : True := by trivial\n';
  const compatibility='theorem helper : True := by trivial\n';
  assert.equal(withCompatibility(source,compatibility),'import A\n'+compatibility+source.slice(9));
  assert.equal(mapDiagnostic('error (line 6, col 0)',source,true),'error (line 3, col 0)');
  assert.equal(mapDiagnostic('syntax error at line 4, column 0',source,false,compatibility),'syntax error at line 3, column 0');
  assert.equal(mapDiagnostic('error (line 2, col 0)',source,false,compatibility),'error (browser compatibility lemma, col 0)');
});

async function simulatedCompiler(probe,main={success:true,messages:[]}) {
  const oldWorker=globalThis.Worker,oldFetch=globalThis.fetch;
  globalThis.fetch=async()=>new Response('',{status:404});
  globalThis.Worker=class {
    postMessage(message){queueMicrotask(()=>{
      const send=data=>this.onmessage?.({data});
      if(message.type==='start')send({type:'ready'});
      if(message.type==='load_modules')send({type:'modules_loaded',id:message.id,results:message.roots.map(root=>({root,files:1}))});
      if(message.type==='compile'){
        const result=message.code.includes('__KOMOREBI_PARSE_COMPLETE__')?probe:main;
        for(const diagnostic of result.messages||[])send({type:'stdout',data:JSON.stringify(diagnostic)});
        send({type:'result',id:message.id,success:result.success,error:result.error});
      }
    });}
    terminate(){}
  };
  try{
    const compiler=await createCompiler({baseUrl:'https://example.invalid/',syntaxCheck:'full'});
    try{return await compiler.run('example : True := by trivial');}finally{compiler.dispose();}
  }finally{globalThis.Worker=oldWorker;globalThis.fetch=oldFetch;}
}
const completed={success:true,messages:[{severity:'information',data:'__KOMOREBI_PARSE_COMPLETE__'}]};
test('a missing or failed syntax probe cannot turn a silent run into success',async()=>{
  await assert.rejects(simulatedCompiler({success:true,messages:[]}),/did not complete the syntax check/);
  await assert.rejects(simulatedCompiler({success:false,error:'parser worker stopped'}),/parser worker stopped/);
});
test('runtime failures are not clean checks and warnings remain warnings',async()=>{
  await assert.rejects(simulatedCompiler(completed,{success:false,error:'runtime exited'}),/runtime exited/);
  const warning=await simulatedCompiler(completed,{success:true,messages:[{severity:'warning',data:'declaration uses sorry'}]});
  assert.equal(outcome(warning),'warning');
  const clean=await simulatedCompiler(completed);
  assert.equal(outcome(clean),'passed');
});
