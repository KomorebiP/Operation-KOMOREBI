'use strict';
const fs=require('node:fs'), crypto=require('node:crypto'), vm=require('node:vm');
const source=fs.readFileSync('computations/inputs/smith-chart.js','utf8');
const sha=crypto.createHash('sha256').update(source,'utf8').digest('hex');
if(sha!=='3e5db4bab9fc548352d32c4294c810b471389bacfd182c32e80b1a0cb49a1515') throw Error('source hash');
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
