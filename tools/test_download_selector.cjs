/* Exercise selection rules and the actual browser worker with an isolated fetch. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assets = path.resolve(__dirname, '../website/assets');
const core = require(path.join(assets, 'download-core.js'));
const fflate = require(path.join(assets, 'vendor/fflate-0.8.3.js'));
const bodies = new Map();
function file(work, name, text, required = false) {
  const raw = Buffer.from(text);
  const id = (work || 'collection-notices') + '/' + name;
  const url = 'documents/files/' + crypto.createHash('sha1').update(raw).digest('hex') + '/' + name;
  bodies.set(new URL(url, 'https://reader.example/collection/').href, raw);
  return {id, work, path:name, archive_path:id, url, size:raw.length,
    sha256:crypto.createHash('sha256').update(raw).digest('hex'), required,
    reader_url:null, category:core.size(0), reading:true};
}
const paper = file('paper-i', 'paper.pdf', '%PDF fixture');
const proof = file('paper-ii', 'proof-α.tex', 'Exact source: α and \\sum_{k=0}^n k.');
const license = file('paper-i', 'LICENSE', 'Work license', true);
const otherLicense = file('unselected', 'LICENSE', 'Other license', true);
const notice = file(null, 'CITATION.md', 'Project authorship', true);
const catalog = {version:1,source_revision:'a'.repeat(40),scope:'Selected files only.',
  works:[{id:'paper-i',url:'works/i.html'},{id:'paper-ii',url:'works/ii.html'},{id:'unselected',url:'works/other.html'}],
  files:[paper,proof,license,otherLicense,notice]};
core.validate(catalog);
assert.deepEqual(core.plan(catalog,[paper.id]).files.map(f=>f.id).sort(),[paper.id,license.id,notice.id].sort());
assert.equal(core.plan(catalog,[paper.id,paper.id]).selectedCount,1);
assert.throws(()=>core.plan(catalog,[]),/Choose at least/);
assert.throws(()=>core.plan(catalog,['missing']),/Choose at least/);
assert.throws(()=>core.plan(catalog,[paper.id,'missing']),/unavailable/);
for (const unsafe of ['../escape','/root','one/../two','C:/file','a\\b','a//b','a\0b']) assert.equal(core.safePath(unsafe),false,unsafe);
for (const mutation of [c=>c.files.push({...c.files[0]}),c=>c.files[0].archive_path='../escape',c=>c.files[0].url='https://elsewhere/file',c=>c.files[0].url='documents/files/%2e%2e/file']) {
  const invalid=structuredClone(catalog);mutation(invalid);assert.throws(()=>core.validate(invalid));
}
const large=structuredClone(catalog);large.files[0].size=core.MAX_BYTES;
assert.equal(core.plan(large,[paper.id]).overLimit,true);
async function runWorker(data, fetcher) {
  const chunks=[];const messages=[];
  return new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(new Error('Worker test timed out')),5000);
    const context={URL,TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,AbortController,setTimeout,clearTimeout,
      crypto:crypto.webcrypto,location:{href:'https://reader.example/collection/assets/download-worker.js?v=test'},
      fetch:fetcher || (async url=>new Response(bodies.get(url),{status:bodies.has(url)?200:404})),
      postMessage(message){
        messages.push(message);
        if(message.type==='chunk')chunks.push(Buffer.from(message.chunk));
        if(message.type==='done'||message.type==='error'){
          clearTimeout(timeout);resolve({messages,archive:Buffer.concat(chunks),last:message});
        }
      }};
    context.self=context;
    vm.createContext(context);
    context.importScripts=(...scripts)=>scripts.forEach(script=>vm.runInContext(fs.readFileSync(path.join(assets,script.split('?')[0]),'utf8'),context));
    vm.runInContext(fs.readFileSync(path.join(assets,'download-worker.js'),'utf8'),context);
    context.onmessage({data});
  });
}
(async()=>{
  const result=await runWorker({catalog,selectedIds:[paper.id,proof.id]});
  assert.equal(result.last.type,'done',JSON.stringify(result.last));
  const files=fflate.unzipSync(result.archive);
  assert.deepEqual(Object.keys(files).sort(),[paper.id,proof.id,license.id,notice.id,'CONTENTS.json','SHA256SUMS','README.txt'].sort());
  assert.equal(Buffer.from(files[proof.id]).toString(), 'Exact source: α and \\sum_{k=0}^n k.');
  const contents=JSON.parse(Buffer.from(files['CONTENTS.json']));
  assert.equal(contents.source_revision,catalog.source_revision);
  assert.equal(contents.works.length,2);
  assert.equal(contents.files.length,4);
  for(const f of contents.files)assert.equal(crypto.createHash('sha256').update(files[f.archive_path]).digest('hex'),f.sha256);
  if(process.env.KOMOREBI_ZIP_TEST_OUTPUT)fs.writeFileSync(process.env.KOMOREBI_ZIP_TEST_OUTPUT,result.archive);
  const corrupt=structuredClone(catalog);corrupt.files[0].sha256='0'.repeat(64);
  assert.match((await runWorker({catalog:corrupt,selectedIds:[paper.id]})).last.message,/integrity check failed/);
  assert.match((await runWorker({catalog,selectedIds:[paper.id]},async()=>new Response('bad',{status:404}))).last.message,/Could not fetch/);
  assert.match((await runWorker({catalog,selectedIds:[paper.id]},async()=>new Response(''))).last.message,/Incomplete download/);
  assert.match((await runWorker({catalog:large,selectedIds:[paper.id]})).last.message,/exceeds 200/);
  if(process.env.KOMOREBI_ZIP_CATALOG){
    const actual=JSON.parse(fs.readFileSync(process.env.KOMOREBI_ZIP_CATALOG));
    const selectedIds=actual.files.filter(f=>['paper-i','paper-ii'].includes(f.work)&&['PDFs','Worked examples'].includes(f.category)&&!f.required).map(f=>f.id);
    const site=path.resolve(process.env.KOMOREBI_ZIP_SITE);
    const packed=await runWorker({catalog:actual,selectedIds},async url=>{
      const relative=decodeURIComponent(new URL(url).pathname.slice('/collection/'.length));
      assert.equal(core.safePath(relative),true);
      return new Response(fs.readFileSync(path.join(site,relative)));
    });
    assert.equal(packed.last.type,'done',JSON.stringify(packed.last));
    const entries=fflate.unzipSync(packed.archive);
    const contents=JSON.parse(Buffer.from(entries['CONTENTS.json']));
    for(const f of contents.files)assert.equal(crypto.createHash('sha256').update(entries[f.archive_path]).digest('hex'),f.sha256);
    fs.writeFileSync(process.env.KOMOREBI_REAL_ZIP_OUTPUT,packed.archive);
    console.log('PASS: actual Komorebi archive with',selectedIds.length,'selected files and',contents.files.length-selectedIds.length,'notices');
  }
  console.log('PASS: selection, notices, safe paths, size limit, UTF-8 ZIP round trip, checksums and download failures');
})().catch(error=>{console.error(error);process.exitCode=1;});
