import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {webcrypto, createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';

// Exercise the actual classic-worker loader without downloading or booting Lean.
const source = await readFile(new URL('../website/assets/lean-wasm/worker.js', import.meta.url), 'utf8');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const deferred = () => { let resolve, reject;const promise = new Promise((a, b) => { resolve = a;reject = b; });return {promise, resolve, reject}; };
async function until(predicate) {
  const deadline = Date.now() + 3000;
  while (!predicate()) { assert.ok(Date.now() < deadline, 'worker protocol did not reach the expected phase');await new Promise(setImmediate); }
}
function fixture(name, text = `checked bytes ${name}`) {
  const raw = new TextEncoder().encode(text), encoded = new Uint8Array(gzipSync(raw));
  return {raw, encoded, pack: {file: `${name}.pack`, bytes: raw.length, compressedBytes: encoded.length,
    sha256: sha(encoded), entries: [{path: `${name}.olean`, offset: 0, bytes: raw.length}]}};
}
function harness(fetchOverride) {
  const records = new Map(), manifests = new Map(), requests = [], writes = [], posts = [];
  const defaultFetch = async url => {
    if (manifests.has(url)) return Response.json(manifests.get(url));
    const record = records.get(url);
    return record ? new Response(record.encoded) : new Response('', {status: 404});
  };
  const sandbox = {
    Blob, URL, URLSearchParams, location: {search: ''}, performance, TextDecoder, TextEncoder,
    Response, DecompressionStream, AbortController, AbortSignal, setTimeout, clearTimeout,
    crypto: webcrypto, console: {log() {}}, __LEAN_WASM_CONFIG__: {assetBase: '/engine/lean-wasm'},
    postMessage: message => posts.push(message), close() {},
    fetch: (url, options = {}) => {
      url = String(url);requests.push({url, signal: options.signal});
      return fetchOverride ? fetchOverride(url, options, defaultFetch) : defaultFetch(url);
    },
    Module: {FS: {mkdir() {}, writeFile(path, bytes) { writes.push({path, bytes: new Uint8Array(bytes)}); }}}
  };
  sandbox.self = sandbox;vm.createContext(sandbox);vm.runInContext(source, sandbox);
  vm.runInContext('checkBuildIdentity = async () => null;tryRootSnapshot = async () => null;', sandbox);
  const evaluate = script => vm.runInContext(script, sandbox);
  return {
    sandbox, requests, writes, posts, records, manifests, evaluate,
    state: () => evaluate('({slots: packSlots, waiters: packSlotWaiters.length, controllers: packDownloadControllers.size})'),
    add(items, prefix = '/packs/') { for (const item of items) records.set(prefix + item.pack.file, item); },
    generic(items, consume = async () => {}) {
      this.add(items);sandbox.inputPacks = items.map(item => item.pack);sandbox.consume = consume;
      return evaluate('forEachDownloadedPack(inputPacks, pack => "/packs/" + pack.file, consume)');
    },
    layer(items, label = 'Test', loose = []) {
      this.add(items);const manifestUrl = `/${label}.json`;
      manifests.set(manifestUrl, {packs: items.map(item => item.pack), loose});
      return evaluate(`loadPackedLayer(${JSON.stringify({manifestUrl, packBase: '/packs', label})})`);
    },
    core(items) {
      this.add(items, '/engine/lean-wasm/core-lib/');
      manifests.set('/engine/lean-wasm/core-layer.json', {modules: items.length, packs: items.map(item => item.pack)});
      return evaluate('loadLibrary()');
    }
  };
}

test('two download slots retain completed lookahead until consumption and install in manifest order', async () => {
  const first = deferred(), consume = deferred(), items = ['a', 'b', 'c'].map(name => fixture(name));
  const h = harness((url, _options, normal) => url.endsWith('/a.pack') ? first.promise : normal(url));
  const order = [];
  const loading = h.generic(items, async (pack, bytes, index) => {
    order.push(pack.file);assert.equal(sha(bytes), pack.sha256);
    if (index === 0) await consume.promise;
  });
  await until(() => h.requests.length === 2);
  assert.deepEqual(h.requests.map(request => request.url), ['/packs/a.pack', '/packs/b.pack']);
  first.resolve(new Response(items[0].encoded));
  await until(() => order.length === 1);
  assert.equal(h.state().slots, 2, 'completed lookahead must still hold its reservation');
  assert.equal(h.requests.length, 2, 'a third encoded body must not start while both slots are retained');
  consume.resolve();await loading;
  assert.deepEqual(order, ['a.pack', 'b.pack', 'c.pack']);
  assert.equal(h.state().slots, 0);assert.equal(h.state().controllers, 0);
});

test('the pack slot budget and hash/inflate/install stage are shared across concurrent layer requests', async () => {
  const gate = deferred(), h = harness(), order = [];
  let consuming = 0, peak = 0;
  const consume = async pack => {
    consuming++;peak = Math.max(peak, consuming);order.push(pack.file);
    if (order.length === 1) await gate.promise;
    consuming--;
  };
  const a = h.generic(['a0', 'a1'].map(name => fixture(name)), consume);
  const b = h.generic(['b0', 'b1'].map(name => fixture(name)), consume);
  await until(() => order.length === 1);
  assert.equal(h.requests.length, 2);assert.equal(h.state().slots, 2);
  assert.equal(h.state().waiters, 2);
  gate.resolve();await Promise.all([a, b]);
  assert.equal(peak, 1);assert.equal(h.requests.length, 4);
  assert.ok(order.indexOf('a0.pack') < order.indexOf('a1.pack'));
  assert.ok(order.indexOf('b0.pack') < order.indexOf('b1.pack'));
  assert.equal(h.state().slots, 0);assert.equal(h.state().waiters, 0);
});

for (const mode of ['unknown', 'oversized']) test(`${mode} encoded sizes use an exclusive serial fallback`, async () => {
  const gate = deferred(), h = harness(), first = fixture('fallback');
  if (mode === 'unknown') delete first.pack.compressedBytes;
  else {
    first.encoded = new Uint8Array(8 * 1024 * 1024 + 1);
    first.pack.compressedBytes = first.encoded.length;
  }
  const items = [first, fixture('next')], order = [];
  const loading = h.generic(items, async pack => { order.push(pack.file);if (order.length === 1) await gate.promise; });
  await until(() => order.length === 1);
  const other = h.generic([fixture('other')]);
  await new Promise(setImmediate);
  assert.equal(h.requests.length, 1);assert.equal(h.state().slots, 1);
  gate.resolve();await Promise.all([loading, other]);
  assert.deepEqual(order, ['fallback.pack', 'next.pack']);assert.equal(h.state().slots, 0);
});

test('actual gzip/SHA layer installation preserves file bytes, progress order and loaded-layer reuse', async () => {
  const items = ['first', 'second', 'third'].map(name => fixture(name)), h = harness();
  const result = await h.layer(items);
  assert.equal(result.files, 3);assert.equal(result.bytes, items.reduce((sum, item) => sum + item.raw.length, 0));
  assert.deepEqual(h.writes.map(write => write.path), items.map(item => '/lib/lean/' + item.pack.entries[0].path));
  for (const [index, write] of h.writes.entries()) assert.deepEqual(write.bytes, items[index].raw);
  assert.deepEqual(h.posts.filter(post => post.stage === 'progress').map(post => post.pack), [1, 2, 3]);
  const requests = h.requests.length;
  assert.equal((await h.layer(items)).alreadyLoaded, true);assert.equal(h.requests.length, requests);
});

test('core uses the same pipeline and accepts legacy packs without a SHA field', async () => {
  const items = [fixture('core0'), fixture('core1')];delete items[0].pack.sha256;
  const h = harness(), files = await h.core(items);
  assert.equal(files.length, 2);
  for (const [index, file] of files.entries()) assert.deepEqual(new Uint8Array(file.data), items[index].raw);
  assert.deepEqual(h.posts.filter(post => post.stage === 'pack').map(post => post.loaded), [1, 2]);
  assert.equal(h.posts.at(-1).stage, 'done');assert.equal(h.state().slots, 0);
});

test('core verifies an optional SHA before decompression and never reports completion on mismatch', async () => {
  const item = fixture('bad-core');item.pack.sha256 = '0'.repeat(64);
  const h = harness();h.evaluate('gunzip = async () => { throw new Error("DECOMPRESS_MUST_NOT_RUN"); };');
  await assert.rejects(h.core([item]), /bad-core.pack: checksum mismatch/);
  assert.ok(!h.posts.some(post => post.stage === 'done'));assert.equal(h.state().slots, 0);
});

test('stream lengths use actual asset bytes even when HTTP Content-Length describes a different transfer encoding', async () => {
  const item = fixture('encoded-header');
  const h = harness((url, _options, normal) => url.endsWith('/encoded-header.pack')
    ? new Response(item.encoded, {headers: {'Content-Length': '1', 'Content-Encoding': 'gzip'}}) : normal(url));
  assert.equal((await h.layer([item])).files, 1);
  assert.deepEqual(h.writes[0].bytes, item.raw);
});

for (const kind of ['encoded-short', 'encoded-overrun', 'decoded-length', 'checksum']) {
  test(`${kind} failures install no bad entries and do not mark the layer loaded`, async () => {
    const item = fixture('bad');
    let response = () => new Response(item.encoded), expected;
    if (kind === 'encoded-short') { response = () => new Response(item.encoded.subarray(0, -1));expected = /encoded bytes, manifest says/; }
    if (kind === 'encoded-overrun') { response = () => new Response(new Uint8Array([...item.encoded, 0]));expected = /encoded length exceeds/; }
    if (kind === 'decoded-length') { item.pack.bytes++;expected = /bytes, manifest says/; }
    if (kind === 'checksum') { item.pack.sha256 = '0'.repeat(64);expected = /checksum mismatch/; }
    const h = harness((url, _options, normal) => url.endsWith('/bad.pack') ? response() : normal(url));
    await assert.rejects(h.layer([item]), expected);
    assert.equal(h.writes.length, 0);assert.equal(h.evaluate('loadedLayers.has("Test")'), false);
    assert.equal(h.state().slots, 0);assert.equal(h.state().controllers, 0);
  });
}

test('a failed lookahead cancels an earlier pending fetch and preserves the original HTTP failure', async () => {
  const items = [fixture('slow'), fixture('missing')];let canceled = 0;
  const h = harness((url, {signal}, normal) => {
    if (url.endsWith('/slow.pack')) return new Promise((_resolve, reject) => signal.addEventListener('abort', () => { canceled++;reject(signal.reason); }, {once: true}));
    if (url.endsWith('/missing.pack')) return new Response('', {status: 404});
    return normal(url);
  });
  await assert.rejects(h.layer(items), /missing.pack: HTTP 404/);
  assert.equal(canceled, 1);assert.equal(h.writes.length, 0);
  assert.equal(h.state().slots, 0);assert.equal(h.state().controllers, 0);
});

test('a checksum failure aborts and drains a pending peer without unhandled rejection or installation', async () => {
  const items = [fixture('bad'), fixture('slow')];items[0].pack.sha256 = '0'.repeat(64);let canceled = 0;
  const h = harness((url, {signal}, normal) => url.endsWith('/slow.pack')
    ? new Promise((_resolve, reject) => signal.addEventListener('abort', () => { canceled++;reject(signal.reason); }, {once: true})) : normal(url));
  await assert.rejects(h.layer(items), /bad.pack: checksum mismatch/);
  assert.equal(canceled, 1);assert.equal(h.writes.length, 0);assert.equal(h.state().slots, 0);
});

for (const phase of ['headers', 'body']) test(`shutdown cancels queued packs during ${phase} and cannot install late bytes`, async () => {
  const items = [fixture('a'), fixture('b')];let canceled = 0;
  const h = harness((url, {signal}, normal) => {
    if (!url.endsWith('.pack')) return normal(url);
    if (phase === 'headers') return new Promise((_resolve, reject) => signal.addEventListener('abort', () => { canceled++;reject(signal.reason); }, {once: true}));
    return new Response(new ReadableStream({cancel() { canceled++; }}));
  });
  const rejected = assert.rejects(h.layer(items), /disposed|abort/i);
  await until(() => h.requests.filter(request => request.url.endsWith('.pack')).length === 2);
  await new Promise(setImmediate);
  h.evaluate('releaseRuntimeResources()');await rejected;
  assert.equal(canceled, 2);assert.equal(h.writes.length, 0);
  assert.equal(h.state().slots, 0);assert.equal(h.state().waiters, 0);assert.equal(h.state().controllers, 0);
});

test('shutdown while hashing completed downloads prevents decompression and filesystem installation', async () => {
  const gate = deferred(), h = harness(), items = [fixture('a'), fixture('b')];let hashing = 0;
  h.sandbox.crypto = {subtle: {async digest(...args) { hashing++;await gate.promise;return webcrypto.subtle.digest(...args); }}};
  const rejected = assert.rejects(h.layer(items), /disposed/);
  await until(() => hashing === 1);
  h.evaluate('releaseRuntimeResources()');gate.resolve();await rejected;
  assert.equal(hashing, 1);assert.equal(h.writes.length, 0);assert.equal(h.state().slots, 0);
});

test('invalid declared compressed sizes fail before requesting a pack', async () => {
  for (const value of [-1, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
    const item = fixture('invalid');item.pack.compressedBytes = value;const h = harness();
    await assert.rejects(h.layer([item]), /invalid compressed size/);
    assert.ok(!h.requests.some(request => request.url.endsWith('.pack')));assert.equal(h.state().slots, 0);
  }
});

test('core and optional manifest HTTP failures cannot install their JSON-shaped bodies', async () => {
  for (const core of [false, true]) {
    const h = harness(() => Response.json({modules: 0, packs: []}, {status: 503}));
    await assert.rejects(core ? h.core([]) : h.layer([]), /HTTP 503/);
    assert.equal(h.requests.length, 1);assert.equal(h.writes.length, 0);
    assert.equal(h.evaluate('loadedLayers.has("Test")'), false);
    assert.equal(h.state().controllers, 0);
  }
});

test('the existing loose-file tail remains capped at16 requests after packed loading', async () => {
  const items = Array.from({length: 17}, (_, index) => fixture('loose' + index)), pending = [];
  let active = 0, peak = 0;
  const h = harness((url, _options, normal) => {
    if (!url.endsWith('.pack')) return normal(url);
    active++;peak = Math.max(peak, active);
    const finish = () => { active--;return normal(url); };
    if (pending.length >= 16) return finish();
    const gate = deferred();pending.push(() => gate.resolve(finish()));return gate.promise;
  });
  h.add(items);
  const loose = items.map(item => ({file: item.pack.file, path: item.pack.entries[0].path, bytes: item.raw.length, sha256: item.pack.sha256}));
  const loading = h.layer([], 'Loose', loose);
  await until(() => pending.length === 16);
  assert.equal(active, 16);for (const release of pending) release();
  const result = await loading;
  assert.equal(peak, 16);assert.equal(result.files, 17);assert.equal(h.writes.length, 17);
});
