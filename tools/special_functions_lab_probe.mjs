// Machine-readable probe consumed by the independent Python/Fraction audit.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import * as M from '../website/assets/special-functions-lab-core.mjs';

const cases=JSON.parse(readFileSync(0,'utf8'));
let controls=0;
function check(f){f();controls++;}
for(const value of ['0','1','-1/2','1/101','1/0','NaN','1e-1','1/2junk','<script>','9'.repeat(10000)])check(()=>assert.throws(()=>M.parameters([value,'1/2','1/2','1/2'])));
for(const radius of ['-1/2','3/2','2','1/0'])check(()=>assert.throws(()=>M.tailBound(radius,12)));
for(const count of [0,17,1.5,NaN])check(()=>assert.throws(()=>M.coefficients(['1/2','1/2','1/2','1/2'],count)));
check(()=>assert.equal(M.text(M.tailBound('1',12)),'1/2048'));
check(()=>assert.equal(M.text(M.tailBound('0',16)),'0'));
check(()=>assert.ok(Math.abs(M.decimal(M.rational(10n**1000n+1n,3n*10n**1000n))-1/3)<1e-15));
check(()=>assert.throws(()=>M.decodeState('#sf='+encodeURIComponent('{"v":1}'))));
check(()=>assert.throws(()=>M.decodeState('#sf='+'x'.repeat(2501))));
check(()=>assert.throws(()=>M.validateState({...M.defaultState(),current:Array(4)})));
const linked={...M.defaultState(),compare:true,count:16,radius:'4/3',term:15};
check(()=>assert.deepEqual(M.decodeState('#'+M.encodeState(linked)),M.validateState(linked)));
check(()=>assert.equal(M.coefficientCSV(linked).trim().split('\n').length,33));
check(()=>assert.equal(M.text(M.parse('2/4')),'1/2'));
const rows=cases.map(c=>{
  const start=performance.now(),result=M.coefficients(c.scales,c.count);
  const term=c.count-1,contributions=M.contributions(c.scales,result,term);
  const swapped=M.coefficients([c.scales[3],c.scales[2],c.scales[1],c.scales[0]],c.count);
  check(()=>assert.deepEqual(swapped.u,result.v));check(()=>assert.deepEqual(swapped.v,result.u));
  if(term>0){check(()=>assert.deepEqual(contributions.reduce((s,v)=>M.add(s,v.u),M.rational(0n)),result.u[term]));check(()=>assert.deepEqual(contributions.reduce((s,v)=>M.add(s,v.v),M.rational(0n)),result.v[term]));}
  return {u:result.u.map(M.text),v:result.v.map(M.text),
    samples:['-4/3','-1/2','0','1/2','4/3'].map(x=>({x,u:M.text(M.evaluateExact(result.u,M.parse(x))),v:M.text(M.evaluateExact(result.v,M.parse(x)))})),
    bounds:['0','1/2','1','4/3'].map(r=>({radius:r,value:M.text(M.tailBound(r,c.count))})),
    elapsed_ms:performance.now()-start};
});
process.stdout.write(JSON.stringify({rows,controls,node:process.version}));
