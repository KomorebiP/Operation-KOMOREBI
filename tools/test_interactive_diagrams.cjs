const {test} = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const core = import(pathToFileURL(path.join(__dirname, '../website/assets/interactive-diagrams-core.mjs')));

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
