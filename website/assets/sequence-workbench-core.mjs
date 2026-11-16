import {transform,coordinate,mod} from './sequence-atlas-core.mjs';

export const WORKBENCH_DEFAULTS=Object.freeze({view:'values',transform:'raw',scale:'signed-log',alignment:'positions',skip:0,count:32,modulus:7,marks:'line'});
export function validateWorkbench(options={}){
  const state={...WORKBENCH_DEFAULTS,...Object.fromEntries(Object.keys(WORKBENCH_DEFAULTS).filter(key=>Object.hasOwn(options,key)).map(key=>[key,options[key]]))};
  for(const [key,choices]of Object.entries({view:['values','mod'],transform:['raw','difference','sum'],scale:['linear','signed-log'],alignment:['positions','indices'],marks:['line','points']}))if(!choices.includes(state[key]))throw Error(`Choose a listed ${key}.`);
  for(const [key,min,max]of [['skip',0,1000000],['count',1,1000],['modulus',2,1000000]]){if(String(state[key]).trim()===''||!Number.isSafeInteger(Number(state[key]))||Number(state[key])<min||Number(state[key])>max)throw Error(`${key} must be an integer from ${min} to ${max}.`);state[key]=Number(state[key]);}
  return state;
}
export function localSource(entry,base){return {key:entry.id,type:'local',id:entry.id,title:entry.title,indexKind:entry.index_symbol==='j'?'local flat index j':'local index n',offset:entry.offset,terms:entry.terms,url:base?new URL(entry.url,base).href:entry.url,collection:entry.collection};}
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
export function descriptor(source){return source.type==='local'?{type:'local',id:source.id}:{type:'oeis',id:source.id,position:source.offset,count:source.terms.length,snapshot:source.snapshot};}
export function workbenchLink(href,sources,state){const url=new URL(href);url.search='';url.hash='comparison';url.searchParams.set('wb',JSON.stringify({schema:1,state:validateWorkbench(state),sources:sources.map(source=>source.pending?source.descriptor:descriptor(source))}));return url.href;}
export function readWorkbenchLink(href,entries,snapshot){
  const raw=new URL(href).searchParams.get('wb');if(!raw)return null;if(raw.length>6000)throw Error('This comparison link is too long.');const data=JSON.parse(raw);
  if(data.schema!==1||!Array.isArray(data.sources)||data.sources.length>4)throw Error('Choose a comparison link with at most four sources.');const lookup=new Map(entries.map(entry=>[entry.id,entry])),state=validateWorkbench(data.state);
  const sources=data.sources.map(item=>{if(item.type==='local'){if(!lookup.has(item.id))throw Error('A linked local record is unavailable in this catalogue.');return localSource(lookup.get(item.id),href);}
    if(item.type!=='oeis'||!/^A\d{6}$/.test(item.id)||!Number.isSafeInteger(item.position)||item.position<0||!Number.isSafeInteger(item.count)||item.count<1||item.count>256||item.snapshot!==snapshot)throw Error('This shared OEIS excerpt does not match the available reference data. Add the excerpt again from an OEIS search.');
    return {key:`OEIS:${item.id}:${item.position}`,type:'oeis',id:item.id,title:item.id+' · OEIS excerpt · select Load OEIS excerpts',pending:true,descriptor:item};});
  if(new Set(sources.map(source=>source.key)).size!==sources.length)throw Error('A comparison link contains duplicate sources.');if(state.alignment==='indices'&&sources.some(source=>source.type==='oeis'))throw Error('Use position alignment for reference excerpts.');return {sources,state};
}
const escape=value=>'"'+String(value??'').replaceAll('"','""')+'"';
export function comparisonCSV(result){return [['series_id','series_name','index_kind','stored_index_or_export_position','window_position','raw_integer','plotted_exact_integer','view','transform','alignment','modulus','source_url','reference_snapshot_sha256','attribution','license'],...result.series.flatMap(({source,rows})=>rows.map(row=>[source.id,source.title,source.indexKind,row.index,row.position,row.raw,row.value??'',result.state.view,result.state.transform,result.state.alignment,result.state.view==='mod'?result.state.modulus:'',source.url,source.snapshot||'',source.type==='oeis'?'The Online Encyclopedia of Integer Sequences, OEIS Foundation Inc.':'',source.type==='oeis'?'CC-BY-SA-4.0':'']))].map(row=>row.map(escape).join(',')).join('\r\n')+'\r\n';}
