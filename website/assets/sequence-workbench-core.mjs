import {transform,coordinate,mod} from './sequence-atlas-core.mjs';
import {generateFamily,validateFamily,familyDescriptor,familyURL,FAMILY_ENGINES} from './sequence-family-core.mjs';
import {validateComparisonChart} from './sequence-comparison-chart.mjs';

export const WORKBENCH_DEFAULTS=Object.freeze({view:'values',transform:'raw',scale:'signed-log',alignment:'positions',skip:0,count:32,modulus:7,marks:'line'});
export function validateWorkbench(options={}){
  const state={...WORKBENCH_DEFAULTS,...Object.fromEntries(Object.keys(WORKBENCH_DEFAULTS).filter(key=>Object.hasOwn(options,key)).map(key=>[key,options[key]]))};
  for(const [key,choices]of Object.entries({view:['values','mod'],transform:['raw','difference','sum'],scale:['linear','signed-log'],alignment:['positions','indices'],marks:['line','points']}))if(!choices.includes(state[key]))throw Error(`Choose a listed ${key}.`);
  for(const [key,min,max]of [['skip',0,1000000],['count',1,1000],['modulus',2,1000000]]){if(String(state[key]).trim()===''||!Number.isSafeInteger(Number(state[key]))||Number(state[key])<min||Number(state[key])>max)throw Error(`${key} must be an integer from ${min} to ${max}.`);state[key]=Number(state[key]);}
  return state;
}
export function localSource(entry,base){
  const receipt=/^[0-9a-f]{64}$/.test(entry.record_sha256||'')?entry.record_sha256:null;
  return {key:entry.id,type:'local',id:entry.id,title:entry.title,indexKind:entry.index_symbol==='j'?'local flat index j':'local index n',offset:entry.offset,terms:entry.terms,url:base?new URL(entry.url,base).href:entry.url,collection:entry.collection,receipt};
}
export function familySource(engine,params,base='https://komorebip.github.io/Operation-KOMOREBI/sequence-library.html'){
  const result=generateFamily(engine,params),descriptor=familyDescriptor(engine,result.params),family=Object.entries(FAMILY_ENGINES).find(([,value])=>value===engine)[0];
  const appellReadout=engine==='appell'?(result.params.appellMode==='column'?', column='+result.params.column:', x='+result.params.x):'';
  return {key:'FAMILY:'+JSON.stringify(descriptor),type:'family',id:'FAMILY-'+engine,title:result.title+' · '+(['linear','kbonacci'].includes(engine)?`k=${result.params.k}, r=${result.params.r}, c=${result.params.c}, ${result.params.seedMode}`:engine==='theta'?`x=${result.params.x}`:engine==='theta-column'?`column=${result.params.column}`:`N=${result.params.N}, r=${result.params.r}, j=${result.params.j}${appellReadout}${engine==='secancy'?', column='+result.params.column:''}${engine==='section'?', '+result.params.parent:''}`)+(result.rationalTerms?' · '+result.params.component:''),indexKind:'local family n'+(result.rationalTerms?' · reduced '+result.params.component+'; original q(n) in family explorer':''),offset:result.offset,terms:result.terms,url:familyURL(base,family,result.params),familyDescriptor:descriptor};
}
export function customSource(data){
  if(!data||typeof data.title!=='string'||!data.title.trim()||data.title.length>120||!Number.isSafeInteger(data.offset)||Math.abs(data.offset)>1000000||!Array.isArray(data.terms)||!data.terms.length||data.terms.length>64||data.terms.some(v=>typeof v!=='string'||!/^(-?[1-9]\d*|0)$/.test(v)||v.replace('-','').length>300))throw Error('A pasted comparison needs 1–64 exact integers, up to 300 digits each, a bounded index and a title.');
  return {key:'CUSTOM:'+data.offset+':'+data.terms.join(','),type:'custom',id:'PASTED',title:data.title,indexKind:'pasted window position n',offset:data.offset,terms:data.terms.slice(),url:''};
}
export function referenceSource(hit,snapshot){
  if(!/^A\d{6}$/.test(hit.id)||!Number.isSafeInteger(hit.sample_position)||hit.sample_position<0||!Array.isArray(hit.values)||!hit.values.length||hit.values.length>256||hit.values.some(v=>typeof v!=='string'||!/^(-?[1-9]\d*|0)$/.test(v)||v.length>10000))throw Error('Choose a reference excerpt with 1–256 integer values, at most 10,000 digits each.');
  return {key:`OEIS:${hit.id}:${hit.sample_position}`,type:'oeis',id:hit.id,title:hit.id+' · '+(hit.name||'OEIS excerpt'),indexKind:'OEIS export position (mathematical offset unknown)',offset:hit.sample_position,terms:hit.values.slice(),url:'https://oeis.org/'+hit.id,snapshot};
}
export function workbenchRows(sources,options={}){
  if(sources.length>4)throw Error('Compare at most four series.');const state=validateWorkbench(options);
  if(state.alignment==='indices'&&sources.some(source=>source.type==='oeis'))throw Error('OEIS bulk exports omit mathematical offsets. Use position alignment for reference excerpts.');
  const series=sources.map(source=>{const values=source.terms.map(BigInt),transformed=transform(values,state.transform),rows=[];
    for(let i=state.skip;i<Math.min(values.length,state.skip+state.count);i++){const q=transformed[i],value=q===null?null:state.view==='mod'?mod(q.a,state.modulus):q.a;rows.push({position:i-state.skip,storedPosition:i,index:source.offset+i,x:state.alignment==='positions'?i-state.skip:source.offset+i,raw:String(values[i]),value:value===null?null:String(value),y:value===null?null:state.view==='mod'?Number(value):coordinate(q,state.scale)});}
    return {source,rows};});
  return {state,series};
}
export function agreements(result){
  const first=result.series[0];if(!first)return[];const baseline=new Map(first.rows.filter(row=>row.value!==null).map(row=>[row.x,row]));
  return result.series.slice(1).map(({source,rows})=>{let compared=0,equal=0,firstMismatch=null;for(const row of rows){const other=baseline.get(row.x);if(row.value===null||!other)continue;compared++;if(row.value===other.value)equal++;else if(firstMismatch===null)firstMismatch={x:row.x,left:other.index,right:row.index,leftValue:other.value,rightValue:row.value};}return {source:source.key,baseline:first.source.key,compared,equal,firstMismatch};});
}
export function descriptor(source){
  if(source.type==='family')return source.familyDescriptor;
  if(source.type==='custom')return {type:'custom',title:source.title,offset:source.offset,terms:source.terms};
  if(source.type==='local')return source.receipt
    ?{type:'local',id:source.id,offset:source.offset,count:source.terms.length,sha256:source.receipt}
    :{type:'local',id:source.id};
  return {type:'oeis',id:source.id,position:source.offset,count:source.terms.length,snapshot:source.snapshot};
}
export function workbenchLink(href,sources,state,chartLabels={}){
  const url=new URL(href);url.search='';url.hash='comparison';
  // Version 2 binds each local record to the exact indexed prefix published on this site.
  // Earlier local callers without receipts keep version 1 links for compatibility.
  const pinned=sources.every(source=>source.type!=='local'||/^[0-9a-f]{64}$/.test(source.receipt||''));
  const data=JSON.stringify({schema:pinned?2:1,state:validateWorkbench(state),sources:sources.map(source=>source.pending?source.descriptor:descriptor(source)),chartLabels:validateComparisonChart(chartLabels)});
  if(data.length>6000)throw Error('This comparison is too large for a view link. Export a research notebook to retain the complete data.');
  url.searchParams.set('wb',data);
  if(url.href.length>6000)throw Error('This comparison link is too large for the host. Export a research notebook JSON file to retain the complete data.');
  return url.href;
}
export function readWorkbenchLink(href,entries,snapshot){
  const params=new URL(href).searchParams;
  if(params.getAll('wb').length>1)throw Error('A comparison link must contain one set of comparison settings.');
  const raw=params.get('wb');if(!raw)return null;if(raw.length>200000)throw Error('This comparison link is too long.');const data=JSON.parse(raw);
  if(!data||![1,2].includes(data.schema)||!Array.isArray(data.sources)||data.sources.length>4)throw Error('Choose a comparison link with at most four sources.');const lookup=new Map(entries.map(entry=>[entry.id,entry])),state=validateWorkbench(data.state),chartLabels=validateComparisonChart(data.chartLabels||{});
  const sources=data.sources.map(item=>{if(item.type==='local'){
    if(!lookup.has(item.id))throw Error('A linked local record is unavailable in this catalogue.');
    const restored=localSource(lookup.get(item.id),href);
    if(data.schema===2){
      if(!/^[0-9a-f]{64}$/.test(item.sha256||'')||!Number.isSafeInteger(item.offset)||!Number.isSafeInteger(item.count)||item.count<1)
        throw Error('A linked local record is missing its exact source receipt.');
      if(item.sha256!==restored.receipt||item.offset!==restored.offset||item.count!==restored.terms.length)
        throw Error('A linked local record no longer matches its exact stored data. Recreate this comparison using current records.');
    }
    return restored;
  }
    if(item.type==='family')return familySource(item.engine,validateFamily(item.engine,item.params),href);
    if(item.type==='custom')return customSource(item);
    if(item.type!=='oeis'||!/^A\d{6}$/.test(item.id)||!Number.isSafeInteger(item.position)||item.position<0||!Number.isSafeInteger(item.count)||item.count<1||item.count>256||item.snapshot!==snapshot)throw Error('This shared OEIS excerpt does not match the available reference data. Add the excerpt again from an OEIS search.');
    return {key:`OEIS:${item.id}:${item.position}`,type:'oeis',id:item.id,title:item.id+' · OEIS excerpt · select Load OEIS excerpts',pending:true,descriptor:item};});
  // Older links kept irrelevant family fields in their descriptors. They can
  // now normalize to the same exact construction; keep its first occurrence.
  const familyKeys=new Set(),restored=sources.filter(source=>{if(source.type!=='family')return true;if(familyKeys.has(source.key))return false;familyKeys.add(source.key);return true;});
  if(new Set(restored.map(source=>source.key)).size!==restored.length)throw Error('A comparison link contains duplicate sources.');if(state.alignment==='indices'&&restored.some(source=>source.type==='oeis'))throw Error('Use position alignment for reference excerpts.');return {sources:restored,state,schema:data.schema,chartLabels};
}
const escape=value=>'"'+String(value??'').replaceAll('"','""')+'"';
export function comparisonCSV(result){return [['series_id','series_name','index_kind','stored_index_or_export_position','window_position','raw_integer','plotted_exact_integer','view','transform','alignment','modulus','source_url','reference_snapshot_sha256','attribution','license'],...result.series.flatMap(({source,rows})=>rows.map(row=>[source.id,source.title,source.indexKind,row.index,row.position,row.raw,row.value??'',result.state.view,result.state.transform,result.state.alignment,result.state.view==='mod'?result.state.modulus:'',source.url,source.snapshot||'',source.type==='oeis'?'The Online Encyclopedia of Integer Sequences, OEIS Foundation Inc.':'',source.type==='oeis'?'CC-BY-SA-4.0':'']))].map(row=>row.map(escape).join(',')).join('\r\n')+'\r\n';}
