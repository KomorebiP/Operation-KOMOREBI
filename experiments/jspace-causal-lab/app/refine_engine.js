/* Causal lab 1.2: case diagnostics and persistent trajectories.
 * Inference only. No training, logit overrides or hard-coded neural answers.
 * Each diagnostic branches from copies. A live step, unlike a read, commits state.
 */
(function(global){
'use strict';
const node=typeof module!=='undefined'&&module.exports;
const E=node?require('./engine.js'):global.KomorebiEngine;
const C=node?require('./causal_engine.js'):global.KomorebiCausal;
const METHODS=['none','J','interaction','PCA','random','complement','native'];
const VERSION='komorebi.causal-session.v1.2';
const MAX_ACTIONS=64, MAX_OPS=256;
const plain=x=>JSON.parse(JSON.stringify(x,(_,v)=>ArrayBuffer.isView(v)?Array.from(v):v));
function integer(x,lo,hi,name){if(!Number.isInteger(x)||x<lo||x>hi)throw Error(name+' must be an integer in '+lo+'…'+hi);return x;}
function array(x,n,name){if(!Array.isArray(x)||x.length!==n)throw Error(name+' must contain '+n+' values');return x;}
function finiteState(h){return array(h,2,'Paired state').map((v,a)=>Float32Array.from(array(v,64,'Agent '+(a+1)+' state'),x=>{if(!Number.isFinite(x)||Math.abs(x)>1e6)throw Error('Invalid hidden-state value');return x;}));}
function softmax(logits){const m=Math.max(...logits),p=logits.map(x=>Math.exp(x-m)),s=p.reduce((a,b)=>a+b,0);return p.map(x=>x/s);}
function normalizeSettings(s={}){
 const method=s.method??'J';if(!METHODS.includes(method))throw Error('Unknown intervention method');
 const strength=s.strength??1;if(!Number.isFinite(strength)||strength<0||strength>1.5)throw Error('Invalid edit strength');
 const agent=s.agent??'both';if(!['both','0','1'].includes(agent))throw Error('Invalid writing agent');
 const offsets=(s.offsets??[0,0,0]).slice();array(offsets,3,'Offsets').forEach(v=>{if(!Number.isFinite(v)||Math.abs(v)>3)throw Error('Invalid coordinate offset');});
 const suffix=(s.suffix??[]).slice();if(suffix.length>12)throw Error('Continuation exceeds 12 operations');suffix.forEach(x=>integer(x,0,3,'Opcode'));
 if(method==='native'&&strength!==0&&strength!==1)throw Error('A native endpoint cannot be interpolated');
 return {method,strength,agent,offsets,suffix};
}
function compareMemory(before,after,world){
 const lost=[0,0],recovered=[0,0];
 for(let a=0;a<2;a++)for(let j=0;j<8;j++){
  if(before.bits[a][j]===world[j]&&after.bits[a][j]!==world[j])lost[a]++;
  if(before.bits[a][j]!==world[j]&&after.bits[a][j]===world[j])recovered[a]++;
 }
 return {lost,recovered,noNewErrors:lost.every(x=>x===0),allFactsCorrect:after.correct.every(n=>n===8)};
}
function point(d,exp,frame,settings,world,roles,audit=true){
 const s=normalizeSettings(settings),r=C.evaluate(d,exp,frame,s),target=E.target(r.targetPair),original=E.target(r.factualPair);
 const before=r.baselineOutputs[0],after=r.outputs[0];
 const out={settings:s,factual:original,target,contrast:target!==original,
  predictions:after.map(o=>o.prediction),originalPredictions:before.map(o=>o.prediction),
  targetScores:after.map(o=>softmax(o.logits)[target]),
  originalTargetScores:before.map(o=>softmax(o.logits)[target]),
  targetMatched:after.map(o=>o.prediction===target),
  changed:after.map((o,a)=>o.prediction!==before[a].prediction),
  privatePredictions:after.map(o=>o.privatePrediction),privateCorrect:after.map((o,a)=>o.privatePrediction===roles[a]),
  editNorm:r.geometry.map(g=>g.deltaNorm),outsideJNorm:r.geometry.map(g=>g.outsideJNorm),
  nativePairWitness:r.nativePairWitness,boundary:r.boundary};
 if(audit){out.memoryBefore=C.memory(d,r.baseline,world);out.memoryAfter=C.memory(d,r.post,world);out.memoryChange=compareMemory(out.memoryBefore,out.memoryAfter,world);
  out.strictCasePass=out.contrast&&out.targetMatched.every(Boolean)&&out.privateCorrect.every(Boolean)&&out.memoryChange.allFactsCorrect;
 }
 return out;
}
function sweepAlphas(method){return method==='native'?[0,1]:Array.from({length:21},(_,i)=>i/20);}
function summary(rows){
 if(!rows.length)return {firstSteering:null,firstPreserving:null};
 // Grid observations, not a continuous optimum or an out-of-sample certificate.
 const steer=rows.find(r=>r.contrast&&r.targetMatched.every(Boolean));
 const clean=rows.find(r=>r.strictCasePass);
 return {firstSteering:steer?steer.settings.strength:null,firstPreserving:clean?clean.settings.strength:null,
  tested:rows.length,gridOnly:true,independentConfirmation:false};
}
function snapshot(session,label){
 const d=session.model,outputs=session.states.map(h=>[0,1,2,3].map(q=>d.outputs(h,q,q===2?3:q===3?1:0)));
 return {label,states:session.states.map(C.clone),references:session.references.map(x=>x.slice()),outputs,step:session.history.length};
}
function begin(d,exp,frame,settings,world,roles){
 const s=normalizeSettings(settings),r=C.evaluate(d,exp,frame,s);
 const t={model:d,world:world.slice(),roles:roles.slice(),settings:s,
  states:[C.clone(r.baseline),C.clone(r.post)],references:[r.factualPair.slice(),r.targetPair.slice()],
  actions:[],history:[],rawOrigin:{baseline:C.clone(exp.baseline),donor:C.clone(exp.donor),factualValue:exp.factualValue,targetValue:exp.targetValue}};
 t.history.push(snapshot(t,'Committed edit + selected continuation + silent delay'));
 return t;
}
function validateAction(a){
 if(!a||typeof a!=='object')throw Error('Invalid action');
 if(a.type==='work'){
  if(!Array.isArray(a.ops)||a.ops.length<1||a.ops.length>12)throw Error('A working step needs 1…12 opcodes');
  return {type:'work',ops:a.ops.map(x=>integer(x,0,3,'Opcode'))};
 }
 if(a.type==='retrieve')return {type:'retrieve',cue:array(a.cue,2,'Cue').map(x=>integer(x,0,7,'Fact index')),
  mode:validateMode(a.mode??'intact')};
 if(a.type==='silent')return {type:'silent',count:integer(a.count??1,1,8,'Silent ticks')};
 throw Error('Unknown live action');
}
function validateMode(mode){if(!['intact','cut','cut_AtoB','cut_BtoA'].includes(mode))throw Error('Invalid access message condition');return mode;}
function step(t,raw){
 const a=validateAction(raw);if(t.actions.length>=MAX_ACTIONS)throw Error('Session limit reached. Export or restart the trajectory.');
 if(a.type==='retrieve'&&a.cue[0]===a.cue[1])throw Error('Choose two different facts');
 const count=t.actions.reduce((s,x)=>s+(x.ops?.length??x.count??1),0)+(a.ops?.length??a.count??1);
 if(count>MAX_OPS)throw Error('Session exceeds its 256-step resource bound');
 if(a.type==='work'){
  t.states=t.states.map(h=>C.finish(t.model,h,a.ops));
  t.references=t.references.map(v=>a.ops.reduce((x,op)=>E.truthOp(x,op),v.slice()));
 }else if(a.type==='retrieve'){
  t.states=t.states.map(h=>t.model.retrieve(C.clone(h),a.cue,0,a.mode));
  // Reload requests the original factual world, even if neural retrieval fails.
  t.references=[0,1].map(()=>a.cue.map(i=>t.world[i]));
 }else t.states=t.states.map(h=>t.model.silent(C.clone(h),a.count));
 t.actions.push(a);
 const label=a.type==='work'?'Work '+a.ops.map(i=>'ILRS'[i]).join('')+' + silent delay':a.type==='retrieve'?'Reload facts '+a.cue.map(i=>i+1).join(', ')+' · '+a.mode:a.count+' silent tick'+(a.count===1?'':'s');
 const r=snapshot(t,label);t.history.push(r);return r;
}
function undo(t){if(!t.actions.length)return false;t.actions.pop();t.history.pop();const r=t.history[t.history.length-1];t.states=r.states.map(C.clone);t.references=r.references.map(x=>x.slice());return true;}
function liveRead(t,q=0,arg=0){integer(q,0,3,'Consumer');integer(arg,0,3,'Argument');return {outputs:t.states.map(h=>t.model.outputs(h,q,q<2?0:arg)),references:t.references.map(v=>E.target(v,q,q<2?0:arg))};}
function auditSession(t){const before=C.memory(t.model,t.states[0],t.world),after=C.memory(t.model,t.states[1],t.world);return {before,after,change:compareMemory(before,after,t.world)};}
function exportSession(t,meta,framesHash,diagnostics=null){
 return plain({schema:VERSION,lineage:t.model.lineage,variant:t.model.variant,weights_sha256:meta.weights_sha256,frames_sha256:framesHash,
  world:t.world,roles:t.roles,settings:t.settings,origin:t.rawOrigin,actions:t.actions,
  provenance:'Captured original/donor activation pair. Replay validates computation and checkpoint hashes, not native provenance of a supplied snapshot.',
  snapshots:t.history,diagnostics});
}
function replay(payload,store,meta,frames,framesHash){
 if(!payload||payload.schema!==VERSION)throw Error('Unsupported session version');
 if(payload.weights_sha256!==meta.weights_sha256||payload.frames_sha256!==framesHash)throw Error('Checkpoint or candidate hash differs');
 if(!['A','B'].includes(payload.lineage)||!['parent','access','calibrated'].includes(payload.variant))throw Error('Unknown model');
 const world=array(payload.world,8,'World').map(x=>integer(x,0,1,'Fact')),roles=array(payload.roles,2,'Private labels').map(x=>integer(x,0,3,'Private label'));
 const settings=normalizeSettings(payload.settings),o=payload.origin;if(!o||typeof o!=='object')throw Error('Missing origin');
 const exp={baseline:finiteState(o.baseline),donor:finiteState(o.donor),factualValue:integer(o.factualValue,0,3,'Original pair'),targetValue:integer(o.targetValue,0,3,'Donor pair')};
 if(!Array.isArray(payload.actions)||payload.actions.length>MAX_ACTIONS)throw Error('Session action bound exceeded');
 // Validate the complete trace before any inference (including total work).
 const actions=payload.actions.map(validateAction);
 if(actions.some(a=>a.type==='retrieve'&&a.cue[0]===a.cue[1]))throw Error('Repeated fact index');
 if(actions.reduce((n,a)=>n+(a.ops?.length??a.count??1),0)>MAX_OPS)throw Error('Session computation bound exceeded');
 const d=new E.Dyad(store,meta,payload.lineage,payload.variant),t=begin(d,exp,frames.lineages[payload.lineage],settings,world,roles);
 actions.forEach(a=>step(t,a));return t;
}
const API={VERSION,METHODS,plain,softmax,normalizeSettings,compareMemory,point,sweepAlphas,summary,begin,step,undo,liveRead,auditSession,exportSession,replay};
if(node)module.exports=API;global.KomorebiRefinement=API;
})(globalThis);
