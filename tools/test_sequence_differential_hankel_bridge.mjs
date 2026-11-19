// Independent Python-to-browser replay for finite differential Hankel determinants.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {computeExactWindow,structuredDifferentialHankel} from '../website/assets/sequence-closed-forms-core.mjs';

const cases=JSON.parse(readFileSync(0,'utf8'));
let values=0;
for(const item of cases){
  const [a,c]=[item.a,item.c];
  assert.equal(a.length,4);assert.equal(c.length,4);
  const entire=structuredDifferentialHankel(a,c,item.expected.length-1).map(String);
  assert.deepEqual(entire,item.expected,
    'Independent Python structured solver disagreed for '+item.label);
  const count=Math.min(32,item.expected.length),start=item.expected.length-count;
  const args={mode:'differential_hankel',start:String(start),count:String(count)};
  for(let k=0;k<4;k++){
    args['a'+k]=String(a[k]);args['c'+k]=String(c[k]);
  }
  const calculated=computeExactWindow(args);
  assert.deepEqual(calculated.rows.map(x=>x.value),item.expected.slice(start),
    'Browser window disagreed with independent Python for '+item.label);
  values+=entire.length;
}
process.stdout.write(JSON.stringify({
  cases:cases.length,exact_values:values,all_exact:true
})+'\n');
