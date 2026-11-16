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
