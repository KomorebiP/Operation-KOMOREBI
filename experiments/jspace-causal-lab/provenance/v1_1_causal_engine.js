/* Actual upstream activation interventions on frozen networks. No answer overrides. */
(function(global){
'use strict';
const E=typeof module!=='undefined'&&module.exports?require('./engine.js'):global.KomorebiEngine;
const clone=h=>h.map(x=>new Float32Array(x));
function finite(x,name){if(!Number.isFinite(x))throw Error(name+' must be finite');return x;}
function parseProgram(s,max=96){const t=String(s).toUpperCase().replace(/[\s,]/g,'');if(/[^ILRS]/.test(t)||t.length>max)throw Error('Use only I, L, R, S; at most '+max+' operations.');return [...t].map(x=>'ILRS'.indexOf(x));}
function initial(d,spec){let h=d.encode(spec.events,spec.roles);h=d.cue(h,spec.cue,spec.alias,'intact',0);return d.program(h,spec.ops,spec.opAliases);}
function prepare(d,source,factualValue,targetValue){
 if(!Number.isInteger(factualValue)||factualValue<0||factualValue>3||!Number.isInteger(targetValue)||targetValue<0||targetValue>3)throw Error('Pair values must be 0,1,2,3');
 const mask=factualValue^targetValue;
 // Equal-duration native histories. Equal-value donor is a real two-flip sham.
 const donorOps=mask===0?[1,1]:[(mask&1)?1:0,(mask&2)?2:0];
 return {baseline:d.program(clone(source),[0,0],[0,0]),donor:d.program(clone(source),donorOps,[0,0]),factualValue,targetValue,donorOps};
}
function matCoords(h,u){return u.map(row=>row.reduce((s,v,i)=>s+v*h[i],0));}
function getBases(frame,method){const key=['native','none','complement'].includes(method)?'J':method; if(!['J','interaction','PCA','random'].includes(key))throw Error('Unknown candidate');return frame.frames.map(f=>f[key]);}
function editedState(exp,frame,settings={}){
 const method=settings.method||'J',alpha=finite(Number(settings.strength??1),'Strength'),offsets=settings.offsets||[0,0,0],agent=settings.agent||'both';
 if(alpha<0||alpha>1.5)throw Error('Strength must be between 0 and 1.5');
 if(!['both','0','1'].includes(agent))throw Error('Choose both agents, agent 1, or agent 2');
 if(offsets.length!==3||offsets.some(v=>!Number.isFinite(v)||Math.abs(v)>3))throw Error('Axis offsets must be finite and within three calibration standard deviations');
 if(method==='native'&&alpha!==0&&alpha!==1)throw Error('Whole-native replacement requires strength 0 or 1; interpolation is not native.');
 const bases=getBases(frame,method),hs=exp.baseline.map((h,a)=>{
  if(agent!=='both'&&agent!==String(a))return new Float32Array(h);
  if(method==='none')return new Float32Array(h);
  if(method==='native')return new Float32Array(alpha===0?h:exp.donor[a]);
  const u=bases[a],difference=Array.from(h,(x,i)=>exp.donor[a][i]-x),c=matCoords(difference,u);
  const scale=frame.statistics[a].scales;
  return Float32Array.from(h,(x,i)=>{
    const projected=u.reduce((s,row,k)=>s+row[i]*c[k],0);
    const delta=method==='complement'?difference[i]-projected:projected;
    const manual=method==='J'?u.reduce((s,row,k)=>s+row[i]*offsets[k]*scale[k],0):0;
    return x+alpha*delta+manual;
  });
 });
 return hs;
}
function outputsAll(d,h){return [0,1,2,3].map(q=>d.outputs(h,q,q===2?3:q===3?1:0));}
function finish(d,h,suffix){return d.silent(d.program(clone(h),suffix,suffix.map(()=>0)));}
function evaluate(d,exp,frame,settings){
 const suffix=settings.suffix||[];if(suffix.length>12||suffix.some(op=>![0,1,2,3].includes(op)))throw Error('At most twelve continuation operations');
 const edited=editedState(exp,frame,settings),baseline=finish(d,exp.baseline,suffix),post=finish(d,edited,suffix),donor=finish(d,exp.donor,suffix);
 let fv=[exp.factualValue&1,exp.factualValue>>1],tv=[exp.targetValue&1,exp.targetValue>>1];for(const op of suffix){fv=E.truthOp(fv,op);tv=E.truthOp(tv,op);}
 const geometry=edited.map((h,a)=>{
   const u=frame.frames[a].J,diff=Array.from(h,(v,i)=>v-exp.baseline[a][i]);
   const coords=matCoords(diff,u),energy=diff.reduce((s,x)=>s+x*x,0), projected=coords.reduce((s,x)=>s+x*x,0);
   return {baseline:matCoords(exp.baseline[a],u),donor:matCoords(exp.donor[a],u),edited:matCoords(h,u),deltaNorm:Math.sqrt(energy),
      outsideJNorm:Math.sqrt(diff.reduce((s,x,i)=>{const e=x-u.reduce((t,row,k)=>t+row[i]*coords[k],0);return s+e*e;},0)),means:frame.statistics[a].means,scales:frame.statistics[a].scales};
 });
 return {edited,baseline,post,donor,baselineOutputs:outputsAll(d,baseline),outputs:outputsAll(d,post),donorOutputs:outputsAll(d,donor),geometry,
    factualPair:fv,targetPair:tv,method:settings.method,
    nativePairWitness:settings.method==='native'&&settings.strength===1&&settings.agent==='both',
    boundary:settings.method==='native'&&settings.strength===1&&settings.agent==='both'?'Whole paired state from actual donor execution. Not localized.':'Artificial activation edit. Natural support is not validated.'};
}
function memory(d,h,world){const pred=[[],[]];for(let j=0;j<4;j++){
 const r=d.retrieve(clone(h),[2*j,2*j+1],0,'intact'),o=d.outputs(r);
 for(let a=0;a<2;a++)pred[a].push(o[a].prediction&1,o[a].prediction>>1);
 }return {bits:pred,correct:pred.map(p=>p.filter((x,i)=>x===world[i]).length),world:world.slice()};}
const API={clone,parseProgram,initial,prepare,matCoords,getBases,editedState,finish,evaluate,memory};
if(typeof module!=='undefined'&&module.exports)module.exports=API;global.KomorebiCausal=API;
})(typeof globalThis==='undefined'?window:globalThis);
