import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';

// UI/protocol integration only. Real Lean source acceptance is checked in a browser.
async function withPage(workspace, check, {isolated=true,savedDraft=null,frontend=true,expandedPlan}={}) {
  const names=['document','fetch','Worker','crypto','window','location','history','sessionStorage','crossOriginIsolated','isSecureContext','navigator'];
  const saved=new Map(names.map(name=>[name,Object.getOwnPropertyDescriptor(globalThis,name)]));
  const install=(name,value)=>Object.defineProperty(globalThis,name,{value,writable:true,configurable:true});
  const elements=new Map(),workers=[],calls=[],storage=new Map();let reloads=0;
  if(savedDraft)storage.set('komorebi-lean-browser-reload',JSON.stringify(savedDraft));
  function element(){return {value:'',textContent:'',dataset:{},listeners:{},children:[],
    addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(){this.children=[];},append(child){this.children.push(child);}};}
  const root={querySelector(selector){const name=selector.match(/data-local-(.*)\]/)[1];if(!elements.has(name))elements.set(name,element());return elements.get(name);}};
  class FakeWorker {
    constructor(){this.index=workers.length;workers.push(this);}
    send(data){this.onmessage?.({data});}
    postMessage(message){queueMicrotask(()=>{
      if(message.type==='dispose'){this.send({type:'disposed',id:message.id});return;}
      if(message.type==='start')this.send({type:'ready'});
      if(message.type==='reset')this.send({type:'reset_done',id:message.id});
      if(message.type==='load_modules')this.send({type:'modules_loaded',id:message.id,results:message.roots.map(root=>({root,files:1}))});
      if(message.type==='load_layer')this.send({type:'layer_loaded',id:message.id,label:message.label,ok:true,files:1});
      if(message.type==='compile'){
        if(message.code.includes('__KOMOREBI_PARSE_COMPLETE__')){
          this.send({type:'stdout',data:JSON.stringify({severity:'information',data:'__KOMOREBI_PARSE_COMPLETE__'})});
          this.send({type:'result',id:message.id,success:true});return;
        }
        const nonce=message.code.match(/__KOMOREBI_FRONTEND_STARTED_([0-9a-f]{32})__/)?.[1];
        const tags=[...message.code.matchAll(/SELECTED_CASE_[A-Z]+/g)].map(match=>match[0]);
        const tag=[...new Set(tags)].join(',');
        calls.push({tag,worker:this.index,exported:message.code.includes('IO.FS.createDirAll')});
        if(nonce)for(const phase of ['STARTED','COMPLETED'])this.send({type:'stdout',data:JSON.stringify({severity:'information',data:`__KOMOREBI_FRONTEND_${phase}_${nonce}__`})});
        if(tag.includes('BAD'))this.send({type:'stdout',data:JSON.stringify({severity:'error',data:'INTENTIONAL_BAD_SOURCE'})});
        if(tag.includes('WARN'))this.send({type:'stdout',data:JSON.stringify({severity:'warning',data:'INTENTIONAL_WARNING'})});
        this.send({type:'result',id:message.id,success:true});
      }
    });}
    terminate(){this.terminated=true;}
  }
  try {
    const mainWindow={};mainWindow.top=mainWindow;
    install('document',{querySelector:()=>root,createElement:element});
    install('fetch',async input=>String(input).endsWith('examples.json')?Response.json({examples:[workspace],expanded_download_plan:expandedPlan}):new Response('',{status:404}));
    install('Worker',FakeWorker);install('crypto',webcrypto);install('window',mainWindow);
    install('location',{href:'https://example.test/lean/browser/index.html'+(frontend?'?frontend=1':''),reload(){reloads++;}});
    install('history',{replaceState(){}});install('sessionStorage',{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)});
    install('crossOriginIsolated',isolated);install('isSecureContext',true);
    install('navigator',{serviceWorker:{register:async()=>({}),ready:Promise.resolve({}),controller:{}}});
    await import('../website/assets/lean-browser.js?selected-ui-'+Math.random());
    await new Promise(setImmediate);
    const pick=index=>{elements.get('file').value=String(index);elements.get('file').listeners.change();};
    const runSelected=()=>elements.get('run-selected').listeners.click();
    const runWorkspace=()=>elements.get('run').listeners.click();
    await check({elements,workers,calls,pick,runSelected,runWorkspace,storage,get reloads(){return reloads;}});
  } finally {
    if(elements.has('stop'))elements.get('stop').listeners.click();
    if(elements.get('draft-download')?.href)URL.revokeObjectURL(elements.get('draft-download').href);
    await new Promise(setImmediate);
    for(const [name,descriptor] of saved){if(descriptor)Object.defineProperty(globalThis,name,descriptor);else delete globalThis[name];}
  }
}
const file=(module,text)=>({module,text,path:module+'.lean',sha256:'0'.repeat(64),download:'source.lean'});

test('first-download notice follows standard and experimental plans without starting a compiler',async()=>{
  const workspace={id:'download-plans',files:[file('Main','import Std')],download_plan:{bytes:4*1048576+1,files:12}};
  await withPage(workspace,async({elements,workers})=>{
    assert.match(elements.get('download-note').textContent,/up to 5 MiB in 12/);
    elements.get('frontend').checked=true;elements.get('frontend').listeners.change();
    assert.match(elements.get('download-note').textContent,/experimental syntax: up to 10 MiB in 40/);
    elements.get('frontend').checked=false;elements.get('frontend').listeners.change();
    assert.match(elements.get('download-note').textContent,/this workspace: up to 5 MiB in 12/);
    assert.equal(workers.length,0);
  },{frontend:false,expandedPlan:{bytes:10*1048576,files:40}});
});

test('required frontend routes cannot display the smaller standard download plan',async()=>{
  const workspace={id:'forced-download-plan',files:[{...file('Library','import Std'),library:true,syntaxCheck:'frontend',revision:'a'.repeat(40)}],download_plan:{bytes:1048576,files:3}};
  await withPage(workspace,async({elements,workers})=>{
    assert.equal(elements.get('frontend').checked,true);
    assert.match(elements.get('download-note').textContent,/experimental syntax: up to 10 MiB in 40/);
    assert.equal(workers.length,0);
  },{frontend:false,expandedPlan:{bytes:10*1048576,files:40}});
});

test('invalid workspace plan falls back to the broader recorded plan',async()=>{
  const workspace={id:'bad-download-plan',files:[file('Main','import Std')],download_plan:{bytes:-1,files:3}};
  await withPage(workspace,async({elements,workers})=>{
    assert.match(elements.get('download-note').textContent,/up to 10 MiB in 40/);
    assert.equal(workers.length,0);
  },{frontend:false,expandedPlan:{bytes:10*1048576,files:40}});
});

test('selected checking executes exactly the ancestor closure and cannot claim the workspace passed',async()=>{
  const workspace={id:'selection',files:[
    file('A','import Std\n-- SELECTED_CASE_A\nexample : True := by trivial'),
    file('Unused','import Std\n-- SELECTED_CASE_BAD\nexample : False := by trivial'),
    file('Main','import A\n-- SELECTED_CASE_MAIN\nexample : True := by trivial')]};
  await withPage(workspace,async({elements,calls,runSelected,runWorkspace})=>{
    await runSelected();
    assert.deepEqual(calls.map(call=>call.tag),['SELECTED_CASE_A','SELECTED_CASE_MAIN']);
    assert.deepEqual(calls.map(call=>call.exported),[true,false]);
    assert.match(elements.get('output').textContent,/Selected file: Main · 2 of 3 workspace files/);
    assert.equal(elements.get('status').textContent,'Selected file and its dependencies checked with no diagnostics.');
    calls.length=0;await runWorkspace();
    assert.deepEqual(calls.map(call=>call.tag),['SELECTED_CASE_A','SELECTED_CASE_BAD']);
    assert.equal(elements.get('status').dataset.state,'failed');
    assert.match(elements.get('status').textContent,/workspace did not pass/);
  });
});

test('isolation setup saves the selected-file scope without starting a compiler',async()=>{
  const workspace={id:'isolation-selection',files:[file('A','import Std\n-- SELECTED_CASE_A\nexample : True := by trivial'),file('Main','import A\n-- SELECTED_CASE_MAIN\nexample : True := by trivial')]};
  await withPage(workspace,async page=>{
    page.pick(0);await page.runSelected();
    const draft=JSON.parse(page.storage.get('komorebi-lean-browser-reload'));
    assert.equal(draft.runScope,'selected');assert.equal(draft.current,0);
    assert.equal(page.reloads,1);assert.equal(page.workers.length,0);
  },{isolated:false});
});

for(const scope of ['selected','unsupported'])test(`saved ${scope} check scope cannot become an unintended full run`,async()=>{
  const workspace={id:'resume-selection',files:[file('A','import Std\n-- SELECTED_CASE_A\nexample : True := by trivial'),file('Main','import A\n-- SELECTED_CASE_BAD\nexample : False := by trivial')]};
  const draft={id:workspace.id,files:workspace.files.map(f=>f.text),fileKeys:workspace.files.map(f=>JSON.stringify([f.module,f.path,'source'])),current:0,run:true,runScope:scope};
  await withPage(workspace,async({elements,calls,workers,storage})=>{
    const deadline=Date.now()+2000;
    while(elements.get('status').dataset.state!==(scope==='selected'?'passed':'failed')){assert.ok(Date.now()<deadline,'saved check did not settle');await new Promise(setImmediate);}
    if(scope==='selected'){
      assert.deepEqual(calls.map(call=>call.tag),['SELECTED_CASE_A']);
      assert.match(elements.get('output').textContent,/1 of 2 workspace files/);
    }else{
      assert.equal(workers.length,0);assert.match(elements.get('status').textContent,/scope is unsupported/);
      assert.equal(storage.has('komorebi-lean-browser-reload'),true);
    }
  },{savedDraft:draft});
});

test('a selected dependency becomes the unwrapped target and changing targets creates a fresh compiler',async()=>{
  const workspace={id:'roles',files:[file('A','import Std\n-- SELECTED_CASE_A\nexample : True := by trivial'),
    file('Main','import A\n-- SELECTED_CASE_MAIN\nexample : True := by trivial')]};
  await withPage(workspace,async({elements,workers,calls,pick,runSelected})=>{
    pick(0);await runSelected();
    assert.deepEqual(calls.map(call=>[call.tag,call.exported]),[['SELECTED_CASE_A',false]]);
    assert.match(elements.get('output').textContent,/1 of 2 workspace files/);
    pick(1);await runSelected();
    assert.deepEqual(calls.slice(1).map(call=>[call.tag,call.exported]),[['SELECTED_CASE_A',true],['SELECTED_CASE_MAIN',false]]);
    assert.equal(workers.length,2);
    assert.equal(workers[0].terminated,true);
  });
});

test('selected import errors reject before a compiler starts, while selected warnings remain warnings',async()=>{
  const workspace={id:'preflight',files:[file('A','import MissingProject\n-- SELECTED_CASE_A\nexample : True := by trivial'),
    file('Main','import Std\n-- SELECTED_CASE_WARN\nexample : True := by trivial')]};
  await withPage(workspace,async({elements,workers,calls,pick,runSelected})=>{
    pick(0);await runSelected();
    assert.equal(workers.length,0);assert.equal(calls.length,0);
    assert.match(elements.get('output').textContent,/Missing project import MissingProject/);
    assert.equal(elements.get('status').dataset.state,'failed');
    pick(1);await runSelected();
    assert.equal(elements.get('status').dataset.state,'warning');
    assert.match(elements.get('status').textContent,/Selected-file check completed with warnings/);
    assert.match(elements.get('output').textContent,/INTENTIONAL_WARNING/);
  });
});

test('standard selected checks reuse only unchanged dependencies and preserve warning receipts and target roles',async()=>{
  const workspace={id:'warm-selection',files:[file('A','import Std\n-- SELECTED_CASE_WARN\nexample : True := by trivial'),file('Main','import A\n-- SELECTED_CASE_MAIN\nexample : True := by trivial')]};
  await withPage(workspace,async({elements,calls,workers,pick,runSelected})=>{
    await runSelected();
    assert.equal(elements.get('status').dataset.state,'warning');
    assert.deepEqual(calls.map(call=>call.tag),['SELECTED_CASE_WARN','SELECTED_CASE_MAIN']);
    await runSelected();
    assert.equal(workers.length,1);
    assert.deepEqual(calls.map(call=>call.tag),['SELECTED_CASE_WARN','SELECTED_CASE_MAIN','SELECTED_CASE_MAIN']);
    assert.equal(elements.get('status').dataset.state,'warning');
    assert.match(elements.get('output').textContent,/Reused unchanged checked dependency/);
    assert.match(elements.get('output').textContent,/INTENTIONAL_WARNING/);
    pick(0);await runSelected();
    assert.equal(workers.length,2,'exported dependency becoming target must retire its imported environment');
    assert.equal(workers[0].terminated,true);assert.equal(calls.at(-1).exported,false);
    pick(1);await runSelected();assert.equal(workers.length,3);
    pick(0);elements.get('code').value='import Std\n-- SELECTED_CASE_CHANGED\nexample : True := by trivial';pick(1);
    await runSelected();
    assert.equal(workers.length,4,'edited dependency must invalidate the warm receipt');
    assert.deepEqual(calls.slice(-2).map(call=>call.tag),['SELECTED_CASE_CHANGED','SELECTED_CASE_MAIN']);
    assert.equal(elements.get('status').dataset.state,'passed');
    assert.doesNotMatch(elements.get('output').textContent,/Reused unchanged|INTENTIONAL_WARNING/);
  },{frontend:false});
});
