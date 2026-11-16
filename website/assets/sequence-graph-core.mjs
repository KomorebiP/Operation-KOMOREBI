import {sequenceTransfer,rationalConvolution,transferAnchor} from './sequence-transfer-core.mjs';
import {readQ} from './sequence-family-core.mjs';
import {exact} from './sequence-atlas-core.mjs';
export function directedRelations(edges){return edges.flatMap(edge=>[{...edge,reversed:false},...(edge.reversible?[{...edge,key:edge.key+'-reverse',source:edge.target,target:edge.source,reversed:true,statement:'Inverse direction of the cited reversible relation. '+edge.statement}]:[])]);}
export function relationPath(edges,source,target,maximum=6){
  if(!Number.isInteger(maximum)||maximum<1||maximum>8)throw Error('Choose a path bound from 1 to 8 relations.');if(source===target)return[];const outgoing=new Map();for(const edge of directedRelations(edges)){if(!outgoing.has(edge.source))outgoing.set(edge.source,[]);outgoing.get(edge.source).push(edge);}const queue=[{id:source,path:[]}],seen=new Set([source]);
  for(let i=0;i<queue.length;i++){const node=queue[i];if(node.path.length>=maximum)continue;for(const edge of outgoing.get(node.id)||[]){const path=[...node.path,edge];if(edge.target===target)return path;if(!seen.has(edge.target)){seen.add(edge.target);queue.push({id:edge.target,path});}}}return null;
}
export function composeScalarTransfers(a,b,c,requested=12){
  const maximum=Math.min(48,...[a,b,c].map(e=>transferAnchor(e).available));if(!Number.isSafeInteger(Number(requested))||Number(requested)<1||Number(requested)>maximum)throw Error('Choose 1–'+maximum+' common tail coefficients.');
  const count=Number(requested),ab=sequenceTransfer(a,b,count),bc=sequenceTransfer(b,c,count),ac=sequenceTransfer(a,c,count),composed=rationalConvolution(bc.rows.map(r=>readQ(r.kernel)),ab.rows.map(r=>readQ(r.kernel)),count),inverse=rationalConvolution(ab.rows.map(r=>readQ(r.inverse)),bc.rows.map(r=>readQ(r.inverse)),count);
  const rows=ac.rows.map((row,i)=>({j:i,sourceIndex:row.sourceIndex,viaIndex:ab.rows[i].targetIndex,targetIndex:row.targetIndex,first:ab.rows[i].kernel,second:bc.rows[i].kernel,composed:exact(composed[i]),direct:row.kernel,inverse:exact(inverse[i]),verified:exact(composed[i])===row.kernel&&exact(inverse[i])===row.inverse}));
  return {source:a.id,via:b.id,target:c.id,count,rows,positionShift:ac.positionShift,indexShift:ac.indexShift,verified:rows.every(r=>r.verified)&&ab.positionShift+bc.positionShift===ac.positionShift&&ab.indexShift+bc.indexShift===ac.indexShift,scope:'Composition of constructed ordinary tail kernels over Q, modulo z^L, including the zero-prefix shifts. This does not establish recurrence equivalence or predict further terms.'};
}
