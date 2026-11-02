const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../website/assets/reference-previews.js'),'utf8');

function fixture(provider,supported=true,preferences={}) {
  const document={activeElement:null},created=[];
  class Element {
    constructor(tag,text='') {this.tagName=tag.toUpperCase();this.textContent=text;this.children=[];this.attrs={};this.dataset={};this.events={};this.isConnected=true;this.hidden=false;this.className='';this.tabIndex=['BUTTON','A'].includes(this.tagName)?0:-1;created.push(this);}
    append(...children) {this.children.push(...children);}
    replaceChildren(...children) {this.children=children;}
    setAttribute(name,value) {this.attrs[name]=value;}
    getAttribute(name) {return this.attrs[name] ?? null;}
    removeAttribute(name) {delete this.attrs[name];}
    get classList() {return {contains:name=>this.className.split(' ').includes(name)};}
    addEventListener(name,callback) {(this.events[name] ||= []).push(callback);}
    emit(name,event={}) {for(const callback of this.events[name] || []) callback({target:this,button:0,preventDefault(){},...event});}
    focus() {document.activeElement=this;}
    showModal() {this.open=true;}
    close() {this.open=false;this.emit('close');}
    after(button) {this.previewButton=button;this.nextElementSibling=button;}
    closest() {return this.tagName==='A' ? this : null;}
    getBoundingClientRect() {return {left:0,top:0,right:600,bottom:500};}
    getClientRects() {return this.hidden ? [] : [{}];}
    querySelectorAll() {return this.children.flatMap(child=>child.tagName ? [child,...child.querySelectorAll()] : []).filter(child=>child.tagName==='BUTTON' || (child.tagName==='A' && child.href) || child.tabIndex>=0);}
  }
  const script=new Element('script');script.dataset={referenceWork:'paper-i',referenceSource:'../../documents/reference-previews/paper-i.json?v=revision'};
  const link=new Element('a','Theorem 2');link.href='https://example.test/collection/read/paper-i/b.html#L2';link.dataset={referencePreview:'thm:finite'};
  document.querySelector=selector=>selector==='#chapter-text' ? {dataset:preferences} : script;document.querySelectorAll=()=>[link];document.body=new Element('body');
  document.createElement=tag=>{const result=new Element(tag);if(tag==='dialog' && !supported) result.showModal=undefined;return result;};
  document.createTextNode=text=>({textContent:text});
  let requests=0;
  const events={},timers=[],history={state:{saved:true},replaceState(state){this.state=state;}};
  vm.runInNewContext(source,{document,window:{addEventListener(name,callback){events[name]=callback;}},history,setTimeout:callback=>timers.push(callback),URL,location:new URL('https://example.test/collection/read/paper-i/a.html'),
    fetch:async()=>{requests++;return provider();}});
  const find=cls=>created.find(node=>node.className===cls);
  return {document,link,history,restoreReturn:()=>{events.pageshow?.();while(timers.length)timers.shift()();},requests:()=>requests,dialog:find('reference-preview'),content:find('reference-preview-content'),
    status:find('reference-preview-status'),context:find('reference-preview-context'),
    close:created.find(node=>node.textContent==='Close'),retry:created.find(node=>node.textContent==='Retry preview'),
    openLink:created.find(node=>node.textContent==='Open referenced passage'),
    open(){link.previewButton.emit('click');}};
}
const key='read/paper-i/b.html#L2|thm:finite';
const index={version:1,work:'paper-i',entries:{[key]:{url:'read/paper-i/b.html#L2',context:'Paper I · Second chapter',excerpt:false,
  parts:[{tag:'p',children:['Finite <script>literal</script> scope.']},{tag:'div',classes:'arithmatex',children:['\\[x<y\\]']}]}}};
const response=value=>({ok:true,json:async()=>value});
const flush=()=>new Promise(resolve=>setImmediate(resolve));

(async()=>{
  let p=fixture(()=>response(index));
  assert.equal(p.requests(),0,'Previews do not download until requested');
  assert.equal(p.link.href,'https://example.test/collection/read/paper-i/b.html#L2','Original reference navigation is unchanged');
  p.open();await flush();
  assert.equal(p.dialog.open,true);assert.equal(p.content.children.length,2);
  assert.equal(p.content.children[0].children[0].textContent,'Finite <script>literal</script> scope.');
  assert.equal(p.content.children[1].attrs['aria-label'],'Displayed equation. Scroll horizontally if needed.');
  assert.equal(p.openLink.href,p.link.href);assert.equal(p.context.textContent,'Paper I · Second chapter');
  p.close.focus();p.dialog.emit('keydown',{key:'Tab',shiftKey:true});assert.equal(p.document.activeElement,p.openLink,'Reverse Tab wraps to the last control');
  p.dialog.emit('keydown',{key:'Tab',shiftKey:false});assert.equal(p.document.activeElement,p.close,'Tab wraps to the first control');
  p.close.emit('click');assert.equal(p.document.activeElement,p.link.previewButton);
  p.open();await flush();assert.equal(p.requests(),1,'The paper index is reused');
  p.dialog.emit('keydown',{key:'Escape'});assert.equal(p.dialog.open,false);assert.equal(p.document.activeElement,p.link.previewButton);
  p.open();await flush();
  p.dialog.emit('click',{target:p.openLink,clientX:10,clientY:10});
  assert.equal(p.dialog.open,false);assert.notEqual(p.document.activeElement,p.link.previewButton,'Opening the passage does not refocus the origin');
  assert.equal(p.history.state.saved,true,'Other reader history state survives');
  p.document.activeElement=p.document.body;p.restoreReturn();await flush();
  assert.equal(p.document.activeElement,p.link.previewButton,'Returning to the page restores the originating control');
  assert.equal(p.history.state.referencePreviewReturn,undefined,'Return focus is consumed once');
  p.open();await flush();p.dialog.emit('click',{target:p.openLink,clientX:10,clientY:10});
  p.document.activeElement={id:'L2',tabIndex:-1};p.restoreReturn();
  assert.equal(p.document.activeElement,p.link.previewButton,'Same-page Back replaces focus on the old destination with the originating control');

  let finish;
  p=fixture(()=>new Promise(resolve=>{finish=resolve;}));p.open();p.close.emit('click');finish(response(index));await flush();
  assert.equal(p.content.children.length,0,'Late data cannot fill a closed preview');
  assert.equal(p.dialog.open,false);

  let fail=true;
  p=fixture(()=>fail ? {ok:false} : response(index));p.open();await flush();
  assert.match(p.status.textContent,/could not load/);assert.equal(p.retry.hidden,false);assert.equal(p.openLink.href,p.link.href);
  fail=false;p.retry.emit('click');await flush();assert.equal(p.requests(),2);assert.equal(p.content.children.length,2);

  const invalid=[{...index,work:'paper-ii'},
    {...index,entries:{[key]:{...index.entries[key],url:'read/paper-ii/b.html#L2'}}},
    {...index,entries:{[key]:{...index.entries[key],parts:[{tag:'script',children:['bad()']}]}}},
    {...index,entries:{[key]:{...index.entries[key],parts:[{tag:'a',url:'javascript:bad()',children:['Bad link']}]}}}];
  for(const value of invalid) {
    p=fixture(()=>response(value));p.open();await flush();
    assert.equal(p.content.children.length,0,'Wrong-work or executable content is never inserted');
    assert.equal(p.retry.hidden,false);
  }
  p=fixture(()=>response(index),false);
  assert.equal(p.link.previewButton,undefined,'Unsupported dialogs keep the original link alone');
  assert.equal(p.requests(),0);
  p=fixture(()=>response(index),true,{textSize:'larger',textFont:'serif'});p.open();await flush();
  assert.equal(p.content.dataset.textSize,'larger');assert.equal(p.content.dataset.textFont,'serif','Previews respect the chapter text preferences');
  console.log('PASS: lazy previews, exact source text, formula access, preserved links, focus, Escape, stale responses, retry and inert content');
})().catch(error=>{console.error(error);process.exitCode=1;});
