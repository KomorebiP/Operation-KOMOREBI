const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const {execFileSync} = require('node:child_process');
const {test, after} = require('node:test');
const {Client, decodeIds} = require('../website/assets/search-engine.js');
const root = path.resolve(__dirname, '..');
const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'komorebi-search-'));
const python = process.env.KOMOREBI_TEST_PYTHON || 'python';
const script = `import sys,json\nfrom pathlib import Path\nsys.path.insert(0,'tools')\nfrom test_search_catalog import build_fixture,fixture_rows\nfrom search_catalog import normalized\nbuild_fixture(sys.argv[1])\nPath(sys.argv[1],'original.json').write_text(json.dumps(fixture_rows()),encoding='utf8')\ncases=['Résumé α','café βeta','Γ gamma','ℓ ρ ω η δ','İstanbul Straße 𝔸','a_b-def Ⅻ ²','École ΣΟΣ']\nPath(sys.argv[1],'normalization.json').write_text(json.dumps([[s,normalized(s)] for s in cases]),encoding='utf8')`;
execFileSync(python, ['-X','utf8','-c',script,fixture], {cwd:root});
after(()=>{
  const resolved=fs.realpathSync(fixture);
  assert.equal(path.dirname(resolved),fs.realpathSync(os.tmpdir()));
  assert.match(path.basename(resolved),/^komorebi-search-/);
  fs.rmSync(resolved,{recursive:true,force:true});
});
const original = JSON.parse(fs.readFileSync(path.join(fixture,'original.json')));
const reader = fs.readFileSync(path.join(root,'website/assets/reader.js'),'utf8');
const context = vm.createContext({});
vm.runInContext(reader.slice(reader.indexOf('function normalized('),reader.indexOf('function highlightedText(')),context);
const normalize = value=>context.normalized(value);

function client(options={}) {
  const calls=[];
  let active=0,maxActive=0;
  const fetch=async url=>{
    const relative=new URL(url).pathname.replace('/Operation-KOMOREBI/','');
    calls.push(relative);active++;maxActive=Math.max(maxActive,active);
    await new Promise(setImmediate);
    active--;
    if(options.fail && options.fail(relative,calls))return {ok:false};
    const value=JSON.parse(fs.readFileSync(path.join(fixture,relative),'utf8'));
    return {ok:true,json:async()=>options.transform ? options.transform(relative,value) : value};
  };
  return {engine:new Client('https://example.test/Operation-KOMOREBI/search-index.json?v=fixture',{fetch}),calls,maxActive:()=>maxActive};
}

test('opening the catalogue loads metadata without terms or result bodies',async()=>{
  const {engine,calls}=client();
  assert.equal(calls.length,0);
  const rows=await engine.load();
  assert.equal(calls.length,2);
  assert.ok(calls.every(p=>!p.includes('entries/')&&!p.includes('terms.json')&&!p.includes('postings/')));
  for(let i=0;i<rows.length;i++)for(const key of ['title','url','group','kind','work_ids'])assert.deepEqual(rows[i][key],original[i][key]);
  assert.equal(rows[3].visual_guide,true);
  assert.equal(rows[0].text,undefined);
});

test('the native fetch receiver is preserved in a browser',async()=>{
  const previous=globalThis.fetch;
  try {
    globalThis.fetch=async function(){assert.equal(this,globalThis);return {ok:true,json:async()=>({ready:true})};};
    const engine=new Client('https://example.test/search-index.json');
    assert.deepEqual(await engine.json('metadata.json'),{ready:true});
  } finally {globalThis.fetch=previous;}
});

test('Python indexing and the existing browser query normalizer agree',()=>{
  for(const [input,expected] of JSON.parse(fs.readFileSync(path.join(fixture,'normalization.json'))))assert.equal(normalize(input),expected,input);
});

test('substring AND matching agrees with the previous full-text scan',async()=>{
  const {engine}=client();
  for(const query of ['eed','euler nilpotent','deepneedle','cafe','α','rho','gamma','Γ','refine','empty','missing','phase seed']){
    const words=normalize(query).split(/\s+/).filter(Boolean);
    const expected=original.flatMap((r,i)=>words.every(w=>normalize(r.title+' '+r.text).includes(w))?[i]:[]);
    assert.deepEqual([...await engine.match(words)].sort((a,b)=>a-b),expected,query);
  }
  assert.equal(await engine.match([]),null);
});

test('only requested previews load and rich math/text stays intact',async()=>{
  const {engine,calls}=client();const rows=await engine.load();
  const previews=await engine.details([rows[1],rows[0]]);
  assert.deepEqual(previews[0].preview_parts,original[1].preview_parts);
  assert.equal(previews[0].math_preview,original[1].math_preview);
  assert.equal(previews[1].preview,original[0].preview);
  assert.deepEqual(calls.filter(p=>p.includes('entries/')),['search/fixture/entries/1.json','search/fixture/entries/0.json']);
  await engine.details([rows[1]]);
  assert.equal(calls.filter(p=>p.endsWith('/1.json')).length,1);
});

test('concurrent searches coalesce requests and failed data can be retried',async()=>{
  const {engine,calls,maxActive}=client({fail:(p,all)=>p.endsWith('entries/0.json')&&all.filter(x=>x===p).length===1});
  const [rows]=await Promise.all([engine.load(),engine.match(['eed']),engine.match(['cafe'])]);
  assert.equal(calls.filter(p=>p.startsWith('search-index.json')).length,1);
  assert.equal(calls.filter(p=>p.endsWith('terms.json')).length,1);
  await assert.rejects(engine.details([rows[0]]));
  assert.equal((await engine.details([rows[0]]))[0].preview,original[0].preview);
  assert.ok(maxActive()<=8);
});

test('failed manifest requests retry and corrupt metadata or postings fail clearly',async()=>{
  const f=client({fail:(p,all)=>p.startsWith('search-index.json')&&all.length===1});
  await assert.rejects(f.engine.load());
  assert.equal((await f.engine.load()).length,5);
  const c=client({transform:(p,data)=>{
    if(p.endsWith('metadata.json'))data.rows.pop();
    return data;
  }});
  await assert.rejects(c.engine.load(),/Incomplete/);
  for(const value of ['', '0.0','!','0..1','zzzzzzzzzzzzzzzzzz'])assert.throws(()=>decodeIds(value,5));
});
