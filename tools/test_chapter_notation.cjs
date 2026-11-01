const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const search=require('../website/assets/notation-search.js');
const source=fs.readFileSync(require('node:path').join(__dirname,'../website/assets/chapter-notation.js'),'utf8');

function fixture(provider) {
  const document={activeElement:null};
  class Element {
    constructor(tag='div',text='') {this.tagName=tag.toUpperCase();this.textContent=text;this.children=[];this.attrs={};this.events={};this.hidden=false;this.isConnected=true;this.value='';}
    append(...children) {this.children.push(...children);}
    replaceChildren(...children) {this.children=children;}
    setAttribute(key,value) {this.attrs[key]=value;}
    removeAttribute(key) {delete this.attrs[key];}
    addEventListener(name,callback) {(this.events[name] ||= []).push(callback);}
    emit(name,event={}) {for(const callback of this.events[name] || []) callback({target:this,preventDefault(){},...event});}
    focus() {document.activeElement=this;}
    showModal() {this.open=true;}
    close() {this.open=false;this.emit('close');}
    closest() {return null;}
    getBoundingClientRect() {return {left:0,top:0,right:600,bottom:500};}
  }
  const opener=new Element('button'),fallback=new Element('a'),dialog=new Element('dialog');
  opener.hidden=true;dialog.open=false;dialog.dataset={work:'paper-i',source:'../../notation/reader/paper-i.json?v=revision'};
  const input=new Element('input'),form=new Element('form'),status=new Element('p'),results=new Element('ol'),close=new Element('button');
  const elements={'#chapter-notation':dialog,'.chapter-notation-open':opener,'.chapter-notation-fallback':fallback,
    '#chapter-notation-query':input,form,'.chapter-notation-status':status,'.chapter-notation-results':results,'.chapter-notation-close':close};
  dialog.querySelector=selector=>elements[selector];
  document.querySelector=selector=>elements[selector] || null;
  document.createElement=tag=>new Element(tag);
  let requests=0;
  const window={KomorebiNotationSearch:search,getSelection(){return null;}};
  vm.runInNewContext(source,{document,window,URL,location:new URL('https://example.test/collection/read/paper-i/chapter.html'),
    fetch:async()=>{requests++;return provider();},setTimeout,clearTimeout});
  return {document,opener,fallback,dialog,input,form,status,results,close,requests:()=>requests,
    open(){opener.emit('click');},submit(value){input.value=value;form.emit('submit');}};
}
const index={version:2,source_revision:'revision',works:[{id:'paper-i'}],
  contexts:[{work:'paper-i',excerpt:'A <script>literal</script> source excerpt.',source_url:'read/paper-i/source.html#L7',
    reading_url:'read/paper-i/chapter.html#L7',source_label:'chapter.tex, line 7',table:null}],
  entries:[{work:'paper-i',tex:'x',names:['x'],aliases:'x',display:null,context:0,kind:'definition-passage',url:'notation/paper-i.html#symbol-x'}]};
const response=data=>({ok:true,json:async()=>data});
const flush=()=>new Promise(resolve=>setImmediate(resolve));

(async()=>{
  let p=fixture(()=>response(index));
  assert.equal(p.requests(),0,'Closed help does not download notation');
  assert.equal(p.opener.hidden,false);assert.equal(p.fallback.hidden,true);
  p.open();await flush();
  assert.equal(p.dialog.open,true);assert.equal(p.document.activeElement,p.input);
  assert.equal(p.results.children.length,1);
  const row=p.results.children[0];
  assert.equal(row.children[2].textContent,'A <script>literal</script> source excerpt.','Source text is inserted as text');
  assert.equal(row.children[3].children[0].href,'https://example.test/collection/read/paper-i/chapter.html#L7');
  p.close.emit('click');assert.equal(p.dialog.open,false);assert.equal(p.document.activeElement,p.opener);
  p.open();await flush();assert.equal(p.requests(),1,'Reopening reuses only this work’s data');
  p.dialog.emit('keydown',{key:'Escape'});assert.equal(p.dialog.open,false);assert.equal(p.document.activeElement,p.opener);
  p.open();await flush();
  p.submit('not-present');await flush();assert.equal(p.results.children.length,0);assert.match(p.status.textContent,/No matching/);
  p.dialog.emit('click',{target:{closest:()=>({})},clientX:10,clientY:10});
  assert.equal(p.dialog.open,false);assert.notEqual(p.document.activeElement,p.opener,'Following a passage does not force focus back onto the opener');

  let finish;
  p=fixture(()=>new Promise(resolve=>{finish=resolve;}));
  p.open();p.close.emit('click');finish(response(index));await flush();
  assert.equal(p.results.children.length,0,'A late request cannot reopen or fill closed help');
  assert.equal(p.dialog.open,false);

  p=fixture(()=>new Promise(resolve=>{finish=resolve;}));
  p.open();p.submit('not-present');finish(response(index));await flush();
  assert.equal(p.results.children.length,0,'An older search cannot replace a newer query');
  assert.match(p.status.textContent,/No matching/);

  let fail=true;
  p=fixture(()=>fail ? {ok:false} : response(index));
  p.open();await flush();assert.match(p.status.textContent,/retry/);
  fail=false;p.submit('x');await flush();assert.equal(p.requests(),2);assert.equal(p.results.children.length,1);

  p=fixture(()=>response({...index,works:[{id:'paper-ii'}]}));
  p.open();await flush();assert.equal(p.results.children.length,0);assert.match(p.status.textContent,/could not load/);
  p=fixture(()=>response({...index,contexts:[{...index.contexts[0],work:'paper-ii'}]}));
  p.open();await flush();assert.equal(p.results.children.length,0,'Meanings from another work are rejected');
  const named={...index,contexts:[
    {...index.contexts[0],table:{label:'Packet pure seed rank',tex:'r',meaning:'A restricted count.'}},
    {...index.contexts[0],table:{label:'Seed rank',tex:'s',meaning:'The generator count.'}}],
    entries:[{...index.entries[0],tex:'r',names:['r'],context:0},
      {...index.entries[0],tex:'s',names:['s'],context:1}]};
  p=fixture(()=>response(named));p.open();await flush();p.submit('seed rank');await flush();
  assert.equal(p.results.children[0].children[0].textContent,'Seed rank','A matching notation-table name comes before a broader contextual match');
  const title='Witness for seed rank <script>literal</script>';
  const definition={...index,contexts:[{...index.contexts[0],title}],
    entries:[{...index.entries[0]}, {...index.entries[0],tex:'y',aliases:'y',names:['y'],url:'notation/paper-i.html#symbol-y'}]};
  p=fixture(()=>response(definition));p.open();await flush();p.submit('witness for seed rank');await flush();
  const namedRow=p.results.children[0];
  assert.equal(namedRow.children[0].textContent,title,'A word search names the source definition using inert text');
  assert.equal(namedRow.children[1].textContent,'Definition passage');
  assert.equal(namedRow.children[2].textContent,index.contexts[0].excerpt);
  assert.equal(namedRow.children[3].children.length,1,'The main action opens the definition, not an incidental symbol');
  assert.equal(namedRow.children[4].tagName,'DETAILS');
  assert.equal(namedRow.children[4].children[0].textContent,'2 matching symbol spellings');
  assert.equal(namedRow.children[4].children[1].children.length,2,'All matching symbol entries remain available');
  p.submit('x');await flush();
  const symbolRow=p.results.children[0];
  assert.equal(symbolRow.children[0].textContent,'Definition passage');
  assert.equal(symbolRow.children[1].children[0].textContent,'x','A symbol query keeps the matching symbol visible');
  assert.equal(symbolRow.children[2].textContent,'From the definition “'+title+'”.');
  console.log('PASS: on-demand work-local lookup, inert excerpts, passage URLs, focus return, stale requests and retry');
})().catch(error=>{console.error(error);process.exitCode=1;});
