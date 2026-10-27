/* Causal Editor 1.3: one write, three matched trajectories, fixed-setting challenges.
 * All read/audit operations branch from copies. Evaluator truth never enters model
 * readouts. A reload intentionally discards temporary content in the reference.
 */
(function(global){
'use strict';
const node=typeof module!=='undefined'&&module.exports;
const E=node?require('./engine.js'):global.KomorebiEngine;
const C=node?require('./causal_engine.js'):global.KomorebiCausal;
const R=node?require('./refine_engine.js'):global.KomorebiRefinement;
const SCHEMA='komorebi.causal-challenge.v1.3';
const BRANCHES=['original','edited','donor'];
function integer(x,lo,hi,name){if(!Number.isInteger(x)||x<lo||x>hi)throw Error(name+' must be an integer in '+lo+'…'+hi);return x;}
function values(a,n,lo,hi,name){if(!Array.isArray(a)||a.length!==n)throw Error(name+' has the wrong length');return a.map(x=>integer(x,lo,hi,name));}
function validateSpec(s){
 if(!s||typeof s!=='object')throw Error('Missing case specification');
 const world=values(s.world,8,0,1,'World'),roles=values(s.roles,2,0,3,'Private labels'),cue=values(s.cue,2,0,7,'Cue');
 if(cue[0]===cue[1])throw Error('Choose distinct cue indices');
 if(!Array.isArray(s.events)||s.events.length!==8)throw Error('Fresh-case replay requires eight initialization events');
 const events=s.events.map(e=>{values(e,7,0,7,'Event');if(e[0]!==0||e[1]!==e[2]||e[3]>1||e[4]!==1||e[5]>1||e[6]>1)throw Error('Invalid initialization event');return e.slice();});
 if(new Set(events.map(e=>e[1])).size!==8||E.exactWorld(events).some((x,i)=>x!==world[i]))throw Error('World disagrees with its initialization');
 if(!Array.isArray(s.ops)||s.ops.length>12)throw Error('Prefix bound is twelve operations');
 const ops=s.ops.map(x=>integer(x,0,3,'Opcode')),opAliases=values(s.opAliases,ops.length,0,1,'Operation aliases');
 return {world,roles,cue,events,ops,opAliases,alias:integer(s.alias,0,1,'Cue alias'),seed:integer(s.seed,0,4294967295,'Seed')};
}
function random(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
function shuffle(a,r){for(let i=a.length-1;i>0;i--){let j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function caseSpec(seed,index){
 integer(seed,0,4294967295,'Bank seed');integer(index,0,63,'Case index');
 const caseSeed=(seed+Math.imul(index+1,2654435761))>>>0,r=random(caseSeed);
 const world=Array.from({length:8},()=>Math.floor(2*r())),order=shuffle([0,1,2,3,4,5,6,7],r),cue=shuffle(order.slice(),r).slice(0,2),n=[0,3,6][index%3];
 const s={seed:caseSeed,world,roles:[Math.floor(4*r()),Math.floor(4*r())],events:order.map(i=>[0,i,i,world[i],1,Math.floor(2*r()),Math.floor(2*r())]),cue,alias:Math.floor(2*r()),ops:Array.from({length:n},()=>Math.floor(4*r())),opAliases:Array.from({length:n},()=>Math.floor(2*r()))};
 return validateSpec(s);
}
function prepareCase(d,s,index=0){s=validateSpec(s);const h=C.initial(d,s),pair=s.ops.reduce((v,op)=>E.truthOp(v,op),s.cue.map(i=>s.world[i])),factual=E.target(pair),target=factual^(1+(index%3));return C.prepare(d,h,factual,target);}
function normalizePlan(p={}){
 const ops=Array.isArray(p.ops)?p.ops.map(x=>integer(x,0,3,'Opcode')):C.parseProgram(p.program??'LRLRLRLRLRLR',48);
 if(ops.length>48)throw Error('Challenge limit is 48 working operations');
 const points=p.points??[0,1,2,4,8,12,24,48].filter(x=>x<=ops.length);
 if(!Array.isArray(points)||points.length>49)throw Error('Invalid checkpoints');
 const checkpoints=Array.from(new Set([0,ops.length,...points.map(x=>integer(x,0,ops.length,'Checkpoint'))])).sort((a,b)=>a-b);
 const reloads=integer(p.reloads??4,0,8,'Reload count');
 if(!['intact','cut','cut_AtoB','cut_BtoA'].includes(p.mode??'intact'))throw Error('Unsupported retrieval channel');
 return {ops,points:checkpoints,reloads,mode:p.mode??'intact'};
}
function pairOf(v){return [v&1,(v>>1)&1];}
function begin(d,exp,frame,settings,world,roles,cue,plan,origin='Captured prepared states; native origin not authenticated'){
 settings=R.normalizeSettings(settings);world=values(world,8,0,1,'World');roles=values(roles,2,0,3,'Private labels');cue=values(cue,2,0,7,'Cue');if(cue[0]===cue[1])throw Error('Cue must contain distinct indices');
 plan=normalizePlan(plan);integer(exp.factualValue,0,3,'Factual value');integer(exp.targetValue,0,3,'Donor value');
 for(const h of [exp.baseline,exp.donor]){if(!Array.isArray(h)||h.length!==2)throw Error('Invalid dyad state');for(const v of h){if(v.length!==64||Array.from(v).some(x=>!Number.isFinite(x)||Math.abs(x)>1e6))throw Error('Invalid activation');}}
 const edited=C.editedState(exp,frame,settings),states=[exp.baseline,edited,exp.donor].map(h=>d.program(C.clone(h),settings.suffix,settings.suffix.map(()=>0)));
 const refs=[pairOf(exp.factualValue),pairOf(exp.targetValue),pairOf(exp.targetValue)].map(v=>settings.suffix.reduce((p,op)=>E.truthOp(p,op),v));
 // Reload the original pair first, then cover the six other facts. Repeat once if requested.
 const order=cue.concat([0,1,2,3,4,5,6,7].filter(x=>!cue.includes(x))),schedule=Array.from({length:8},(_,i)=>order.slice((i%4)*2,(i%4)*2+2));
 return {d,settings,world,roles,cue,plan,origin,states,references:refs,work:0,reloads:0,closed:false,records:[],schedule,
   initial:{baseline:C.clone(exp.baseline),donor:C.clone(exp.donor),factualValue:exp.factualValue,targetValue:exp.targetValue},memoryOrigin:null};
}
function inspect(t,label,phase='work',capture=false){
 // Standard silent delay is on a copy during work monitoring. Retrieval already includes it.
 const states=t.states.map(h=>phase==='work'?t.d.silent(C.clone(h)):C.clone(h));
 const qargs=[0,0,3,E.target(t.references[0])]; // same late verification proposal for all branches
 const outputs=states.map(h=>qargs.map((arg,q)=>t.d.outputs(h,q,arg))),memory=states.map(h=>C.memory(t.d,h,t.world));
 const reference=t.references.map(p=>qargs.map((arg,q)=>E.target(p,q,arg))),contrast=reference[0][0]!==reference[2][0];
 const status=[0,1].map(a=>{
  if(phase==='reload')return outputs[1][0][a].prediction===reference[1][0]?'reload_correct':'reload_error';
  if(!contrast)return 'no_contrast';
  if(outputs[0][0][a].prediction!==reference[0][0]||outputs[2][0][a].prediction!==reference[2][0])return 'reference_error';
  return outputs[1][0][a].prediction===reference[2][0]?'transferred':outputs[1][0][a].prediction===reference[0][0]?'reverted':'other_error';
 });
 const privateCorrect=outputs.map(o=>o[0].map((v,a)=>v.privatePrediction===t.roles[a]));
 const conditional=[];for(let q=0;q<4;q++)for(let a=0;a<2;a++){if(reference[0][q]===reference[2][q])continue;conditional.push({q,agent:a,referenceCompetent:outputs[0][q][a].prediction===reference[0][q]&&outputs[2][q][a].prediction===reference[2][q],transferred:outputs[1][q][a].prediction===reference[2][q]});}
 if(!t.memoryOrigin)t.memoryOrigin=R.plain(memory);
 const rec={label,phase,work:t.work,reloads:t.reloads,reference,queryArgs:qargs,outputs,memory,status,contrast,privateCorrect,conditional,
  memoryComparedToOriginal:R.compareMemory(memory[0],memory[1],t.world),
  editedMemoryComparedToStart:R.compareMemory(t.memoryOrigin[1],memory[1],t.world),
  allRequirements:phase==='work'&&status.every(x=>x==='transferred')&&privateCorrect[1].every(Boolean)&&memory[1].correct.every(x=>x===8)};
 if(capture)rec.states=states.map(C.clone);
 t.records.push(rec);return rec;
}
function workStep(t){if(t.closed||t.work>=t.plan.ops.length)throw Error('No remaining work');const op=t.plan.ops[t.work];t.states=t.states.map(h=>t.d.operate(h,op,0));t.references=t.references.map(v=>E.truthOp(v,op));t.work++;}
function reloadStep(t){if(t.work!==t.plan.ops.length||t.reloads>=t.plan.reloads)throw Error('Reload is out of schedule');if(!t.closed){t.states=t.states.map(h=>t.d.silent(h));t.closed=true;}
 const cue=t.schedule[t.reloads];t.states=t.states.map(h=>t.d.retrieve(h,cue,0,t.plan.mode));t.references=[0,1,2].map(()=>cue.map(i=>t.world[i]));t.reloads++;return cue;
}
function* steps(t,capture=false){yield inspect(t,'After one edit','work',capture);while(t.work<t.plan.ops.length){workStep(t);if(t.plan.points.includes(t.work))yield inspect(t,'Work '+t.work,'work',capture);}while(t.reloads<t.plan.reloads){const cue=reloadStep(t);yield inspect(t,'Reload '+t.reloads+': F'+(cue[0]+1)+' / F'+(cue[1]+1),'reload',capture);} }
function summarize(records){const w=records.filter(x=>x.phase==='work');let eligible=0,transferred=0,referenceErrors=0,reversions=0,other=0,consumerEligible=0,consumerTransferred=0;for(const r of w){for(const s of r.status){if(s==='reference_error')referenceErrors++;if(['transferred','reverted','other_error'].includes(s)){eligible++;if(s==='transferred')transferred++;if(s==='reverted')reversions++;if(s==='other_error')other++;}}for(const c of r.conditional)if(c.referenceCompetent){consumerEligible++;if(c.transferred)consumerTransferred++;}}
 return {workSnapshots:w.length,eligibleAgentSnapshots:eligible,transferred,referenceErrors,reversions,other,conditionalTransferRate:eligible?transferred/eligible:null,consumerEligible,consumerTransferred,firstEditSpecificFailure:w.find(r=>r.status.some(s=>s==='reverted'||s==='other_error'))?.work??null,firstReferenceFailure:w.find(r=>r.status.includes('reference_error'))?.work??null,
 firstNewMemoryError:w.find(r=>r.editedMemoryComparedToStart.lost.some(x=>x>0))?.work??null,
 reloadRows:records.filter(r=>r.phase==='reload').length,
 note:'Snapshot counts reuse cases, agents and times. Conditional scores exclude reference failures, which are reported separately. Reload intentionally resets temporary references to facts.'};}
function run(t,capture=false){for(const _ of steps(t,capture)){}return {records:t.records,summary:summarize(t.records)};}
function cleanExport(t,hashes){return R.plain({schema:SCHEMA,lineage:t.d.lineage,variant:t.d.variant,...hashes,settings:t.settings,world:t.world,roles:t.roles,cue:t.cue,plan:t.plan,origin:t.origin,initial:t.initial,records:t.records,summary:summarize(t.records),scope:'Measured frozen-model intervention; no learned-state or natural-localization certificate.'});}
const API={SCHEMA,BRANCHES,validateSpec,caseSpec,prepareCase,normalizePlan,begin,inspect,workStep,reloadStep,steps,run,summarize,cleanExport};
if(node)module.exports=API;global.KomorebiChallenge=API;
})(globalThis);
