// Offsets are mathematical indices; array positions remain internal.
import {mod, coordinate, fraction} from './sequence-atlas-core.mjs';

export function archiveWindow(entry, options={}) {
  const state={view:'mod',scale:'signed-log',start:entry.offset,size:Math.min(32,entry.terms.length),mod:7,marks:'points',color:'single',...options};
  const last=entry.offset+entry.terms.length-1;
  if(!['raw','difference','sum','mod','pairs'].includes(state.view))throw Error('Choose a listed plot view.');
  if(!['linear','signed-log'].includes(state.scale))throw Error('Choose a listed scale.');
  if(!['points','line','stems'].includes(state.marks))throw Error('Choose points, connected points, or stems.');
  if(!['single','value','index'].includes(state.color))throw Error('Choose a listed point-color mode.');
  for(const [key,min,max,label] of [['start',entry.offset,last,'First index'],['size',1,Math.min(1000,entry.terms.length),'Index positions'],['mod',2,1000000,'Modulus']]) {
    if(String(state[key]).trim()===''||!Number.isSafeInteger(Number(state[key]))||Number(state[key])<min||Number(state[key])>max){const error=Error(`${label} must be a whole number from ${min} to ${max}.`);error.field=key;throw error;}
    state[key]=Number(state[key]);
  }
  if(state.start+state.size-1>last){const error=Error(`This window goes beyond stored index ${last}. Reduce its size or first index.`);error.field='size';throw error;}
  const values=entry.terms.map(BigInt),rows=[];let sum=0n;
  for(let i=0;i<values.length;i++) {
    sum+=values[i];const n=i+entry.offset;
    if(n<state.start||n>=state.start+state.size)continue;
    let v=values[i],next=null,x=n,y;
    if(state.view==='difference')v=i?values[i]-values[i-1]:null;
    if(state.view==='sum')v=sum;
    if(state.view==='mod'||state.view==='pairs')v=mod(v,state.mod);
    if(state.view==='pairs') {x=Number(v);next=i+1<values.length?mod(values[i+1],state.mod):null;y=next===null?null:Number(next);}
    else y=v===null?null:state.view==='mod'?Number(v):coordinate(fraction(v),state.scale);
    rows.push({n,raw:String(values[i]),value:v===null?null:String(v),next:next===null?null:String(next),x,y});
  }
  return {state,rows};
}

export function moveArchiveWindow(entry,state,action){
  const {state:valid}=archiveWindow(entry,state),length=entry.terms.length,last=entry.offset+length-1;let start=valid.start,size=valid.size;
  if(action==='all'){start=entry.offset;size=Math.min(1000,length);}
  else if(action==='next')start=Math.min(last-size+1,start+size);
  else if(action==='previous')start=Math.max(entry.offset,start-size);
  else if(action==='in')size=Math.max(1,Math.ceil(size/2));
  else if(action==='out'){size=Math.min(length,1000,size*2);start=Math.min(start,last-size+1);}
  else throw Error('Choose a listed window action.');
  return {...valid,start,size};
}

export function triangleWindow(entry,row){
  if(entry.id!=='KOM084'||String(row).trim()===''||!Number.isSafeInteger(Number(row))||Number(row)<0)throw Error('Choose a stored polynomial row.');
  row=Number(row);const start=row*(row+1)/2,size=row+1;
  if(start+size>entry.terms.length)throw Error('That polynomial row is not fully stored.');
  return {start,size,view:'raw',scale:'linear',marks:'line',color:'single'};
}

export function archivePreset(entry,name){
  const presets={growth:{view:'raw',scale:'signed-log',marks:'line',color:'single'},residues:{view:'mod',scale:'linear',marks:'points',color:'value'},changes:{view:'difference',scale:'linear',marks:'stems',color:'single'},profile:{view:'raw',scale:'linear',marks:'stems',color:'single'}};
  if(!Object.hasOwn(presets,name))throw Error('Choose a listed preset.');
  return {...presets[name]};
}

export function archiveLink(href, values, hash='records') {
  const url=new URL(href);url.search='';url.hash=hash;
  for(const [key,value] of Object.entries(values))if(value!==''&&value!==null&&value!==undefined)url.searchParams.set(key,String(value));
  return url.href;
}

export function windowCSV(rows,symbol='n') {
  if(!['n','j'].includes(symbol))throw Error('Unknown index symbol.');
  return `${symbol},a(${symbol}),plotted_value,following_residue\n`+rows.map(row=>[row.n,row.raw,row.value??'',row.next??''].join(',')).join('\n')+'\n';
}
