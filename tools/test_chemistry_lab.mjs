import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {rational as q,add,sub,mul,str,approximate,sqrtUpper,multiply,positiveSemidefinite,decode,analyze,probeView,verifyResponse,certificate,ERROR_FACTORS,SOURCE_ERRORS} from '../website/assets/chemistry-lab-core.mjs';
const root=fileURLToPath(new URL('..',import.meta.url)),data=JSON.parse(fs.readFileSync(new URL('../website/assets/chemistry/lab-v1.json',import.meta.url)));
const le=(a,b)=>sub(a,b).n<=0n;
let cases=0;
for(const sample of data.samples){
  const decoded=decode(data,sample);
  assert.deepEqual(decoded.h.map(r=>r.map(str)),sample.estimated_H);
  assert.deepEqual(decoded.theta.map(str),sample.theta);
  assert.equal(str(decoded.residual2),sample.residual_squared);
  for(const count of [1,2,3]){
    const view=probeView(data,decoded,count);assert.equal(view.stage.rank+view.stage.nullity,21);
    assert.equal(view.witness.flat().some(x=>x.n!==0n),count!==3);cases++;
  }
  for(const eta of data.etas){
    const center=verifyResponse(decoded,sample,eta);assert.ok(approximate(center.imaginary)<=0);cases++;
    for(const factor of ERROR_FACTORS){
      const epsilon=mul(q(factor),q(sample.cache.raw_error_radius));
      for(const delta of [SOURCE_ERRORS[0],SOURCE_ERRORS[1],SOURCE_ERRORS[4]]){
        const r=analyze(data,sample,decoded,{epsilon,delta,eta});
        assert.equal(r.consistent,le(decoded.residual2,mul(epsilon,epsilon)));
        if(r.consistent){
          assert.ok(le(r.radius2,mul(r.rH,r.rH)));assert.ok(r.radius.n>=0n);
          assert.equal(str(add(r.operatorPart,r.sourcePart)),str(r.radius));
          if(r.allPositive)assert.equal(r.feasibility,true);
        }else assert.equal(r.radius,undefined);
        const c=certificate(data,sample,decoded,r,center,{});assert.equal(c.response_center===null,!r.consistent);
        if(sample.id==='unresolved'&&factor!=='0')assert.equal(r.feasibility,null);
        if(sample.id==='unresolved'&&factor==='0')assert.equal(r.feasibility,false);
        if(sample.id==='zero')assert.equal(r.feasibility,true);
        cases++;
      }
    }
  }
  if(sample.saved_certificate){
    assert.deepEqual(decoded.theta.map(str),sample.saved_certificate.theta);
    const center=verifyResponse(decoded,sample,sample.cache.eta);
    assert.deepEqual({real:str(center.real),imaginary:str(center.imaginary)},sample.saved_certificate.response_center);
  }
}
const b=data.basis.map(h=>h.map(r=>r.map(q))),v=data.probes.map(r=>r.map(q));
const action=b.map(h=>multiply(h,v).flat());
for(let k=0;k<21;k++)for(let j=0;j<21;j++){
  const row=data.left_inverse[k].map(q),value=row.reduce((s,x,i)=>add(s,mul(x,action[j][i])),q(0));
  assert.equal(str(value),k===j?'1':'0');cases++;
}
for(const value of ['0','1','4/9','2','1/10000000000000000000000000000000000000000000000000000000000000000000000000000000000']){
  const r=sqrtUpper(q(value));assert.ok(le(q(value),mul(r,r)));cases++;
}
assert.equal(str(sqrtUpper(q('4/9'))),'2/3');
assert.equal(positiveSemidefinite([[q(0),q(1)],[q(1),q(0)]]),false);
assert.equal(positiveSemidefinite([[q(1),q(-1)],[q(-1),q(1)]]),true);
assert.equal(approximate('1'+'0'.repeat(400)+'/'+'1'+'0'.repeat(410)),1e-10);
const report={status:'passed',cases,examples:data.samples.length,exactResponseSubstitutions:25,decoderLeftInverseIdentities:441,scope:'Finite fixture and implementation checks; no new continuum theorem or physical error certificate.'};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
