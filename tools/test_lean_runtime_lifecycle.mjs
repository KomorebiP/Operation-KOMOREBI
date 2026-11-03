import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {createRuntime} from '../website/assets/lean-wasm/runtime.js';
import {createCompiler} from '../website/assets/lean-wasm/compiler.js';

// Protocol and resource-ownership tests. These do not boot Lean or establish
// when a browser physically reclaims a terminated worker's shared-memory pages.
async function withRuntime(check, {ack = true, assets = true, start = true} = {}) {
  const originalWorker = Object.getOwnPropertyDescriptor(globalThis, 'Worker');
  const create = URL.createObjectURL, revoke = URL.revokeObjectURL;
  const harness = {workers: [], created: [], revoked: [], statuses: [], events: []};
  URL.createObjectURL = blob => {
    const url = `blob:lifecycle/${harness.created.length}`;
    harness.created.push({url, blob});
    return url;
  };
  URL.revokeObjectURL = url => harness.revoked.push(url);
  class FakeWorker {
    constructor(url) { this.url = url;this.terminations = 0;harness.workers.push(this); }
    send(data) { this.onmessage?.({data}); }
    terminate() { this.terminations++;harness.events.push('terminate'); }
    postMessage(message) {
      harness.events.push(message);
      queueMicrotask(() => {
        if (message.type === 'start' && start) {
          if (assets) this.send({type: 'create_blob_url', id: 1, kind: 'wasm', blob: new Blob(['wasm'])});
          else this.send({type: 'ready'});
        } else if (message.type === 'blob_url' && !message.error) {
          if (message.id === 1) this.send({type: 'create_blob_url', id: 2, kind: 'script', blob: new Blob(['script'])});
          else this.send({type: 'ready'});
        } else if (message.type === 'dispose' && ack) {
          this.send({type: 'disposed', id: message.id, cleanup: {threadShutdownRequested: true}});
        }
      });
    }
  }
  Object.defineProperty(globalThis, 'Worker', {value: FakeWorker, writable: true, configurable: true});
  const runtime = createRuntime({onStatus: status => harness.statuses.push(status)});
  try { await check(runtime, harness); }
  finally {
    await runtime.dispose({force: true});
    URL.createObjectURL = create;URL.revokeObjectURL = revoke;
    if (originalWorker) Object.defineProperty(globalThis, 'Worker', originalWorker);
    else delete globalThis.Worker;
  }
}

test('idle shutdown acknowledges pthread cleanup then terminates and revokes every host-owned URL', async () => {
  await withRuntime(async (runtime, h) => {
    await runtime.start();
    assert.equal(h.created.length, 3, 'wrapper, Wasm and pthread script must all be owned');
    assert.match(await h.created[0].blob.text(), /"hostOwnsBlobUrls":true/);
    assert.match(await h.created[0].blob.text(), /worker\.js\?v=20261103-lifecycle1/);
    const closing = runtime.dispose();
    assert.equal(closing, runtime.closed);
    assert.equal(h.workers[0].terminations, 0, 'idle disposal allows a cleanup acknowledgement');
    const result = await closing;
    assert.equal(result.acknowledged, true);
    assert.equal(result.cleanup.threadShutdownRequested, true);
    assert.equal(h.workers[0].terminations, 1);
    assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
    assert.equal(runtime.dispose(), closing);
    await assert.rejects(runtime.start(), /cannot be started again/);
    await assert.rejects(runtime.compile('late'), /not running/);
  });
});

test('unsupported idle cleanup has a bounded hard fallback', async () => {
  await withRuntime(async (runtime, h) => {
    await runtime.start();
    const result = await runtime.dispose();
    assert.equal(result.acknowledged, false);
    assert.equal(h.workers[0].terminations, 1);
    assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
  }, {ack: false});
});

test('compiler exposes the same terminal promise returned by dispose', async () => {
  await withRuntime(async (_runtime, h) => {
    const fetch = globalThis.fetch;
    globalThis.fetch = async () => new Response('', {status: 404});
    try {
      const compiler = await createCompiler({baseUrl: 'https://example.invalid/engine/'});
      const closing = compiler.dispose();
      assert.equal(closing, compiler.closed);
      assert.equal((await closing).acknowledged, true);
      assert.equal(h.workers[0].terminations, 1);
      assert.equal(compiler.dispose(), closing);
    } finally { globalThis.fetch = fetch; }
  });
});

test('Stop during startup immediately terminates and rejects the pending start', async () => {
  await withRuntime(async (runtime, h) => {
    const rejected = assert.rejects(runtime.start(), /disposed/);
    const closed = runtime.dispose();
    assert.equal(h.workers[0].terminations, 1);
    assert.ok(!h.events.some(event => event.type === 'dispose'));
    await rejected;await closed;
    assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
  }, {start: false});
});

for (const [name, operation] of [
  ['compile', runtime => runtime.compile('busy')],
  ['module load', runtime => runtime.loadModules(['Lean'])],
  ['layer load', runtime => runtime.loadLayer({label: 'mathlib', manifestUrl: '/layer.json'})]
]) {
  test(`Stop during ${name} is immediate and ignores all captured late messages`, async () => {
    await withRuntime(async (runtime, h) => {
      await runtime.start();
      const worker = h.workers[0], staleDispatch = worker.onmessage;
      const rejected = assert.rejects(operation(runtime), /disposed/);
      runtime.dispose();
      assert.equal(worker.terminations, 1);
      assert.ok(!h.events.some(event => event.type === 'dispose'));
      for (const data of [
        {type: 'status', data: 'stale'}, {type: 'ready'},
        {type: 'create_blob_url', id: 99, kind: 'wasm', blob: new Blob(['late'])}
      ]) staleDispatch({data});
      await rejected;await runtime.closed;
      assert.deepEqual(h.statuses, []);
      assert.equal(h.created.length, 3);
      assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
    });
  });
}

test('force disposal escalates a pending idle close and ignores a mismatched acknowledgement', async () => {
  await withRuntime(async (runtime, h) => {
    await runtime.start();
    const closing = runtime.dispose(), worker = h.workers[0];
    const request = h.events.find(event => event.type === 'dispose');
    worker.send({type: 'disposed', id: request.id + 1});
    assert.equal(worker.terminations, 0);
    assert.equal(runtime.dispose({force: true}), closing);
    assert.equal(worker.terminations, 1);
    assert.equal((await closing).forced, true);
    runtime.dispose({force: true});
    assert.equal(worker.terminations, 1);
  }, {ack: false});
});

test('worker errors and request timeouts are terminal and release all host-owned URLs', async () => {
  for (const timeout of [false, true]) {
    await withRuntime(async (runtime, h) => {
      await runtime.start();
      const originalTimeout = globalThis.setTimeout;
      if (timeout) globalThis.setTimeout = (fn, ms, ...args) => originalTimeout(fn, ms === 30000 ? 0 : ms, ...args);
      try {
        const rejected = assert.rejects(runtime.reset(), timeout ? /timed out/ : /engine failed/);
        if (!timeout) h.workers[0].onerror({message: 'engine failed'});
        await rejected;await runtime.closed;
        assert.equal(h.workers[0].terminations, 1);
        assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
      } finally { globalThis.setTimeout = originalTimeout; }
    });
  }
});

test('invalid or duplicate asset requests never create an untracked URL', async () => {
  await withRuntime(async (runtime, h) => {
    await runtime.start();
    const worker = h.workers[0];
    for (const request of [
      {id: 3, kind: 'wasm', blob: new Blob(['duplicate'])},
      {id: 4, kind: 'other', blob: new Blob(['invalid'])},
      {id: 5, kind: 'script', blob: {}},
      {id: NaN, kind: 'wasm', blob: new Blob(['invalid'])}
    ]) worker.send({type: 'create_blob_url', ...request});
    assert.equal(h.created.length, 3);
    assert.equal(h.events.filter(event => event.type === 'blob_url' && event.error).length, 4);
    await runtime.dispose();
    assert.equal(h.revoked.length, 3);
  });
});

const workerSource = await readFile(new URL('../website/assets/lean-wasm/worker.js', import.meta.url), 'utf8');
function workerContext(config = {}, overrides = {}) {
  const events = [], revoked = [], created = [];
  class WorkerURL extends URL {
    static createObjectURL(blob) { const url = `blob:worker/${created.length}`;created.push({url, blob});return url; }
    static revokeObjectURL(url) { revoked.push(url);events.push('revoke'); }
  }
  const sandbox = {
    Blob, URL: WorkerURL, URLSearchParams, location: {search: ''}, performance,
    TextDecoder, TextEncoder, Response, setTimeout, clearTimeout, WebAssembly, SharedArrayBuffer,
    console: {log() {}}, __LEAN_WASM_CONFIG__: config,
    postMessage: message => events.push(message), close: () => events.push('close'), ...overrides
  };
  sandbox.self = sandbox;
  vm.createContext(sandbox);vm.runInContext(workerSource, sandbox);
  return {sandbox, events, revoked, created, evaluate: source => vm.runInContext(source, sandbox)};
}

test('worker JS-only shutdown terminates global PThread before revoking assets and acknowledging', async () => {
  const h = workerContext();
  h.sandbox.PThread = {runningWorkers: [1], unusedWorkers: [2, 3], terminateAllThreads() { h.events.push('threads'); }};
  h.sandbox.Module = new Proxy({}, {get() { throw new Error('cleanup must not touch Wasm or C++ finalizers'); }});
  await h.evaluate('runtimeBlobUrl(new Blob(["wasm"]), "wasm")');
  await h.evaluate('runtimeBlobUrl(new Blob(["script"]), "script")');
  await h.sandbox.onmessage({data: {type: 'dispose', id: 8}});
  assert.deepEqual(h.events.map(event => typeof event === 'string' ? event : event.type), ['threads', 'revoke', 'revoke', 'disposed', 'close']);
  const ack = h.events.find(event => event.type === 'disposed');
  assert.equal(ack.id, 8);assert.equal(ack.cleanup.threadShutdownRequested, true);
  assert.equal(ack.cleanup.threadsBefore.running, 1);assert.equal(ack.cleanup.threadsBefore.unused, 2);
  assert.deepEqual(h.revoked, h.created.map(entry => entry.url));
  const before = h.events.length;
  await h.sandbox.onmessage({data: {type: 'compile', id: 9, code: 'late'}});
  assert.equal(h.events.length, before);
});

test('worker cooperates with host URL ownership and cancels pending requests on shutdown', async () => {
  const h = workerContext({hostOwnsBlobUrls: true});
  const pending = h.evaluate('runtimeBlobUrl(new Blob(["wasm"]), "wasm")');
  const request = h.events.find(event => event.type === 'create_blob_url');
  assert.equal(h.created.length, 0);
  await h.sandbox.onmessage({data: {type: 'blob_url', id: request.id, url: 'blob:host/wasm'}});
  assert.equal(await pending, 'blob:host/wasm');
  const rejected = assert.rejects(h.evaluate('runtimeBlobUrl(new Blob(["script"]), "script")'), /disposed/);
  await h.sandbox.onmessage({data: {type: 'dispose', id: 10}});
  await rejected;
  assert.deepEqual(h.revoked, ['blob:host/wasm']);
});

test('cleanup still acknowledges when pthread hooks are unavailable or throw', async () => {
  for (const throwing of [false, true]) {
    const h = workerContext();
    if (throwing) h.sandbox.PThread = {terminateAllThreads() { throw new Error('unsupported shutdown'); }};
    await h.evaluate('runtimeBlobUrl(new Blob(["wasm"]), "wasm")');
    await h.sandbox.onmessage({data: {type: 'dispose', id: 11}});
    assert.equal(h.revoked.length, 1);
    const ack = h.events.find(event => event.type === 'disposed');
    assert.equal(ack.cleanup.threadShutdownRequested, false);
    if (throwing) assert.match(ack.cleanup.error, /unsupported shutdown/);
    assert.equal(h.events.at(-1), 'close');
  }
});

test('fatal compile invokes JS-only cleanup and still delivers its fatal result', async () => {
  const h = workerContext();
  h.sandbox.PThread = {terminateAllThreads() { h.events.push('threads'); }};
  h.sandbox.Module = {_lean_wasm_compile() { throw new WebAssembly.RuntimeError('fatal trap'); }};
  h.evaluate('moduleReady = true;mkLeanString = () => 0;');
  await h.sandbox.onmessage({data: {type: 'compile', id: 12, code: 'trap'}});
  assert.equal(h.events[0], 'threads');
  const result = h.events.find(event => event.type === 'result');
  assert.equal(result.id, 12);assert.equal(result.fatal, true);assert.equal(result.error, 'fatal trap');
});

test('allocation exhaustion reports resources separately from the missing-isolation gate', async () => {
  for (const isolated of [true, false]) {
    const attempts = [];
    const h = workerContext({memory: {mode: 'shared', initial: 1024, maximum: 65536}}, {
      SharedArrayBuffer: isolated ? SharedArrayBuffer : undefined,
      WebAssembly: {Memory: function (descriptor) { attempts.push(descriptor);throw new Error('SharedArrayBuffer reservation failed: engine cause'); }}
    });
    await h.evaluate('startLeanModule()');
    assert.equal(attempts.length, 4);
    assert.deepEqual(attempts.map(attempt => attempt.initial), [32768, 24576, 16384, 12288]);
    const message = h.events.find(event => event.type === 'error').data;
    if (isolated) {
      assert.match(message, /could not reserve enough memory.*Close other Lean workspaces/);
      assert.doesNotMatch(message, /SharedArrayBuffer|COOP|COEP|cross.origin|isolation|Cross-Origin/i);
      assert.ok(h.events.some(event => event.type === 'status' && event.data.includes('engine cause')));
    } else assert.match(message, /SharedArrayBuffer.*cross-origin isolated/);
  }
});
