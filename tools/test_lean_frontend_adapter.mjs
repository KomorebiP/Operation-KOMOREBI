import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {createCompiler} from '../website/assets/lean-wasm/compiler.js';

// Exercise the real compiler/runtime protocol without booting the large Wasm artifact.
// These tests establish adapter behavior, not Lean elaboration correctness.
const defaultSource = 'import Mathlib.Data.Nat.Basic\nexample : True := by trivial\n';

function frontendProtocol(code) {
  const started = code.match(/__KOMOREBI_FRONTEND_STARTED_([0-9a-f]{32})__/);
  assert.ok(started, 'the one compilation must contain a fresh frontend started marker');
  const nonce = started[1];
  const completed = `__KOMOREBI_FRONTEND_COMPLETED_${nonce}__`;
  const fileName = `<komorebi-frontend-${nonce}>`;
  assert.ok(code.includes(completed), 'the transport must contain its matching completion marker');
  assert.ok(code.includes(fileName), 'embedded diagnostics need an invocation-specific filename');
  return {started: started[0], completed, fileName};
}

function information(data, fileName = '<input>') {
  return {severity: 'information', data, fileName};
}

function complete(protocol, messages = []) {
  return {success: true, messages: [information(protocol.started), ...messages, information(protocol.completed)]};
}

async function withCompiler(compileResult, check, options = {}) {
  const descriptors = new Map(['Worker', 'fetch', 'crypto'].map(name => [name, Object.getOwnPropertyDescriptor(globalThis, name)]));
  const harness = {events: [], compiles: [], terminations: 0, failures: []};
  let compiler;
  const install = (name, value) => Object.defineProperty(globalThis, name, {value, writable: true, configurable: true});
  install('crypto', webcrypto);
  install('fetch', async () => new Response('', {status: 404}));
  install('Worker', class FakeWorker {
    postMessage(message) {
      harness.events.push(message);
      queueMicrotask(() => {
        const send = data => this.onmessage?.({data});
        try {
          if (message.type === 'start') send({type: 'ready'});
          if (message.type === 'load_modules') {
            send({type: 'modules_loaded', id: message.id,
              results: message.roots.map(root => ({root, files: 1}))});
          }
          if (message.type === 'load_layer') {
            send({type: 'layer_loaded', id: message.id, label: message.label, ok: true, files: 1});
          }
          if (message.type === 'compile') {
            harness.compiles.push(message);
            assert.equal(harness.compiles.length, 1, 'frontend mode must never replay source');
            const protocol = frontendProtocol(message.code);
            const result = compileResult(protocol, message.code);
            for (const diagnostic of result.messages ?? []) {
              send({type: 'stdout', data: JSON.stringify(diagnostic)});
            }
            for (const line of result.stdout ?? []) send({type: 'stdout', data: line});
            for (const line of result.stderr ?? []) send({type: 'stderr', data: line});
            send({type: 'result', id: message.id, success: result.success,
              error: result.error, fatal: result.fatal});
          }
        } catch (error) {
          harness.failures.push(error);
          send({type: 'error', data: error.message});
        }
      });
    }
    terminate() { harness.terminations++; }
  });
  try {
    compiler = await createCompiler({baseUrl: 'https://example.invalid/engine/',
      syntaxCheck: 'frontend', mathlibManifest: 'workspaces/narrow-proof.json', ...options});
    await check(compiler, harness);
    assert.deepEqual(harness.failures, [], 'the fake worker must finish each protocol exchange');
  } finally {
    compiler?.dispose();
    for (const [name, descriptor] of descriptors) {
      if (descriptor) Object.defineProperty(globalThis, name, descriptor);
      else delete globalThis[name];
    }
  }
}

test('frontend preloads the full library and standard roots before exactly one compile', async () => {
  await withCompiler(protocol => complete(protocol, [information('user output')]), async (compiler, harness) => {
    const result = await compiler.run(defaultSource);
    assert.equal(result.exitCode, 0);
    assert.deepEqual(result.errors, []);
    assert.deepEqual(result.diagnostics, []);
    assert.equal(result.output, 'user output');
    assert.equal(harness.compiles.length, 1);
    const layers = harness.events.filter(event => event.type === 'load_layer');
    assert.equal(layers.length, 1);
    assert.equal(layers[0].manifestUrl, 'https://example.invalid/engine/lean-mathlib/real-analysis-layer.json');
    assert.equal(layers[0].packBase, 'https://example.invalid/engine/lean-mathlib');
    assert.ok(!layers.some(event => event.manifestUrl.includes('/workspaces/')));
    const compileIndex = harness.events.findIndex(event => event.type === 'compile');
    const before = harness.events.slice(0, compileIndex);
    const roots = new Set(before.filter(event => event.type === 'load_modules').flatMap(event => event.roots));
    for (const root of ['Std', 'Lean', 'Batteries']) assert.ok(roots.has(root), `${root} must load before execution`);
    assert.ok(before.some(event => event === layers[0]));
    assert.ok(!harness.events.slice(compileIndex + 1).some(event => event.type.startsWith('load_')));
  });
});

test('captured import traces are removed while multiline user output and spacing survive', async () => {
  const output = [
    '[DEBUG:PROGRESS] Loading 1112 modules...',
    'ordinary output α',
    '[DEBUG:PROGRESS] 1112/1112: Std',
    '  indented user output  ',
    '',
    'user mentions [DEBUG:PROGRESS] literally',
    'mainModule? = anonymous',
    '- /lib/lean/Std.olean',
    'last output'
  ].join('\n');
  await withCompiler(protocol => complete(protocol, [
    information(output), information('[DEBUG:PROGRESS] trailing import trace')
  ]), async compiler => {
    const result = await compiler.run(defaultSource);
    assert.equal(result.exitCode, 0);
    assert.deepEqual(result.errors, []);
    assert.equal(result.output, 'ordinary output α\n  indented user output  \n\nuser mentions [DEBUG:PROGRESS] literally\nlast output');
  });
});

test('noise cleanup cannot manufacture an exact completion marker from a mixed message', async () => {
  await withCompiler(protocol => ({success: true, messages: [
    information(protocol.started), information('[DEBUG:PROGRESS] import finished\n' + protocol.completed)
  ]}), async (compiler, harness) => {
    await assert.rejects(compiler.run(defaultSource), /complet/i);
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1);
  });
});

test('missing imports after the started marker never cause a second execution', async () => {
  await withCompiler(protocol => ({success: true, messages: [information(protocol.started),
    {severity: 'error', fileName: protocol.fileName, data: "unknown module prefix 'Mathlib'", pos: {line: 3, column: 2}},
    {severity: 'error', fileName: protocol.fileName,
      data: "object file '/lib/lean/Mathlib/Extra.olean' of module Mathlib.Extra does not exist"}]}),
  async (compiler, harness) => {
    await assert.rejects(compiler.run(defaultSource), /complet/i);
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1, 'an incomplete frontend must dispose the worker immediately');
    assert.equal(harness.events.filter(event => event.type === 'load_layer').length, 1);
  });
});

test('missing imports before the started marker are also never retried', async () => {
  await withCompiler(() => ({success: true, messages: [
    {severity: 'error', data: "unknown module prefix 'Mathlib'", fileName: '<input>'}
  ]}), async (compiler, harness) => {
    await assert.rejects(compiler.run('import Std\nexample : True := by trivial\n'), /complet/i);
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1);
    const compileIndex = harness.events.findIndex(event => event.type === 'compile');
    assert.ok(!harness.events.slice(compileIndex + 1).some(event => event.type.startsWith('load_')),
      'even a previously unloaded, fetchable root must not trigger adaptive loading after execution');
  });
});

test('marker prefixes, embedded marker text, and another nonce do not establish completion', async () => {
  for (const spoof of [
    protocol => protocol.completed + ':started',
    protocol => 'printed text ' + protocol.completed,
    protocol => protocol.completed + '\nextra output',
    protocol => protocol.completed.replace(/_([0-9a-f])([0-9a-f]{31})__$/,
      (_, first, rest) => '_' + (first === '0' ? '1' : '0') + rest + '__')
  ]) {
    await withCompiler(protocol => ({success: true, messages: [information(protocol.started), information(spoof(protocol))]}),
    async (compiler, harness) => {
      await assert.rejects(compiler.run(defaultSource), /complet/i);
      assert.equal(harness.compiles.length, 1);
      assert.equal(harness.terminations, 1);
    });
  }
});

test('plain printed marker text cannot impersonate an informational completion message', async () => {
  await withCompiler(protocol => ({success: true, messages: [information(protocol.started)], stdout: [protocol.completed]}),
  async (compiler, harness) => {
    await assert.rejects(compiler.run(defaultSource), /complet/i);
    assert.equal(harness.terminations, 1);
  });
});

test('exit zero without a completed marker fails closed and disposes the worker', async () => {
  await withCompiler(protocol => ({success: true, messages: [information(protocol.started)]}), async (compiler, harness) => {
    await assert.rejects(compiler.run('import Lean\nrun_cmd IO.Process.exit 0\n'), /complet/i);
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1);
  });
});

test('embedded diagnostics preserve source coordinates and distinguish transport errors', async () => {
  await withCompiler(protocol => complete(protocol, [
    {severity: 'error', data: 'unexpected token at α', fileName: protocol.fileName, pos: {line: 7, column: 13}},
    {severity: 'error', data: 'transport elaboration failed', fileName: '<input>', pos: {line: 49, column: 4}}
  ]), async compiler => {
    const result = await compiler.run(defaultSource);
    assert.equal(result.exitCode, 1);
    assert.deepEqual(result.errors, [
      'error: unexpected token at α  (line 7, col 13)',
      'error: transport elaboration failed  (line 49, col 4)'
    ]);
    assert.deepEqual(result.diagnostics, [
      {text: result.errors[0], origin: 'compiled-source'},
      {text: result.errors[1], origin: 'frontend-guard'}
    ]);
    assert.equal(result.output, '');
  });
});

test('incomplete checks label outer transport errors without relabeling embedded diagnostics', async () => {
  await withCompiler(protocol => ({success: true, messages: [information(protocol.started),
    {severity: 'error', data: 'source parser failure', fileName: protocol.fileName, pos: {line: 2, column: 6}},
    {severity: 'error', data: 'guard transport failure', fileName: '<input>', pos: {line: 49, column: 4}}
  ]}), async (compiler, harness) => {
    await assert.rejects(compiler.run(defaultSource), error => {
      const lines = error.message.split('\n');
      assert.ok(lines.includes('error: source parser failure  (line 2, col 6)'));
      assert.ok(lines.includes('Browser frontend check: error: guard transport failure  (line 49, col 4)'));
      assert.match(error.message, /complet/i);
      return true;
    });
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1);
  });
});

test('warnings survive completion while a real error prevents a clean result', async () => {
  for (const severity of ['warning', 'error']) {
    await withCompiler(protocol => complete(protocol, [
      {severity, data: severity === 'warning' ? 'declaration uses sorry' : 'type mismatch',
        fileName: protocol.fileName, pos: {line: 2, column: 0}}
    ]), async compiler => {
      const result = await compiler.run(defaultSource);
      assert.equal(result.exitCode, severity === 'error' ? 1 : 0);
      assert.equal(result.errors.length, 1);
      assert.ok(result.errors[0].startsWith(severity + ':'));
      assert.equal(result.diagnostics[0].origin, 'compiled-source');
      assert.equal(result.output, '');
    });
  }
});

test('an exact completion marker cannot rescue an unsuccessful runtime result', async () => {
  await withCompiler(protocol => ({...complete(protocol), success: false, error: 'native worker stopped'}),
  async (compiler, harness) => {
    await assert.rejects(compiler.run(defaultSource), /native worker stopped/);
    assert.equal(harness.compiles.length, 1);
    assert.equal(harness.terminations, 1);
  });
});

test('original source controls are rejected before encoding or execution', async () => {
  for (const control of ['\u0000', '\u000b', '\u2028', '\u2029']) {
    await withCompiler(protocol => complete(protocol), async (compiler, harness) => {
      await assert.rejects(compiler.run('import Std\nexample' + control + ': True := by trivial'), /unsupported control characters/i);
      assert.equal(harness.compiles.length, 0);
    });
  }
});

test('dependency module identity reaches the inner initial environment', async () => {
  await withCompiler((protocol, code) => {
    assert.match(code, /let env := importedEnv\.setMainModule `Demo\.Dependency/);
    return complete(protocol);
  }, async (compiler, harness) => {
    const result = await compiler.run('import Std\ndef value : Nat := 7\n', undefined, {mainModule: 'Demo.Dependency'});
    assert.equal(result.exitCode, 0);
    assert.equal(harness.compiles.length, 1);
  });
});

test('a per-run frontend override also ignores the prepared workspace manifest', async () => {
  await withCompiler(protocol => complete(protocol), async (compiler, harness) => {
    const result = await compiler.run(defaultSource, undefined, {syntaxCheck: 'frontend'});
    assert.equal(result.exitCode, 0);
    assert.equal(harness.compiles.length, 1);
    const layers = harness.events.filter(event => event.type === 'load_layer');
    assert.equal(layers.length, 1);
    assert.ok(layers[0].manifestUrl.endsWith('/real-analysis-layer.json'));
    assert.ok(!layers[0].manifestUrl.includes('/workspaces/'));
  }, {syntaxCheck: 'full'});
});
