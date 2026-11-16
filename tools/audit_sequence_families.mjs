import assert from 'node:assert/strict';
import {generateFamily,workedFamily,linearBinomial,linearHyper,constantRecurrence} from '../website/assets/sequence-family-core.mjs';
import {exact} from '../website/assets/sequence-atlas-core.mjs';
import {modularCycle} from '../website/assets/sequence-modular-core.mjs';
import {composeScalarTransfers} from '../website/assets/sequence-graph-core.mjs';
import {identifyLocal} from '../website/assets/sequence-discovery-core.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;const data=JSON.parse(input);let values=0,hyper=0,worked=0;
for(const example of data.cases){const actual=generateFamily(example.engine,example.params);assert.deepEqual(actual.terms,example.terms,example.name);assert.equal(actual.offset,example.offset,example.name);assert.deepEqual(actual.degrees,example.degrees,example.name);if(example.rationals)assert.deepEqual(actual.rationalTerms,example.rationals,example.name);values+=actual.terms.length;
  const w=workedFamily(actual,actual.terms.length-1);if(w.alternative!==null){assert.equal(w.value,w.alternative,example.name);worked++;}
  if(example.engine==='linear'&&actual.params.seedMode==='tail')for(let n=0;n<actual.terms.length;n++){assert.equal(String(linearBinomial(actual.params.k,actual.params.r,actual.params.c,n)),actual.terms[n],example.name);assert.equal(exact(linearHyper(actual.params.k,actual.params.r,actual.params.c,n)),actual.terms[n],example.name);hyper++;}
}
const cycles=data.cycles.map(item=>{const r=modularCycle(item.params,item.modulus,item.maximum);return {params:item.params,modulus:item.modulus,maximum:item.maximum,model:r.model,certified:r.certified,preperiod:r.preperiod,period:r.period,repeatIndex:r.repeatIndex,repeatedState:r.repeatedState,initialState:r.initialState,values:r.values,scanned:r.scanned};});
for(const item of data.compositions){const r=composeScalarTransfers(item.a,item.b,item.c,12);assert.ok(r.verified);assert.deepEqual(r.rows.map(row=>row.composed),item.expected);assert.deepEqual(r.rows.map(row=>row.inverse),item.inverse);assert.equal(r.indexShift,item.indexShift);assert.equal(r.positionShift,item.positionShift);}
const identifications=data.identifications.map(item=>{const r=identifyLocal(data.entries,item.text,{both:item.both});assert.equal(r.scanned,data.scalarCount);assert.ok(r.results.some(hit=>hit.id===item.expected),item.expected);return {records:r.scanned,probes:r.probes,matches:r.total};});
process.stdout.write(JSON.stringify({cases:data.cases.length,values,hypergeometric_values:hyper,worked_alternatives:worked,cycles,composition_cases:data.compositions.length,composition_coefficients:data.compositions.length*12,identifications}));
