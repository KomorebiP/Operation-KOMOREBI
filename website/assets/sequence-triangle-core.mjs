import {triangleLayout} from './sequence-archive-core.mjs';
import {mod} from './sequence-atlas-core.mjs';

export function tableState(entry, options={}) {
  const rows=triangleLayout(entry), width=Math.max(...rows.map(row=>row.size));
  const state={kind:'row',view:'exact',mod:7,scale:'signed-log',zero:'on',...options};
  for(const [key,allowed] of Object.entries({kind:['row','column','diagonal'],view:['exact','mod'],scale:['linear','signed-log'],zero:['on','off']})) {
    if(!allowed.includes(state[key]))throw Object.assign(Error('Choose a listed '+key+' option.'),{field:key});
  }
  const maximum=state.kind==='row'?rows.length-1:width-1;
  if(state.index===undefined)state.index=Math.min(state.kind==='row'?4:1,maximum);
  for(const [key,low,high,label] of [['index',0,maximum,'Selection index'],['mod',2,1000000,'Modulus']]) {
    if(String(state[key]).trim()===''||!Number.isSafeInteger(Number(state[key]))||Number(state[key])<low||Number(state[key])>high)throw Object.assign(Error(`${label} must be a whole number from ${low} to ${high}.`),{field:key});
    state[key]=Number(state[key]);
  }
  return state;
}

export function tableCells(entry) {
  return triangleLayout(entry).flatMap(row=>Array.from({length:row.size},(_,k)=>{
    const j=row.start+k,raw=entry.terms[j-entry.offset];
    if(!/^-?\d+$/.test(String(raw)))throw Error('A stored coefficient is not an exact integer.');
    const multiplier=entry.triangle?.degree_multiplier??1;
    if(!Number.isSafeInteger(multiplier)||multiplier<1)throw Error('Invalid source-degree metadata.');
    return {j,n:row.row,k,degree:row.row*multiplier,raw:String(raw),edge:row.size-1-k};
  }));
}

export function tableSlice(entry, options={}) {
  const state=tableState(entry,options),cells=tableCells(entry).filter(cell=>cell[state.kind==='row'?'n':state.kind==='column'?'k':'edge']===state.index);
  const axis=state.kind==='row'?'k':'n';
  const label=state.kind==='row'?`Row n=${state.index}`:state.kind==='column'?`Column k=${state.index}`:`Right-edge diagonal d=${state.index}`;
  return {state,axis,label,cells:cells.map(cell=>({...cell,x:cell[axis],residue:String(mod(BigInt(cell.raw),state.mod))}))};
}

export function tableCSV(slice) {
  const residue=slice.state.view==='mod';
  return 'flat_j,row_n,column_k,source_degree,coefficient'+(residue?',residue_mod_'+slice.state.mod:'')+'\n'+slice.cells.map(cell=>[cell.j,cell.n,cell.k,cell.degree,cell.raw,...(residue?[cell.residue]:[])].join(',')).join('\n')+'\n';
}

export function shortInteger(raw) {
  const digits=raw.replace(/^-/,'');
  return digits.length>48?`${raw.startsWith('-')?'negative ':''}${digits.length} digits, beginning with ${digits.slice(0,10)}, ending with ${digits.slice(-6)}`:raw;
}

export const TABLE_KEYS=['kind','index','view','mod','scale','zero'];
export function tableLink(href,state) {
  const url=new URL(href);url.hash='triangle';
  for(const key of TABLE_KEYS)url.searchParams.set('table-'+key,String(state[key]));
  return url.href;
}

export function tableSearch(href,slice) {
  const query='terms:'+slice.cells.map(cell=>cell.raw).join(',');
  if(query.length>20000)throw Error('This selection is too long for one search. Download its CSV instead.');
  const url=new URL('../sequence-library.html',href);url.searchParams.set('q',query);url.hash='library-search';return url.href;
}
