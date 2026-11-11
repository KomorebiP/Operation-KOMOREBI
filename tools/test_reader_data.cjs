const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const path = require('node:path');
const loader = fs.readFileSync(path.join(__dirname, '../website/assets/reader-data.js'), 'utf8');
const fallback = fs.readFileSync(path.join(__dirname, '../website/assets/vendor/fflate-0.8.3.js'), 'utf8');
const base = 'https://komorebip.github.io/Operation-KOMOREBI/';
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function fixture({native = true, corrupt = false, missing = false, legacy = false} = {}) {
  const original = Buffer.from(JSON.stringify({exact: '\\Phi  x', alpha: 'α', lines: 'first\n second', rows: ['context '.repeat(50)]}));
  const packed = zlib.gzipSync(original);
  const logical = 'notation/data/book.json';
  const entry = {gzip: logical+'.gz', gzip_bytes: packed.length, gzip_sha256: hash(packed), bytes: original.length,
    sha256: corrupt ? '0'.repeat(64) : hash(original), export_url: 'https://github.com/example/releases/download/pinned/book.json'};
  const manifest = {schema: 1, revision: 'a'.repeat(40), files: missing ? {} : {[logical]: entry},
    fallback_integrity: 'sha256-'+crypto.createHash('sha256').update(fallback).digest('base64')};
  const requests = [], scripts = [], events = {}, redirects = [];
  let context;
  const document = {
    currentScript: {src: base+'assets/reader-data.js?v=123'}, baseURI: base+'notation/book.html',
    addEventListener: (name, callback) => events[name] = callback,
    querySelector: () => legacy ? {} : null,
    createElement: () => ({}),
    head: {append(tag) {
      scripts.push(tag);
      assert.equal(tag.integrity, manifest.fallback_integrity);
      vm.runInContext(fallback, context);
      tag.onload();
    }}
  };
  const fetch = async (input, init) => {
    const url = new URL(input, document.baseURI);
    requests.push({url: url.href, init});
    if (url.pathname.endsWith('/delivery.json')) return Response.json(manifest);
    if (url.pathname.endsWith('/'+logical+'.gz')) return new Response(packed);
    return new Response('unchanged response', {status: 201});
  };
  const sandbox = {document, location: {href: base+logical, replace: url => redirects.push(url)}, fetch,
    URL, Response, Blob, Uint8Array, DOMException, crypto: crypto.webcrypto,
    DecompressionStream: native ? DecompressionStream : undefined, console};
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  context = vm.createContext(sandbox);
  vm.runInContext(loader, context);
  return {read: context.KomorebiReaderData.fetch, original, requests, scripts, events, redirects, entry};
}

test('native gzip delivery restores exact JSON bytes and preserves query parameters', async () => {
  const f = fixture();
  const response = await f.read('data/book.json?v=revision');
  assert.deepEqual(Buffer.from(await response.arrayBuffer()), f.original);
  assert.ok(f.requests.some(r => r.url.includes('book.json.gz?v=revision&delivery=')));
  assert.equal(f.scripts.length, 0);
});

test('pinned fallback restores exact bytes without DecompressionStream', async () => {
  const f = fixture({native: false});
  const results = await Promise.all([f.read('data/book.json'), f.read('data/book.json')]);
  for (const response of results) assert.deepEqual(Buffer.from(await response.arrayBuffer()), f.original);
  assert.equal(f.scripts.length, 1);
  assert.equal(f.requests.filter(r => r.url.endsWith('/delivery.json')).length, 1);
});

test('source files and non-index fetches retain native fetch behavior', async () => {
  const f = fixture();
  const init = {credentials: 'omit'};
  const response = await f.read('../documents/files/source.json', init);
  assert.equal(response.status, 201);
  assert.equal(await response.text(), 'unchanged response');
  assert.equal(f.requests.length, 1);
  assert.equal(f.requests[0].init, init);
});

test('corrupt indexes and unrecorded indexes are rejected', async () => {
  await assert.rejects(fixture({corrupt: true}).read('data/book.json'), /checksum mismatch/);
  await assert.rejects(fixture({missing: true}).read('data/book.json'), /missing from its download record/);
});

test('abort state is preserved', async () => {
  const f = fixture();
  const controller = new AbortController(); controller.abort();
  await assert.rejects(f.read('data/book.json', {signal: controller.signal}), {name: 'AbortError'});
});

test('old bookmarked exports hand off to the recorded native download', async () => {
  const f = fixture({legacy: true});
  await f.events.DOMContentLoaded();
  assert.deepEqual(f.redirects, [f.entry.export_url]);
});
