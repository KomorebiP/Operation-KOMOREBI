import {searchEntries} from './sequence-atlas-search.mjs';

export const SEARCH_KEYS=['q','scope','collection','kind','representation','status','match','sort','hits','saved','mode','paper'];
export const RECORD_FILTERS=['collection','kind','representation','status','hits','saved','match'];
export const FAMILY_FILTERS=['mode','paper'];

export function emptySearch(scope='records'){
  return Object.fromEntries(SEARCH_KEYS.map(key=>[key,key==='scope'?(scope==='families'?'families':'records'):key==='sort'?'relevance':key==='match'?'any':'']));
}

export function normalizeSearch(value){
  const state={...emptySearch(value.scope),...value};
  state.scope=state.scope==='families'?'families':'records';
  for(const key of state.scope==='families'?RECORD_FILTERS:FAMILY_FILTERS)state[key]=key==='match'?'any':'';
  return state;
}

export function librarySearch(entries,families,state,saved=new Set()){
  const s=normalizeSearch(state);
  return searchEntries(s.scope==='families'?families:entries,s.q,{sort:s.sort,match:s.match}).filter(({entry})=>
    (!s.collection||entry.collection===s.collection)&&
    (!s.kind||entry.kind===s.kind)&&
    (!s.representation||entry.formulas.some(f=>f.kind===s.representation))&&
    (!s.status||entry.status===s.status)&&
    (!s.hits||(s.hits==='matched')===Boolean(entry.matches?.length))&&
    (!s.saved||saved.has(entry.id))&&
    (!s.mode||entry.mode===s.mode)&&
    (!s.paper||entry.paper_refs?.includes(s.paper))
  );
}

export function librarySearchCSV(hits,scope,base){
  const rows=scope==='families'
    ?[['id','title','construction_type','parameter_domain','definition','notes','source_id','source_title','source','indexed_records','url'],
      ...hits.map(({entry:e})=>[e.id,e.title,e.mode,e.domain,e.formula,e.note,e.paper,e.paper_title,e.source,e.record_ids.length,new URL(e.url,base).href])]
    :[['id','title','family','collection','offset','formulas','construction_type','source','indexed_records','url'],
      ...hits.map(({entry:e})=>[e.id,e.title,e.kind,e.collection,e.offset,e.formulas.length,e.mode||'',e.source||'',e.record_ids?.length??'',new URL(e.url,base).href])];
  return rows.map(row=>row.map(value=>'"'+String(value??'').replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
}
