import {constantRecurrence} from './sequence-family-core.mjs';
const residue=(value,m)=>Number((BigInt(value)%BigInt(m)+BigInt(m))%BigInt(m));
export function modularCycle(options={},modulus=7,maximum=5000){
  if(!Number.isSafeInteger(Number(modulus))||Number(modulus)<2||Number(modulus)>256)throw Error('Choose an integer modulus from 2 to 256.');
  if(!Number.isSafeInteger(Number(maximum))||Number(maximum)<1||Number(maximum)>20000)throw Error('Choose a state-search bound from 1 to 20,000.');
  modulus=Number(modulus);maximum=Number(maximum);const model=constantRecurrence(options),coefficients=model.coefficients.map(v=>residue(v,modulus)),initial=model.seeds.map(v=>residue(v,modulus)),seen=new Map(),values=[],states=[];let state=initial.slice(),first=null,repeat=null;
  for(let n=0;n<=maximum;n++){
    const key=state.join(',');if(seen.has(key)){first=seen.get(key);repeat=n;break;}if(n===maximum)break;seen.set(key,n);values.push(state[0]);if(states.length<64)states.push(state.slice());let next=0;for(let j=1;j<=model.order;j++)next=(next+coefficients[j-1]*state[model.order-j])%modulus;state=[...state.slice(1),next];
  }
  return {schema:1,model,modulus,maximum,scanned:seen.size,certified:repeat!==null,preperiod:first,period:repeat===null?null:repeat-first,repeatIndex:repeat,repeatedState:repeat===null?null:state.slice(),initialState:initial,coefficients,values:values.slice(0,256),states,scope:'Deterministic complete recurrence states modulo m. A repeated complete state certifies the subsequent cycle; reaching the search bound without a repeat supplies no period claim.'};
}
export function modularCSV(result){return 'n,residue,modulus,certified_preperiod,certified_period\r\n'+result.values.map((v,n)=>[n,v,result.modulus,result.preperiod??'',result.period??''].join(',')).join('\r\n')+'\r\n';}
