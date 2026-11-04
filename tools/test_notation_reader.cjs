const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {test}=require('node:test');
const vm=require('node:vm');
const search=require('../website/assets/notation-search.js');
const source=fs.readFileSync(path.join(__dirname,'../website/assets/notation.js'),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));

function fixture(data,local=false) {
  const document={activeElement:null};
  class Element {
    constructor(tag='div',text='') {
      this.tagName=tag.toUpperCase();this.textContent=text;this.children=[];
      this.events={};this.dataset={};this.className='';this.value='';
      this.hidden=false;this.isConnected=true;this.checked=false;
    }
    append(...children) {this.children.push(...children);}
    replaceChildren(...children) {this.children=children;}
    matches(selector) {
      return selector.startsWith('.') ? this.className.split(/\s+/).includes(selector.slice(1)) : this.tagName===selector.toUpperCase();
    }
    querySelectorAll(selector) {
      return this.children.flatMap(child=>[...(child.matches(selector)?[child]:[]),...child.querySelectorAll(selector)]);
    }
    querySelector(selector) {return this.querySelectorAll(selector)[0] || null;}
    addEventListener(name,callback) {(this.events[name] ||= []).push(callback);}
    async emit(name) {
      await Promise.all((this.events[name] || []).map(callback=>callback({target:this,preventDefault(){}})));
      await flush();
    }
    focus() {document.activeElement=this;}
  }
  const input=new Element('input'),status=new Element('p'),more=new Element('button'),kind=new Element('select');
  const form=new Element('form'),results=new Element('ol'),work=new Element('select'),exact=new Element('input');
  const options=new Element('details');options.append(new Element('summary'));
  const ids={'notation-query':input,'notation-status':status,'notation-more':more,'notation-kind':kind};
  const entries=[];
  if(local) {
    form.dataset={notationWork:data.work,source:'data/sample.json'};
    for(const record of data.entries) {
      const entry=new Element('details'),button=new Element('button'),target=new Element('div');
      entry.id=record.id;entry.className='notation-entry';entry.dataset={kind:'use',search:'x'};
      button.className='notation-occurrences';button.dataset.symbol=record.id;button.hidden=true;
      target.className='notation-all';entry.append(new Element('summary'),button,target);
      entries.push(entry);ids[record.id]=entry;
    }
  } else {
    form.dataset.index='notation/search.json';
    Object.assign(ids,{'notation-search':form,'notation-results':results,'notation-work':work,
      'notation-exact':exact,'notation-options':options});
  }
  document.getElementById=id=>ids[id] || null;
  document.querySelector=selector=>local && selector==='[data-notation-work]' ? form : null;
  document.querySelectorAll=selector=>selector==='.notation-entry' ? entries : [];
  document.createElement=tag=>new Element(tag);
  const requests=[];
  const window={KomorebiNotationSearch:search,addEventListener(){}};
  vm.runInNewContext(source,{document,window,URLSearchParams,
    location:new URL('https://example.test/collection/'+(local?'notation/sample.html':'notation.html')),
    history:{replaceState(){}},setTimeout,clearTimeout,
    fetch:async url=>{requests.push(url);return {ok:true,json:async()=>data};}});
  return {document,input,status,more,form,results,entries,requests,
    async submit(value) {input.value=value;await form.emit('submit');}};
}

function localData(passages,version=2) {
  return {version,work:'sample',contexts:['A retained mathematical context.'],
    sources:[{repository_path:'sample/book/main.tex',url:'read/sample/main-fallback.html',source_url:'read/sample/main-source.html'},
      {repository_path:'sample/book/included.tex',url:'read/sample/included-source.html'}],
    passages,entries:[{id:'symbol-x',occurrences:passages.map((_,i)=>i)}]};
}
const links=element=>element.querySelectorAll('a');

test('packed occurrence data keeps readable and exact source routes across pagination',async()=>{
  const passages=Array.from({length:101},(_,i)=>({source:0,line:11+i,context:0,kind:'use'}));
  passages[0].reading_url='read/sample/chapter.html#L10';
  passages[100]={source:1,line:24,context:0,kind:'use',reading_url:'read/sample/appendix.html#included-L18'};
  const p=fixture(localData(passages),true),entry=p.entries[0];
  const button=entry.querySelector('.notation-occurrences');
  assert.equal(p.requests.length,0,'The occurrence data remains on demand');
  await button.emit('click');
  const target=entry.querySelector('.notation-all'),list=target.querySelector('ol'),next=target.querySelector('button');
  assert.equal(list.children.length,100);
  assert.deepEqual(links(list.children[0]).map(link=>[link.textContent,link.href]),[
    ['Read passage','../read/sample/chapter.html#L10'],
    ['main.tex, line 11','../read/sample/main-source.html#L11']]);
  assert.equal(links(list.children[0])[0].title,'main.tex, line 11');
  assert.equal(p.document.activeElement,links(list.children[0])[0],'Focus starts at the readable destination');
  assert.equal(links(list.children[1])[0].href,'../read/sample/main-source.html#L12');
  assert.equal(links(list.children[99])[0].href,'../read/sample/main-source.html#L110');
  assert.ok(list.children.slice(1).every(row=>links(row).length===1),'An occurrence cannot borrow a different occurrence’s reading route');
  assert.equal(next.hidden,false);
  assert.equal(button.textContent,'101 source passages listed below');
  await next.emit('click');
  assert.equal(list.children.length,101);
  assert.deepEqual(links(list.children[100]).map(link=>[link.textContent,link.href]),[
    ['Read passage','../read/sample/appendix.html#included-L18'],
    ['included.tex, line 24','../read/sample/included-source.html#L24']]);
  assert.equal(p.document.activeElement,links(list.children[100])[0],'More results focus the first new reading destination');
  assert.equal(next.hidden,true);
  assert.deepEqual(p.requests,['data/sample.json'],'Pagination reuses the fetched work data');
});

test('legacy occurrence data without a reading route retains its exact source destination',async()=>{
  const data=localData([{source:1,line:7,context:'A legacy literal context.',kind:'use'}],1);
  delete data.contexts;
  const p=fixture(data,true),entry=p.entries[0],button=entry.querySelector('.notation-occurrences');
  await button.emit('click');
  const target=entry.querySelector('.notation-all'),list=target.querySelector('ol');
  assert.deepEqual(links(list).map(link=>[link.textContent,link.href]),[
    ['included.tex, line 7','../read/sample/included-source.html#L7']]);
  assert.equal(p.document.activeElement,links(list)[0]);
  assert.equal(target.querySelector('button').hidden,true);
  assert.equal(button.textContent,'1 source passage listed below');
});

function globalData() {
  return {version:2,source_revision:'revision',works:[{id:'sample',title:'Sample work'}],
    contexts:[{work:'sample',excerpt:'A retained example.',source_url:'read/sample/main-source.html#L11',
      reading_url:'read/sample/chapter.html#L10',source_label:'main.tex, line 11',
      table:{label:'Spectrum decomposition',tex:'x',display:null,meaning:'The example’s recorded decomposition.'}}],
    entries:[{work:'sample',tex:'x',names:['x'],aliases:'x',display:null,context:0,
      kind:'notation-table',url:'notation/sample.html#symbol-x',count:1}]};
}

test('a named notation-table result offers both reading and source routes',async()=>{
  const p=fixture(globalData());
  await p.submit('Spectrum decomposition');
  assert.equal(p.results.children.length,1);
  const row=p.results.children[0],heading=row.querySelector('h2');
  assert.equal(links(heading)[0].href,'read/sample/chapter.html#L10','The named table heading opens its readable passage');
  assert.deepEqual(links(row.querySelector('.notation-result-actions')).map(link=>[link.textContent,link.href]),[
    ['Read passage','read/sample/chapter.html#L10'],
    ['Read source','read/sample/main-source.html#L11'],
    ['Open entry','notation/sample.html#symbol-x']]);
  assert.equal(links(row.querySelector('.notation-result-actions'))[0].title,'main.tex, line 11');
});

test('global search does not label a source-only destination as a reading passage',async()=>{
  for(const available of [false,true]) {
    const data=globalData(),context=data.contexts[0];
    if(available)context.reading_url=context.source_url;else delete context.reading_url;
    const p=fixture(data);await p.submit('Spectrum decomposition');
    assert.equal(p.results.children.length,1);
    const row=p.results.children[0];
    assert.equal(links(row.querySelector('h2'))[0].href,'read/sample/main-source.html#L11');
    assert.deepEqual(links(row.querySelector('.notation-result-actions')).map(link=>[link.textContent,link.href]),[
      ['Read source','read/sample/main-source.html#L11'],
      ['Open entry','notation/sample.html#symbol-x']]);
  }
});

test('an exact symbol query keeps the entry heading and adds an explicit reading action',async()=>{
  const p=fixture(globalData());await p.submit('x');
  assert.equal(p.results.children.length,1);
  const row=p.results.children[0];
  assert.equal(links(row.querySelector('h2'))[0].href,'notation/sample.html#symbol-x');
  assert.equal(links(row.querySelector('.notation-result-actions'))[0].href,'read/sample/chapter.html#L10');
});
