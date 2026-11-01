// Versioned, bounded settings for links to the finite teaching experiments.
const fail = () => { throw new RangeError('Invalid experiment settings'); };
function integer(value, bound) {
  if (!Number.isInteger(value) || Math.abs(value) > bound) fail();
  return value || 0;
}
function list(value, length, accept) {
  if (!Array.isArray(value) || value.length !== length) fail();
  return Array.from(value, accept);
}
const integers = (value, length, bound) => list(value, length, item => integer(item, bound));
const flags = (value, length) => list(value, length, item => {
  if (typeof item !== 'boolean') fail();
  return item;
});
function settings(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || value.v !== 1) fail();
  const result = {v:1, name:value.name};
  if (value.name === 'packets') {
    return {...result, matrix:integers(value.matrix,4,9), vector:integers(value.vector,2,5), keep:flags(value.keep,4)};
  }
  if (value.name === 'refinement') {
    if (![2,4,8].includes(value.count)) fail();
    return {...result, signal:integers(value.signal,8,8), count:value.count, keep:flags(value.keep,value.count)};
  }
  if (value.name === 'recovery') {
    return {...result, summary:integer(value.summary,4), position:integer(value.position,4), coefficients:integers(value.coefficients,2,3)};
  }
  if (value.name === 'haar') {
    if (!['all','coarse','no-fine','mean','threshold','custom'].includes(value.mode)) fail();
    if (!Number.isFinite(value.cutoff) || value.cutoff < 0 || value.cutoff > 16 || !Number.isInteger(value.cutoff*4)) fail();
    if (value.coefficient !== null && (integer(value.coefficient,15) < 0)) fail();
    if (integer(value.address,15) < 0) fail();
    const haar = {...result, signal:integers(value.signal,16,16), mode:value.mode,
      cutoff:value.cutoff, coefficient:value.coefficient, address:value.address};
    if (value.mode === 'custom') {
      haar.keep = flags(value.keep,16);
      if (!haar.keep[0]) fail();
    } else if (Object.hasOwn(value,'keep')) fail();
    return haar;
  }
  fail();
}

export function encodeExperiment(value) {
  return btoa(JSON.stringify(settings(value))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}

export function decodeExperiment(encoded) {
  if (typeof encoded !== 'string' || encoded.length > 2048 || !/^[A-Za-z0-9_-]+$/.test(encoded)) fail();
  try {
    return settings(JSON.parse(atob(encoded.replace(/-/g,'+').replace(/_/g,'/'))));
  } catch {
    fail();
  }
}
