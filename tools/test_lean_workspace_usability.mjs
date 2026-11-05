import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';

globalThis.document={querySelector:()=>null};
const {storedWorkspaceDraft,restoreStoredWorkspaceDraft,sourceLineRange,diagnosticSourceLine}=await import('../website/assets/lean-browser.js');
const hash='a'.repeat(64),otherHash='b'.repeat(64);
function workspaces(){return [
  {id:'first',files:[{module:'Helper',path:'paper/Helper.lean',text:'def value : Nat := 1\n',sha256:hash,download:'helper.lean'},
    {module:'Main',path:'paper/Main.lean',text:'import Helper\nexample : value = 1 := rfl\n',sha256:hash,download:'main.lean'}]},
  {id:'second',files:[{module:'Other',path:'other/Other.lean',text:'example : True := by trivial\n',sha256:otherHash,download:'other.lean'}]}
];}

test('stored drafts follow file identities but reject changed original hashes and formats',()=>{
  const [workspace]=workspaces(),draft=storedWorkspaceDraft(workspace,['edited helper','edited main'],0);
  const reordered={...workspace,files:[...workspace.files].reverse()};
  assert.deepEqual(restoreStoredWorkspaceDraft(reordered,JSON.parse(JSON.stringify(draft))),{files:['edited main','edited helper'],current:1});
  for(const bad of [{...draft,schema:2},{...draft,baseHashes:undefined},{...draft,baseHashes:[hash]},
    {...draft,baseHashes:[otherHash,hash]}])assert.throws(()=>restoreStoredWorkspaceDraft(workspace,bad),/published sources changed/);
  assert.throws(()=>restoreStoredWorkspaceDraft({...workspace,files:[{...workspace.files[0],sha256:otherHash},workspace.files[1]]},draft),/published sources changed/);
  assert.throws(()=>restoreStoredWorkspaceDraft({...workspace,id:'another'},draft),/could not be matched/);
});

test('source navigation selects whole Unicode lines and never turns guard locations into proof locations',()=>{
  const source='-- 🌿 α\nexample : False := by trivial\n';
  assert.deepEqual(sourceLineRange(source,2),{start:8,end:source.length-1});
  for(const line of [0,-1,4,1.5,NaN,null])assert.equal(sourceLineRange(source,line),null);
  assert.equal(diagnosticSourceLine({origin:'compiled-source'},'error (line 2, col 20): failed',source),2);
  assert.equal(diagnosticSourceLine({origin:'compiled-source'},'warning (line 2, col 20): unfinished',source),2);
  assert.equal(diagnosticSourceLine({origin:'compiled-source'},'error: unknown identifier  (line 2, col 20)',source),2);
  assert.equal(diagnosticSourceLine({origin:'compiled-source'},'warning: declaration uses sorry  (line 2, col 20)',source),2);
  assert.equal(diagnosticSourceLine({origin:'syntax-input'},'error: syntax error at line 2, column 10',source),2);
  for(const origin of ['syntax-guard','frontend-guard','note'])assert.equal(diagnosticSourceLine({origin},'error (line 2, col 20): guard',source),null);
  for(const mapped of ['error (browser module setup, col 0): failed','error (line 90, col 0): invalid','note: example at line 2'])
    assert.equal(diagnosticSourceLine({origin:'compiled-source'},mapped,source),null);
});

let fixtureId=0;
async function fixture({storage=new Map(),sources=workspaces(),storageError=false,frontend=true,warningDependency=false}={}) {
  const names=['document','fetch','window','location','history','sessionStorage','crossOriginIsolated','Worker','crypto','getComputedStyle'];
  const saved=new Map(names.map(name=>[name,Object.getOwnPropertyDescriptor(globalThis,name)]));
  const install=(name,value)=>Object.defineProperty(globalThis,name,{value,writable:true,configurable:true});
  const elements=new Map(),windowEvents={},workers=[];
  let focused=null,severity=null,compiled=0;
  function element(){return {value:'',textContent:'',dataset:{},listeners:{},children:[],hidden:false,
    addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(){this.children=[];},append(child){this.children.push(child);},
    focus(){focused=this;},setSelectionRange(start,end){this.selectionStart=start;this.selectionEnd=end;},scrollIntoView(){this.scrolled=true;}};}
  const root={querySelector(selector){const name=selector.match(/data-local-(.*)\]/)[1];if(!elements.has(name))elements.set(name,element());return elements.get(name);}};
  const mainWindow={addEventListener(name,fn){windowEvents[name]=fn;}};mainWindow.top=mainWindow;
  class FakeWorker {
    constructor(){workers.push(this);}
    postMessage(message){queueMicrotask(()=>{
      const send=data=>this.onmessage?.({data});
      if(message.type==='start')send({type:'ready'});
      if(message.type==='dispose')send({type:'disposed',id:message.id});
      if(message.type==='load_modules')send({type:'modules_loaded',id:message.id,results:message.roots.map(root=>({root,files:1}))});
      if(message.type==='load_layer')send({type:'layer_loaded',id:message.id,label:message.label,ok:true,files:1});
      if(message.type==='reset')send({type:'reset_done',id:message.id});
      if(message.type==='compile'){
        compiled++;
        const nonce=message.code.match(/__KOMOREBI_FRONTEND_STARTED_([0-9a-f]{32})__/)?.[1];
        if(nonce){
          send({type:'stdout',data:JSON.stringify({severity:'information',data:`__KOMOREBI_FRONTEND_STARTED_${nonce}__`})});
          if(severity&&message.code.includes('example :'))send({type:'stdout',data:JSON.stringify({severity,data:severity==='warning'?'declaration uses sorry':'unknown identifier',fileName:`<komorebi-frontend-${nonce}>`,pos:{line:2,column:0}})});
          send({type:'stdout',data:JSON.stringify({severity:'information',data:`__KOMOREBI_FRONTEND_COMPLETED_${nonce}__`})});
        }else if(message.code.includes('__KOMOREBI_PARSE_COMPLETE__'))send({type:'stdout',data:JSON.stringify({severity:'information',data:'__KOMOREBI_PARSE_COMPLETE__'})});
        else if(warningDependency&&message.code.includes('def value : Nat'))send({type:'stdout',data:JSON.stringify({severity:'warning',data:'declaration uses sorry',pos:{line:4,column:0}})});
        send({type:'result',id:message.id,success:true});
      }
    });}
    terminate(){}
  }
  install('document',{querySelector:()=>root,createElement:element});
  install('fetch',async input=>String(input).endsWith('examples.json')?Response.json({examples:sources}):new Response('',{status:404}));
  install('window',mainWindow);install('location',{href:'https://example.test/lean/browser/index.html'+(frontend?'?frontend=1':'')});
  install('history',{replaceState(){}});install('crossOriginIsolated',true);install('Worker',FakeWorker);install('crypto',webcrypto);
  install('getComputedStyle',()=>({lineHeight:'23px'}));
  install('sessionStorage',{
    getItem:key=>{if(storageError)throw Error('storage unavailable');return storage.get(key)??null;},
    setItem:(key,value)=>{if(storageError)throw Error('quota exceeded');storage.set(key,value);},
    removeItem:key=>{if(storageError)throw Error('storage unavailable');storage.delete(key);}
  });
  await import('../website/assets/lean-browser.js?usability-test-'+(++fixtureId));await new Promise(setImmediate);
  async function until(done){for(let n=0;n<50;n++){if(done())return;await new Promise(setImmediate);}assert.fail('UI operation did not settle');}
  return {elements,storage,windowEvents,workers,get compiled(){return compiled;},setSeverity(value){severity=value;},get focused(){return focused;},until,
    edit(text){elements.get('code').value=text;elements.get('code').listeners.input();},
    async close(){windowEvents.pagehide?.();await new Promise(setImmediate);for(const [name,descriptor] of saved){if(descriptor)Object.defineProperty(globalThis,name,descriptor);else delete globalThis[name];}}
  };
}

test('edited files survive switching workspaces and refresh without restoring or starting a check',async()=>{
  const storage=new Map();let f=await fixture({storage});
  try {
    f.edit('import Helper\nexample : value = 2 := by rfl\n');
    f.elements.get('example').value='second';f.elements.get('example').listeners.change();
    f.edit('example : False := by trivial\n');f.windowEvents.pagehide();
    assert.equal(storage.size,2);assert.equal(f.compiled,0);
  }finally{await f.close();}
  f=await fixture({storage});
  try {
    assert.match(f.elements.get('code').value,/value = 2/);
    assert.match(f.elements.get('draft-status').textContent,/recovered/);
    assert.equal(f.elements.get('output').textContent,'No checks yet.');assert.equal(f.compiled,0);
    assert.notEqual(f.elements.get('status').dataset.state,'passed');
    f.elements.get('example').value='second';f.elements.get('example').listeners.change();
    assert.match(f.elements.get('code').value,/False/);
    f.elements.get('restore').listeners.click();assert.equal(storage.has('komorebi-lean-browser-draft-v1:second'),false);
    assert.equal(storage.has('komorebi-lean-browser-draft-v1:first'),true,'restoring one workspace must preserve other drafts');
  }finally{await f.close();}
});

test('incompatible drafts remain recoverable and unavailable storage does not break editing',async()=>{
  const [workspace]=workspaces(),old=storedWorkspaceDraft(workspace,['my helper','my proof'],1);
  const key='komorebi-lean-browser-draft-v1:first',raw=JSON.stringify({...old,baseHashes:[otherHash,otherHash]});
  const storage=new Map([[key,raw]]);let f=await fixture({storage});
  try {
    assert.equal(f.elements.get('draft-recovery').hidden,false);assert.match(f.elements.get('draft-download').href,/^blob:/);
    assert.equal(f.elements.get('code').value,workspace.files[1].text);
    f.edit('new edits');f.windowEvents.pagehide();
    assert.equal(storage.get(key),raw);assert.match(f.elements.get('draft-status').textContent,/earlier draft needs recovery/);
    assert.equal(f.compiled,0);
  }finally{await f.close();}
  f=await fixture({storageError:true});
  try {
    f.edit('unsaved edits');f.windowEvents.pagehide();
    assert.equal(f.elements.get('code').value,'unsaved edits');assert.match(f.elements.get('draft-status').textContent,/unavailable or full/);
    assert.equal(f.elements.get('run').disabled,false);assert.doesNotMatch(f.elements.get('status').textContent,/Could not load/);
  }finally{await f.close();}
});

test('setup-reload recovery remains downloadable while editing and switching workspaces',async()=>{
  const [workspace]=workspaces(),draft=storedWorkspaceDraft(workspace,['old helper','old proof'],1);
  const key='komorebi-lean-browser-reload',raw=JSON.stringify({...draft,fileKeys:['missing source',draft.fileKeys[1]],run:true});
  const storage=new Map([[key,raw]]),f=await fixture({storage});
  try {
    const link=f.elements.get('draft-download').href;assert.match(link,/^blob:/);
    assert.equal(f.elements.get('draft-recovery').hidden,false);assert.equal(f.compiled,0);
    f.edit('new edits');f.windowEvents.pagehide();
    assert.equal(f.elements.get('draft-recovery').hidden,false);assert.equal(f.elements.get('draft-download').href,link);
    f.elements.get('example').value='second';f.elements.get('example').listeners.change();
    assert.equal(f.elements.get('draft-recovery').hidden,false);assert.equal(f.elements.get('draft-download').href,link);
    assert.equal(storage.get(key),raw);assert.equal(f.compiled,0);
  }finally{await f.close();}
});

test('old results are marked stale after edits, restores and mode changes; diagnostics select the original file and line',async()=>{
  const f=await fixture();
  try {
    await f.elements.get('run-selected').listeners.click();assert.equal(f.elements.get('status').dataset.state,'passed');
    f.edit('import Helper\nexample : value = 2 := by rfl\n');
    assert.equal(f.elements.get('result-note').hidden,false);assert.notEqual(f.elements.get('status').dataset.state,'passed');
    f.setSeverity('error');await f.elements.get('run-selected').listeners.click();
    assert.equal(f.elements.get('status').dataset.state,'failed');assert.equal(f.elements.get('result-note').hidden,true);
    // The target diagnostic must take the reader back from a different file.
    const buttons=f.elements.get('diagnostics').children;
    assert.equal(buttons.length,1,f.elements.get('output').textContent);assert.equal(buttons[0].textContent,'Main · line 2');
    f.elements.get('file').value='0';f.elements.get('file').listeners.change();
    buttons[0].listeners.click();assert.equal(f.elements.get('file').value,'1');
    assert.equal(f.focused,f.elements.get('code'));
    const code=f.elements.get('code');assert.equal(code.value.slice(code.selectionStart,code.selectionEnd),'example : value = 2 := by rfl');
    f.edit(code.value+'-- edit\n');assert.equal(buttons[0].disabled,true);
    f.setSeverity('warning');await f.elements.get('run-selected').listeners.click();
    assert.equal(f.elements.get('status').dataset.state,'warning');assert.match(f.elements.get('output').textContent,/declaration uses sorry/);
    assert.equal(f.elements.get('diagnostics').children.length,1);
    f.setSeverity(null);await f.elements.get('run-selected').listeners.click();assert.equal(f.elements.get('status').dataset.state,'passed');
    f.elements.get('restore').listeners.click();assert.equal(f.elements.get('result-note').hidden,false);
    await f.elements.get('run-selected').listeners.click();assert.equal(f.elements.get('status').dataset.state,'passed');
    f.elements.get('frontend').checked=false;f.elements.get('frontend').listeners.change();
    assert.equal(f.elements.get('result-note').hidden,false);assert.notEqual(f.elements.get('status').dataset.state,'passed');
  }finally{await f.close();}
});

test('editor shortcuts keep selected/workspace scope and ignore composition, Alt and key repeat',async()=>{
  const f=await fixture();
  try {
    f.elements.get('file').value='0';f.elements.get('file').listeners.change();
    let prevented=0;
    const event={key:'Enter',ctrlKey:true,preventDefault(){prevented++;}};
    for(const extra of [{isComposing:true},{altKey:true},{repeat:true}])f.elements.get('code').listeners.keydown({...event,...extra});
    assert.equal(f.compiled,0);
    f.elements.get('code').listeners.keydown(event);
    await f.until(()=>f.elements.get('status').dataset.state==='passed');
    assert.match(f.elements.get('output').textContent,/1 of 2 workspace files/);assert.equal(f.compiled,1);
    f.elements.get('code').listeners.keydown({...event,ctrlKey:false,metaKey:true,shiftKey:true});
    await f.until(()=>f.elements.get('status').dataset.state==='passed');
    assert.equal(f.compiled,3);assert.doesNotMatch(f.elements.get('output').textContent,/1 of 2 workspace files/);
    assert.equal(prevented,3);
  }finally{await f.close();}
});

test('reused dependency warnings retain source navigation without recompiling the dependency',async()=>{
  const f=await fixture({frontend:false,warningDependency:true});
  try {
    await f.elements.get('run-selected').listeners.click();
    assert.equal(f.elements.get('status').dataset.state,'warning');assert.equal(f.compiled,4);
    assert.equal(f.elements.get('diagnostics').children[0].textContent,'Helper · line 1');
    await f.elements.get('run-selected').listeners.click();
    assert.equal(f.compiled,6,'second check runs only the target and its syntax probe');
    assert.equal(f.workers.length,1);assert.equal(f.elements.get('status').dataset.state,'warning');
    assert.match(f.elements.get('output').textContent,/Reused unchanged checked dependency/);
    const buttons=f.elements.get('diagnostics').children;
    assert.equal(buttons.length,1);assert.equal(buttons[0].textContent,'Helper · line 1');
    buttons[0].listeners.click();assert.equal(f.elements.get('file').value,'0');
    const code=f.elements.get('code');assert.equal(code.value.slice(code.selectionStart,code.selectionEnd),'def value : Nat := 1');
    f.edit(code.value+'-- dependency edited\n');assert.equal(buttons[0].disabled,true);
  }finally{await f.close();}
});
