/* Emit the actual browser arithmetic for an independent Fraction check. */
'use strict';
const api = require('../website/assets/large-signal-atlas.js');
const encode = value => Array.isArray(value) ? value.map(encode) :
  value && typeof value === 'object' && 'n' in value && 'd' in value ? api.text(value) :
  value && typeof value === 'object' ? Object.fromEntries(Object.entries(value).map(([k,v]) => [k,encode(v)])) : value;
const cases = [];
for (let h = -2; h <= 2; h++) for (let t = 0; t <= api.MAX_T; t++) cases.push(encode(api.compare(h,t)));
process.stdout.write(JSON.stringify({max_step:api.MAX_T,cases,
  original:encode(api.trace([api.q(1),api.q(0)],12))}) + '\n');
