// Finite teaching models. Bounded integer inputs keep every operation exact.
function integers(values, length, bound) {
  if (!Array.isArray(values) || values.length !== length ||
      values.some(value => !Number.isInteger(value) || Math.abs(value) > bound)) {
    throw new RangeError('Invalid bounded integer input');
  }
}

export function reconstruct(matrix, vector, keep) {
  integers(matrix, 4, 9);
  integers(vector, 2, 5);
  if (!Array.isArray(keep) || keep.length !== 4 || keep.some(v => typeof v !== 'boolean')) {
    throw new RangeError('Choose four blocks');
  }
  const contributions = matrix.map((value, i) => value * vector[i % 2] || 0);
  const direct = [contributions[0] + contributions[1], contributions[2] + contributions[3]];
  const rebuilt = [0, 0];
  contributions.forEach((value, i) => { if (keep[i]) rebuilt[Math.floor(i / 2)] += value; });
  return {contributions, direct, rebuilt, residual: direct.map((v, i) => v - rebuilt[i])};
}

export function refine(signal, count, keep) {
  integers(signal, 8, 8);
  if (![2, 4, 8].includes(count) || !Array.isArray(keep) || keep.length !== count ||
      keep.some(v => typeof v !== 'boolean')) throw new RangeError('Invalid packet selection');
  const packets = Array.from({length: count}, () => []);
  signal.forEach((value, index) => packets[index % count].push({index, value}));
  const rebuilt = signal.map((value, index) => keep[index % count] ? value : 0);
  const residual = signal.map((value, index) => value - rebuilt[index]);
  return {packets, rebuilt, residual, energy: residual.reduce((sum, v) => sum + v * v, 0)};
}

export function recover(summary, position, coefficients) {
  integers([summary, position], 2, 4);
  integers(coefficients, 2, 3);
  const [a, b] = coefficients;
  const u = [position, summary - position];
  const v = [position - 1, summary - position + 1];
  const answers = [u, v].map(([x, y]) => a * x + b * y || 0);
  return {u, v, answers, difference: a - b, compatible: a === b, recovered: a * summary || 0};
}
