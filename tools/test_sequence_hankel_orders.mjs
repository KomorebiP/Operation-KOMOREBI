import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {rational,text,coefficients,classify,normalizedTerms} from '../website/assets/sequence-hankel-orders-core.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../verification/sequence-library/hankel-compression/'+name,import.meta.url),'utf8'));
const rows=coefficients(read('interior-coefficients.json'));
if(process.argv.includes('--bridge')){
  const cases=JSON.parse(fs.readFileSync(0,'utf8'));
  process.stdout.write(JSON.stringify(cases.map(({t,q})=>({...classify(t,q,rows),terms:normalizedTerms(t,q,8)}))));
}else{
  test('every saved exact GF case has the certified order and defining terms',()=>{
    for(const item of read('interior-replay.json').samples.cases){
      const result=classify(item.t,item.q,rows);assert.equal(result.order,item.order,item.label);
      assert.equal(result.root_type,item.root_type,item.label);
      assert.deepEqual(normalizedTerms(item.t,item.q,8),item.first_eight,item.label);
    }
  });
  test('rational input stays exact and invalid/boundary inputs fail',()=>{
    for(const [input,expected]of [['.125','1/8'],['1.','1'],['-0.50','-1/2'],['001/002','1/2'],['+3','3']])assert.equal(text(rational(input)),expected);
    for(const input of ['0.'+'1234567890'.repeat(3)+'1','9'.repeat(32)+'/'+'1'+'0'.repeat(31)])assert.equal(text(rational(text(rational(input)))),text(rational(input)));
    assert.throws(()=>rational('2'.repeat(33)),/32 digits/);
    for(const input of ['','NaN','Infinity','1/0','1e100','<img>','1/-2','2'.repeat(81)])assert.throws(()=>rational(input));
    assert.throws(()=>rational(1.25));assert.throws(()=>classify('0','1',rows),/nonzero/);
    assert.throws(()=>classify('1','0',rows),/nonzero/);assert.throws(()=>normalizedTerms('1','1',14));
    assert.deepEqual(normalizedTerms('1','4',4),['1','1','0','-256']);
    const bad=structuredClone(read('interior-coefficients.json'));bad.first_eight_with_unit[8].push([9,0,'1']);assert.throws(()=>coefficients(bad));
  });
}
