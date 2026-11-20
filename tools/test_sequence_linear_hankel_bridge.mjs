// Independent BigInt arithmetic against Python rational and Schur fixtures.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {linearHankelGeneratingFunction,linearHankelCoefficients} from '../website/assets/sequence-linear-hankel.mjs';
import {computeExactWindow,differentialMomentCanonicalKernel,differentialHankel,
        exactViewURL,readExactView} from '../website/assets/sequence-closed-forms-core.mjs';
const {fixtures,kernels}=JSON.parse(readFileSync(0,'utf8'));
let checked=0;
function trim(values){
  values=values.map(String);
  while(values.length>1&&values.at(-1)==='0')values.pop();
  return values;
}
for(const fixture of fixtures){
  const {a,b,values,numerator,denominator}=fixture;
  const actual=linearHankelCoefficients(a,b,256).map(String);
  assert.deepEqual(actual,values,'Full linear Hankel window '+a+','+b);
  const g=linearHankelGeneratingFunction(a,b);
  assert.deepEqual(trim(g.numerator),numerator);
  assert.deepEqual(trim(g.denominator),denominator);
  for(let n=0;n<=12;n++)assert.equal(actual[n],String(differentialHankel(n,[a,b],[1])));
  const raw={mode:'linear_hankel',a0:String(a),a1:String(b),start:'225',count:'32'};
  const result=computeExactWindow(raw);
  assert.deepEqual(result.rows.map(x=>x.value),values.slice(225,257));
  assert.equal(result.generatingFunction.kind,'rational-hankel');
  assert.match(result.generatingFunction.expression,/n >= 1/);
  assert.deepEqual(readExactView(exactViewURL('https://example.test/sequence-library.html',raw)),raw);
  checked+=actual.length;
}
for(const fixture of kernels){
  const result=differentialMomentCanonicalKernel(fixture.a,fixture.c);
  assert.deepEqual(result.numerator,fixture.numerator);
  assert.equal(result.poleOrder,fixture.pole);
}
assert.throws(()=>linearHankelCoefficients(1,1,257),/between 0 and 256/);
assert.throws(()=>linearHankelCoefficients(0.5,1,5),/integers|rounding/);
assert.throws(()=>linearHankelCoefficients(Number.MAX_SAFE_INTEGER+1,1,5),/rounding/);
process.stdout.write(JSON.stringify({cases:fixtures.length,exact_values:checked,
  kernel_cases:kernels.length,all_exact:true})+'\n');
