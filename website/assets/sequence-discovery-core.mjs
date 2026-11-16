import {transform,exact} from './sequence-atlas-core.mjs';
import {matchTerms} from './sequence-atlas-search.mjs';
const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b)[a,b]=[b,a%b];return a;};
const NAMES={raw:'Original terms',difference:'First differences','second-difference':'Second differences',sum:'Partial sums',alternating:'Alternating signs',absolute:'Absolute values',binomial:'Binomial transform','inverse-binomial':'Inverse binomial transform',negated:'Negated terms',even:'Even window positions',odd:'Odd window positions'};
export function identifyInput(text){
  if(typeof text!=='string'||text.length>20000)throw Error('Keep identification input below 20,000 characters.');const tokens=text.replaceAll('−','-').trim().split(/[\s,;]+/);if(tokens.length<6||tokens.length>64||tokens.some(v=>!/^[-+]?\d{1,300}$/.test(v)))throw Error('Supply 6–64 consecutive integers, up to 300 digits each. Use the main search for wildcard patterns.');return tokens.map(v=>String(BigInt(v)));
}
export function discoveryProbes(values,all=true){
  const integers=values.map(BigInt),probes=[],seen=new Set(),operations=all?Object.keys(NAMES):['raw','difference','second-difference','sum','negated','alternating','absolute','even','odd'];
  const add=(operation,label,terms,positions)=>{if(terms.length<6)return;const key=terms.join(',');if(seen.has(key))return;seen.add(key);probes.push({operation,label,values:terms,positions,lowInformation:new Set(terms).size<3});};
  for(const operation of operations){
    let terms,positions;
    if(operation==='even'||operation==='odd'){const start=operation==='odd'?1:0;positions=integers.map((_,i)=>i).filter(i=>i%2===start);terms=positions.map(i=>String(integers[i]));}
    else if(operation==='negated'){terms=integers.map(v=>String(-v));positions=integers.map((_,i)=>i);}
    else{const q=transform(integers,operation).map(exact);positions=q.map((_,i)=>i).filter(i=>q[i]!=='undefined');terms=positions.map(i=>q[i]);}
    add(operation,NAMES[operation],terms,positions);
    const divisor=terms.reduce((d,v)=>gcd(d,BigInt(v)),0n);if(divisor>1n)add(operation+'-gcd',NAMES[operation]+'; divide by gcd '+divisor,terms.map(v=>String(BigInt(v)/divisor)),positions);
  }
  if(all)for(const skip of [1,2])add('drop-'+skip,'Omit the first '+skip+' window positions',values.slice(skip),values.slice(skip).map((_,i)=>i+skip));
  return probes;
}
export function matchProbe(target,probe){const positions=matchTerms(target,probe.values);if(!positions.length)return null;return {position:positions[0],positions,length:probe.values.length,score:(probe.lowInformation?-100000:0)+probe.values.length*100+(probe.operation==='raw'?80:0)-positions[0]};}
export function identifyLocal(entries,text,{both=false,limit=40}={}){
  const values=identifyInput(text),probes=discoveryProbes(values),matches=[];let scanned=0,forms=0;
  for(const entry of entries){if(entry.triangle||entry.id==='KOM084'||entry.index_symbol==='j')continue;scanned++;const candidates=both?discoveryProbes(entry.terms,false):[{operation:'raw',label:'Original terms',values:entry.terms,positions:entry.terms.map((_,i)=>i)}];let best=null,alternatives=0;
    for(const target of candidates)for(const probe of probes){const hit=matchProbe(target.values,probe);if(!hit)continue;forms++;alternatives++;const result={id:entry.id,title:entry.title,url:entry.url,inputOperation:probe.label,targetOperation:target.label,inputPositions:probe.positions,targetPositions:hit.positions.map(at=>entry.offset+target.positions[at]),targetIndex:entry.offset+target.positions[hit.position],matchedTerms:hit.length,values:probe.values,score:hit.score-(target.operation==='raw'?0:30),lowInformation:probe.lowInformation};if(!best||result.score>best.score)best=result;}
    if(best)matches.push({...best,alternatives});
  }
  matches.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));return {input:values,probes:probes.length,scanned,total:matches.length,matchingForms:forms,results:matches.slice(0,limit),scope:'Exact finite matches under the displayed transformations. Matching prefixes do not prove an infinite identity.'};
}
