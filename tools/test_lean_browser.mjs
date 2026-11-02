import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
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

async function simulatedCompiler(probe,main={success:true,messages:[]},source='example : True := by trivial') {
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
    try{return await compiler.run(source);}finally{compiler.dispose();}
  }finally{globalThis.Worker=oldWorker;globalThis.fetch=oldFetch;}
}
const completed={success:true,messages:[{severity:'information',data:'__KOMOREBI_PARSE_COMPLETE__'}]};
test('a missing or failed syntax probe cannot turn a silent run into success',async()=>{
  await assert.rejects(simulatedCompiler({success:true,messages:[]}),/did not complete the syntax check/);
  await assert.rejects(simulatedCompiler({success:false,error:'parser worker stopped'}),/parser worker stopped/);
  await assert.rejects(simulatedCompiler(completed,{success:true,messages:[]},'example : False := b\u0000y trivial'),/unsupported control characters/);
});
test('runtime failures are not clean checks and warnings remain warnings',async()=>{
  await assert.rejects(simulatedCompiler(completed,{success:false,error:'runtime exited'}),/runtime exited/);
  const warning=await simulatedCompiler(completed,{success:true,messages:[{severity:'warning',data:'declaration uses sorry'}]});
  assert.equal(outcome(warning),'warning');
  const clean=await simulatedCompiler(completed);
  assert.equal(outcome(clean),'passed');
});

test('public asset proxy verifies bytes, omits credentials and reuses its checked cache',async()=>{
  const script=await readFile(new URL('../website/assets/lean-browser-sw.js',import.meta.url),'utf8');
  const bytes=new TextEncoder().encode('compiler bytes');
  const digest=Buffer.from(await webcrypto.subtle.digest('SHA-256',bytes)).toString('hex');
  const events={},stored=new Map();let downloads=0;
  const source={files:{},remote_files:{
    'shared/good.pack':{size:bytes.length,sha256:digest,url:'https://raw.githubusercontent.com/pinned/good'},
    'shared/bad.pack':{size:bytes.length,sha256:digest,url:'https://raw.githubusercontent.com/pinned/bad'}
  }};
  vm.runInNewContext(script,{
    self:{registration:{scope:'https://example.test/lean/browser/'},addEventListener:(name,handler)=>events[name]=handler},
    URL,Request,Response,Headers,crypto:webcrypto,
    caches:{open:async()=>({match:async key=>stored.get(key.url)?.clone(),put:async(key,value)=>stored.set(key.url,value.clone())})},
    fetch:async(input,options)=>{
      const url=String(input);
      if(url.endsWith('SOURCE.json'))return Response.json(source);
      assert.equal(options.credentials,'omit');assert.equal(options.mode,'cors');downloads++;
      return new Response(url.endsWith('/bad')?'wrong bytes':bytes);
    }
  });
  async function request(name){let answer;events.fetch({request:new Request('https://example.test/lean/browser/engine/shared/'+name+'.pack'),respondWith:p=>answer=p});return answer;}
  let response=await request('good');assert.equal(response.status,200);assert.equal(await response.text(),'compiler bytes');
  response=await request('good');assert.equal(response.headers.get('Cross-Origin-Embedder-Policy'),'require-corp');assert.equal(downloads,1);
  response=await request('bad');assert.equal(response.status,503);assert.match(await response.text(),/checksum mismatch/);
});
