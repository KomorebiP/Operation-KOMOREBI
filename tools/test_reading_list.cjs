const {test} = require('node:test');
const assert = require('node:assert/strict');
const api = require('../website/assets/reading-list.js');
const base = 'https://example.test/project/';
const entry = {url:'read/paper-i/chapter.html#lemma', title:'Chapter one', section:'A lemma', work:'Paper I'};

test('only reading destinations inside the current site can be saved', () => {
  assert.equal(api.target(base+entry.url, base), entry.url);
  assert.equal(api.target('read/page.html#résumé:one', base), 'read/page.html#r%C3%A9sum%C3%A9%3Aone');
  assert.equal(api.target('read/page.html#r%C3%A9sum%C3%A9%3Aone', base), 'read/page.html#r%C3%A9sum%C3%A9%3Aone');
  assert.notEqual(api.storageKey(base), api.storageKey('https://example.test/another-project/'));
  assert.equal(api.target('signal-lab.html?signal=1%2C2#result', base), 'signal-lab.html?signal=1%2C2#result');
  for (const value of ['javascript:alert(1)', '//other.test/a.html', '../outside.html',
    '/project-other/a.html', 'assets/example.html', 'documents/files/example.html',
    'read/%2e%2e/%2e%2e/outside.html', 'read/a%5cb.html', 'read/%2e%2e%2foutside.html',
    'https://name:secret@example.test/project/a.html', 'read/source.py', 'x'.repeat(4097)]) {
    assert.equal(api.target(value, base), null, value);
  }
});

test('stored data is bounded, validated and deduplicated', () => {
  const data = JSON.stringify({schema:1,items:[entry, entry, null, {url:'//other.test/a.html',title:'Outside'},
    {url:'read/two.html',title:'',section:'Missing title'}, {url:'read/three.html',title:'Valid',section:42}]});
  assert.deepEqual(api.parse(data, base), [entry, {url:'read/three.html',title:'Valid',section:'',work:''}]);
  for (const raw of ['', '{', 'null', '{}', JSON.stringify({schema:2,items:[entry]}), 'x'.repeat(1000001)])
    assert.deepEqual(api.parse(raw, base), []);
  const full = Array.from({length:api.LIMIT+10}, (_,i) => ({...entry,url:`read/${i}.html`}));
  assert.equal(api.parse(JSON.stringify({schema:1,items:full}), base).length, api.LIMIT);
});

test('adding and removing preserves other places and never evicts them silently', () => {
  const other = {...entry,url:'read/other.html'};
  assert.deepEqual(api.edit([other], entry), [entry, other]);
  assert.deepEqual(api.edit([entry, other], entry), [other]);
  const full = Array.from({length:api.LIMIT}, (_,i) => ({...entry,url:`read/${i}.html`}));
  assert.throws(() => api.edit(full, entry), /full/);
  assert.equal(api.edit(full, full[0]).length, api.LIMIT-1);
});

function memory(initial = null) {
  return {value:initial,getItem(){return this.value;},setItem(key,value){if(this.blocked)throw Error('Blocked');this.value=value;}};
}

function fixture({storage=memory(), listing=false, hash=''} = {}) {
  const document = {activeElement:null,addEventListener(){}};
  class Element {
    constructor(tag='div') { this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attrs={};this.events={};this.value='';this.textContent='';this.hidden=true; }
    append(...children) {this.children.push(...children);}
    replaceChildren(...children) {this.children=children;}
    setAttribute(key,value) {this.attrs[key]=value;}
    getAttribute(key) {return this.attrs[key];}
    addEventListener(name,callback) {this.events[name]=callback;}
    click() {this.events.click?.({target:this});}
    focus() {document.activeElement=this;}
    matches(selector) {return selector.split(',').some(s=>s[0]==='.' ? this.className===s.slice(1) : this.tagName===s.toUpperCase());}
    querySelectorAll(selector) {return this.children.flatMap(c=>[...(c.matches(selector)?[c]:[]),...c.querySelectorAll(selector)]);}
    querySelector(selector) {if(selector==='[data-save-page]')return this.pageButton;if(selector==='[data-saved-reading-link]')return this.savedLink;return this.querySelectorAll(selector)[0]||null;}
  }
  const bar = new Element(), list = new Element(), button = new Element('button'), label = new Element('span');
  bar.dataset.pageTitle='Chapter one';button.append(label);bar.pageButton=button;
  const link = new Element('a'), status = new Element('span');status.className='reading-save-status';
  bar.savedLink=link;bar.append(button,link,status);
  const input=new Element('input'),count=new Element('p'),output=new Element('ol'),empty=new Element(),listStatus=new Element('p');
  count.className='saved-reading-count';empty.className='reading-list-empty';listStatus.className='reading-list-status';
  list.append(input,count,output,empty,listStatus);
  const heading = new Element('h2');heading.id='lemma';heading.textContent='A lemma';
  const brand={href:base+'index.html'},work={textContent:'Paper I'};
  document.querySelector=s=>({'[data-reading-save]':listing?null:bar,'[data-reading-list]':listing?list:null,'.brand':brand,'.reading-position a':work}[s]||null);
  document.querySelectorAll=()=>listing?[]:[heading];
  document.getElementById=id=>id==='lemma'?heading:null;
  document.createElement=tag=>new Element(tag);
  const events={},window={document,localStorage:storage,setTimeout,location:new URL(base+'read/paper-i/chapter.html'+hash),addEventListener(name,callback){events[name]=callback;}};
  api.start(window);
  return {bar,list,button,label,status,listStatus,heading,input,output,empty,count,document,storage,events,window};
}

test('page and passage saves persist and update pressed states across tabs', () => {
  const p=fixture();
  p.button.click();
  assert.equal(p.button.attrs['aria-pressed'],'true');
  assert.equal(api.parse(p.storage.value,base)[0].url,'read/paper-i/chapter.html');
  p.heading.children[0].click();
  assert.deepEqual(api.parse(p.storage.value,base)[0],entry);
  const restored=fixture({storage:p.storage,hash:'#lemma'});
  assert.equal(restored.button.attrs['aria-pressed'],'true');
  p.storage.value=null;restored.events.storage({key:api.storageKey(base)});
  assert.equal(restored.button.attrs['aria-pressed'],'false');
  assert.equal(restored.label.textContent,'Save passage');
});

test('blocked storage reports failure without pretending the place is saved', () => {
  const p=fixture();p.storage.blocked=true;p.button.click();
  assert.equal(p.button.attrs['aria-pressed'],'false');
  assert.match(p.status.textContent,/storage is unavailable/);
  assert.equal(p.storage.value,null);
});

test('search, removal, empty state and focus work without recreating an externally removed save', () => {
  const storage=memory(JSON.stringify({schema:1,items:[entry,{...entry,url:'read/other.html',section:'Another section'}]}));
  const p=fixture({storage,listing:true});
  assert.equal(p.output.children.length,2);assert.equal(p.empty.hidden,true);
  p.input.value='lemma';p.input.events.input();assert.equal(p.output.children.length,1);
  p.input.value='';p.input.events.input();
  storage.value=JSON.stringify({schema:1,items:[{...entry,url:'read/other.html',section:'Another section'}]});
  p.output.querySelectorAll('button')[0].click();
  assert.equal(api.parse(storage.value,base).length,1);
  assert.equal(p.document.activeElement,p.output.querySelectorAll('button')[0]);
  p.output.querySelectorAll('button')[0].click();
  assert.equal(p.empty.hidden,false);assert.equal(p.document.activeElement,p.input);
});
