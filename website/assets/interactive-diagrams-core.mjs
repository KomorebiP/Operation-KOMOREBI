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

export function haarAnalyze(signal) {
  integers(signal, 16, 16);
  let averages = signal.slice();
  const levels = [];
  for (let level = 1; level <= 4; level++) {
    const next = [], details = [];
    for (let i = 0; i < averages.length; i += 2) {
      next.push((averages[i] + averages[i+1]) / 2);
      details.push((averages[i] - averages[i+1]) / 2);
    }
    levels.push({level, averages: next, details});
    averages = next;
  }
  // A coefficient at level j has squared synthesis-vector norm 2^j.
  const coefficients = [{id: 'mean', level: 4, index: 0, start: 0, end: 15,
    value: averages[0], weight: 16, kind: 'average'}];
  for (const {level, details} of levels.slice().reverse()) {
    details.forEach((value, index) => coefficients.push({id: `detail-${level}-${index}`,
      level, index, start: index * 2**level, end: (index+1) * 2**level-1,
      value, weight: 2**level, kind: 'detail'}));
  }
  return {levels, coefficients};
}

export function haar(signal, keep) {
  const analysis = haarAnalyze(signal);
  if (!Array.isArray(keep) || keep.length !== 16 || keep.some(v => typeof v !== 'boolean')) {
    throw new RangeError('Choose sixteen Haar coefficients');
  }
  let rebuilt = [keep[0] ? analysis.coefficients[0].value : 0];
  let offset = 1;
  for (let level = 4; level >= 1; level--) {
    const next = [];
    for (const average of rebuilt) {
      const detail = keep[offset] ? analysis.coefficients[offset].value : 0;
      next.push(average + detail, average - detail);
      offset++;
    }
    rebuilt = next;
  }
  const residual = signal.map((value, index) => value - rebuilt[index]);
  const squaredNorm = values => values.reduce((sum, value) => sum + value*value, 0);
  const weighted = selected => analysis.coefficients.reduce((sum, coefficient, i) =>
    sum + (keep[i] === selected ? coefficient.weight * coefficient.value**2 : 0), 0);
  return {...analysis, rebuilt, residual, energy: squaredNorm(signal),
    rebuiltEnergy: squaredNorm(rebuilt), residualEnergy: squaredNorm(residual),
    keptEnergy: weighted(true), discardedEnergy: weighted(false),
    retained: keep.filter(Boolean).length};
}
