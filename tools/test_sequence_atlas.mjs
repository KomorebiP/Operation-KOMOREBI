import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {generate,mod,parseTerms,transform,exact,coordinate,rowsFor,candidatePeriod,findMatches} from '../website/assets/sequence-atlas-core.mjs';

const root=fileURLToPath(new URL('..',import.meta.url));
const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','tools/sequence_atlas.py'],{cwd:root,encoding:'utf8',maxBuffer:10*1024*1024}));
test('every browser generator matches independent Python terms, including large integers',()=>{
  for(const entry of entries)assert.deepEqual(generate(entry,64).map(String),entry.terms,entry.id);
  assert.ok(entries.some(e=>e.terms.some(v=>v.length>100)));
});
test('negative and very large residues stay exact',()=>{
  assert.equal(mod(-1n,7),6n);assert.equal(mod(9007199254740993n,7),5n);
  assert.equal(mod(BigInt('9'.repeat(200)),11),0n);
  assert.deepEqual(parseTerms(' +01, -2; 0\n9999999999999999999999'),[1n,-2n,0n,9999999999999999999999n]);
  assert.throws(()=>parseTerms('1, 2.3'));assert.throws(()=>parseTerms('1e10'));
});
test('transforms preserve exact fractions, undefined values, and full prefix sums',()=>{
  const values=[0n,2n,5n,-1n];
  assert.deepEqual(transform(values,'difference').map(exact),['undefined','2','3','-6']);
  assert.deepEqual(transform(values,'sum').map(exact),['0','2','7','6']);
  assert.deepEqual(transform(values,'ratio').map(exact),['undefined','undefined','5/2','-1/5']);
  assert.deepEqual(transform(values,'average').map(exact),['0','1','7/3','3/2']);
  const state={start:2,count:2,transform:'sum',view:'mod',scale:'linear',modulus:5};
  assert.deepEqual(rowsFor(values,state,'test').map(r=>[r.n,r.value,r.residue]),[[2,'7',2],[3,'6',1]]);
  assert.throws(()=>rowsFor(values,{...state,transform:'average'},'test'));
});
test('second differences agree with the polynomial identity at every tested index',()=>{
  const squares=Array.from({length:64},(_,n)=>BigInt(n)**2n);
  assert.deepEqual(transform(squares,'second-difference').map(exact),['undefined','undefined',...Array(62).fill('2')]);
  assert.deepEqual(transform([5n,-2n,7n,1n],'second-difference').map(exact),['undefined','undefined','16','-15']);
});
test('successive modular coordinates use exact residues before floating conversion',()=>{
  const values=[-1n,9007199254740993n,3n];
  const state={start:0,count:3,transform:'raw',view:'mod-pairs',scale:'log',modulus:7};
  assert.deepEqual(rowsFor(values,state,'fixture').map(row=>[row.x,row.y]),[[6,5],[5,3],[3,null]]);
  assert.throws(()=>rowsFor([2n,3n,7n],{...state,transform:'average'},'fixture'));
});
test('plot boundary handles large exact ratios and log domains',()=>{
  assert.equal(coordinate({a:10n**400n,b:10n**399n},'linear'),10);
  assert.equal(coordinate({a:-2n,b:1n},'log'),null);
  assert.equal(coordinate({a:10n**400n,b:1n},'linear'),null);
  assert.equal(coordinate({a:10n**400n,b:1n},'log'),400);
});
test('search is contiguous, exact, bounded to catalogue, and supports source identifiers',()=>{
  assert.ok(findMatches(entries,'1,1,69').some(e=>e.N===4&&e.power===1));
  assert.ok(!findMatches(entries,'1,69,1').some(e=>e.N===4&&e.power===1));
  assert.equal(findMatches(entries,'A000364')[0].id,'KSEQ-000001');
  assert.equal(findMatches(entries,'Fubini').length,1);
});
test('period suggestions require three repetitions and reject null values',()=>{
  assert.equal(candidatePeriod([0,1,0,1,0,1]),2);
  assert.equal(candidatePeriod([0,1,0,1]),null);
  assert.equal(candidatePeriod([0,1,null,0,1,null]),null);
});
