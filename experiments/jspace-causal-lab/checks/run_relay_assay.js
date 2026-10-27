'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib');
const root=path.resolve(__dirname,'..'),out=root+'/checks/relay';
const E=require('../app/engine'),T=require('../app/challenge_engine'),M=require('../app/relay_engine');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(root+'/'+p)).digest('hex');
const inputs=['app/engine.js','app/causal_engine.js','app/refine_engine.js','app/challenge_engine.js','app/relay_engine.js','app/frames.json','app/weights.json','app/weights.bin','checks/relay/CONTRACT.md','checks/run_relay_assay.js'];
const before=Object.fromEntries(inputs.map(p=>[p,hash(p)]));
const start=new Date().toISOString(),time=performance.now();
fs.writeFileSync(out+'/SOURCE_FREEZE.json',JSON.stringify({started_at:start,input_hashes:before},null,2));
const meta=JSON.parse(fs.readFileSync(root+'/app/weights.json')),b=fs.readFileSync(root+'/app/weights.bin'),store=E.load(meta,b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)),frames=JSON.parse(fs.readFileSync(root+'/app/frames.json'));
const records=[],cells=[],reference=[];
for(const lineage of ['A','B'])for(const writer of [0,1])for(const method of ['J','random','complement','native']){
 const d=new E.Dyad(store,meta,lineage,'calibrated');
 const cell={lineage,writer,method,histories:32,first:{},last:{},memory:{}};
 for(const v of [cell.first,cell.last]){v.recipientDonor=Array(5).fill(0);v.writerDonor=Array(5).fill(0);v.referenceErrors=0;v.eligible=0;v.eligibleTransfer=0;v.restoredFactual=0;v.meanTargetProbability=Array(5).fill(0);v.maxReplayError=0;v.maxRestorationError=0;}
 cell.memory.allFacts=Array.from({length:5},()=>[0,0]);cell.memory.private=Array.from({length:5},()=>[0,0]);
 for(let i=0;i<32;i++){
  const spec=T.caseSpec(271449,i),exp=T.prepareCase(d,spec,i),capture=i<2&&['J','native'].includes(method);
  const t=M.begin(d,exp,frames.lineages[lineage],{method,strength:1,offsets:[0,0,0]},spec.world,spec.roles,{writer,program:'ISLR'},'Fixed generated input history, no per-case selection',capture);
  for(const _ of M.steps(t)){}
  const record=M.exportTrace(t,{weights_sha256:meta.weights_sha256,frames_sha256:before['app/frames.json']});record.spec=spec;record.caseIndex=i;
  if(capture)reference.push(record);
  for(const r of record.records)delete r.states;
  records.push(record);
  const receive=t.records.filter(r=>r.phase==='receive');
  for(const [k,r] of [['first',receive[0]],['last',receive.at(-1)]]){
   const c=cell[k];r.receiverDonor.forEach((v,b)=>c.recipientDonor[b]+=v?1:0);r.writerDonor.forEach((v,b)=>c.writerDonor[b]+=v?1:0);r.targetProbability.forEach((v,b)=>c.meanTargetProbability[b]+=v/32);
   c.referenceErrors+=r.referenceError?1:0;c.eligible+=r.eligible?1:0;c.eligibleTransfer+=r.eligible&&r.receiverDonor[1]?1:0;c.restoredFactual+=r.receiverRestored?1:0;
   c.maxReplayError=Math.max(c.maxReplayError,r.firstPacketSufficiency||0);c.maxRestorationError=Math.max(c.maxRestorationError,r.firstPacketRestoration||0);
  }
  for(let b=0;b<5;b++)for(let a=0;a<2;a++){cell.memory.allFacts[b][a]+=t.finalMemory[b].correct[a]===8?1:0;cell.memory.private[b][a]+=t.records.at(-1).outputs[b][0][a].privatePrediction===spec.roles[a]?1:0;}
 }
 cells.push(cell);console.log(lineage,writer,method,cell.first.recipientDonor[1],cell.last.recipientDonor[1],'/32');
}
// Numeric references deliberately keep state arrays, unlike the compact all-case bank.
// Recreate them because the compact records above share their export objects.
const refs=[];
for(const lineage of ['A','B'])for(const writer of [0,1])for(const method of ['J','native','random']){
 const d=new E.Dyad(store,meta,lineage,'calibrated'),spec=T.caseSpec(271449,0),exp=T.prepareCase(d,spec,0);
 const t=M.begin(d,exp,frames.lineages[lineage],{method,strength:1,offsets:[0,0,0]},spec.world,spec.roles,{writer,program:'ISLR'},'Independent PyTorch-check fixture',true);for(const _ of M.steps(t)){}
 const r=M.exportTrace(t);r.spec=spec;refs.push(r);
}
fs.writeFileSync(out+'/reference.json',JSON.stringify(refs));
fs.writeFileSync(out+'/raw.json.gz',zlib.gzipSync(Buffer.from(JSON.stringify(records)),{level:6}));
const after=Object.fromEntries(inputs.map(p=>[p,hash(p)]));if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Frozen inputs changed');
const result={schema:'komorebi.relay-assay.v1.4',status:'COMPLETED_WITH_EXPLICIT_LIMITS',seed:271449,input_histories:32,lineages:2,writer_directions:2,methods:['J','random','complement','native'],branches:M.BRANCHES,trajectories:records.length,program:'ISLR',cells,
 execution:{started_at:start,seconds:(performance.now()-time)/1000,node:process.version,input_hashes_before:before,input_hashes_after:after,exit_expected:0},
 limits:['Two previously competence-selected lineages, not independent population sample','Histories reused across writer, method, branch, time and lineage','First-packet equalities follow from receiver-interface structure','Projected and unilateral native donor edits have no validated paired-state support','No new training, Jacobian uniqueness, or reliable workspace reciprocity demonstrated']};
fs.writeFileSync(out+'/assay.json',JSON.stringify(result,null,2));console.log('Completed',records.length,'traces in',result.execution.seconds.toFixed(2),'seconds');
