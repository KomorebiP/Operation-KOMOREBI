import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {parseQuery,searchEntries,matchTerms,termPattern,suggestions,searchLink} from '../website/assets/sequence-atlas-search.mjs';
import {readSaved,writeSaved,STORAGE_KEY} from '../website/assets/sequence-atlas-saved.mjs';
const root=fileURLToPath(new URL('..',import.meta.url));
const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','tools/sequence_atlas.py'],{cwd:root,encoding:'utf8',maxBuffer:10*1024*1024}));
const ids=(query,options)=>searchEntries(entries,query,options).map(hit=>hit.entry.id);

test('words use AND; quoted phrases and qualified fields stay together',()=>{
  assert.deepEqual(ids('bell factorial'),['KSEQ-000023']);
  assert.deepEqual(ids('name:"ordered bell"'),['KSEQ-000023']);
  assert.deepEqual(ids('n:4 r:2'),['KSEQ-000008']);
  assert.deepEqual(ids('n:04 r:+2'),['KSEQ-000008']);
  assert.deepEqual(ids('formula:convolution n:8'),['KSEQ-000019','KSEQ-000020','KSEQ-000021']);
  assert.deepEqual(ids('tag:partitions -name:fubini'),['KSEQ-000022','KSEQ-000036']);
  assert.equal(ids('n:4 | name:bell').length,5);
});
test('identifiers are normalized and exact references rank ahead of descriptions',()=>{
  assert.equal(ids('KSEQ7')[0],'KSEQ-000007');
  assert.deepEqual(ids('id:KSEQ-7'),['KSEQ-000007']);
  assert.deepEqual(ids('id:A364'),['KSEQ-000001']);
  assert.deepEqual(ids('oeis:A000364'),['KSEQ-000001']);
  assert.equal(ids('Fibonacci')[0],'KSEQ-000025');
});
test('numeric patterns retain signs and large integers and report their offsets',()=>{
  assert.deepEqual(ids('1, ?, 69'),['KSEQ-000007']);
  const hit=searchEntries(entries,'69, 33661, 60376809')[0];
  assert.equal(hit.entry.id,'KSEQ-000007');assert.equal(hit.termMatch.start,2);assert.equal(hit.termMatch.length,3);
  assert.deepEqual(ids('69, 33661',{match:'start'}),[]);
  assert.deepEqual(ids('1, −1, 5'),['KSEQ-000026']);
  assert.deepEqual(ids('terms:"1, ?, 69" n:4'),['KSEQ-000007']);
  assert.deepEqual(matchTerms(['9007199254740993','-1','7'],termPattern('9007199254740993, ?, 7')),[0]);
  assert.deepEqual(matchTerms(['9007199254740992','-1','7'],termPattern('9007199254740993, ?, 7')),[]);
  assert.deepEqual(matchTerms(['1','1'],['1','1','1']),[]);
  assert.deepEqual(matchTerms(['1','1'],['1',null,null]),[]);
});
test('filters, stable sorting and saved entries compose with queries',()=>{
  assert.equal(ids('',{filter:'family'}).length,21);
  assert.equal(ids('',{filter:'reference'}).length,18);
  assert.equal(ids('status:"known reference"').length,18);
  assert.equal(ids('status:unassessed').length,20);
  assert.deepEqual(ids('',{filter:'saved',saved:['KSEQ-000025']}),['KSEQ-000025']);
  assert.deepEqual(ids('',{topic:'partitions',sort:'id'}),['KSEQ-000022','KSEQ-000023','KSEQ-000036']);
  const names=searchEntries(entries,'',{sort:'name'}).map(hit=>hit.entry.title);
  assert.deepEqual(names,[...names].sort((a,b)=>a.localeCompare(b,'en')));
});
test('malformed syntax is explained; spelling suggestions do not alter numeric matching',()=>{
  for(const query of ['name:"bell','name:','unknown:bell','bell |','| bell','? , ?'])assert.throws(()=>parseQuery(query),query);
  assert.ok(suggestions(entries,'fibonaci').includes('Fibonacci'));
  assert.deepEqual(suggestions(entries,'1,2,3'),[]);
  assert.deepEqual(ids('1,69,1'),[]);
  assert.deepEqual(ids('name:"<script>"'),[]);
});
test('deep search links preserve exact query state without altering the source view',()=>{
  const url=new URL(searchLink('https://example.com/sequences.html?sequence=KSEQ-000007','1, ?, 69',{topic:'reciprocal',match:'start',sort:'id'}));
  assert.equal(url.searchParams.get('q'),'1, ?, 69');assert.equal(url.searchParams.get('sequence'),'KSEQ-000007');
  assert.equal(url.searchParams.get('topic'),'reciprocal');assert.equal(url.searchParams.get('match'),'start');assert.equal(url.hash,'#find');
});
test('saved-entry storage validates data and handles corruption, denial and duplicates',()=>{
  const values=new Map(),storage={getItem:key=>values.get(key)||null,setItem:(key,value)=>values.set(key,value)};
  assert.equal(writeSaved(storage,['KSEQ-000007','KSEQ-000007','invalid']),true);
  assert.deepEqual(readSaved(storage,new Set(['KSEQ-000007'])),{ids:['KSEQ-000007'],available:true});
  assert.deepEqual(readSaved(storage,new Set(['KSEQ-000001'])).ids,[]);
  values.set(STORAGE_KEY,'{"not":"an array"}');assert.equal(readSaved(storage).available,false);
  const blocked={getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}};
  assert.deepEqual(readSaved(blocked),{ids:[],available:false});assert.equal(writeSaved(blocked,['KSEQ-000007']),false);
});
