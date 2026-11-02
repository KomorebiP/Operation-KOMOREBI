const assert = require('node:assert/strict');
const {test} = require('node:test');
const {search,readFilters,filterUrl} = require('../website/assets/statement-search.js');
const entries = [
  {id:'a',kind:'theorem',name:'Theorem',number:'1.2',text:'Theorem 1.2: Finite support',labels:'thm:finite-support',hasProof:true},
  {id:'b',kind:'theorem',name:'Theorem',number:'1.20',text:'Theorem 1.20: Infinite support',labels:'thm:infinite',hasProof:true},
  {id:'c',kind:'definition',name:'Definition',number:'1.2',text:'Definition 1.2: Theorem 1.2 notation',labels:'def:rho',hasProof:false},
  {id:'d',kind:'lemma',name:'Lemma',number:'II.3.1',text:'Lemma II.3.1: Étale ρ packets',labels:'lem:packets',hasProof:true},
  {id:'e',kind:'conjecture',name:'Conjecture',number:'66',text:'Conjecture 66: Global realization',labels:'conj:global',hasProof:false},
  {id:'f',kind:'histtheorem',name:'Historical theorem',number:'A.2',text:'Historical theorem A.2: Old checkpoint',labels:'hist:old',hasProof:false}
];
const ids = (query,proofOnly=false) => search(entries,query,proofOnly).map(entry=>entry.id);
test('printed numbers match exactly and type prefixes disambiguate repeated numbers',()=>{
  assert.deepEqual(ids('1.2'),['a','c']);
  assert.deepEqual(ids('Theorem 1.2'),['a']);
  assert.deepEqual(ids('thm1.2'),['a']);
  assert.deepEqual(ids('Thm. 1.2'),['a']);
  assert.deepEqual(ids('Definition 1.2'),['c']);
  assert.deepEqual(ids('II. 3.1'),['d']);
  assert.deepEqual(ids('Historical theorem A.2'),['f']);
});
test('shared display names, appendix numbering and short Greek names stay precise',()=>{
  const records=[
    {kind:'certificate',name:'Numerical certificate',number:'II.A.1',text:'Numerical certificate II.A.1',labels:'',hasProof:false},
    {kind:'numericalcertificate',name:'Numerical certificate',number:'II.A.10',text:'Numerical certificate II.A.10',labels:'',hasProof:false},
    {kind:'lemma',name:'Lemma',number:'3',text:'Lemma 3: The ν fiber',labels:'',hasProof:true}
  ];
  assert.equal(search(records,'Numerical certificate').length,2);
  assert.equal(search(records,'II.A.1').length,1);
  assert.equal(search(records,'Numerical certificate II.A.1')[0].kind,'certificate');
  assert.equal(search(records,'nu')[0].kind,'lemma');
  assert.equal(search(records,'ν').length,1);
});
test('extended-section numbers retain exact type and number matching',()=>{
  const records=[
    {kind:'theorem',name:'Theorem',number:'E5.1',text:'Theorem E5.1: Stable banks',labels:''},
    {kind:'theorem',name:'Theorem',number:'E5.10',text:'Theorem E5.10: Another bank',labels:''},
    {kind:'definition',name:'Definition',number:'E5.1',text:'Definition E5.1: Theorem E5.1 notation',labels:''}
  ];
  assert.equal(search(records,'Theorem E5.1').length,1);
  assert.equal(search(records,'E5.1').length,2);
  assert.equal(search(records,'Thm. E5.1')[0].kind,'theorem');
});
test('title, type, source labels, accents and Greek names are searchable',()=>{
  assert.deepEqual(ids('finite support'),['a']);
  assert.deepEqual(ids('infinite support'),['b']);
  assert.deepEqual(ids('support'),['a','b']);
  assert.deepEqual(ids('thm'),['a','b']);
  assert.deepEqual(ids('definition'),['c']);
  assert.deepEqual(ids('Historical theorem'),['f']);
  assert.deepEqual(ids('thm:finite-support'),['a']);
  assert.deepEqual(ids('etale rho'),['d']);
  assert.deepEqual(ids('ρ packets'),['d']);
  assert.deepEqual(ids('conjecture'),['e']);
  assert.deepEqual(ids('nothing matches'),[]);
});
test('proof filter follows recorded links and preserves source order without mutation',()=>{
  const original = JSON.stringify(entries);
  assert.deepEqual(ids('',true),['a','b','d']);
  assert.deepEqual(ids('66',true),[]);
  assert.deepEqual(ids('',false),['a','b','c','d','e','f']);
  assert.equal(JSON.stringify(entries),original);
});

test('paper finder URLs restore encoded queries and the explicit proof filter',()=>{
  assert.deepEqual(readFilters('?q=Theorem+II.2.2&proof=1'),{query:'Theorem II.2.2',proofOnly:true});
  assert.deepEqual(readFilters('?q=conj%3Aarithmetic_realization&proof=no'),{query:'conj:arithmetic_realization',proofOnly:false});
  assert.deepEqual(readFilters(''),{query:'',proofOnly:false});
});

test('updating paper finder URLs preserves other parameters and anchors',()=>{
  const href='https://example.test/read/paper-v/statements.html?lang=en&q=old&proof=1#main';
  const updated=new URL(filterUrl(href,' Theorem E5.1 ',false));
  assert.equal(updated.searchParams.get('q'),'Theorem E5.1');
  assert.equal(updated.searchParams.has('proof'),false);
  assert.equal(updated.searchParams.get('lang'),'en');
  assert.equal(updated.hash,'#main');
  const cleared=new URL(filterUrl(updated.href,' ',true));
  assert.equal(cleared.searchParams.has('q'),false);
  assert.equal(cleared.searchParams.get('proof'),'1');
});
