import assert from 'node:assert/strict';import fs from 'node:fs';
import {validate,select,options,certificate,defaults,tolerance,settings,str,q,sharp,edge,strip} from '../website/assets/chemistry-budget-core.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url))),plans=read('../website/assets/chemistry/planner-v1.json'),data=read('../website/assets/chemistry/continuous-v1.json');
assert.equal(validate(plans,data),717);
for(const [text,expected]of [['0.1','1/10'],['0.10','1/10'],['1/100','1/100'],['1e-3','1/1000'],['.25','1/4'],['2e2','200']])assert.equal(str(tolerance(text)),expected);
for(const bad of ['0','-1','NaN','1/0','Infinity','<img>','.'])assert.throws(()=>tolerance(bad));
assert.deepEqual(settings(''),defaults);assert.equal(settings('?bpeta=1%2F2&bptol=0.01&bpgoal=energies').objective,'energies');
let p=select(plans,defaults);assert.equal(p.group.order,32);assert.equal(p.plan.nodes,14);p=select(plans,{...defaults,objective:'energies'});assert.equal(p.group.order,64);assert.equal(p.plan.nodes,13);
assert.equal(select(plans,{...defaults,tolerance:'.001'}),null);assert.equal(select(plans,{...defaults,eta:'1/100'}).plan.nodes,166);
let checks=0;
for(const eta of ['1/100','1/10','1/2'])for(const T of ['100','1','0.1','0.01','0.001','1e-8'])for(const objective of ['actions','energies']){const state={eta,tolerance:T,objective},p=select(plans,state),c=certificate(plans,data,state,{planner:'hash',continuous:'old'});assert.equal(Boolean(c),Boolean(p));if(c){assert.equal(c.endpoint_evaluations,c.selected_indices.length);assert.equal(c.cells.length,c.endpoint_evaluations-1);assert.equal(c.new_hamiltonian_actions_performed_by_planner,0);assert.equal(c.source_sha256.planner,'hash');const g=data.groups.find(g=>g.eta===eta&&g.order===c.hamiltonian_actions);assert.ok(!strip(g,c.selected_indices,true).includes('NaN'));}checks++;}
const corrupt=structuredClone(plans);corrupt.groups[0].frontier[0].radius='0';assert.throws(()=>validate(corrupt,data),/frontier bound/);
const badPath=structuredClone(plans);badPath.groups[0].frontier[0].indices[0]=1;assert.throws(()=>validate(badPath,data),/ordering/);
assert.equal(str(sharp(q(0),q(1),q(1))),'1');assert.equal(str(sharp(q(0),q(0),q(4))),'1');
console.log(JSON.stringify({status:'passed',frontierPaths:717,planningQueries:checks,decimalAndFractionInputs:true,corruptPathsAndBoundsRejected:true}));
