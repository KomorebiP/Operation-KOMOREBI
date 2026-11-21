import assert from 'node:assert/strict';import fs from 'node:fs';
import {validate,selection,certificate,settings,defaults,plot,q,approximate} from '../website/assets/chemistry-continuous-core.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../website/assets/chemistry/continuous-v1.json',import.meta.url)));
assert.equal(validate(data),1005);assert.deepEqual(settings(''),defaults);assert.equal(settings('?cceta=1%2F2&cck=512').order,128);
let checked=0;
for(const curve of data.groups){for(const index of [0,1,205,399,400]){const state={eta:curve.eta,order:curve.order,index},s=selection(data,state),c=certificate(data,state,'digest');assert.ok(approximate(q(s.t))>=0&&approximate(q(s.t))<=1);assert.equal(c.extra_hamiltonian_actions,0);assert.equal(c.cell.full_endpoints.length,2);assert.equal(c.public_data_sha256,'digest');checked++;}const graphic=plot(data,{eta:curve.eta,order:curve.order,index:205},true);assert.match(graphic.svg,/ Q/);assert.match(graphic.svg,/clipPath/);assert.ok(!graphic.svg.includes('NaN'));}
const bad=structuredClone(data);bad.groups[0].cells[0].coefficient='0';assert.throws(()=>validate(bad),/Interpolation inequality/);
const wrong=structuredClone(data);wrong.groups[0].maximum_radius='0';assert.throws(()=>validate(wrong),/Whole-interval/);
assert.ok(approximate(q(selection(data,defaults).full.radius))>.001);assert.ok(approximate(q(selection(data,{...defaults,index:200}).full.radius))<4e-9);
console.log(JSON.stringify({status:'passed',continuousCells:1005,energySelections:checked,curvedBandEdges:true,corruptBoundsRejected:true}));
