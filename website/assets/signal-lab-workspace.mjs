import {BASES,defaults,settings,experiment} from './signal-lab-core.mjs';

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
function sampleRegion(n,region) {
  if(region===null)return [0,n-1];
  if(!Array.isArray(region)||region.length!==2||!region.every(Number.isInteger)||region[0]<0||region[1]>=n||region[0]>region[1])
    throw new RangeError('Choose an inclusive region with whole-number addresses from 0 to '+(n-1)+', start no later than end.');
  return [...region];
}
export function targetBudgets(result,metric,value) {
  const maximum=metric==='energy'?100:metric==='reference'?64:null;
  if(maximum===null||!Number.isFinite(value)||value<0||value>maximum)throw new RangeError('Choose an energy target from 0 to 100%, or a reference RMS limit from 0 to 64.');
  const observedEnergy=result.observed.reduce((sum,v)=>sum+v*v,0),referenceEnergy=result.reference.reduce((sum,v)=>sum+v*v,0),n=result.config.n;
  const energy=metric==='energy'?observedEnergy:referenceEnergy;
  const threshold=metric==='energy'?energy*(1-value/100):n*value*value,tolerance=1e-10*Math.max(1,energy);
  const rows=BASES.map(basis=>{
    const curve=result.analyses[basis].curve,field=metric==='energy'?'observedError':'referenceError';
    // Reference error need not be monotone: inspect every budget in order.
    const point=curve.find(row=>row[field]<=threshold+tolerance);
    return {basis,budget:point?.budget??null,
      referenceRms:point?Math.sqrt(point.referenceError/n):null,
      retainedPercent:point?(observedEnergy===0?100:Math.max(0,Math.min(100,100*(1-point.observedError/observedEnergy)))):null,
      bestReferenceRms:Math.sqrt(Math.min(...curve.map(row=>row.referenceError))/n)};
  });
  return {metric,value,threshold,tolerance,observedEnergy,referenceEnergy,rows};
}
export function targetRuns(result,metric,value) {
  const labels={haar:'Haar',cosine:'Cosine',samples:'Samples'};
  return targetBudgets(result,metric,value).rows.filter(row=>row.budget!==null).map(row=>({
    label:labels[row.basis]+' · '+(metric==='energy'?value+'% energy':'RMS≤'+value),
    settings:settings({...result.config,basis:row.basis,budget:row.budget})}));
}
export function comparisonState(raw) {
  if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.v!==1||!Array.isArray(raw.entries)||raw.entries.length!==2||!['overlay','error','difference'].includes(raw.view))
    throw new RangeError('Use a supported comparison with exactly two runs.');
  const entries=readNotebook(writeNotebook(raw.entries)),results=entries.map(entry=>experiment(entry.settings));
  if(!sameObservation(...results))throw new RangeError('Shared comparisons require identical reference and observed samples.');
  if(!Number.isInteger(raw.address)||raw.address<0||raw.address>=entries[0].settings.n)throw new RangeError('The comparison sample address is outside the signal.');
  const clean={v:1,entries,view:raw.view,address:raw.address};
  if(Object.hasOwn(raw,'region')){
    if(raw.region===null)throw new RangeError('A shared region needs two sample addresses.');
    clean.region=sampleRegion(entries[0].settings.n,raw.region);
    if(raw.address<clean.region[0]||raw.address>clean.region[1])throw new RangeError('The selected sample must be inside the shared region.');
  }
  return clean;
}
export function encodeComparison(raw) {
  const bytes=new TextEncoder().encode(JSON.stringify(comparisonState(raw)));
  const encoded=btoa(String.fromCharCode(...bytes)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  if(encoded.length>8192)throw new RangeError('This comparison is too large for a shared link.');
  return encoded;
}
export function decodeComparison(encoded) {
  if(typeof encoded!=='string'||encoded.length>8192||!/^[A-Za-z0-9_-]+$/.test(encoded))throw new RangeError('This comparison link is invalid or too large.');
  try{const bytes=Uint8Array.from(atob(encoded.replace(/-/g,'+').replace(/_/g,'/')),character=>character.charCodeAt(0));return comparisonState(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes)));}
  catch{throw new RangeError('This comparison link could not be restored.');}
}
export function starterRuns(id) {
  const base={...defaults(),noise:0,budget:8};let entries;
  if(id==='edges')entries=[{label:'Edges · Haar',settings:{...base,basis:'haar'}},{label:'Edges · cosine',settings:{...base,basis:'cosine'}}];
  if(id==='tone')entries=[{label:'Tone · Haar',settings:{...base,shape:'wave',cycles:5,budget:1,basis:'haar'}},{label:'Tone · cosine',settings:{...base,shape:'wave',cycles:5,budget:1,basis:'cosine'}}];
  if(id==='noise')entries=[{label:'Noisy steps · 6 kept',settings:{...base,noise:8,budget:6}},{label:'Noisy steps · 32 kept',settings:{...base,noise:8,budget:32}}];
  if(id==='ranking') {
    const benchmark={...base,n:16,shape:'custom',custom:[2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4],budget:1,address:8};
    entries=[{label:'Haar · weighted energy',settings:{...benchmark,policy:'energy'}},{label:'Haar · raw magnitude',settings:{...benchmark,policy:'magnitude'}}];
  }
  if(!entries)throw new RangeError('Choose a known starter experiment.');
  return readNotebook(writeNotebook(entries));
}
export function compareRuns(a,b) {
  if(!sameObservation(a,b))throw new RangeError('Comparison data requires identical reference and observed samples.');
  const aa=a.analyses[a.config.basis].reconstruction,bb=b.analyses[b.config.basis].reconstruction;
  const rows=a.reference.map((reference,address)=>({address,reference,observed:a.observed[address],a:aa[address],b:bb[address],
    errorA:aa[address]-reference,errorB:bb[address]-reference,difference:bb[address]-aa[address]}));
  const maximum=Math.max(...rows.map(row=>Math.abs(row.difference)));
  return {rows,maximum,maximumAddress:rows.findIndex(row=>Math.abs(row.difference)===maximum)};
}
export function compareRegion(a,b,region=null) {
  const [start,end]=sampleRegion(a.config.n,region),rows=compareRuns(a,b).rows.slice(start,end+1),count=rows.length;
  const summarize=field=>{
    const errors=rows.map(row=>row[field]),maximum=Math.max(...errors.map(Math.abs));
    return {rms:Math.sqrt(errors.reduce((sum,error)=>sum+error*error,0)/count),bias:errors.reduce((sum,error)=>sum+error,0)/count,
      maximum,maximumAddress:rows[errors.findIndex(error=>Math.abs(error)===maximum)].address};
  };
  const maximum=Math.max(...rows.map(row=>Math.abs(row.difference)));
  return {start,end,count,rows,a:summarize('errorA'),b:summarize('errorB'),maximum,
    maximumAddress:rows.find(row=>Math.abs(row.difference)===maximum).address};
}
export function comparisonCsv(a,b,region=null) {
  const {rows}=compareRegion(a,b,region);
  return 'address,reference,observed,a_reconstruction,b_reconstruction,a_error_to_reference,b_error_to_reference,b_minus_a\n'+
    rows.map(row=>[row.address,row.reference,row.observed,row.a,row.b,row.errorA,row.errorB,row.difference].join(',')).join('\n')+'\n';
}
export function notebookCsv(entries,results) {
  if(entries.length!==results.length)throw new RangeError('Recompute every run before exporting.');
  const quote=label=>'"'+(/^[=+@-]/.test(label)?"'":'')+label.replace(/"/g,'""')+'"';
  return 'run,basis,samples,retained,noise_amplitude,seed,policy,reference_error,discarded_energy\n'+entries.map((entry,i)=>{
    const r=results[i],s=r.config,a=r.analyses[s.basis];
    return [quote(entry.label),s.basis,s.n,s.budget,s.noise,s.seed,s.policy,a.referenceError,a.observedError].join(',');
  }).join('\n')+'\n';
}
