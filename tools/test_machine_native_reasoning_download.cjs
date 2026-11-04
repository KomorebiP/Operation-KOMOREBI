const test = require('node:test');
const assert = require('node:assert/strict');
const { readFile } = require('node:fs/promises');
const { join } = require('node:path');
const { pathToFileURL } = require('node:url');
const root = join(__dirname, '..');
const modulePromise = import(pathToFileURL(join(root, 'website/assets/machine-native-reasoning-download.mjs')));
const manifestPromise = readFile(join(root,'publication/machine-native-reasoning-reconstructed/2026-11-04/PUBLICATION.json'),'utf8').then(JSON.parse);
const revision = '65e73adf1f0c9f79325ea5d893c3cd77c9ff9183';
async function localFetch(url) {
  const parsed = new URL(url);
  assert.equal(parsed.origin,'https://raw.githubusercontent.com');
  const prefix = '/KomorebiP/Operation-KOMOREBI/' + revision + '/';
  assert.ok(parsed.pathname.startsWith(prefix));
  const raw = await readFile(join(root,parsed.pathname.slice(prefix.length)));
  return {ok:true,status:200,arrayBuffer:async()=>raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength)};
}
test('browser transport reproduces both complete admitted artifacts',async()=>{
  const {assembleAsset,sha256}=await modulePromise, data=await manifestPromise;
  for(const kind of ['pdf','source']) {
    let progress=0;
    const raw=await assembleAsset(kind,data.assets[kind],{revision,fetcher:localFetch,onprogress:x=>{assert.ok(x>=progress);progress=x;}});
    assert.equal(progress,1); assert.equal(raw.length,data.assets[kind].bytes);
    assert.equal(await sha256(raw),data.assets[kind].sha256);
  }
});
test('corrupted bytes, altered aggregate identity, unsafe paths and failed HTTP are rejected',async()=>{
  const {assembleAsset,validateAsset}=await modulePromise, data=await manifestPromise;
  const asset=data.assets.pdf;
  await assert.rejects(assembleAsset('pdf',asset,{revision,fetcher:async url=>{
    const r=await localFetch(url), b=new Uint8Array(await r.arrayBuffer());b[0]^=1;
    return {ok:true,arrayBuffer:async()=>b.buffer};
  }}),/integrity/);
  assert.throws(()=>validateAsset('pdf',{...asset,sha256:'0'.repeat(64)},revision),/Unknown/);
  const unsafe=structuredClone(asset);unsafe.parts[0].path='../outside';
  assert.throws(()=>validateAsset('pdf',unsafe,revision),/Invalid file part/);
  await assert.rejects(assembleAsset('pdf',asset,{revision,fetcher:async()=>({ok:false,status:503})}),/503/);
});
test('cancel stops assembly and a subsequent retry succeeds',async()=>{
  const {assembleAsset}=await modulePromise, {assets}=await manifestPromise;
  const controller=new AbortController();controller.abort(new Error('cancelled'));
  let calls=0;
  await assert.rejects(assembleAsset('pdf',assets.pdf,{revision,signal:controller.signal,fetcher:async()=>{calls++;}}),/cancelled/);
  assert.equal(calls,0);
  const bytes=await assembleAsset('pdf',assets.pdf,{revision,fetcher:localFetch});
  assert.equal(bytes.length,assets.pdf.bytes);
});
