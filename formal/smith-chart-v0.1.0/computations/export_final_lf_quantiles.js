'use strict';
const fs=require('node:fs'), crypto=require('node:crypto'), vm=require('node:vm');
const source=fs.readFileSync('computations/inputs/smith-chart-final-lf.js','utf8');
const sha=crypto.createHash('sha256').update(source,'utf8').digest('hex');
if(sha!=='e63ed0d751da83de7b2828aa496855cd6d645d36605607b9d84be1f644e51081') throw Error('source hash');
const marker='const fmt=', cut=source.indexOf(marker);
if(cut<0||source.indexOf(marker,cut+1)!==-1) throw Error('source structure');
const sandbox={};
vm.runInNewContext(source.slice(0,cut)+'\nglobalThis.tested={smithQuantile,smithCdf};})();',sandbox,{timeout:5000});
const radii=[.70,.84,.94,.97], masses=[0,1/64,1/16,1/8,1/4,.5-1e-13,.5,.5+1e-13,3/4,.9,1];
const cases=[];
for(const rho of radii) for(const u of masses){
  const theta=sandbox.tested.smithQuantile(rho,u);
  cases.push({rho,u,theta,browserCdf:sandbox.tested.smithCdf(rho,theta)});
}
console.log(JSON.stringify({node:process.version,source_sha256:sha,radii,masses,cases}));
