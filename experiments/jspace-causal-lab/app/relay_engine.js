/* Causal Editor 1.4: single-writer edits and first-packet interchange.
 * Uses the original learned work/send/receive/answer functions. No new weights.
 * Branches share inputs and scheduling; ONLY the first writer packet is replaced
 * in the restoration and replay controls. All later traffic is autonomous.
 */
(function(global){
'use strict';
const node=typeof module!=='undefined'&&module.exports;
const E=node?require('./engine.js'):global.KomorebiEngine;
const C=node?require('./causal_engine.js'):global.KomorebiCausal;
const R=node?require('./refine_engine.js'):global.KomorebiRefinement;
const BRANCHES=['original','edited','restored','replay','donor'];
const SCHEMA='komorebi.causal-relay.v1.4';
const plain=x=>JSON.parse(JSON.stringify(x,(_,v)=>ArrayBuffer.isView(v)?Array.from(v):v));
const clone=C.clone;
function int(x,lo,hi,name){if(!Number.isInteger(x)||x<lo||x>hi)throw Error(name+' must be an integer in '+lo+'…'+hi);return x;}
function state(h){if(!Array.isArray(h)||h.length!==2||h.some(v=>v.length!==64||Array.from(v).some(x=>!Number.isFinite(x)||Math.abs(x)>1e6)))throw Error('Invalid paired activations');return clone(h);}
function normalize(p={}){
 const writer=int(p.writer??0,0,1,'Writer'),kind=p.kind??'work';
 if(!['work','exchange'].includes(kind))throw Error('Choose native work or bare exchange');
 const ops=kind==='work'?C.parseProgram(p.program??'ISLR',8):[];
 const exchanges=kind==='exchange'?int(p.exchanges??4,1,8,'Exchange count'):0;
 if(kind==='work'&&!ops.length)throw Error('Enter at least one operation');
 return {writer,kind,ops,exchanges,firstPacketOnly:true};
}
function begin(d,exp,frame,settings,world,roles,plan={},origin='Source origin not authenticated',capture=false){
 const p=normalize(plan),s=R.normalizeSettings({...settings,agent:String(p.writer),suffix:[]});
 if(!Array.isArray(world)||world.length!==8||world.some(v=>v!==0&&v!==1))throw Error('Invalid factual world');
 if(!Array.isArray(roles)||roles.length!==2||roles.some(v=>!Number.isInteger(v)||v<0||v>3))throw Error('Invalid private labels');
 int(exp.factualValue,0,3,'Original working value');int(exp.targetValue,0,3,'Donor working value');
 const baseline=state(exp.baseline),donor=state(exp.donor),edited=C.editedState({...exp,baseline,donor},frame,s);
 const eventCount=p.kind==='exchange'?p.exchanges:p.ops.length*int(d.c.work_exchanges,1,8,'Model work exchanges');
 if(eventCount>32)throw Error('Model schedule exceeds relay bound');
 return {d,plan:p,settings:s,world:world.slice(),roles:roles.slice(),origin,capture,frame,
  states:[clone(baseline),clone(edited),clone(edited),clone(baseline),clone(donor)],
  pair:[exp.factualValue&1,exp.factualValue>>1],target:[exp.targetValue&1,exp.targetValue>>1],
  initial:{baseline,donor,factualValue:exp.factualValue,targetValue:exp.targetValue},
  events:0,opsDone:0,records:[],packet:null,finished:false,eventCount};
}
function probability(logits,k){const m=Math.max(...logits),e=logits.map(x=>Math.exp(x-m));return e[k]/e.reduce((a,b)=>a+b,0);}
function maxdiff(a,b){let m=0;for(let i=0;i<a.length;i++)m=Math.max(m,Math.abs(a[i]-b[i]));return m;}
function inspect(t,label,phase){
 // Read-only: delay and all fact probes operate on copies, never on trajectory.
 const h=t.states.map(v=>t.d.silent(clone(v))),fv=E.target(t.pair),tv=E.target(t.target),proposal=fv;
 const qs=[0,1,2,3],args=[0,0,3,proposal];
 const outputs=h.map(v=>qs.map((q,i)=>t.d.outputs(v,q,args[i])));
 const references={factual:qs.map((q,i)=>E.target(t.pair,q,args[i])),donor:qs.map((q,i)=>E.target(t.target,q,args[i]))};
 const writer=t.plan.writer,receiver=1-writer;
 const competent=outputs[0][0][receiver].prediction===fv&&outputs[4][0][receiver].prediction===tv,contrast=fv!==tv;
 const m=outputs.map(o=>probability(o[0][receiver].logits,tv));
 const eligible=contrast&&competent;
 const record={label,phase,exchange:t.events,operation:t.opsDone,outputs,references,writer,receiver,
  targetProbability:m,eligible,referenceError:!competent,
  receiverDonor:outputs.map(o=>o[0][receiver].prediction===tv),
  writerDonor:outputs.map(o=>o[0][writer].prediction===tv),
  receiverRestored:outputs[2][0][receiver].prediction===fv,
  firstPacketSufficiency:phase==='receive'&&t.events===1?maxdiff(t.states[1][receiver],t.states[3][receiver]):null,
  firstPacketRestoration:phase==='receive'&&t.events===1?maxdiff(t.states[0][receiver],t.states[2][receiver]):null,
  packet:t.packet?plain(t.packet):null};
 if(t.capture)record.states=t.states.map(clone);
 t.records.push(record);return record;
}
function exchange(t){
 const nets=t.d.agents,w=t.plan.writer,r=1-w;
 const messages=t.states.map(h=>nets.map((a,i)=>a.send(h[i])));
 const original=messages[0][w].slice(),edited=messages[1][w].slice();
 // Only the first packet is controlled. Receiver updates still execute normally.
 if(t.events===0){messages[2][w]=original.slice();messages[3][w]=edited.slice();}
 t.packet={writer:w,receiver:r,index:t.events+1,intervened:t.events===0,
  original:Array.from(original),edited:Array.from(edited),sent:messages.map(v=>Array.from(v[w])),
  maxDifference:maxdiff(original,edited)};
 t.states=t.states.map((h,b)=>nets.map((a,i)=>a.cell('receive',messages[b][1-i],h[i])));
 t.events++;
}
function* steps(t){
 if(t.finished||t.records.length)throw Error('A relay run can be executed only once');
 yield inspect(t,'Before communication','initial');
 if(t.plan.kind==='exchange'){
  for(let i=0;i<t.plan.exchanges;i++){exchange(t);yield inspect(t,'Exchange '+t.events,'receive');}
 }else{
  for(const op of t.plan.ops){
   t.states=t.states.map(h=>t.d.agents.map((a,i)=>a.work(h[i],op,0)));
   t.pair=E.truthOp(t.pair,op);t.target=E.truthOp(t.target,op);t.opsDone++;t.packet=null;
   yield inspect(t,'Local '+ 'ILRS'[op]+' · before send','local');
   for(let i=0;i<t.d.c.work_exchanges;i++){exchange(t);yield inspect(t,'After '+ 'ILRS'[op]+' · exchange '+t.events,'receive');}
  }
 }
 t.finalMemory=t.states.map(h=>C.memory(t.d,t.d.silent(clone(h)),t.world));
 t.finished=true;
}
function summary(t){
 const receive=t.records.filter(r=>r.phase==='receive'),first=receive[0],last=receive.at(-1);
 function stats(r){if(!r)return null;return {exchange:r.exchange,referenceError:r.referenceError,eligible:r.eligible,
  donor:r.receiverDonor.slice(),writerDonor:r.writerDonor.slice(),restoredFactual:r.receiverRestored,
  probability:r.targetProbability.slice(),effect:r.targetProbability[1]-r.targetProbability[0],
  firstPacketRescueError:r.firstPacketRestoration,firstPacketReplayError:r.firstPacketSufficiency};}
 return {completed:t.finished,first:stats(first),last:stats(last),
  firstEligibleTransfer:receive.find(r=>r.eligible&&r.receiverDonor[1])?.exchange??null,
  finalAllFacts:t.finalMemory?.map(b=>b.correct.map(n=>n===8))??null};
}
function exportTrace(t,hashes={}){return {schema:SCHEMA,branches:BRANCHES.slice(),status:t.finished?'Completed':'Incomplete',
 model:{lineage:t.d.lineage,variant:t.d.variant},hashes,origin:t.origin,world:t.world.slice(),roles:t.roles.slice(),
 settings:plain(t.settings),plan:plain(t.plan),initial:plain(t.initial),records:plain(t.records),
 finalMemory:plain(t.finalMemory??null),summary:summary(t),scope:[
 'An upstream edit is applied to one agent once; no answers or weights are replaced.',
 'Only the first outgoing writer packet is restored/replayed. Later exchanges are ordinary learned computation.',
 'At the first exchange, identical recipient state and message imply identical recipient update by construction; this is a software/causal-path check, not independent emergence evidence.',
 'Projected and one-agent whole-state edits lack a certified native joint-state witness.',
 'Bare exchanges are a diagnostic schedule, not ordinary supplied work tokens.',
 'The donor reference has both agent states replaced and is a competence control, not selective localization.'
 ]};}
const API={SCHEMA,BRANCHES,normalize,begin,inspect,exchange,steps,summary,exportTrace,plain};
if(node)module.exports=API;global.KomorebiRelay=API;
})(typeof globalThis==='undefined'?window:globalThis);
