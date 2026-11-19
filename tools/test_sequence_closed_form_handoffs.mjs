// Independent cross-language fixture audit for every curated closed-form record.
// The Python catalogue supplies exact indexed terms, not the BigInt algorithm.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {computeExactWindow} from '../website/assets/sequence-closed-forms-core.mjs';

const cases=JSON.parse(readFileSync(0,'utf8'));
assert.equal(Array.isArray(cases),true);
const modes=new Set(),seen=new Set();
let checked=0;
for(const item of cases){
  assert.equal(typeof item.id,'string');
  assert.equal(seen.has(item.id),false,'Duplicate record '+item.id);
  seen.add(item.id);
  assert.ok(Array.isArray(item.expected)&&item.expected.length>0);
  const params=item.calculator;
  assert.ok(params&&typeof params.mode==='string','No recorded calculator parameters: '+item.id);
  modes.add(params.mode);
  const actual=computeExactWindow({
    ...params,start:String(item.offset),count:String(item.expected.length)
  });
  const values=actual.rows.map(row=>row.value);
  assert.deepEqual(values,item.expected,'Exact calculator mismatch for '+item.id);
  assert.equal(actual.rows[0].index,item.offset,'Index mismatch for '+item.id);
  checked+=values.length;
}
process.stdout.write(JSON.stringify({
  records:cases.length,checked_integer_values:checked,
  modes:[...modes].sort(),all_exact:true
})+'\n');
