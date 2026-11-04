const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {test}=require('node:test');
const source=fs.readFileSync(path.join(__dirname,'../website/assets/reader.js'),'utf8');
const helpers=source.slice(source.indexOf('function normalized('),source.indexOf('function filterItems('));
const search=source.slice(source.indexOf('const form = document.querySelector("#site-search")'),source.indexOf('\nfor (const pre'));
const flush=async()=>{for(let i=0;i<8;i++)await new Promise(setImmediate);};

function setup(query='',options={}){
  let focused=null;
  class Element{
    constructor(tag='div'){this.tag=tag;this.children=[];this.attrs={};this.events={};this.value='';this.hidden=false;this.dataset={};this.isConnected=true;this._text='';}
    addEventListener(name,callback){this.events[name]=callback;}
    append(...nodes){this.children.push(...nodes.map(n=>typeof n==='string'?{textContent:n}:n));}
    replaceChildren(...nodes){this.children=[];this._text='';this.append(...nodes);}
    set textContent(value){this._text=String(value);this.children=[];}
    get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}
    setAttribute(k,v){this.attrs[k]=v;}
    removeAttribute(k){delete this.attrs[k];}
    focus(){focused=this;}
    scrollIntoView(){}
    get options(){return this.children;}
    querySelector(selector){return this.selectors[selector];}
  }
  const names=['search-query','search-group','search-kind','search-work','search-discipline','search-stage','search-lean','search-evidence','search-status','search-results','search-size','search-extra-options'];
  const elements=Object.fromEntries(names.map(n=>['#'+n,new Element()]));
  const form=new Element('form');elements['#site-search']=form;
  form.dataset={index:'search-index.json?v=test',facets:'work-facets.json?v=test'};
  const size=elements['#search-size'];size.value='40';size.children=['10','20','40','80'].map(value=>({value}));
  const summary=new Element('summary');elements['#search-extra-options'].selectors={summary};
  const pagers=[0,1].map(()=>{
    const pager=new Element();pager.selectors={'.search-page-status':new Element(),'.search-page-select':new Element('select'),
      '[data-search-page="previous"]':new Element('button'),'[data-search-page="next"]':new Element('button')};
    pager.selectors['[data-search-page="previous"]'].dataset.searchPage='previous';
    pager.selectors['[data-search-page="next"]'].dataset.searchPage='next';return pager;
  });
  const location=new URL('https://example.test/Operation-KOMOREBI/search.html'+query);
  const pushes=[];const history={replaceState(a,b,url){location.href=String(url);},pushState(a,b,url){pushes.push(String(url));location.href=String(url);}};
  const document={querySelector:s=>elements[s],querySelectorAll:s=>s==='.search-pagination'?pagers:
    s==='[data-search-page]'?pagers.flatMap(p=>[p.selectors['[data-search-page="previous"]'],p.selectors['[data-search-page="next"]']]):
    s==='.search-page-select'?pagers.map(p=>p.selectors['.search-page-select']):[],
    createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})};
  const rows=options.rows||Array.from({length:85},(_,id)=>({id,title:id===0?'Euler':id<80?'Euler source '+String(id).padStart(2,'0'):'Haar source '+id,
    group:id%2?'Collection':'Komorebi Math',kind:id===0?'Claims':'Guides',work_ids:[id%2?'a':'b'],
    url:'result-'+id+'.html#statement',text:id<80?'Euler full text seed generation':'Haar wavelet body',preview:'Preview '+id}));
  const requests={load:0,match:[],details:[],facets:0,pending:[]};
  const events={};
  const window={addEventListener:(n,fn)=>{events[n]=fn;}};
  const context=vm.createContext({document,window,location,history,URL,URLSearchParams,setTimeout:fn=>fn()});
  vm.runInContext(helpers,context);
  window.KomorebiSearch={Client:class{
    async load(){requests.load++;if(options.failLoad&&requests.load===1)throw Error('offline');return rows.map(({text,preview,preview_parts,math_preview,...meta})=>meta);}
    async match(words){requests.match.push(words);return words.length?new Set(rows.filter(r=>words.every(w=>context.normalized(r.title+' '+r.text).includes(w))).map(r=>r.id)):null;}
    async details(batch){
      requests.details.push(batch.map(r=>r.id));
      if(options.manual)return new Promise((resolve,reject)=>requests.pending.push({resolve:()=>resolve(batch.map(r=>({...r,...rows.find(x=>x.id===r.id)}))),reject}));
      if(options.failPreview&&requests.details.length===2)throw Error('offline preview');
      return batch.map(r=>({...r,...rows.find(x=>x.id===r.id)}));
    }
  }};
  context.fetch=async()=>{requests.facets++;return {ok:true,json:async()=>({works:{
    a:{discipline:'algebra',stage:'development',lean:'none',evidence:'author'},
    b:{discipline:'analysis',stage:'scoped_release',lean:'contract',evidence:'formal'}
  }})};};
  vm.runInContext(search,context);
  return {elements,form,requests,rows,location,events,pagers,pushes,summary,
    status:()=>elements['#search-status'].textContent,
    titles:()=>elements['#search-results'].children.map(li=>li.children[0].textContent),
    submit(value){elements['#search-query'].value=value;return form.events.submit({preventDefault(){}});},
    change(name,value){const e=elements['#search-'+name];e.value=value;return e.events.change();},
    next(){return pagers[0].selectors['[data-search-page="next"]'].events.click();},
    reset(){for(const n of names)if(n!=='search-size')elements['#'+n].value='';size.value='40';form.events.reset();},
    focused:()=>focused};
}

test('empty page is idle; ranking, literal previews, and pagination remain usable',async()=>{
  const p=setup();assert.equal(p.requests.load,0);assert.equal(p.requests.details.length,0);
  await p.submit('Euler');
  assert.equal(p.titles().length,40);assert.equal(p.titles()[0],'Euler');
  assert.match(p.status(),/80 results\. Showing 1–40/);
  assert.equal(p.requests.details[0].length,40);
  assert.equal(p.requests.facets,0);
  assert.equal(new URL(p.location).searchParams.get('q'),'Euler');
  p.next();await flush();
  assert.match(p.status(),/Showing 41–80/);assert.equal(p.requests.details[1].length,40);
  assert.equal(new URL(p.location).searchParams.get('page'),'2');
  assert.equal(p.pushes.length,1);
});

test('work, repository, kind, visual-guide and combined work facets keep their meaning',async()=>{
  const rows=[
    {id:0,title:'Both',url:'both.html',group:'Collection',kind:'Guides',work_ids:['a','b'],visual_guide:true,text:'target',preview:'both'},
    {id:1,title:'A only',url:'a.html',group:'Collection',kind:'Claims',work_ids:['a'],text:'target',preview:'a'},
    {id:2,title:'B code',url:'b.html',group:'Komorebi Math',kind:'Code',work_ids:['b'],text:'target',preview:'b'}
  ];
  const p=setup('',{rows});await p.submit('target');
  await p.change('kind','Visual guides');assert.deepEqual(p.titles(),['Both']);
  await p.change('kind','');await p.change('work','b');assert.deepEqual(p.titles(),['B code','Both']);
  await p.change('group','Collection');assert.deepEqual(p.titles(),['Both']);
  await p.change('discipline','algebra');await p.change('stage','scoped_release');
  assert.equal(p.titles().length,0,'Two different associated works cannot supply two halves of one facet match');
  await p.change('stage','development');assert.deepEqual(p.titles(),['Both']);
});

test('deep-linked pages and Back restore work, size, and page selection',async()=>{
  const p=setup('?q=Euler&per_page=10&page=3');await flush();
  assert.match(p.status(),/Showing 21–30/);assert.equal(p.titles().length,10);
  p.location.search='?q=Haar&per_page=20';p.events.popstate();await flush();
  assert.match(p.status(),/5 results/);assert.ok(p.titles().every(t=>t.startsWith('Haar')));
  p.reset();await flush();assert.equal(p.location.search,'');assert.equal(p.titles().length,0);
  assert.equal(p.focused(),p.elements['#search-query']);
});

test('late result previews cannot overwrite a reset or newer query',async()=>{
  const p=setup('',{manual:true});const old=p.submit('Euler');await flush();
  assert.equal(p.requests.pending.length,1);
  p.reset();p.requests.pending[0].resolve();await old;
  assert.equal(p.titles().length,0);assert.match(p.status(),/Enter a term/);
  const a=p.submit('Euler');await flush();const b=p.submit('Haar');await flush();
  p.requests.pending[2].resolve();await b;
  assert.ok(p.titles().every(t=>t.startsWith('Haar')));
  p.requests.pending[1].reject(Error('late old request'));await a;
  assert.ok(p.titles().every(t=>t.startsWith('Haar')));assert.doesNotMatch(p.status(),/could not/);
});

test('failed initial data and failed page previews can be retried',async()=>{
  let p=setup('',{failLoad:true});await p.submit('Euler');assert.match(p.status(),/could not load/);
  await p.submit('Euler');assert.equal(p.titles().length,40);assert.equal(p.requests.load,2);
  p=setup('',{failPreview:true});await p.submit('Euler');const first=p.titles();p.next();await flush();
  assert.match(p.status(),/Results could not load/);assert.deepEqual(p.titles(),first);
  assert.equal(new URL(p.location).searchParams.get('page'),null);
  p.next();await flush();assert.match(p.status(),/Showing 41–80/);
});

test('authored math previews render as text nodes and source URLs keep their anchors',async()=>{
  const rows=[{id:0,title:'<img> Euler',url:'proof.html#lemma',group:'Collection',kind:'Written proofs',work_ids:['a'],
    text:'Euler',preview:'<img> literal',preview_parts:[{type:'text',text:'<script>alert(1)</script>'},{type:'math',text:'E_8=1385'}],math_preview:'<svg> exact'}];
  const p=setup('',{rows});await p.submit('Euler');
  const li=p.elements['#search-results'].children[0];
  assert.equal(li.children[0].children[0].href,'proof.html#lemma');
  assert.ok(li.textContent.includes('<script>alert(1)</script>'));
  const tags=[];const visit=n=>{if(n.tag)tags.push(n.tag);for(const c of n.children||[])visit(c);};visit(li);
  assert.ok(!tags.includes('script')&&!tags.includes('img')&&!tags.includes('svg'));
  assert.ok(tags.includes('mark'));assert.ok(li.textContent.includes('E_8=1385'));
});
