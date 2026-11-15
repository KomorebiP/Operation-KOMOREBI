import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {selectDirectory,readDirectoryURL,directoryURL} from '../website/assets/sequence-atlas-directory.mjs';
import {transform,exact} from '../website/assets/sequence-atlas-core.mjs';
const root=fileURLToPath(new URL('..',import.meta.url));
const fixture=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','-c',"import sys,json;sys.path.insert(0,'tools');from sequence_atlas import catalogue;from sequence_atlas_index import connection_graph;c=catalogue();print(json.dumps(dict(entries=c,graph=connection_graph(c))))"],{cwd:root,encoding:'utf8',maxBuffer:10*1024*1024}));
const entries=fixture.entries;
test('directory combines exact atlas queries, topics, stable sorting and both connection directions',()=>{
  assert.equal(selectDirectory(entries).entries.length,38);
  assert.equal(selectDirectory(entries,{order:'id'}).entries[0].id,'KSEQ-000001');
  assert.equal(selectDirectory(entries).entries[0].title,'Bell numbers');
  assert.deepEqual(selectDirectory(entries,{query:'KSEQ7'}).entries.map(e=>e.id),['KSEQ-000007']);
  assert.equal(selectDirectory(entries,{query:'n:4 r:2'}).entries[0].id,'KSEQ-000008');
  assert.equal(selectDirectory(entries,{query:'"ordered bell"',topic:'partitions'}).entries.length,1);
  assert.equal(selectDirectory(entries,{connected:true}).entries.length,6);
  const incomingOnly=entries.map(e=>({...e,connections:e.id==='KSEQ-000027'?e.connections:[]}));
  assert.ok(selectDirectory(incomingOnly,{connected:true}).entries.some(e=>e.id==='KSEQ-000029'));
  assert.equal(selectDirectory(entries,{query:'no-such-entry'}).entries.length,0);
  assert.throws(()=>selectDirectory(entries,{query:'name:"broken'}));
});
test('directory shares only applied filters while local history retains its context, with explicit invalid recovery',()=>{
  const state={query:'name:"ordered bell"',topic:'partitions',order:'id',connected:false};
  const original='https://example.test/sequences.html?q=n%3A4&sequence=custom&terms=12,34,56&discover=1,2,3,4,5,6#find';
  const url=directoryURL(original,state);
  assert.equal(url.hash,'#catalogue');for(const key of ['q','terms','sequence','discover'])assert.equal(url.searchParams.has(key),false,key);assert.deepEqual(readDirectoryURL(url,entries).state,state);
  const local=directoryURL(original,state,{preserveContext:true});assert.equal(local.searchParams.get('q'),'n:4');assert.equal(local.searchParams.get('terms'),'12,34,56');
  for(const query of ['index-order=wrong','index-connected=maybe','index-topic=unlisted','index-query=name%3A%22broken']){const result=readDirectoryURL('https://example.test/?'+query,entries);assert.ok(result.error,query);assert.equal(result.entries.length,38);}
  const reset=directoryURL(local,{query:'',topic:'',order:'name',connected:false},{preserveContext:true});assert.equal(reset.searchParams.has('index-query'),false);assert.equal(reset.searchParams.get('q'),'n:4');
});
test('all seven directed connections and 84 evidence rows agree with independent browser transforms at original indices',()=>{
  const {graph}=fixture,lookup=new Map(entries.map(e=>[e.id,e]));assert.equal(graph.edges.length,7);assert.equal(new Set(graph.edges.map(e=>e.key)).size,7);
  let rows=0;
  for(const edge of graph.edges){const source=lookup.get(edge.source_id),target=lookup.get(edge.target_id),values=transform(source.terms.map(BigInt),edge.operation);assert.equal(edge.rows.length,12);for(const [k,row]of edge.rows.entries()){assert.equal(row.source_n,edge.source_start+k);assert.equal(row.target_n,edge.target_start+k);assert.equal(row.source_value,source.terms[row.source_n]);assert.equal(row.transformed_value,exact(values[row.source_n]));assert.equal(row.target_value,target.terms[row.target_n]);assert.equal(row.transformed_value,row.target_value);rows++;}}
  assert.equal(rows,84);
  const shifted=graph.edges.find(e=>e.source_id==='KSEQ-000028');assert.equal(shifted.target_start,1);assert.deepEqual(shifted.rows.slice(0,3).map(r=>r.transformed_value),['1','4','9']);
});
