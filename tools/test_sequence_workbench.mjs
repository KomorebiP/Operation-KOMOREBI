import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {WORKBENCH_DEFAULTS,validateWorkbench,localSource,referenceSource,workbenchRows,agreements,readWorkbenchLink,workbenchLink,comparisonCSV} from '../website/assets/sequence-workbench-core.mjs';
import {readSaved,writeSaved,STORAGE_KEY} from '../website/assets/sequence-atlas-saved.mjs';
import {referenceQuery,referenceValues,referencePositions,referenceNameMatches} from '../website/assets/sequence-oeis-core.mjs';
const entry=(id,offset,terms)=>({id,title:id,offset,terms:terms.map(String),url:'records/'+id+'.html',collection:'atlas'});
const a=entry('KSEQ-000001',2,[0,-1,'9007199254740993',7]),b=entry('KOM085',3,[0,-1,'9007199254740992',7]);
test('windows preserve exact arithmetic and stored prefix transformations',()=>{
  let r=workbenchRows([localSource(a)],{skip:1,count:2,transform:'sum'});assert.deepEqual(r.series[0].rows.map(r=>r.value),['-1','9007199254740992']);assert.deepEqual(r.series[0].rows.map(r=>r.index),[3,4]);
  r=workbenchRows([localSource(a)],{skip:1,count:1,transform:'difference'});assert.equal(r.series[0].rows[0].value,'-1');
  assert.equal(workbenchRows([localSource(a)],{transform:'difference'}).series[0].rows[0].value,null);
  assert.equal(workbenchRows([localSource(a)],{view:'mod',modulus:7}).series[0].rows[1].value,'6');
  assert.equal(workbenchRows([localSource(a)],{skip:50}).series[0].rows.length,0);
});
test('finite agreement joins use exact integers and the selected alignment',()=>{
  let r=workbenchRows([localSource(a),localSource(b)]);let c=agreements(r)[0];assert.equal(c.compared,4);assert.equal(c.equal,3);assert.equal(c.firstMismatch.x,2);
  r=workbenchRows([localSource(a),localSource(b)],{alignment:'indices'});c=agreements(r)[0];assert.equal(c.compared,3);assert.equal(c.equal,0);
  const ref=referenceSource({id:'A000001',sample_position:8,values:['0','-1']},'snapshot');assert.throws(()=>workbenchRows([ref],{alignment:'indices'}),/omit mathematical offsets/);
  assert.equal(workbenchRows([ref],{skip:1}).series[0].rows[0].index,9);
});
test('shared references require explicit restoration against the same snapshot',()=>{
  const ref=referenceSource({id:'A000001',sample_position:8,values:['0','-1'],name:'Test'},'snapshot');
  const href=workbenchLink('https://example.test/sequence-library.html?q=old',[localSource(a),ref],{...WORKBENCH_DEFAULTS,view:'mod',modulus:11});
  const restored=readWorkbenchLink(href,[a,b],'snapshot');assert.equal(restored.state.modulus,11);assert.equal(restored.sources[1].pending,true);assert.equal(restored.sources[1].descriptor.position,8);assert.equal(new URL(href).searchParams.has('q'),false);
  assert.throws(()=>readWorkbenchLink(href,[a,b],'other'),/snapshot/);assert.throws(()=>readWorkbenchLink(href,[b],'snapshot'),/unavailable/);
  assert.throws(()=>readWorkbenchLink(workbenchLink(href,[localSource(a),localSource(a)],{}),[a],'snapshot'),/duplicate/);
  for(const value of [{skip:''},{count:0},{count:1.1},{modulus:1},{scale:'invented'}])assert.throws(()=>validateWorkbench(value));
  for(const values of [['-0'],['01'],[],['1.2']])assert.throws(()=>referenceSource({id:'A000001',sample_position:0,values},'snapshot'));
});
test('comparison CSV retains exact values, source positions and attribution',()=>{
  const ref=referenceSource({id:'A000001',sample_position:8,values:['9007199254740993']},'sha');const csv=comparisonCSV(workbenchRows([ref]));
  for(const text of ['9007199254740993','mathematical offset unknown','"8"','CC-BY-SA-4.0','OEIS Foundation','"sha"'])assert.ok(csv.includes(text),text);
});
test('scoped saves preserve other collections and reject oversized writes',()=>{
  let raw='[]';const storage={getItem:()=>raw,setItem:(key,value)=>{assert.equal(key,STORAGE_KEY);raw=value;}};
  writeSaved(storage,['KFOR-S-catalan-03-01','KOM085','KSEQ-000001']);
  writeSaved(storage,[],new Set(['KSEQ-000001']));assert.deepEqual(readSaved(storage).ids,['KFOR-S-catalan-03-01','KOM085']);
  writeSaved(storage,['KSEQ-000002'],new Set(['KSEQ-000001','KSEQ-000002']));assert.equal(readSaved(storage).ids.length,3);
  const before=raw;assert.equal(writeSaved(storage,Array.from({length:501},(_,i)=>'KFOR-test-'+i)),false);assert.equal(raw,before);
  assert.equal(readSaved({getItem:()=>{throw Error('denied');}}).available,false);
});
test('worker restores selected slices and rejects absent or malformed excerpts',async()=>{
  // Run the actual worker body over bounded exported-line fixtures, without a network request.
  const code=fs.readFileSync(new URL('../website/assets/sequence-oeis-worker.mjs',import.meta.url),'utf8').replace(/^import .*;\r?\n/,'').replaceAll('import.meta.url',"'https://example.test/assets/sequence-oeis-worker.mjs'");
  const messages=[],files={'stripped.gz':'A000001 ,99,0,-1,9007199254740993,7,\n','names.gz':'A000001 Test reference\n'};
  const self={postMessage:data=>messages.push(data)},context=vm.createContext({self,referenceQuery,referenceValues,referencePositions,referenceNameMatches,URL,Blob,TextDecoderStream,DecompressionStream,Uint8Array,fetch:async url=>new Response(files[new URL(url).pathname.split('/').pop()])});
  vm.runInContext(code,context);
  await self.onmessage({data:{type:'records',records:[{id:'A000001',position:2,count:2}]}});assert.equal(messages.at(-1).type,'results');assert.deepEqual(Array.from(messages.at(-1).results[0].values),['-1','9007199254740993']);
  for(const records of [[{id:'A000001',position:99,count:1}],[{id:'A999999',position:0,count:1}],[],[{id:'bad',position:0,count:1}],[{id:'A000001',position:0,count:257}]]){await self.onmessage({data:{type:'records',records}});assert.equal(messages.at(-1).type,'error');}
});
