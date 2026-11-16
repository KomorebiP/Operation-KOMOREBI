import test from 'node:test';
import assert from 'node:assert/strict';
import {sequenceTransfer,transferAnchor,transferMatrix,transferCSV,transferLink} from '../website/assets/sequence-transfer-core.mjs';
import {searchEntries} from '../website/assets/sequence-atlas-search.mjs';
const entry=(id,terms,offset=0)=>({id,terms:terms.map(String),offset,index_symbol:'n'});
test('Euler to shifted Fibonacci preserves source values and exact inverse',()=>{
  const map=sequenceTransfer(entry('E',[1,-1,5,-61,1385,-50521]),entry('F',[0,1,1,2,3,5,8]),6);
  assert.equal(map.verified,true);assert.equal(map.targetAnchor.index,1);assert.equal(map.positionShift,1);
  assert.deepEqual(map.rows.map(x=>x.kernel),['1','2','-1','53','-1200','46233']);
  assert.deepEqual(map.rows.map(x=>x.inverse),['1','-2','5','-65','1441','-51845']);
  assert.deepEqual(transferMatrix(map,false,3),[['1','0','0'],['2','1','0'],['-1','2','1']]);
});
test('nonunit and negative anchors retain rational coefficients and both index conventions',()=>{
  const map=sequenceTransfer(entry('A',[0,0,-2,3,7],-4),entry('B',[0,3,-2,1],10),3);
  assert.equal(map.indexShift,13);assert.equal(map.positionShift,-1);assert.equal(map.rows[0].kernel,'-3/2');assert.equal(map.rows[0].inverse,'-2/3');
  assert.equal(map.integerKernel,false);assert.equal(map.integerInverse,false);assert.equal(map.verified,true);
  const csv=transferCSV(map);assert.match(csv,/source_zero_prefix/);assert.match(csv,/original_index_shift/);assert.match(csv,/"Q"/);assert.match(csv,/"-3\/2"/);
  const url=new URL(transferLink('https://example.test/library?q=old#search',map));assert.equal(url.searchParams.get('tr-source'),'A');assert.equal(url.searchParams.get('tr-count'),'3');assert.equal(url.hash,'#transfers');assert.equal(url.searchParams.has('q'),false);
});
test('identity, reversed transfer and late zero seeds preserve exact tails',()=>{
  const a=entry('A',[0,0,0,1,2,4]),b=entry('B',[2,3,9]);
  const id=sequenceTransfer(a,a,3);assert.deepEqual(id.rows.map(x=>x.kernel),['1','0','0']);
  const ab=sequenceTransfer(a,b,3),ba=sequenceTransfer(b,a,3);assert.deepEqual(ab.rows.map(x=>x.inverse),ba.rows.map(x=>x.kernel));assert.equal(ba.positionShift,3);
});
test('zero windows, tables, malformed values and unavailable lengths are rejected',()=>{
  assert.throws(()=>transferAnchor(entry('Z',[0,0])),/no stored nonzero anchor/);
  assert.throws(()=>transferAnchor({...entry('T',[1]),triangle:{}}),/scalar column/);
  assert.throws(()=>transferAnchor(entry('KOM084',[1])),/scalar column/);
  assert.throws(()=>transferAnchor(entry('J',[1],0.5)),/integer index/);
  assert.throws(()=>transferAnchor({...entry('D',[1]),terms:['1.5']}),/exact integer/);
  const a=entry('A',[1,2]);for(const count of ['',0,3,1.5,'NaN'])assert.throws(()=>sequenceTransfer(a,a,count),/Choose 1/);
});
test('recurrence order and parent search retain polynomial k semantics',()=>{
  const a={...entry('KFOR-LR-03-02-02',[1,4]),title:'Weighted k-step',formula:'ordinary',recurrence:'',tags:[],status:'Derived',kind:'k-step',recurrence_order:3,power:2,weight:2,parent:'KSEQ-000025'};
  assert.equal(searchEntries([a],'order:03 r:02 weight:02 parent:KSEQ-25').length,1);
  assert.equal(searchEntries([a],'k:3').length,0);assert.equal(searchEntries([a],'order:30').length,0);
});
