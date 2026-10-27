const fs=require('fs'),path=require('path'),root=path.resolve(__dirname,'..');
const E=require('../app/engine'),C=require('../app/causal_engine'),T=require('../app/challenge_engine'),M=require('../app/relay_engine');
const meta=JSON.parse(fs.readFileSync(root+'/app/weights.json')),b=fs.readFileSync(root+'/app/weights.bin'),store=E.load(meta,b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)),frames=JSON.parse(fs.readFileSync(root+'/app/frames.json'));
for(const l of ['A','B'])for(const w of [0,1])for(const kind of ['work','exchange']){
const d=new E.Dyad(store,meta,l,'calibrated'),s=T.caseSpec(271414,0),exp=T.prepareCase(d,s,0);
const t=M.begin(d,exp,frames.lineages[l],{method:'J',strength:1,offsets:[0,0,0]},s.world,s.roles,{writer:w,kind,program:'ISLR',exchanges:4});for(const _ of M.steps(t)){};
console.log(l,w,kind,JSON.stringify(M.summary(t)));}
