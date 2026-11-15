import {transform,exact,fraction,mod,coordinate} from './sequence-atlas-core.mjs';

export const STUDY_MODES={
  raw:['Original terms','b(n) = a(n).'],
  difference:['First differences','b(n) = a(n) - a(n-1), defined for n ≥ 1.'],
  'second-difference':['Second differences','b(n) = a(n) - 2a(n-1) + a(n-2), defined for n ≥ 2.'],
  sum:['Partial sums','b(n) = a(0) + … + a(n). Sums always start at index zero.'],
  ratio:['Successive ratios','b(n) = a(n)/a(n-1). Undefined at n=0 or when a(n-1)=0.'],
  average:['Running averages','b(n) = (a(0) + … + a(n))/(n+1). Averages always start at index zero.'],
  alternating:['Alternating signs','b(n) = (-1)^n a(n), using the original index n.'],
  absolute:['Absolute values','b(n) = |a(n)|.'],
  binomial:['Binomial transform','b(n) = Σ from k=0 to n of binom(n,k) a(k).'],
  'inverse-binomial':['Inverse binomial transform','b(n) = Σ from k=0 to n of (-1)^(n-k) binom(n,k) a(k).'],
  mod:['Residues','b(n) is the least nonnegative residue of a(n) modulo m.']
};
export const STUDY_DEFAULTS={transform:'raw',start:0,count:12,modulus:7};
const abs=v=>v<0n?-v:v;
const gcd=(a,b)=>{a=abs(a);b=abs(b);while(b)[a,b]=[b,a%b];return a;};
export function validateStudy(options,length=64){
  const state={...STUDY_DEFAULTS,...options};
  const fail=(message,field)=>{const error=Error(message);error.field=field;throw error;};
  if(!Object.hasOwn(STUDY_MODES,state.transform))fail('Choose a listed transformation.','transform');
  for(const [key,min,max,label] of [['start',0,length-2,'First index'],['count',2,32,'Index positions'],['modulus',2,128,'Modulus']]){
    const value=state[key];if(String(value).trim()===''||!Number.isInteger(Number(value))||Number(value)<min||Number(value)>max)fail(`${label} must be a whole number from ${min} to ${max}.`,key);state[key]=Number(value);
  }
  if(state.start+state.count>length)fail(`This window ends beyond n=${length-1}. Reduce its size or first index.`,'count');
  return state;
}
export function readStudyURL(href){
  const url=new URL(href),keys={study:'transform',from:'start',size:'count',mod:'modulus'},options={};
  for(const [key,name] of Object.entries(keys))if(url.searchParams.has(key))options[name]=url.searchParams.get(key);
  try{return {state:validateStudy(options),error:null};}catch(error){return {state:{...STUDY_DEFAULTS},error:'The study options in this link were invalid. Showing the first 12 original terms. '+error.message};}
}
export function studyURL(href,state){
  state=validateStudy(state);const url=new URL(href);
  for(const [key,value] of Object.entries({study:state.transform,from:state.start,size:state.count,mod:state.modulus}))url.searchParams.set(key,String(value));
  url.hash='analysis';return url;
}
export function analyzeStudy(input,options={}){
  const raw=input.map(BigInt),state=validateStudy(options,raw.length);
  const all=state.transform==='mod'?raw.map(v=>fraction(mod(v,state.modulus))):transform(raw,state.transform);
  const window=all.slice(state.start,state.start+state.count),defined=window.filter(v=>v!==null),integers=defined.filter(v=>v.b===1n);
  const facts={defined:defined.length,undefined:window.length-defined.length,integers:integers.length,
    zero:defined.filter(v=>v.a===0n).length,positive:defined.filter(v=>v.a>0n).length,negative:defined.filter(v=>v.a<0n).length,
    even:integers.filter(v=>v.a%2n===0n).length,odd:integers.filter(v=>v.a%2n!==0n).length,
    gcd:defined.length&&integers.length===defined.length?String(integers.reduce((a,v)=>gcd(a,v.a),0n)):null};
  let difference=raw.map(v=>v),observation=null;const ladder=[];
  for(let order=0;order<=4;order++){
    const current=difference.slice(state.start,state.start+state.count).filter(v=>v!==null);
    if(order>0&&!observation&&current.length>=4&&current.every(v=>v===current[0]))observation={order,value:String(current[0]),count:current.length,start:Math.max(order,state.start),end:state.start+state.count-1};
    ladder.push(difference.slice(state.start,state.start+Math.min(state.count,8)).map(v=>v===null?null:String(v)));
    const previous=difference;difference=previous.map((v,n)=>n&&v!==null&&previous[n-1]!==null?v-previous[n-1]:null);
  }
  const rows=window.map((v,i)=>({n:state.start+i,value:v===null?null:exact(v)}));
  // A linked search must never join across an undefined or noninteger position.
  let first=window.findIndex(v=>v!==null),run=[];
  if(first>=0)for(let i=first;i<window.length&&window[i]!==null&&window[i].b===1n;i++)run.push(String(window[i].a));
  const prefix=(maxDigits,maxCount)=>{const result=[];for(const value of run){if(value.replace('-','').length>maxDigits||result.length>=maxCount||(result.join(',').length+value.length+1)>20000)break;result.push(value);}return result;};
  const search=prefix(2000,8),discovery=prefix(300,32);
  const coordinates=defined.map(v=>coordinate(v,'linear'));
  const plotScale=state.transform!=='mod'&&coordinates.length&&(coordinates.some(v=>v===null)||!Number.isFinite(Math.max(...coordinates)-Math.min(...coordinates)))?'signed-log':'linear';
  return {state,rows,facts,ladder,observation,plotScale,search,discovery:discovery.length>=6?discovery:[],searchStart:first<0?null:state.start+first};
}
export function studyCSV(model){return 'n,value,defined\n'+model.rows.map(row=>`${row.n},${row.value??''},${row.value!==null}`).join('\n')+'\n';}
export function studyIndexed(model){return model.rows.map(row=>`${row.n} ${row.value??'undefined'}`).join('\n');}
