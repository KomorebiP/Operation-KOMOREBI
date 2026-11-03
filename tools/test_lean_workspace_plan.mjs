import test from 'node:test';
import assert from 'node:assert/strict';
import {planSelectedFile} from '../website/assets/lean-workspace-plan.js';

function workspace(modules, extra = {}) {
  return {files: modules.map(module => typeof module === 'string' ? {module} : module), ...extra};
}

test('a selected target omits unrelated malformed and missing-import sources', () => {
  const work = workspace(['Unused', 'Chosen', 'Missing']);
  const sources = ['import "unsupported"\n', 'example : True := by trivial\n', 'import Absent.Project\n'];
  assert.deepEqual(planSelectedFile(work, sources, 1), [1]);
});

test('diamond ancestors execute once and ready nodes follow original registry order', () => {
  const work = workspace(['Target', 'Right', 'Shared', 'Left', 'Unrelated']);
  const sources = ['import Left Right\nexample : True := by trivial', 'import Shared\n', 'import Std\n', 'import Shared\n', 'import Absent\n'];
  assert.deepEqual(planSelectedFile(work, sources, 0), [2, 1, 3, 0]);
});

test('edited forward imports select new ancestors and drop removed dependencies', () => {
  const work = workspace(['Target', 'Old', 'New', 'Leaf']);
  const sources = ['import New\n', 'import Missing\n', 'import Leaf\n', 'def value : Nat := 1'];
  assert.deepEqual(planSelectedFile(work, sources, 0), [3, 2, 0]);
  sources[0] = 'example : True := by trivial';
  assert.deepEqual(planSelectedFile(work, sources, 0), [0]);
});

test('module, prelude and supported import flags preserve exact project edges', () => {
  const work = workspace(['Target', 'A', 'B', 'C', 'D', 'E']);
  const sources = ['module\nprelude\npublic import A\nprivate import B\nmeta import C\npublic meta import all D E\nexample : True := by trivial',
    '', '', '', '', ''];
  assert.deepEqual(planSelectedFile(work, sources, 0), [1, 2, 3, 4, 5, 0]);
});

test('Unicode names, nested comments, BOM and CRLF retain routing and source identity', () => {
  const work = workspace(['Main', 'Δ.基础', "Lemma'", 'Ignored']);
  const sources = ['\uFEFF/- 🌿 import Ignored /- nested -/ -/\r\nmodule\r\npublic /- flags -/ import Δ.基础 Lemma\' -- import Ignored\r\nexample : True := by trivial\r\n',
    'import Std\n', '', 'import Missing\n'];
  const before = sources.slice();
  assert.deepEqual(planSelectedFile(work, sources, 0), [1, 2, 0]);
  assert.deepEqual(sources, before);
});

test('commented and string-masked import lines in bodies do not become dependencies', () => {
  const work = workspace(['Target', 'Real', 'Fake']);
  const sources = ['import Real\n-- import Fake\ndef text := "import Fake"\ndef lines := "first\nimport Fake\nlast"\n', '', 'import Missing\n'];
  assert.deepEqual(planSelectedFile(work, sources, 0), [1, 0]);
});

test('ordinary multiline body commands remain outside the header', () => {
  const work = workspace(['Target']);
  for (const command of ['section\nexample : True := by trivial\nend', 'initialize\n  pure ()',
    'universe\n  u', 'open\n  Nat']) {
    assert.deepEqual(planSelectedFile(work, ['import Std\n' + command], 0), [0]);
  }
});

test('known binary roots are allowed, while exact generated tactic modules take precedence', () => {
  const work = workspace(['Target', {module: 'Mathlib.Tactic', generated: true}, 'Helper']);
  const sources = ['import Mathlib.Tactic Std Lean Batteries Aesop Qq Plausible ProofWidgets ImportGraph LeanSearchClient Game Init\n',
    'import Helper\n', 'example : True := by trivial'];
  assert.deepEqual(planSelectedFile(work, sources, 0), [2, 1, 0]);
  sources[0] = 'import Mathlib.Tactic.Ring\n';
  assert.deepEqual(planSelectedFile(work, sources, 0), [0]);
});

test('legacy compatibility is an implicit edge only for retained source files', () => {
  const work = workspace(['Target', {module: 'Compat.Version', generated: true},
    {module: 'Library', library: true}, {module: 'OtherGenerated', generated: true}], {legacy: 'Compat.Version'});
  const sources = ['example : True := by trivial', 'import Std\n', '', ''];
  assert.deepEqual(planSelectedFile(work, sources, 0), [1, 0]);
  assert.deepEqual(planSelectedFile(work, sources, 1), [1]);
  assert.deepEqual(planSelectedFile(work, sources, 2), [2]);
  assert.deepEqual(planSelectedFile(work, sources, 3), [3]);
  assert.throws(() => planSelectedFile(workspace(['Target'], {legacy: 'Compat.Version'}), [''], 0), /Missing generated compatibility/);
  assert.throws(() => planSelectedFile(workspace(['Target', 'Compat.Version'], {legacy: 'Compat.Version'}), ['', ''], 0), /Missing generated compatibility/);
});

test('missing project imports and duplicate module identities reject before execution', () => {
  assert.throws(() => planSelectedFile(workspace(['Target']), ['import Absent.Local\n'], 0), /Missing project import Absent.Local requested by Target/);
  assert.throws(() => planSelectedFile(workspace(['Target', 'Unused', 'Unused']), ['', '', ''], 0), /Duplicate workspace module/);
});

test('reachable cycles and self imports reject, unrelated cycles stay outside the plan', () => {
  const work = workspace(['Target', 'A', 'B']);
  assert.throws(() => planSelectedFile(work, ['import A\n', 'import B\n', 'import A\n'], 0), /Project import cycle/);
  assert.throws(() => planSelectedFile(work, ['import Target\n', '', ''], 0), /Project import cycle/);
  assert.deepEqual(planSelectedFile(work, ['', 'import B\n', 'import A\n'], 0), [0]);
});

test('repeated imports are one edge, with shared ancestors included only once', () => {
  const work = workspace(['Target', 'Helper']);
  assert.deepEqual(planSelectedFile(work, ['import Helper Helper\nmeta import Helper\n', ''], 0), [1, 0]);
});

test('unsupported or ambiguous reachable headers fail closed', () => {
  const work = workspace(['Target', 'A']);
  for (const source of ['import\nA\n', 'import A; import A\n', 'import A as Alias\n',
    'import «A»\n', 'import A "hidden"\n', '"hidden"\nimport A\n', 'module Name\n',
    'module\nmodule\n', 'prelude\nprelude\n', 'import A\nprelude\n', 'import A\n  A\n',
    'public public import A\n', 'public private import A\n', 'public\nimport A\n',
    'all import A\n', 'protected import A\n', 'import all\n', 'import A all\n',
    'example : True := by trivial\nimport A\n', 'import A /- unfinished']) {
    assert.throws(() => planSelectedFile(work, [source, ''], 0), /unsupported or ambiguous import header/, source);
  }
});

test('invalid selection metadata is rejected without modifying workspace files', () => {
  const work = workspace(['Target']);
  for (const target of [-1, 1, 0.5, '0', null]) assert.throws(() => planSelectedFile(work, [''], target), /Invalid selected workspace file/);
  assert.throws(() => planSelectedFile(work, [], 0), /Invalid selected workspace file/);
  assert.throws(() => planSelectedFile(workspace(['../Bad']), [''], 0), /Invalid workspace module name/);
  assert.throws(() => planSelectedFile(work, [null], 0), /Missing edited source/);
  assert.deepEqual(work, workspace(['Target']));
});
