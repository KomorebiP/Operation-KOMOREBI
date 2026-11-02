import test from 'node:test';
import assert from 'node:assert/strict';
globalThis.document={querySelector:()=>null};
const {moduleSource,outcome}=await import('../website/assets/lean-browser.js');

test('only a completed clean check receives the clean state',()=>{
  assert.equal(outcome({exitCode:0,errors:[]}),'passed');
  assert.equal(outcome({exitCode:0,errors:['warning: declaration uses sorry']}),'warning');
  assert.equal(outcome({exitCode:1,errors:[]}),'failed');
  assert.equal(outcome(undefined),'failed');
});
test('module export wrapper keeps the original proof body and names the real import',()=>{
  const original='import Mathlib.Data.Set.Function\n\nnamespace ProofPath\ntheorem t : True := by trivial\nend ProofPath\n';
  const wrapped=moduleSource(original,'ProofPath.Compression');
  assert.ok(wrapped.includes(original.slice(original.indexOf('\n')+1)));
  assert.ok(wrapped.includes('setMainModule `ProofPath.Compression'));
  assert.ok(wrapped.includes('/lib/lean/ProofPath/Compression.olean'));
  assert.throws(()=>moduleSource(original,'../bad'));
  assert.throws(()=>moduleSource('namespace Changed','ProofPath.Compression'));
});
