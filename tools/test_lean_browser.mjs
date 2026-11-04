import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
import {deflateRawSync} from 'node:zlib';
globalThis.document={querySelector:()=>null};
const {moduleSource,outcome,withCompatibility,mapDiagnostic,mapWorkspaceDiagnostic,withCompatibilityImport,workspaceCheckMode,savedWorkspaceDraft,restoreWorkspaceDraft}=await import('../website/assets/lean-browser.js');
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

test('generated import profiles require a fresh completed frontend without changing other workspace modes',()=>{
  assert.deepEqual(workspaceCheckMode({files:[{generated:true,syntaxCheck:'frontend'}]}),{required:true,frontend:true});
  assert.deepEqual(workspaceCheckMode({files:[{syntaxCheck:'frontend'}]}),{required:false,frontend:false});
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
test('pinned library sources are checked separately and cannot replace receipt-bound paper sources',async()=>{
  const path='paper/Main.lean',raw=Buffer.from('import Mathlib.Tactic.Ext\nexample : True := by trivial\n');
  const bytes=sourceZip([['inputs/'+path,raw]]),revision='a'.repeat(40),module='Mathlib.Tactic.Ext';
  const source='import Mathlib.Init\n-- exact library bytes 🌿\n',libraryPath='Mathlib/Tactic/Ext.lean';
  const record={module,path:libraryPath,source,size:Buffer.byteLength(source),sha256:await sha256(Buffer.from(source)),revision,url:'https://github.com/leanprover-community/mathlib4/blob/'+revision+'/'+libraryPath};
  const entry={id:'a',path,work:'paper',label:'Paper',inspect:'source.html',files:[{module:'Main',input:0}],library:[module],issues:[]};
  const catalog={entries:[entry],inputs:[{path,work:'paper',size:raw.length,sha256:await sha256(raw)}],mathlibRevision:revision,librarySources:{[module]:record}};
  const bundle={bytes,entries:zipDirectory(bytes)},workspace=await sourceWorkspace(catalog,entry,bundle);
  assert.equal(workspace.files[0].library,true);assert.equal(workspace.files[0].generated,undefined);
  assert.equal(workspace.files[0].text,source);assert.deepEqual(workspace.files[0].originalBytes,new Uint8Array(Buffer.from(source)));
  assert.equal(workspace.files[1].path,path);assert.equal(workspace.files[1].library,undefined);
  record.syntaxCheck='frontend';
  const required=await sourceWorkspace(catalog,entry,bundle);
  assert.equal(required.files[0].syntaxCheck,'frontend');
  assert.deepEqual(workspaceCheckMode(required),{required:true,frontend:true});
  record.syntaxCheck='skip';await assert.rejects(sourceWorkspace(catalog,entry,bundle),/Unsupported library source syntax check/);delete record.syntaxCheck;
  record.source+='-- changed';await assert.rejects(sourceWorkspace(catalog,entry,bundle),/library source checksum/);record.source=source;
  record.revision='b'.repeat(40);await assert.rejects(sourceWorkspace(catalog,entry,bundle),/Invalid pinned/);record.revision=revision;
  entry.library=['Mathlib.Missing'];await assert.rejects(sourceWorkspace(catalog,entry,bundle),/Invalid pinned/);
});

test('workspace assembly follows the full import order with compatibility helpers first',async()=>{
  const helperPath='paper/Helper.lean',path='paper/Main.lean',helperRaw=Buffer.from('\uFEFFimport Std\r\ndef value : Nat := 1\r\n');
  const raw=Buffer.from('import Helper\nimport Mathlib.Tactic.Positivity\nexample : value = 1 := rfl\n');
  const bytes=sourceZip([['inputs/'+helperPath,helperRaw],['inputs/'+path,raw]]),bundle={bytes,entries:zipDirectory(bytes)},revision='a'.repeat(40);
  const finset='Mathlib.Tactic.Positivity.Finset',umbrella='Mathlib.Tactic.Positivity';
  async function libraryRecord(module,source,syntaxCheck) {
    const libraryPath=module.replaceAll('.','/')+'.lean';
    return {module,path:libraryPath,source,size:Buffer.byteLength(source),sha256:await sha256(Buffer.from(source)),revision,url:'https://github.com/leanprover-community/mathlib4/blob/'+revision+'/'+libraryPath,...(syntaxCheck?{syntaxCheck}:{})};
  }
  const entry={id:'a',path,work:'paper',label:'Paper',files:[{module:'Helper',input:0},{module:'Main',input:1}],library:[finset,umbrella],order:[{file:0},{library:finset},{library:umbrella},{file:1}],issues:[],legacy:true,tactics:true};
  const compatibility={module:'Mathlib.Tactic',source:'import Mathlib.Tactic.Ring\n',sha256:await sha256(Buffer.from('import Mathlib.Tactic.Ring\n'))};
  const legacy={module:'Browser.Legacy',source:'import Std\n',sha256:await sha256(Buffer.from('import Std\n'))};
  const catalog={entries:[entry],inputs:[{path:helperPath,work:'paper',size:helperRaw.length,sha256:await sha256(helperRaw)},{path,work:'paper',size:raw.length,sha256:await sha256(raw)}],mathlibRevision:revision,
    librarySources:{[finset]:await libraryRecord(finset,'import Std\n','frontend'),[umbrella]:await libraryRecord(umbrella,'public import '+finset+'\n')},compatibility,legacy};
  const workspace=await sourceWorkspace(catalog,entry,bundle);
  assert.deepEqual(workspace.files.map(file=>file.module),['Browser.Legacy','Mathlib.Tactic','Helper',finset,umbrella,'Main']);
  assert.equal(workspace.files[2].text,'import Std\ndef value : Nat := 1\n');
  assert.deepEqual(workspace.files[2].originalBytes,new Uint8Array(helperRaw));
  assert.equal(workspace.files[3].syntaxCheck,'frontend');assert.equal(workspace.files.at(-1).path,path);
  assert.equal(workspaceCheckMode(workspace).frontend,true);
  const invalid=[[],[{file:0},{file:1}],entry.order.concat({file:1}),
    [{file:0},{library:finset},{library:umbrella},{file:2}],
    [{file:false},{library:finset},{library:umbrella},{file:1}],
    [{file:0},{library:finset},{library:'Mathlib.Missing'},{file:1}],
    [{file:0},{library:finset},{file:1},{library:umbrella}],
    [{file:0},{library:finset,file:1},{library:umbrella}],
    [{file:0},{other:0},{library:finset},{library:umbrella},{file:1}]];
  for(const order of invalid)await assert.rejects(sourceWorkspace(catalog,{...entry,order},bundle),/source order/);
  await assert.rejects(sourceWorkspace(catalog,{...entry,path:'paper/Other.lean'},bundle),/Selected retained source identity/);
  const oldEntry={...entry};delete oldEntry.order;
  assert.deepEqual((await sourceWorkspace(catalog,oldEntry,bundle)).files.map(file=>file.module),['Browser.Legacy','Mathlib.Tactic',finset,umbrella,'Helper','Main']);
});

test('required library mode does not overwrite the reader preference for other workspaces',()=>{
  assert.deepEqual(workspaceCheckMode(undefined),{required:false,frontend:false});
  const standard={files:[{module:'Main'}]},required={files:[{module:'Library',library:true,syntaxCheck:'frontend'},{module:'Main'}]};
  assert.deepEqual(workspaceCheckMode(required,false),{required:true,frontend:true});
  assert.deepEqual(workspaceCheckMode(standard,false),{required:false,frontend:false});
  assert.deepEqual(workspaceCheckMode(standard,true),{required:false,frontend:true});
  assert.deepEqual(workspaceCheckMode(required,true),{required:true,frontend:true});
});

test('saved drafts follow source identities when dependencies change checking order',()=>{
  const library={module:'Mathlib.Tactic.Pilot',path:'Mathlib/Tactic/Pilot.lean',library:true};
  const dependency={module:'Helper',path:'paper/Helper.lean'},main={module:'Main',path:'paper/Main.lean'};
  const old={id:'source-main',files:[library,dependency,main]};
  const draft=savedWorkspaceDraft(old,['edited library','edited helper','edited main'],0);
  const next={id:old.id,files:[dependency,library,main]};
  assert.deepEqual(restoreWorkspaceDraft(next,draft),{files:['edited helper','edited library','edited main'],current:1});
  assert.deepEqual(draft.files,['edited library','edited helper','edited main']);
  for(const bad of [
    {...draft,fileKeys:undefined}, {...draft,fileKeys:[draft.fileKeys[0],draft.fileKeys[0],draft.fileKeys[2]]},
    {...draft,files:[1,'helper','main']}, {...draft,id:'another-source'},
    {...draft,fileKeys:['unknown',...draft.fileKeys.slice(1)]}
  ])assert.throws(()=>restoreWorkspaceDraft(next,bad),/saved draft could not be matched/);
});

test('compatibility is explicit and diagnostics point to the original proof',()=>{
  const source='import A\n\nexample : True := by trivial\n';
  const compatibility='theorem helper : True := by trivial\n';
  assert.equal(withCompatibility(source,compatibility),'import A\n'+compatibility+source.slice(9));
  assert.equal(mapDiagnostic('error (line 6, col 0)',source,true),'error (line 3, col 0)');
  assert.equal(mapDiagnostic('syntax error at line 4, column 0',source,false,compatibility),'syntax error at line 3, column 0');
  assert.equal(mapDiagnostic('error (line 2, col 0)',source,false,compatibility),'error (browser compatibility lemma, col 0)');
});

test('dependency parser locations are not mapped through the export wrapper twice',()=>{
  const source='import Std\nexample : := by\n';
  const parser={text:'error: syntax error at line 2, column 10',origin:'syntax-input'};
  assert.equal(mapWorkspaceDiagnostic(parser,source,true),parser.text);
  assert.equal(mapWorkspaceDiagnostic({text:'error (line 5, col 10)',origin:'compiled-source'},source,true),'error (line 2, col 10)');
  const versioned=withCompatibilityImport(source,'KomorebiBrowser.Compatibility');
  assert.equal(mapWorkspaceDiagnostic({...parser,text:'error: syntax error at line 3, column 10'},versioned,true,'',source),parser.text);
  const guard={text:'error (line 20, col 2)',origin:'syntax-guard'};
  assert.equal(mapWorkspaceDiagnostic(guard,versioned,true,'',source),'Browser syntax check: '+guard.text);
});

async function simulatedCompiler(probe,main={success:true,messages:[]},source='example : True := by trivial',runOptions={}) {
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
    try{return await compiler.run(source,undefined,runOptions);}finally{compiler.dispose();}
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
test('partial library installation reports its cause before attempting compilation',async()=>{
  const oldWorker=globalThis.Worker,oldFetch=globalThis.fetch;
  try {
    for(const source of ['import Mathlib.Init','import Lean']) {
      let compiled=false;
      globalThis.fetch=async()=>new Response('',{status:404});
      globalThis.Worker=class {
        postMessage(message){queueMicrotask(()=>{
          const send=data=>this.onmessage?.({data});
          if(message.type==='start')send({type:'ready'});
          if(message.type==='load_layer')send({type:'layer_loaded',id:message.id,label:message.label,ok:false,error:'pack checksum mismatch'});
          if(message.type==='load_modules')send({type:'modules_loaded',id:message.id,results:[{root:'Lean',files:0,error:'pack checksum mismatch'}]});
          if(message.type==='compile'){compiled=true;send({type:'result',id:message.id,success:true});}
        });}
        terminate(){}
      };
      const compiler=await createCompiler({baseUrl:'https://example.invalid/',syntaxCheck:'full'});
      try {await assert.rejects(compiler.run(source),/Loading (Mathlib|Lean): pack checksum mismatch/);assert.equal(compiled,false);}
      finally{compiler.dispose();}
    }
  }finally{globalThis.Worker=oldWorker;globalThis.fetch=oldFetch;}
});

test('a missing or failed syntax probe cannot turn a silent run into success',async()=>{
  await assert.rejects(simulatedCompiler({success:true,messages:[]}),/did not complete the syntax check/);
  await assert.rejects(simulatedCompiler({success:false,error:'parser worker stopped'}),/parser worker stopped/);
  await assert.rejects(simulatedCompiler(completed,{success:true,messages:[]},'example : False := b\u0000y trivial'),/unsupported control characters/);
  for(const separator of ['\u2028','\u2029']) {
    await assert.rejects(simulatedCompiler(completed,undefined,'example'+separator+': True := by trivial'),/unsupported control characters/);
    await assert.rejects(simulatedCompiler(completed,undefined,undefined,{syntaxSource:'example'+separator+': True := by trivial'}),/unsupported control characters/);
  }
  await assert.rejects(simulatedCompiler(completed,undefined,undefined,{syntaxSource:42}),/syntaxSource must be a source string/);
});

test('compiler distinguishes input parser coordinates from generated guard diagnostics',async()=>{
  const parsed=await simulatedCompiler({success:true,messages:[{severity:'error',data:'syntax error at line 2, column 10'}]});
  assert.equal(parsed.exitCode,1);
  assert.deepEqual(parsed.diagnostics,[{text:parsed.errors[0],origin:'syntax-input'}]);
  const guard=await simulatedCompiler({success:true,messages:[{severity:'error',data:'unknown identifier in guard',pos:{line:20,column:2}}]});
  assert.equal(guard.exitCode,1);
  assert.deepEqual(guard.diagnostics,[{text:guard.errors[0],origin:'syntax-guard'}]);
});

test('Stop during each isolation setup wait cannot reload or resume the canceled check',async()=>{
  const names=['document','fetch','window','location','history','navigator','sessionStorage','crossOriginIsolated','isSecureContext'];
  const saved=new Map(names.map(name=>[name,Object.getOwnPropertyDescriptor(globalThis,name)]));
  const install=(name,value)=>Object.defineProperty(globalThis,name,{value,writable:true,configurable:true});
  try {
    for(const phase of ['registration','ready','controller']) {
      const elements=new Map();
      function element(){return {value:'',textContent:'',dataset:{},listeners:{},children:[],
        addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(){this.children=[];},append(child){this.children.push(child);}};}
      const root={querySelector(selector){const name=selector.match(/data-local-(.*)\]/)[1];if(!elements.has(name))elements.set(name,element());return elements.get(name);}};
      const mainWindow={};mainWindow.top=mainWindow;
      let release,reloads=0,controllerChanged;
      const pending=new Promise(resolve=>{release=resolve;});
      const worker={
        register:()=>phase==='registration'?pending:Promise.resolve({}),
        ready:phase==='ready'?pending:Promise.resolve({}),
        controller:phase==='controller'?null:{},
        addEventListener(name,handler){controllerChanged=handler;},
        removeEventListener(){controllerChanged=null;}
      };
      const storage=new Map();
      install('document',{querySelector:()=>root,createElement:element});
      install('fetch',async()=>Response.json({examples:[{id:'example',files:[{module:'Example',text:'example : True := by trivial',sha256:'0'.repeat(64),download:'source.lean'}]}]}));
      install('window',mainWindow);
      install('location',{href:'https://example.test/lean/browser/index.html',reload(){reloads++;}});
      install('history',{replaceState(){}});
      install('navigator',{serviceWorker:worker});
      install('sessionStorage',{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)});
      install('crossOriginIsolated',false);install('isSecureContext',true);
      await import('../website/assets/lean-browser.js?cancel-isolation-'+phase);
      await new Promise(setImmediate);
      const running=elements.get('run').listeners.click();
      await new Promise(setImmediate);
      elements.get('stop').listeners.click();
      if(phase==='controller'){assert.equal(typeof controllerChanged,'function');worker.controller={};controllerChanged();}
      else release({});
      await running;
      assert.equal(reloads,0,phase);
      assert.equal(storage.size,0,phase);
      assert.equal(elements.get('status').textContent,'Stopped. This run produced no result.',phase);
    }
  } finally {
    for(const [name,descriptor] of saved){if(descriptor)Object.defineProperty(globalThis,name,descriptor);else delete globalThis[name];}
  }
});

for(const cancelWaitingRun of [false,true])test(`new Run waits for idle compiler cleanup${cancelWaitingRun?' across repeated Stop and canceled waits':''}`,async()=>{
  const names=['document','fetch','Worker','crypto','window','location','history','sessionStorage','crossOriginIsolated','setTimeout'];
  const saved=new Map(names.map(name=>[name,Object.getOwnPropertyDescriptor(globalThis,name)]));
  const install=(name,value)=>Object.defineProperty(globalThis,name,{value,writable:true,configurable:true});
  const schedule=globalThis.setTimeout;
  const elements=new Map(),workers=[],events=[];
  function element(){return {value:'',textContent:'',dataset:{},listeners:{},children:[],
    addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(){this.children=[];},append(child){this.children.push(child);}};}
  const root={querySelector(selector){const name=selector.match(/data-local-(.*)\]/)[1];if(!elements.has(name))elements.set(name,element());return elements.get(name);}};
  const mainWindow={};mainWindow.top=mainWindow;
  class FakeWorker {
    constructor(){this.index=workers.length;workers.push(this);events.push('create '+this.index);}
    send(data){this.onmessage?.({data});}
    postMessage(message){
      if(message.type==='dispose'){this.disposal=message;return;}
      queueMicrotask(()=>{
        if(message.type==='start')this.send({type:'ready'});
        if(message.type==='load_modules')this.send({type:'modules_loaded',id:message.id,results:message.roots.map(root=>({root,files:1}))});
        if(message.type==='load_layer')this.send({type:'layer_loaded',id:message.id,label:message.label,ok:true,files:1});
        if(message.type==='reset')this.send({type:'reset_done',id:message.id});
        if(message.type==='compile'){
          const nonce=message.code.match(/__KOMOREBI_FRONTEND_STARTED_([0-9a-f]{32})__/)[1];
          for(const phase of ['STARTED','COMPLETED'])this.send({type:'stdout',data:JSON.stringify({severity:'information',data:`__KOMOREBI_FRONTEND_${phase}_${nonce}__`})});
          this.send({type:'result',id:message.id,success:true});
        }
      });
    }
    terminate(){this.terminated=true;events.push('terminate '+this.index);}
    acknowledge(){assert.ok(this.disposal);this.send({type:'disposed',id:this.disposal.id});}
  }
  try {
    install('document',{querySelector:()=>root,createElement:element});
    install('fetch',async input=>String(input).endsWith('examples.json')
      ?Response.json({examples:[{id:'example',files:[{module:'Example',text:'example : True := by trivial',sha256:'0'.repeat(64),download:'source.lean'}]}]})
      :new Response('',{status:404}));
    install('Worker',FakeWorker);install('crypto',webcrypto);install('window',mainWindow);
    // Hold the idle fallback deterministically; the runtime suite separately
    // tests its 100 ms bound. This test releases the matching acknowledgement.
    install('setTimeout',(fn,delay,...args)=>schedule(fn,delay===100?60000:delay,...args));
    install('location',{href:'https://example.test/lean/browser/index.html?frontend=1'});
    install('history',{replaceState(){}});
    install('sessionStorage',{getItem:()=>null,removeItem(){}});install('crossOriginIsolated',true);
    await import('../website/assets/lean-browser.js?retiring-compiler-'+cancelWaitingRun);
    await new Promise(setImmediate);
    const run=()=>elements.get('run').listeners.click();
    await run();
    assert.equal(elements.get('status').dataset.state,'passed');
    assert.equal(workers.length,1);assert.ok(workers[0].disposal);
    let waiting=run();
    await new Promise(setImmediate);
    assert.equal(workers.length,1,'idle cleanup must finish before a replacement worker is created');
    if(cancelWaitingRun){
      elements.get('stop').listeners.click();
      const canceled=waiting;
      waiting=run();
      await new Promise(setImmediate);
      assert.equal(workers.length,1,'repeated dispose with compiler=null must retain the pending closure');
      workers[0].acknowledge();
      await canceled;
    }else workers[0].acknowledge();
    await waiting;
    assert.equal(workers.length,2,'a canceled generation must not create another compiler after its wait');
    assert.ok(events.indexOf('terminate 0')<events.indexOf('create 1'));
    assert.equal(elements.get('status').dataset.state,'passed');
    workers[1].acknowledge();
    await new Promise(setImmediate);
  } finally {
    for(const worker of workers)if(worker.disposal&&!worker.terminated)worker.acknowledge();
    for(const [name,descriptor] of saved){if(descriptor)Object.defineProperty(globalThis,name,descriptor);else delete globalThis[name];}
  }
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
