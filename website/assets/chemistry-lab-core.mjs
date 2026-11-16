// Rational calculations for the fixed, hash-bound nine-state fixtures.
// Exact certificates use BigInt; SVG coordinates and short labels are rounded.
const abs=n=>n<0n?-n:n;
const gcd=(a,b)=>{a=abs(a);b=abs(b);while(b)[a,b]=[b,a%b];return a;};
export function rational(value){
  if(typeof value==='object'&&typeof value?.n==='bigint')return value;
  const s=String(value);
  if(s.length>12000||!/^[-+]?\d+(?:\/[1-9]\d*)?$/.test(s))throw new RangeError('Invalid fixture fraction.');
  const [n,d='1']=s.split('/');return q(BigInt(n),BigInt(d));
}
function q(n,d=1n){if(!d)throw new RangeError('Zero denominator.');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return {n:n/g,d:d/g};}
export const add=(a,b)=>q(a.n*b.d+b.n*a.d,a.d*b.d);
export const neg=a=>q(-a.n,a.d);
export const sub=(a,b)=>add(a,neg(b));
export const mul=(a,b)=>q(a.n*b.n,a.d*b.d);
export const div=(a,b)=>q(a.n*b.d,a.d*b.n);
export const str=a=>a.d===1n?String(a.n):`${a.n}/${a.d}`;
const zero=()=>q(0n),one=()=>q(1n),square=a=>mul(a,a);
const le=(a,b)=>a.n*b.d<=b.n*a.d;
const dot=(a,b)=>a.reduce((s,v,i)=>add(s,mul(v,b[i])),zero());
const matrix=a=>a.map(row=>row.map(rational));
const flatten=a=>a.flat();
export const multiply=(a,b)=>a.map(row=>b[0].map((_,j)=>dot(row,b.map(r=>r[j]))));
export function approximate(a){
  a=rational(a);if(!a.n)return 0;
  const n=String(abs(a.n)),d=String(a.d),size=16;
  return (a.n<0n?-1:1)*Number(n.slice(0,size))/Number(d.slice(0,size))*10**(Math.max(0,n.length-size)-Math.max(0,d.length-size));
}
function isqrt(n){if(n<2n)return n;let x=1n<<BigInt(Math.ceil(n.toString(2).length/2));while(true){const y=(x+n/x)/2n;if(y>=x)return x;x=y;}}
export function sqrtUpper(a){
  a=rational(a);if(a.n<0n)throw new RangeError('Negative squared radius.');
  const n=isqrt(a.n),d=isqrt(a.d);if(n*n===a.n&&d*d===a.d)return q(n,d);
  const scale=10n**30n,k=isqrt(a.n*scale*scale/a.d);
  return q(k*k*a.d===a.n*scale*scale?k:k+1n,scale);
}
function determinant(input){
  const a=input.map(row=>row.slice());let result=one();
  for(let j=0;j<a.length;j++){
    const p=a.findIndex((row,i)=>i>=j&&row[j].n!==0n);if(p<0)return zero();
    if(p!==j){[a[j],a[p]]=[a[p],a[j]];result=neg(result);}
    const pivot=a[j][j];result=mul(result,pivot);
    for(let i=j+1;i<a.length;i++){
      const f=div(a[i][j],pivot);
      for(let k=j+1;k<a.length;k++)a[i][k]=sub(a[i][k],mul(f,a[j][k]));
    }
  }return result;
}
export function positiveSemidefinite(a){
  for(let i=0;i<a.length;i++)for(let j=0;j<a.length;j++)if(str(a[i][j])!==str(a[j][i]))return false;
  for(let mask=1;mask<(1<<a.length);mask++){
    const ids=a.map((_,i)=>i).filter(i=>mask&(1<<i));
    if(determinant(ids.map(i=>ids.map(j=>a[i][j]))).n<0n)return false;
  }return true;
}
export function decode(data,sample){
  const basis=data.basis.map(matrix),probes=matrix(data.probes),left=matrix(data.left_inverse);
  const observed=matrix(sample.cache.action_matrix),y=flatten(observed);
  const theta=left.map(row=>dot(row,y));
  const h=basis[0].map((row,i)=>row.map((_,j)=>dot(theta,basis.map(a=>a[i][j]))));
  const actions=multiply(h,probes);
  const residual2=flatten(actions).reduce((s,v,i)=>add(s,square(sub(y[i],v))),zero());
  const c=Array.from({length:5},()=>Array.from({length:5},zero));let k=6;
  for(let i=0;i<5;i++)for(let j=i;j<5;j++)c[i][j]=c[j][i]=theta[k++];
  return {h,theta,actions,observed,residual2,c,positive:positiveSemidefinite(c)};
}
export function verifyResponse(decoded,sample,eta){
  const saved=sample.responses[eta];if(!saved)throw new RangeError('Unsupported broadening.');
  const e=rational(sample.cache.energy),t=rational(eta),b=sample.cache.b_hat.map(rational);
  const u=saved.solution_real.map(rational),v=saved.solution_imaginary.map(rational);
  for(let i=0;i<9;i++){
    const au=sub(mul(e,u[i]),dot(decoded.h[i],u)),av=sub(mul(e,v[i]),dot(decoded.h[i],v));
    if(sub(sub(au,mul(t,v[i])),b[i]).n||add(av,mul(t,u[i])).n)throw new Error('Response identity failed.');
  }
  if(str(dot(b,u))!==saved.real||str(dot(b,v))!==saved.imaginary)throw new Error('Response center failed.');
  return {real:rational(saved.real),imaginary:rational(saved.imaginary)};
}
export function analyze(data,sample,decoded,{epsilon,delta,eta}){
  epsilon=rational(epsilon);delta=rational(delta);eta=rational(eta);
  if(epsilon.n<0n||delta.n<0n||eta.n<=0n)throw new RangeError('Use nonnegative errors and positive broadening.');
  const consistent=le(decoded.residual2,square(epsilon));
  const base={consistent,residual2:decoded.residual2,epsilon,delta,eta,positiveEstimate:decoded.positive,feasibility:consistent?(decoded.positive?true:null):false};
  if(!consistent)return base;
  const radius2=mul(rational(20),sub(square(epsilon),decoded.residual2)),rH=sqrtUpper(radius2);
  if(radius2.n===0n&&!decoded.positive)base.feasibility=false;
  const shifted=decoded.c.map((row,i)=>row.map((x,j)=>i===j?sub(x,div(rH,rational(4))):x));
  const b=sample.cache.b_hat.map(rational),b2=dot(b,b),bNorm=sqrtUpper(b2);
  const operatorPart=div(mul(b2,rH),square(eta));
  const sourcePart=div(mul(delta,add(mul(rational(2),bNorm),delta)),eta);
  const radius=add(operatorPart,sourcePart);
  return {...base,radius2,rH,operatorPart,sourcePart,radius,allPositive:positiveSemidefinite(shifted),singleton:radius2.n===0n};
}
export function probeView(data,decoded,count){
  if(![1,2,3].includes(count))throw new RangeError('Choose one, two or three probes.');
  const stage=data.stages[count-1],witness=matrix(stage.witness_operator);
  const alternative=decoded.h.map((row,i)=>row.map((x,j)=>add(x,witness[i][j])));
  const probes=matrix(data.probes).map(row=>row.slice(0,count));
  const a=multiply(decoded.h,probes),b=multiply(alternative,probes);
  if(a.some((row,i)=>row.some((x,j)=>str(x)!==str(b[i][j]))))throw new Error('Invisible direction identity failed.');
  return {stage,witness,alternative,actions:a};
}
export const ERROR_FACTORS=['0','1/2','1','2','10','100','1000','10000'];
export const SOURCE_ERRORS=['0','1/8192','1/1024','1/128','1/16'];
export function certificate(data,sample,decoded,result,center,settings){
  const exact=v=>v===undefined?null:str(v);
  return {format:'komorebi-chemistry-lab-v1',example:sample.id,settings,source_archive_sha256:data.archive_sha256,
    source_cache_sha256:sample.source_sha256||null,scope:'Conditional on the declared 21-dimensional family and valid action/source caps. Browser replays rational identities; controls do not measure physical error.',
    raw_error_radius:exact(result.epsilon),source_radius:exact(result.delta),eta:exact(result.eta),energy:sample.cache.energy,
    theta:decoded.theta.map(str),estimated_H:decoded.h.map(row=>row.map(str)),least_squares_residual_squared:exact(result.residual2),
    full_linear_consistent:result.consistent,positive_integral_estimate:result.positiveEstimate,positive_integral_feasibility:result.feasibility,
    all_compatible_positive_integral_sufficient_test:result.consistent?result.allPositive:null,
    operator_radius_squared_upper:exact(result.radius2),operator_radius_rational_upper:exact(result.rH),
    response_center:result.consistent?{real:str(center.real),imaginary:str(center.imaginary)}:null,
    response_radius_rational_upper:exact(result.radius),rounding:'Square roots rounded outward to rational multiples of 1e-30; exact squares remain exact.'};
}
