const {test} = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const core = import(pathToFileURL(path.join(__dirname, '../website/assets/interactive-diagrams-core.mjs')));
const links = import(pathToFileURL(path.join(__dirname, '../website/assets/interactive-diagrams-state.mjs')));

test('experiment links round-trip bounded settings without changing their calculations', async () => {
  const {encodeExperiment,decodeExperiment} = await links;
  const {reconstruct,refine,recover,haar} = await core;
  const examples = [
    [{v:1,name:'packets',matrix:[-9,0,7,9],vector:[-5,5],keep:[false,true,true,false]},
      s=>reconstruct(s.matrix,s.vector,s.keep)],
    [{v:1,name:'refinement',signal:[-8,8,0,1,-1,3,6,-7],count:8,keep:[true,false,false,true,true,false,true,false]},
      s=>refine(s.signal,s.count,s.keep)],
    [{v:1,name:'recovery',summary:-4,position:4,coefficients:[-3,3]},
      s=>recover(s.summary,s.position,s.coefficients)],
    [{v:1,name:'haar',signal:Array.from({length:16},(_,i)=>i===10 ? 16 : -16),mode:'custom',cutoff:3.25,
      keep:Array.from({length:16},(_,i)=>i===0 || i%3===0),coefficient:13,address:15},
      s=>haar(s.signal,s.keep)],
  ];
  for (const [state,calculate] of examples) {
    const encoded = encodeExperiment(state);
    assert.match(encoded,/^[A-Za-z0-9_-]+$/);
    assert.ok(encoded.length < 2048);
    const restored = decodeExperiment(encoded);
    assert.deepEqual(restored,state);
    assert.deepEqual(calculate(restored),calculate(state));
  }
  for (const mode of ['all','coarse','no-fine','mean','threshold']) {
    const state = {v:1,name:'haar',signal:Array(16).fill(0),mode,cutoff:.25,coefficient:null,address:0};
    assert.deepEqual(decodeExperiment(encodeExperiment(state)),state);
  }
});

test('malformed, incompatible and out-of-range experiment links are rejected', async () => {
  const {encodeExperiment,decodeExperiment} = await links;
  const signal = {v:1,name:'refinement',signal:Array(8).fill(1),count:4,keep:Array(4).fill(true)};
  const wavelet = {v:1,name:'haar',signal:Array(16).fill(0),mode:'custom',cutoff:0,keep:Array(16).fill(true),coefficient:0,address:15};
  const invalid = [
    null,[],{}, {...signal,v:2}, {...signal,name:'unknown'},
    {...signal,count:3}, {...signal,signal:[.5,...Array(7).fill(0)]},
    {...signal,keep:[true,true,true]}, {...signal,keep:[true,true,true,1]},
    {...signal,signal:Array(8)}, {...signal,signal:Array(8).fill(9)},
    {...wavelet,signal:Array(16).fill(17)}, {...wavelet,cutoff:.1}, {...wavelet,cutoff:17},
    {...wavelet,coefficient:-1}, {...wavelet,coefficient:16}, {...wavelet,address:-1},
    {...wavelet,address:16}, {...wavelet,mode:'unknown'}, {...wavelet,keep:Array(16).fill(false)},
    {...wavelet,mode:'all'},
    {v:1,name:'packets',matrix:[1,2,3,10],vector:[0,0],keep:Array(4).fill(true)},
    {v:1,name:'recovery',summary:0,position:0,coefficients:[0,4]},
  ];
  for (const state of invalid) {
    assert.throws(()=>encodeExperiment(state),RangeError);
    assert.throws(()=>decodeExperiment(btoa(JSON.stringify(state)).replace(/=+$/,'')),RangeError);
  }
  for (const value of ['',null,'A','not!base64','x'.repeat(2049),btoa('not JSON')]) {
    assert.throws(()=>decodeExperiment(value),RangeError);
  }
});

test('decoded links copy known fields into fresh settings objects', async () => {
  const {encodeExperiment,decodeExperiment} = await links;
  const source = {v:1,name:'packets',matrix:[1,2,3,4],vector:[0,0],keep:Array(4).fill(true),unused:'discard me'};
  const restored = decodeExperiment(encodeExperiment(source));
  assert.equal(Object.hasOwn(restored,'unused'),false);
  restored.matrix[0] = 9;
  assert.equal(source.matrix[0],1);
  const incoming = btoa('{"v":1,"name":"recovery","summary":0,"position":0,"coefficients":[1,1],"__proto__":{"polluted":true}}').replace(/=+$/,'');
  assert.equal(Object.hasOwn(decodeExperiment(incoming),'__proto__'),false);
  assert.equal({}.polluted,undefined);
});

test('published examples agree with the standalone exact teaching program', async () => {
  const {reconstruct, refine, recover} = await core;
  const blocks = reconstruct([1,2,3,4], [2,3], [true,true,true,false]);
  assert.deepEqual(blocks.direct, [8,18]);
  assert.deepEqual(blocks.rebuilt, [8,6]);
  assert.deepEqual(blocks.residual, [0,12]);
  const signal = refine([1,2,3,4,5,6,7,8], 4, [true,true,false,true]);
  assert.deepEqual(signal.rebuilt, [1,2,0,4,5,6,0,8]);
  assert.equal(signal.energy, 58);
  const collision = recover(1, 1, [1,0]);
  assert.deepEqual(collision.u, [1,0]);
  assert.deepEqual(collision.v, [0,1]);
  assert.deepEqual(collision.answers, [1,0]);
});

test('all block masks preserve direct = rebuilt + residual, including cancellation', async () => {
  const {reconstruct} = await core;
  for (let seed = 0; seed < 91; seed++) {
    const matrix = [seed%19-9, (seed*3)%19-9, (seed*7)%19-9, (seed*11)%19-9];
    const x = [seed%11-5, (seed*7)%11-5];
    const expected = [matrix[0]*x[0]+matrix[1]*x[1], matrix[2]*x[0]+matrix[3]*x[1]].map(v => v || 0);
    for (let bits = 0; bits < 16; bits++) {
      const result = reconstruct(matrix, x, Array.from({length:4}, (_, i) => Boolean(bits & (1 << i))));
      assert.deepEqual(result.direct, expected);
      assert.deepEqual(result.rebuilt.map((v,i) => v+result.residual[i]), expected);
      if (bits === 15) assert.deepEqual(result.rebuilt, expected);
      if (bits === 0) assert.deepEqual(result.rebuilt, [0,0]);
    }
  }
  assert.deepEqual(reconstruct([1,-1,0,0], [1,1], [false,false,true,true]).residual, [0,0]);
});

test('address refinement preserves samples and disjoint packet energies add', async () => {
  const {refine} = await core;
  for (const count of [2,4,8]) {
    for (let seed = 0; seed < 17; seed++) {
      const x = Array.from({length:8}, (_, i) => (seed*(i+1)+i)%17-8);
      const all = refine(x, count, Array(count).fill(true));
      const roundTrip = [];
      all.packets.flat().forEach(({index,value}) => { roundTrip[index] = value; });
      assert.deepEqual(roundTrip, x);
      assert.deepEqual(all.rebuilt, x);
      assert.equal(all.energy, 0);
      for (let mask = 0; mask < 1 << count; mask++) {
        const keep = Array.from({length:count}, (_, i) => Boolean(mask & (1 << i)));
        const result = refine(x, count, keep);
        assert.deepEqual(result.rebuilt.map((v,i) => v+result.residual[i]), x);
        const squaredNorm = values => values.reduce((sum, v) => sum+v*v, 0);
        assert.equal(squaredNorm(result.rebuilt)+result.energy, squaredNorm(x));
      }
    }
  }
  assert.equal(refine(Array(8).fill(0), 4, [false,false,false,false]).energy, 0);
});

test('every incompatible question has a collision; compatible questions factor through the sum', async () => {
  const {recover} = await core;
  for (let a = -3; a <= 3; a++) for (let b = -3; b <= 3; b++) {
    for (let s = -4; s <= 4; s++) for (let t = -4; t <= 4; t++) {
      const r = recover(s,t,[a,b]);
      assert.equal(r.u[0]+r.u[1], s);
      assert.equal(r.v[0]+r.v[1], s);
      assert.equal(r.answers[0]-r.answers[1], a-b);
      assert.equal(r.compatible, r.answers[0] === r.answers[1]);
      if (r.compatible) assert.equal(r.answers[0], a*s || 0);
      assert.ok([...r.u,...r.v].every(v => Math.abs(v) <= 10));
    }
  }
});

test('unbounded, fractional and malformed model inputs are rejected', async () => {
  const {reconstruct, refine, recover} = await core;
  for (const bad of [NaN, Infinity, 0.5, 10]) {
    assert.throws(() => reconstruct([bad,2,3,4], [2,3], [true,true,true,true]), RangeError);
  }
  assert.throws(() => refine(Array(8).fill(1), 3, [true,true,true]), RangeError);
  assert.throws(() => refine(Array(8).fill(1), 4, [true]), RangeError);
  assert.throws(() => recover(5,0,[1,0]), RangeError);
  assert.throws(() => recover(1,0,[1]), RangeError);
});

const haarExample = [2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4];

test('the four-level example reproduces every published coefficient and selection', async () => {
  const {haarAnalyze, haar} = await core;
  const analysis = haarAnalyze(haarExample);
  assert.deepEqual(analysis.levels.map(level => level.averages),
    [[2,2,6,6,-4,4,4,4],[2,6,0,4],[4,2],[3]]);
  assert.deepEqual(analysis.levels.map(level => level.details),
    [[0,0,0,0,0,8,0,0],[0,0,-4,0],[-2,-2],[1]]);
  const policies = [
    ['all', () => true, 16, 0],
    ['nonzero', c => Math.abs(c.value) >= .25, 6, 0],
    ['drop finest', c => c.level >= 2, 8, 128],
    ['coarse', c => c.level >= 3, 4, 192],
    ['cutoff four', c => Math.abs(c.value) >= 4, 3, 80],
    ['mean', () => false, 1, 272],
  ];
  for (const [name, policy, count, error] of policies) {
    const keep = analysis.coefficients.map((c,i) => i === 0 || policy(c));
    const result = haar(haarExample, keep);
    assert.equal(result.energy, 416, name);
    assert.equal(result.retained, count, name);
    assert.equal(result.residualEnergy, error, name);
  }
  const fine = haar(haarExample, analysis.coefficients.map((c,i) => i === 0 || c.level >= 2));
  assert.deepEqual(fine.rebuilt, [2,2,2,2,6,6,6,6,-4,-4,4,4,4,4,4,4]);
  const fourSampleRepeated = Array(4).fill([2,6,10,14]).flat();
  assert.equal(haar(fourSampleRepeated, Array(16).fill(true)).energy, 4*336);
});

test('every detail mask preserves exact weighted energy and the reconstruction identity', async () => {
  const {haar} = await core;
  for (let mask = 0; mask < 1 << 15; mask++) {
    const keep = Array.from({length:16}, (_, i) => i === 0 || Boolean(mask & (1 << (i-1))));
    const result = haar(haarExample, keep);
    assert.equal(result.energy, result.rebuiltEnergy + result.residualEnergy);
    assert.equal(result.keptEnergy, result.rebuiltEnergy);
    assert.equal(result.discardedEnergy, result.residualEnergy);
    assert.deepEqual(result.rebuilt.map((value,i) => value+result.residual[i]), haarExample);
  }
});

test('recursive Haar analysis and synthesis agree with independent support-vector dot products', async () => {
  const {haarAnalyze, haar} = await core;
  for (let seed = 0; seed < 67; seed++) {
    const signal = Array.from({length:16}, (_, i) => (seed*(i+1)+i*i)%33-16);
    const analysis = haarAnalyze(signal);
    const basis = analysis.coefficients.map(c => signal.map((_,i) =>
      c.kind === 'average' ? 1 : i < c.start || i > c.end ? 0 : i < (c.start+c.end+1)/2 ? 1 : -1));
    const dot = (a,b) => a.reduce((sum,v,i) => sum+v*b[i], 0);
    const coordinates = basis.map(vector => dot(signal,vector)/dot(vector,vector));
    assert.deepEqual(analysis.coefficients.map(c => c.value), coordinates.map(v => v || 0));
    for (let sample = 0; sample < 64; sample++) {
      const keep = Array.from({length:16}, (_, i) => Boolean(((sample+seed*61)*7919) & (1 << i)));
      const result = haar(signal, keep);
      const reference = signal.map((_,i) => coordinates.reduce((sum,c,j) => sum+(keep[j] ? c*basis[j][i] : 0),0));
      assert.deepEqual(result.rebuilt, reference.map(v => v || 0));
    }
    assert.deepEqual(haar(signal, Array(16).fill(true)).rebuilt, signal);
    assert.deepEqual(haar(signal, Array(16).fill(false)).rebuilt, Array(16).fill(0));
  }
});

test('Haar fractions remain exact at small details and bounded inputs are enforced', async () => {
  const {haarAnalyze, haar} = await core;
  const impulse = Array.from({length:16}, (_,i) => i === 0 ? 1 : 0);
  const analysis = haarAnalyze(impulse);
  assert.equal(analysis.coefficients[0].value, 1/16);
  assert.equal(analysis.coefficients[1].value, 1/16);
  const mean = haar(impulse, Array.from({length:16}, (_,i) => i === 0));
  assert.equal(mean.rebuiltEnergy, 1/16);
  assert.equal(mean.residualEnergy, 15/16);
  assert.throws(() => haarAnalyze(Array(15).fill(0)), RangeError);
  assert.throws(() => haarAnalyze([.5,...Array(15).fill(0)]), RangeError);
  assert.throws(() => haarAnalyze([17,...Array(15).fill(0)]), RangeError);
  assert.throws(() => haar(impulse, Array(15).fill(true)), RangeError);
});
