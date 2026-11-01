import {defaults,settings} from './signal-lab-core.mjs';

export const MAX_RUNS=12;
export const NOTEBOOK_SCHEMA='komorebi-signal-notebook-v1';
export function customSettings(config,values) {
  if(!Array.isArray(values))throw new RangeError('A reference sample array is required.');
  return settings({...config,n:values.length,shape:'custom',custom:values,
    cycles:Math.min(config.cycles,values.length/4),budget:Math.min(config.budget,values.length),
    coefficient:Math.min(config.coefficient,values.length-1),address:Math.min(config.address,values.length-1)});
}
function samples(values) {return customSettings(defaults(),values).custom;}
const equal=(a,b)=>a.length===b.length&&a.every((v,i)=>v===b[i]);

// Fill every crossed address, even when pointer events skip several samples.
export function paintSegment(values,from,to) {
  const result=samples(values);
  for(const point of [from,to]) {
    if(!point||!Number.isInteger(point.index)||point.index<0||point.index>=result.length||
      !Number.isInteger(point.value)||Math.abs(point.value)>64)throw new RangeError('Use a sample address and a whole-number value from −64 to 64.');
  }
  const distance=Math.abs(to.index-from.index),direction=Math.sign(to.index-from.index);
  if(distance===0)result[to.index]=to.value;
  else for(let step=0;step<=distance;step++)result[from.index+step*direction]=Math.round(from.value+(to.value-from.value)*step/distance)||0;
  return result;
}

export class SampleHistory {
  constructor(){this.past=[];this.future=[];}
  clear(){this.past=[];this.future=[];}
  record(before,after){
    const a=samples(before),b=samples(after);
    if(equal(a,b))return false;
    this.past.push(a);if(this.past.length>32)this.past.shift();this.future=[];return true;
  }
  undo(current){if(!this.past.length)return null;this.future.push(samples(current));return this.past.pop();}
  redo(current){if(!this.future.length)return null;this.past.push(samples(current));return this.future.pop();}
}

export function readNotebook(text) {
  if(typeof text!=='string'||text.length>65536)throw new RangeError('Use a notebook JSON file under 64 KiB.');
  let value;try{value=JSON.parse(text);}catch{throw new RangeError('This is not valid notebook JSON.');}
  if(value?.schema!==NOTEBOOK_SCHEMA||!Array.isArray(value.entries)||value.entries.length>MAX_RUNS)
    throw new RangeError('Use a Signal Laboratory notebook with at most 12 runs.');
  return value.entries.map(entry=>{
    const label=entry?.label;
    if(typeof label!=='string'||!label.trim()||label.trim().length>48||/[\u0000-\u001f\u007f]/.test(label))
      throw new RangeError('Run names need 1–48 characters on one line.');
    return {label:label.trim(),settings:settings(entry.settings)};
  });
}
export function writeNotebook(entries) {
  const clean=readNotebook(JSON.stringify({schema:NOTEBOOK_SCHEMA,entries}));
  return JSON.stringify({schema:NOTEBOOK_SCHEMA,entries:clean},null,2)+'\n';
}
export function appendRuns(entries,additional) {
  if(entries.length+additional.length>MAX_RUNS)throw new RangeError('The notebook holds 12 runs. Remove a run or export this notebook before importing more.');
  return readNotebook(writeNotebook([...entries,...additional]));
}
export function sameObservation(a,b) {return equal(a.reference,b.reference)&&equal(a.observed,b.observed);}
export function notebookCsv(entries,results) {
  if(entries.length!==results.length)throw new RangeError('Recompute every run before exporting.');
  const quote=label=>'"'+(/^[=+@-]/.test(label)?"'":'')+label.replace(/"/g,'""')+'"';
  return 'run,basis,samples,retained,noise_amplitude,seed,policy,reference_error,discarded_energy\n'+entries.map((entry,i)=>{
    const r=results[i],s=r.config,a=r.analyses[s.basis];
    return [quote(entry.label),s.basis,s.n,s.budget,s.noise,s.seed,s.policy,a.referenceError,a.observedError].join(',');
  }).join('\n')+'\n';
}
