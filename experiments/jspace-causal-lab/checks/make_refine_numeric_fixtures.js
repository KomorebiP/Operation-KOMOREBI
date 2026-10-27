'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),E=require('../app/engine.js'),C=require('../app/causal_engine.js'),R=require('../app/refine_engine.js');
const meta=JSON.parse(fs.readFileSync(root+'/app/weights.json')),raw=fs.readFileSync(root+'/app/weights.bin'),fr=fs.readFileSync(root+'/app/frames.json'),frames=JSON.parse(fr),hash=crypto.createHash('sha256').update(fr).digest('hex');
const store=E.load(meta,raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength)),specs=JSON.parse(fs.readFileSync(__dirname+'/causal_specs.json')),sessions=[];
let count=0;
for(const lineage of ['A','B'])for(const variant of ['parent','access','calibrated'])for(const method of ['J','PCA','complement','native']){
 const d=new E.Dyad(store,meta,lineage,variant),spec=specs[count++%specs.length],source=C.initial(d,spec);
 let v=spec.cue.map(i=>spec.world[i]);for(const op of spec.ops)v=E.truthOp(v,op);
 const exp=C.prepare(d,source,E.target(v),E.target(v)^1),settings={method,strength:method==='native'?1:.65,agent:method==='complement'?'0':'both',offsets:method==='J'?[.1,-.2,0]:[0,0,0],suffix:[3]};
 const t=R.begin(d,exp,frames.lineages[lineage],settings,spec.world,spec.roles);
 const actions=[{type:'work',ops:[1]},{type:'work',ops:[3,1,2]},{type:'retrieve',cue:[2,3],mode:'intact'},{type:'silent',count:1},{type:'work',ops:[2]},{type:'retrieve',cue:[0,7],mode:'cut_AtoB'}];
 actions.forEach(a=>R.step(t,a));const o=R.exportSession(t,meta,hash);o.finalMemory=R.auditSession(t);sessions.push(o);
}
fs.writeFileSync(__dirname+'/refined_numeric_fixtures.json',JSON.stringify(sessions));console.log('Saved '+sessions.length+' live trajectory fixtures');
