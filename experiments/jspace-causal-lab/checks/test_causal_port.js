'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),E=require('../app/engine.js'),C=require('../app/causal_engine.js');
const meta=JSON.parse(fs.readFileSync(root+'/app/weights.json')),bin=fs.readFileSync(root+'/app/weights.bin');
const store=E.load(meta,bin.buffer.slice(bin.byteOffset,bin.byteOffset+bin.byteLength)),frames=JSON.parse(fs.readFileSync(root+'/app/frames.json'));
const refs=JSON.parse(fs.readFileSync(__dirname+'/causal_reference.json')),specs=JSON.parse(fs.readFileSync(__dirname+'/causal_specs.json'));
let maxState=0,maxEdited=0,maxLogit=0,decisions=0,mismatch=0;const cached=new Map();
for(const r of refs){
 const key=r.lineage+':'+r.spec_index+':'+r.target;
 if(!cached.has(key)){
  const d=new E.Dyad(store,meta,r.lineage,'calibrated'),spec=specs[r.spec_index];
  let value=spec.cue.map(i=>spec.world[i]);for(const op of spec.ops)value=E.truthOp(value,op);
  cached.set(key,[d,C.prepare(d,C.initial(d,spec),E.target(value),r.target)]);
 }
 const [d,exp]=cached.get(key),before=JSON.stringify(exp);
 const out=C.evaluate(d,exp,frames.lineages[r.lineage],r);
 assert.equal(before,JSON.stringify(exp),'Editing must not mutate captured factual or donor states');
 for(let a=0;a<2;a++){
  for(let i=0;i<64;i++){maxState=Math.max(maxState,Math.abs(out.post[a][i]-r.state[a][i]));maxEdited=Math.max(maxEdited,Math.abs(out.edited[a][i]-r.edited[a][i]));}
  for(let q=0;q<4;q++){
   const l=out.outputs[q][a].logits,expect=r.logits[a][q];maxLogit=Math.max(maxLogit,...l.map((x,i)=>Math.abs(x-expect[i])));
   decisions++;if(E.argmax(l)!==E.argmax(expect))mismatch++;
  }
 }
}
const checks=[];
const [d,exp]=cached.values().next().value,frame=frames.lineages.A;
function check(name,fn){fn();checks.push(name);}
check('Zero strength is exactly baseline',()=>assert.deepStrictEqual(C.editedState(exp,frame,{method:'J',strength:0}),exp.baseline));
check('Native is exactly donor',()=>assert.deepStrictEqual(C.editedState(exp,frame,{method:'native',strength:1}),exp.donor));
check('One-agent edit leaves other untouched',()=>assert.deepStrictEqual(C.editedState(exp,frame,{method:'J',strength:1,agent:'0'})[1],exp.baseline[1]));
check('Native interpolation rejected',()=>assert.throws(()=>C.editedState(exp,frame,{method:'native',strength:.5})));
check('Nonfinite values rejected',()=>assert.throws(()=>C.editedState(exp,frame,{method:'J',strength:NaN})));
check('Invalid programs rejected',()=>assert.throws(()=>C.parseProgram('S + L')));
check('Memory audit preserves live activations',()=>{const h=C.finish(d,exp.baseline,[]),s=JSON.stringify(h);C.memory(d,h,specs[0].world);assert.equal(JSON.stringify(h),s);});
check('Candidate and complement sum to donor delta',()=>{const j=C.editedState(exp,frame,{method:'J',strength:1}),p=C.editedState(exp,frame,{method:'complement',strength:1});for(let a=0;a<2;a++)for(let i=0;i<64;i++)assert(Math.abs(j[a][i]+p[a][i]-exp.baseline[a][i]-exp.donor[a][i])<3e-5);});
assert.equal(mismatch,0);assert(maxState<.0002);assert(maxLogit<.001);
const out={status:'PASS',paths:refs.length,decisions,mismatches:mismatch,max_state_abs_error:maxState,max_edited_abs_error:maxEdited,max_logit_abs_error:maxLogit,contract_checks:checks,scope:'Sampled numeric agreement with PyTorch. Does not certify natural support or every browser/input.'};
fs.writeFileSync(__dirname+'/causal_port_validation.json',JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));
