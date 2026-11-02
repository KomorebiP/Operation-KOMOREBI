import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
import {deflateRawSync} from 'node:zlib';
globalThis.document={querySelector:()=>null};
const {moduleSource,outcome,withCompatibility,mapDiagnostic}=await import('../website/assets/lean-browser.js');
const {createCompiler}=await import('../website/assets/lean-wasm/compiler.js');
const {optionalLayers,importedRoots,importLines,sourceHeader}=await import('../website/assets/lean-wasm/roots.js');
const {zipDirectory,readZipSource,sourceWorkspace,sha256}=await import('../website/assets/lean-source-bundle.js');
const {syntaxProbeSource,leanSourceExpression}=await import('../website/assets/lean-wasm/syntax-probe.js');

test('large parser inputs reconstruct the complete source across Unicode and escape boundaries',()=>{
  function reconstruct(expression){
    let offset=0;
    function part(){
      if(expression.startsWith('String.join [',offset)){
        offset+=13;let value='';
        while(expression[offset]!==']'){value+=part();if(expression.startsWith(', ',offset))offset+=2;else break;}
        assert.equal(expression[offset++],']');return value;
      }
      const start=offset++;for(;;){if(expression[offset]==='\\'){offset+=2;continue;}if(expression[offset++]==='"')break;}
      return JSON.parse(expression.slice(start,offset));
    }
    const value=part();assert.equal(offset,expression.length);return value;
  }
  const source=('example : True := by trivial\n-- α🌿 \\ " Unicode\t\r\n').repeat(1100);
  const expression=leanSourceExpression(source);
  assert.ok(expression.startsWith('String.join ['));assert.equal(reconstruct(expression),source);
});

test('module-format public imports supply the same notation to the syntax check',()=>{
  const source='module\npublic import Mathlib.Analysis.Complex.Basic\npublic import Std Lean\npublic section\nexample : (1 : ℂ) = 1 := rfl';
  assert.deepEqual(importedRoots(source),['Mathlib','Std','Lean']);
  assert.equal(importLines(source),'import Mathlib.Analysis.Complex.Basic\nimport Std Lean');
  assert.ok(syntaxProbeSource(source).startsWith(importLines(source)+'\nopen Lean'));
});

test('workspace libraries use their own manifest without changing the shared pack base',()=>{
  const assets={layerBase:'https://example.test/engine/lean-mathlib'};
  const [layer]=optionalLayers(assets,'workspaces/proof-path-compression.json');
  assert.equal(layer.manifestUrl,assets.layerBase+'/workspaces/proof-path-compression.json');
  assert.equal(layer.packBase,assets.layerBase);
  assert.throws(()=>optionalLayers(assets,'../other.json'),/Invalid workspace/);
  assert.throws(()=>optionalLayers(assets,'https://other.test/manifest.json'),/Invalid workspace/);
});

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
  assert.ok(moduleSource('def value : Nat := 1\n','Demo.Helper').includes('def value : Nat := 1'));
  const modern='/- nested /- import Fake -/ comment 🌿 -/\nmodule\npublic import Std\npublic section\nnamespace Demo\ndef value : Nat := 1\nend Demo\n';
  const exported=moduleSource(modern,'Demo.Helper');
  assert.ok(exported.startsWith('/- nested /- import Fake -/ comment 🌿 -/\nmodule\nimport Lean\npublic import Std\n'));
  assert.ok(exported.includes(sourceHeader(modern).body));
  assert.deepEqual(importedRoots(modern),['Std']);
  assert.equal(mapDiagnostic('error (line 9, col 0)',modern,true),'error (line 6, col 0)');
});

function sourceZip(inputs) {
  const local=[],central=[];let offset=0;
  for(const [name,raw] of inputs) {
    const path=Buffer.from(name),packed=deflateRawSync(raw),header=Buffer.alloc(30),directory=Buffer.alloc(46);
    header.writeUInt32LE(0x04034b50);header.writeUInt16LE(8,8);header.writeUInt32LE(packed.length,18);header.writeUInt32LE(raw.length,22);header.writeUInt16LE(path.length,26);
    directory.writeUInt32LE(0x02014b50);directory.writeUInt16LE(8,10);directory.writeUInt32LE(packed.length,20);directory.writeUInt32LE(raw.length,24);directory.writeUInt16LE(path.length,28);directory.writeUInt32LE(offset,42);
    local.push(header,path,packed);central.push(directory,path);offset+=header.length+path.length+packed.length;
  }
  const records=Buffer.concat(central),end=Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50);end.writeUInt16LE(inputs.length,8);end.writeUInt16LE(inputs.length,10);end.writeUInt32LE(records.length,12);end.writeUInt32LE(offset,16);
  return new Uint8Array(Buffer.concat([...local,records,end]));
}
test('source bundles preserve original bytes and reject changed sources, duplicate paths and traversal',async()=>{
  const raw=Buffer.from('\uFEFFimport Std\r\ndef α : Nat := 1\r\n'),path='paper/Helper.lean';
  const bytes=sourceZip([['inputs/'+path,raw]]),entries=zipDirectory(bytes),record={size:raw.length,sha256:await sha256(raw)};
  assert.deepEqual(await readZipSource(bytes,entries,path,record),new Uint8Array(raw));
  await assert.rejects(readZipSource(bytes,entries,path,{...record,sha256:'0'.repeat(64)}),/checksum/);
  assert.throws(()=>zipDirectory(sourceZip([['inputs/../escape.lean',raw]])),/Invalid source path/);
  assert.throws(()=>zipDirectory(sourceZip([['inputs/'+path,raw],['inputs/'+path,raw]])),/Duplicate/);
  assert.throws(()=>zipDirectory(bytes.subarray(0,bytes.length-5)),/archive/);
});
test('opened workspaces bind each dependency to its edition and keep generated compatibility separate',async()=>{
  const path='paper/Helper.lean',raw=Buffer.from('import Std\r\ndef value : Nat := 1\r\n'),bytes=sourceZip([['inputs/'+path,raw]]);
  const entry={id:'a',path,work:'paper',label:'Paper',inspect:'source.html',files:[{module:'Helper',input:0}],issues:[],tactics:true};
  const compatibility={module:'Mathlib.Tactic',source:'import Mathlib.Tactic.Ring\n',sha256:await sha256(new TextEncoder().encode('import Mathlib.Tactic.Ring\n'))};
  const catalog={entries:[entry],inputs:[{path,work:'paper',size:raw.length,sha256:await sha256(raw)}],compatibility};
  const bundle={bytes,entries:zipDirectory(bytes)},workspace=await sourceWorkspace(catalog,entry,bundle);
  assert.equal(workspace.files[0].generated,true);assert.equal(workspace.files[1].text,'import Std\ndef value : Nat := 1\n');
  assert.deepEqual(workspace.files[1].originalBytes,new Uint8Array(raw));
  catalog.inputs[0].work='other';await assert.rejects(sourceWorkspace(catalog,entry,bundle),/ownership/);
  catalog.compatibility.sha256='0'.repeat(64);await assert.rejects(sourceWorkspace(catalog,entry,bundle),/compatibility source checksum/);
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
test('edited imports expand a prepared library once and genuinely unavailable modules still fail',async()=>{
  const oldWorker=globalThis.Worker,oldFetch=globalThis.fetch;
  try {
    for(const unavailable of [false,true]) {
      const loaded=[];let expanded=false;
      globalThis.fetch=async()=>new Response('',{status:404});
      globalThis.Worker=class {
        postMessage(message){queueMicrotask(()=>{
          const send=data=>this.onmessage?.({data});
          if(message.type==='start')send({type:'ready'});
          if(message.type==='load_layer'){loaded.push(message.label);expanded||=message.label==='Additional Mathlib';send({type:'layer_loaded',id:message.id,label:message.label,ok:true,files:1});}
          if(message.type==='compile'){
            const probe=message.code.includes('__KOMOREBI_PARSE_COMPLETE__');
            if(!expanded||unavailable)send({type:'stdout',data:JSON.stringify({severity:'error',data:"object file '/lib/lean/Mathlib/Extra.olean' of module Mathlib.Extra does not exist"})});
            else if(probe)send({type:'stdout',data:JSON.stringify(completed.messages[0])});
            send({type:'result',id:message.id,success:true});
          }
        });}
        terminate(){}
      };
      const compiler=await createCompiler({baseUrl:'https://example.invalid/',mathlibManifest:'workspaces/example.json',syntaxCheck:'full'});
      try {
        const result=await compiler.run('import Mathlib.Extra\nexample : True := by trivial');
        assert.equal(result.exitCode,unavailable?1:0);assert.deepEqual(loaded,['Mathlib','Additional Mathlib']);
        if(unavailable)assert.match(result.errors.join('\n'),/outside the available compiler-matched/);
      }finally{compiler.dispose();}
    }
  }finally{globalThis.Worker=oldWorker;globalThis.fetch=oldFetch;}
});
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
