import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validatePolynomial,polynomialSelection,polynomialCertificate,polynomialPlot,fullGridAlternative,fullGridCertificate,q,str,approximate,bernstein,leaves,cubicEnvelope,evaluatePolynomial} from '../website/assets/chemistry-polynomial-core.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../website/assets/chemistry/'+name,import.meta.url))),data=read('continuous-v1.json'),poly=read('polynomial-v1.json');
assert.equal(validatePolynomial(poly,data),1005);
const state={eta:'1/10',order:64,index:205},s=polynomialSelection(data,poly,state);
assert.ok(approximate(q(s.curve.maximum_radius))<.001);assert.equal(s.degree,3);
for(const g of poly.groups){for(const index of [0,1,5,100,205,399,400]){const p=polynomialSelection(data,poly,{eta:g.eta,order:g.order,index});assert.ok(approximate(q(p.full.radius))>=0);assert.ok(approximate(q(p.full.radius))<=approximate(q(p.cell.uniform_radius))+1e-18);}
  const c=data.groups.find(c=>c.eta===g.eta&&c.order===g.order);for(const index of [0,400]){const p=polynomialSelection(data,poly,{eta:g.eta,order:g.order,index}),node=index?c.points[0]:c.points.at(-1);assert.deepEqual(p.full.center,node.center);assert.equal(p.full.radius,node.radius);}
}
const g=fullGridAlternative(poly,{eta:'1/10',objective:'actions'},q('1/1000'));assert.equal(g.order,64);assert.equal(g.nodes,41);assert.equal(fullGridAlternative(poly,{eta:'1/10',objective:'actions'},q('1/1000000000000')),null);
const narrow=fullGridAlternative(poly,{eta:'1/100',objective:'actions'},q('1/20'));assert.equal(narrow.order,512);assert.equal(narrow.nodes,166);
assert.equal(polynomialCertificate(data,poly,state,{}).kind,'local-polynomial-energy-response');assert.equal(fullGridCertificate(data,poly,g,q('1/1000'),{}).endpoint_evaluations,41);
for(const change of [p=>p.groups[0].cells[0].full.stencil=[0,0],p=>p.groups[0].cells[0].full.coefficient='0',p=>p.groups[0].maximum_radius='0',p=>p.groups[0].cells[0].gap.absolute_lower='1000000']){const p=structuredClone(poly);change(p);assert.throws(()=>validatePolynomial(p,data));}
for(const compact of [false,true]){const drawing=polynomialPlot(data,poly,state,compact);assert.match(drawing.svg,/outward padding/);assert.ok(!/NaN|Infinity/.test(drawing.svg));assert.match(drawing.svg,/ C/);}
// The quartic t^4 differs from its cubic endpoint Hermite interpolant by 6 e2 t²(1-t)².
const b=bernstein([q(0),q(0),q(0),q(0),q(1)]),e=cubicEnvelope(b);assert.equal(str(e.padding),'1/16');
assert.equal(leaves(b).length,4);assert.equal(str(evaluatePolynomial([q(1),q(-2),q(3)],q('1/2'))),'3/4');
console.log('Polynomial: 1005 exact cell validations, 22 endpoint-recovery curves, strict-target alternatives, corruption rejection and conservative drawing passed.');
