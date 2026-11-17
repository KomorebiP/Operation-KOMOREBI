import {fraction,exact} from './sequence-atlas-core.mjs';

const q=(a,b=1n)=>{const value=fraction(BigInt(a),BigInt(b));if(!value)throw Error('A transfer coefficient has zero denominator.');return value;};
const add=(x,y)=>q(x.a*y.b+y.a*x.b,x.b*y.b),neg=x=>q(-x.a,x.b),mul=(x,y)=>q(x.a*y.a,x.b*y.b),div=(x,y)=>q(x.a*y.b,x.b*y.a);
export function rationalConvolution(a,b,count){return Array.from({length:count},(_,n)=>{let total=q(0);for(let j=0;j<=n;j++)if(a[j]&&b[n-j])total=add(total,mul(a[j],b[n-j]));return total;});}
function quotient(b,a,count){const h=[];for(let n=0;n<count;n++){let value=b[n];for(let j=0;j<n;j++)value=add(value,neg(mul(h[j],a[n-j])));h.push(div(value,a[0]));}return h;}

export function transferAnchor(entry){
  if(entry.triangle||entry.id==='KOM084'||entry.index_symbol==='j')throw Error('For coefficient tables, choose a scalar column or specialization before building this transfer.');
  if(!Number.isSafeInteger(entry.offset))throw Error('The stored sequence needs an explicit integer index offset.');
  if(!Array.isArray(entry.terms)||!entry.terms.length||entry.terms.some(value=>typeof value!=='string'||!/^(-?\d+)$/.test(value)||value.length>10000))throw Error('A transfer needs stored exact integer values.');
  const position=entry.terms.findIndex(value=>BigInt(value)!==0n);
  if(position<0)throw Error(entry.id+' has no stored nonzero anchor. A unique unit transfer cannot be calculated from this window.');
  return {position,index:entry.offset+position,value:entry.terms[position],available:entry.terms.length-position};
}

export function sequenceTransfer(source,target,count=12){
  let left,right;try{left=transferAnchor(source);}catch(error){error.field='source';throw error;}try{right=transferAnchor(target);}catch(error){error.field='target';throw error;}const maximum=Math.min(48,left.available,right.available);
  if(!Number.isSafeInteger(Number(count))||String(count).trim()===''||Number(count)<1||Number(count)>maximum)throw Object.assign(Error('Choose 1–'+maximum+' coefficients from the available nonzero tails.'),{field:'count'});
  count=Number(count);const a=source.terms.slice(left.position,left.position+count).map(value=>q(value)),b=target.terms.slice(right.position,right.position+count).map(value=>q(value));
  const h=quotient(b,a,count),inverse=quotient(a,b,count),forward=rationalConvolution(h,a,count),recovered=rationalConvolution(inverse,b,count),identity=rationalConvolution(h,inverse,count);
  const rows=Array.from({length:count},(_,j)=>({j,sourceIndex:left.index+j,targetIndex:right.index+j,source:exact(a[j]),target:exact(b[j]),kernel:exact(h[j]),inverse:exact(inverse[j]),forward:exact(forward[j]),recovered:exact(recovered[j]),residual:exact(add(forward[j],neg(b[j]))),identity:exact(identity[j])}));
  const verified=rows.every((row,j)=>row.forward===row.target&&row.recovered===row.source&&row.identity===(j?'0':'1'));
  return {sourceId:source.id,targetId:target.id,count,sourceAnchor:left,targetAnchor:right,positionShift:right.position-left.position,indexShift:right.index-left.index,integerKernel:h.every(value=>value.b===1n),integerInverse:inverse.every(value=>value.b===1n),rows,verified};
}

export function transferMatrix(result,inverse=false,size=8){
  const count=Math.min(size,result.count);return Array.from({length:count},(_,n)=>Array.from({length:count},(_,j)=>j>n?'0':result.rows[n-j][inverse?'inverse':'kernel']));
}

/** Independently evaluate one entry of a finite Toeplitz matrix product over Q.
 * The displayed matrix dimension is bounded by eight, while the transfer
 * certificate may contain up to 48 stored coefficients.
 */
export function transferProductEntry(result,row,column,order='HK',size=Math.min(8,result?.count||0)){
  if(!result||!Array.isArray(result.rows)||!Number.isSafeInteger(size)||size<1||size>8||size>result.count||
     !Number.isSafeInteger(row)||!Number.isSafeInteger(column)||row<0||column<0||row>=size||column>=size||
     !['HK','KH'].includes(order)){
    throw Error('Choose a valid matrix product, row and column within the displayed block.');
  }
  const parse=value=>{
    if(typeof value!=='string'||!/^[-]?\d+(?:\/\d+)?$/.test(value)||value.length>10000){
      throw Error('The matrix product requires exact rational coefficients.');
    }
    const [a,b='1']=value.split('/');
    return q(a,b);
  };
  const leftKey=order==='HK'?'kernel':'inverse',rightKey=order==='HK'?'inverse':'kernel';
  const terms=[];let total=q(0);
  for(let ell=column;ell<=row;ell++){
    const left=result.rows[row-ell]?.[leftKey],right=result.rows[ell-column]?.[rightKey];
    const product=mul(parse(left),parse(right));
    total=add(total,product);
    terms.push({ell,left,right,product:exact(product)});
  }
  const expected=row===column?'1':'0',value=exact(total);
  return {row,column,order,size,terms,value,expected,verified:value===expected};
}

export function transferCSV(result){
  const columns=['source_id','target_id','source_zero_prefix','target_zero_prefix','window_position_shift','original_index_shift','coefficient_domain','tail_position','source_index','target_index','source_integer','target_integer','kernel_h','inverse_k','forward_exact','recovered_exact','residual','kernel_product'];
  const rows=result.rows.map(row=>[result.sourceId,result.targetId,result.sourceAnchor.position,result.targetAnchor.position,result.positionShift,result.indexShift,'Q',row.j,row.sourceIndex,row.targetIndex,row.source,row.target,row.kernel,row.inverse,row.forward,row.recovered,row.residual,row.identity]);
  return [columns,...rows].map(row=>row.map(value=>'"'+String(value).replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
}

export function transferJSON(result){
  return JSON.stringify({
    schema:1,
    calculation:'finite ordinary power series transfer',
    coefficient_domain:'Q',
    source_id:result.sourceId,
    target_id:result.targetId,
    coefficients:result.count,
    source_anchor:result.sourceAnchor,
    target_anchor:result.targetAnchor,
    window_position_shift:result.positionShift,
    original_index_shift:result.indexShift,
    integer_kernel:result.integerKernel,
    integer_inverse:result.integerInverse,
    verified:result.verified,
    certificate_conditions:['H*A=B','K*B=A','H*K=1'],
    rows:result.rows
  },null,2)+'\n';
}

export function transferLink(href,result){const url=new URL(href);url.search='';url.hash='transfers';url.searchParams.set('tr-source',result.sourceId);url.searchParams.set('tr-target',result.targetId);url.searchParams.set('tr-count',String(result.count));return url.href;}
