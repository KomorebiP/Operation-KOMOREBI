// Bounded exact transform lookup. Results are finite coincidences to investigate.
import {transform,exact,parseTerms} from './sequence-atlas-core.mjs';
import {matchTerms} from './sequence-atlas-search.mjs';
export const OPERATIONS=[
  ['raw','Original terms','b(n) = a(n)'],['difference','First differences','b(n) = a(n)-a(n-1), n >= 1'],
  ['second-difference','Second differences','b(n) = a(n)-2a(n-1)+a(n-2), n >= 2'],
  ['sum','Partial sums','b(n) = sum(k=0..n) a(k)'],['alternating','Alternating signs','b(n) = (-1)^n a(n)'],
  ['absolute','Absolute values','b(n) = |a(n)|'],['binomial','Binomial transform','b(n) = sum(k=0..n) binom(n,k) a(k)'],
  ['inverse-binomial','Inverse binomial transform','b(n) = sum(k=0..n) (-1)^(n-k) binom(n,k) a(k)'],
];
function probe(values,operation){
  const rows=transform(values,operation).map(exact),start=rows.findIndex(v=>v!=='undefined');
  return {operation,start,values:rows.slice(start)};
}
export function analyzeInput(text){
  if(text.length>20000)throw Error('Keep discovery input below 20,000 characters.');
  let values;
  try{values=parseTerms(text.replace(/\u2212/g,'-'));}catch{throw Error('Use 6–64 comma- or space-separated integers, with at most 300 digits per integer. Fractions and decimal values are not supported.');}
  if(values.length<6||values.length>64)throw Error('Use 6–64 consecutive integers for discovery. Up to 300 digits per integer.');
  return values;
}
export function discover(entries,text,{both=false,limit=24}={}){
  const values=analyzeInput(text),probes=OPERATIONS.map(([operation])=>probe(values,operation));
  for(const skip of [1,2])probes.push({operation:'drop-'+skip,start:skip,values:values.slice(skip).map(String)});
  const usable=probes.filter(input=>input.values.length>=6&&(input.operation==='raw'||input.start!==0||input.values.some((v,n)=>v!==String(values[n]))));
  const results=[];
  for(const entry of entries){
    const raw=entry.terms.map(BigInt),candidates=(both?OPERATIONS.filter(([op])=>!['binomial','inverse-binomial'].includes(op)):[OPERATIONS[0]]).map(([op])=>probe(raw,op));
    for(const input of usable){
      for(const target of candidates){
        if(target.operation!=='raw'&&target.values.every((v,n)=>v===entry.terms[n]))continue;
        const positions=matchTerms(target.values,input.values);
        if(positions.length){const position=positions[0];
          results.push({id:entry.id,title:entry.title,inputOperation:input.operation,inputStart:input.start,targetOperation:target.operation,targetStart:target.start+position,targetStarts:positions.map(at=>target.start+at),length:input.values.length,values:input.values,
            score:input.values.length*100-(input.operation==='raw'?0:10)-(target.operation==='raw'?0:20)-position,
            constant:new Set(input.values).size<3});
        }
      }
    }
  }
  const simplified=results.filter(hit=>!hit.inputOperation.startsWith('drop-')||!results.some(other=>other.id===hit.id&&other.targetOperation===hit.targetOperation&&other.inputOperation==='raw'));
  simplified.sort((a,b)=>Number(a.constant)-Number(b.constant)||b.score-a.score||a.id.localeCompare(b.id)||a.inputOperation.localeCompare(b.inputOperation));
  return {input:values.map(String),testedOperations:usable.length,catalogueEntries:entries.length,total:simplified.length,results:simplified.slice(0,limit)};
}
export function operationLabel(operation){return OPERATIONS.find(([id])=>id===operation)?.[1]||(operation.startsWith('drop-')?'Omit the first '+operation.slice(5)+' input terms':operation);}
