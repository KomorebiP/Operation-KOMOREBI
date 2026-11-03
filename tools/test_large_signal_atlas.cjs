'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const api = require('../website/assets/large-signal-atlas.js');

test('the source counterexample retains equal present observations and different next outputs', () => {
  const pair=api.compare(1,0);
  assert.deepEqual(pair.outputs.map(api.text),['0','0']);
  assert.deepEqual(pair.next.map(api.text),['0','1']);
  assert.equal(pair.histories,null);assert.equal(pair.delayed,null);
});

test('a causal delay state is withheld until the first observed step', () => {
  const pair=api.compare(1,1);
  assert.deepEqual(pair.histories.map(row=>row.map(api.text)),[['0','0'],['0','1']]);
  assert.deepEqual(pair.delayed.map(api.text),['0','5/6']);
  assert.deepEqual(pair.delayed,pair.next);
});

test('signed rational arithmetic normalizes exactly and coincident states stay coincident', () => {
  assert.equal(api.text(api.q(2,-4)),'-1/2');
  assert.equal(api.text(api.add(api.q(-1,3),api.q(1,2))),'1/6');
  assert.equal(api.text(api.mul(api.q(-2,3),api.q(3,4))),'-1/2');
  assert.throws(()=>api.q(1,0),RangeError);
  const pair=api.compare(0,8);assert.deepEqual(pair.outputs.map(api.text),['0','0']);
  assert.equal(pair.observed.length,9);assert.deepEqual(pair.delayed,pair.next);
});

test('the public teaching interface enforces its declared finite domain', () => {
  for(const [h,t] of [[-3,0],[3,0],[1.5,0],[1,-1],[1,9],[1,0.5],[NaN,0],[1,Infinity]]) {
    assert.throws(()=>api.compare(h,t),RangeError);
  }
  for(const t of [-1,13,1.5])assert.throws(()=>api.trace([api.q(0),api.q(0)],t),RangeError);
});

test('proposition queries distinguish P6 from P66 while topic queries remain flexible', () => {
  assert.equal(api.matches('P6','Closure P6 Proposition 6'),true);
  assert.equal(api.matches('P6','Confidence P66 Proposition 66'),false);
  assert.equal(api.matches('memory bound','Memory and error bounds'),true);
  assert.equal(api.matches('CLOSURE','Predictive closure'),true);
  assert.equal(api.matches('','Any plate'),true);
});
