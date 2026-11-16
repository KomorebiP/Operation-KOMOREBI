import assert from 'node:assert/strict';
import fs from 'node:fs';
import {settings,defaults,rational,curve,sample,certificate,plot} from '../website/assets/chemistry-responses-core.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../website/assets/chemistry/responses-v1.json',import.meta.url)));
assert.deepEqual(settings(''),defaults);assert.deepEqual(settings('#eta=bad&k=77&i=-1'),defaults);
assert.deepEqual(settings('#eta=1%2F100&k=256&i=999'),{eta:'1/100',order:256,index:40});
let points=0;
for(const eta of data.etas)for(const order of data.orders){
  assert.equal(curve(data,{eta,order}).length,41);
  for(let index=0;index<=40;index++){
    const state={eta,order,index},{point,reduced}=sample(data,state),cert=certificate(data,state,'test-digest');
    assert.equal(point.energy,reduced.energy);assert.ok(rational(point.radius)>0);assert.ok(Number.isFinite(rational(point.center.imaginary)));
    assert.equal(cert.full_target_sample,point);assert.equal(cert.public_data_sha256,'test-digest');assert.match(cert.scope,/sampled/);points++;
  }
  const graphic=plot(data,{eta,order,index:20});assert.match(graphic.svg,/Forty-one/);assert.match(graphic.svg,/Vertical marks/);assert.ok(!graphic.svg.includes('NaN'));
}
assert.equal(points,861);assert.ok(plot(data,{eta:'1/100',order:3,index:20}).capped>0);
console.log(JSON.stringify({status:'passed',selectedSamples:points,etaOrderCombinations:21,invalidLinkDefaults:true,plotScaleClippingDisclosed:true}));
