// Exact, bounded sequence calculations. No floating point, network or storage.
// Author: Komorebi P. Source: Closed Forms Collections II–III.
export const MODE_LIMITS=Object.freeze({
  sparse:{maxIndex:96,maxCount:32},
  padovan:{maxIndex:96,maxCount:32},
  fourblock:{maxIndex:32,maxCount:24},
  jet:{maxIndex:80,maxCount:32},
  hankel:{maxIndex:12,maxCount:13},
  beta_moments:{maxIndex:96,maxCount:32},
  beta_hankel:{maxIndex:17,maxCount:18},
  differential_hankel:{maxIndex:12,maxCount:13},
  differential_moments:{maxIndex:160,maxCount:32},
  meixner:{maxIndex:96,maxCount:32}
});
export const MODE_DEFAULTS=Object.freeze({
  sparse:{mode:'sparse',start:'0',count:'12',p:'2',q:'5',r:'1',u:'1',v:'1'},
  padovan:{mode:'padovan',start:'0',count:'12',h:'1'},
  fourblock:{mode:'fourblock',start:'1',count:'10',a:'0'},
  jet:{mode:'jet',start:'0',count:'12',d:'1',lambda:'1',c:'1'},
  hankel:{mode:'hankel',start:'0',count:'8',d:'1',c:'1'},
  beta_moments:{mode:'beta_moments',start:'0',count:'12',L:'4',a:'1',b:'1'},
  beta_hankel:{mode:'beta_hankel',start:'0',count:'8',L:'4',a:'1',b:'1'},
  differential_hankel:{mode:'differential_hankel',start:'0',count:'8',a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'},
  differential_moments:{mode:'differential_moments',start:'0',count:'12',a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'},
  meixner:{mode:'meixner',start:'0',count:'12',s:'1',twox:'2'}
});
export const MODE_FIELDS=Object.freeze({
  sparse:['p','q','r','u','v'],
  padovan:['h'],
  fourblock:['a'],
  jet:['d','lambda','c'],
  hankel:['d','c'],
  beta_moments:['L','a','b'],
  beta_hankel:['L','a','b'],
  differential_hankel:['a0','a1','a2','a3','c0','c1','c2','c3'],
  differential_moments:['a0','a1','a2','a3','c0','c1','c2','c3'],
  meixner:['s','twox']
});
const FIELD_LIMITS=Object.freeze({
  p:[1,16],q:[1,16],r:[-12,12],u:[-12,12],v:[-12,12],
  d:[0,8],lambda:[-12,12],c:[-12,12],s:[-12,20],twox:[-20,20],
  h:[1,8],a:[-12,12],b:[1,12],L:[0,12],
  a0:[-12,12],a1:[-12,12],a2:[-12,12],a3:[-12,12],
  c0:[-12,12],c1:[-12,12],c2:[-12,12],c3:[-12,12]
});
function integer(value,label,min,max){
  const text=String(value);
  if(!/^-?(0|[1-9][0-9]*)$/.test(text))throw Error(label+' must be an integer.');
  const n=Number(text);
  if(!Number.isSafeInteger(n)||n<min||n>max)throw Error(label+' must be between '+min+' and '+max+'.');
  return n;
}
export function binomial(n,k){
  if(k<0||k>n)return 0n;
  k=Math.min(k,n-k);
  let result=1n;
  for(let j=1;j<=k;j++)result=result*BigInt(n-j+1)/BigInt(j);
  return result;
}
export function falling(n,d){
  if(d<0)throw Error('Falling-factorial order must be nonnegative.');
  if(n<d)return 0n;
  let value=1n;
  for(let j=0;j<d;j++)value*=BigInt(n-j);
  return value;
}
function abs(n){return n<0n?-n:n;}
function gcd(a,b){a=abs(a);b=abs(b);while(b){const t=a%b;a=b;b=t;}return a;}
function addFraction(a,b,c,d){
  if(d===0n||b===0n)throw Error('Division by zero.');
  const top=a*d+c*b,bottom=b*d,div=gcd(top,bottom);
  return [top/div,bottom/div];
}
export function sparseCoefficients(p,q,r,u,v,last){
  if(!Number.isInteger(last)||last<0||last>96)throw Error('The requested index is outside the exact calculator limit.');
  const P=BigInt(p),Q=BigInt(q),R=BigInt(r),U=BigInt(u),V=BigInt(v);
  const values=[1n];
  for(let n=1;n<=last;n++){
    const N=BigInt(n);
    let numerator=0n;
    if(n>=p)numerator+=U*(N+(R-1n)*P)*values[n-p];
    if(n>=q)numerator+=V*(N+(R-1n)*Q)*values[n-q];
    if(numerator%N!==0n)throw Error('The sparse exact recurrence failed its divisibility check.');
    values.push(numerator/N);
  }
  return values;
}

export function rising(n,k){
  if(k<0)throw Error('Rising-factorial order must be nonnegative.');
  let value=1n;
  for(let j=0;j<k;j++)value*=BigInt(n)+BigInt(j);
  return value;
}
export function padovanCoefficients(h,last){
  const denominator=sparseCoefficients(2,3,h,1,1,last),values=[];
  for(let n=0;n<=last;n++){
    let sum=0n;
    for(let j=0;j<=Math.min(h,Math.floor(n/2));j++){
      sum+=(j%2?-1n:1n)*binomial(h,j)*denominator[n-2*j];
    }
    values.push(sum);
  }
  return values;
}
export function fourBlockCoefficients(a,last){
  const parameter=BigInt(a),values=[0n];
  const A=m=>1n-4n*BigInt(m)*parameter+
    2n*BigInt(m)*BigInt(4*m-1)*parameter*parameter;
  for(let m=1;m<=last;m++){
    let value=(m%2===1?1n:-1n)*A(m);
    for(let k=1;k<m;k++){
      value+=(k%2===1?1n:-1n)*binomial(4*m-1,4*k)*A(k)*values[m-k];
    }
    values.push(value);
  }
  return values;
}
export function betaWeights(L,a,b){
  return Array.from({length:L+1},(_,k)=>
    binomial(L,k)*rising(a,k)*rising(b,L-k));
}
export function betaMomentCoefficients(L,a,b,last){
  if(!Number.isInteger(last)||last<0||last>96)
    throw Error('The beta moment index is outside the exact calculator limit.');
  const weights=betaWeights(L,a,b);
  return Array.from({length:last+1},(_,n)=>
    weights.reduce((sum,weight,k)=>sum+weight*BigInt(k)**BigInt(n),0n));
}
export function betaHankelCoefficients(L,a,b,last){
  if(!Number.isInteger(last)||last<0||last>17)
    throw Error('The beta determinant order is outside the exact calculator limit.');
  const available=Math.min(last,L+1),highestMoment=Math.max(0,2*available-2);
  const moments=betaMomentCoefficients(L,a,b,highestMoment);
  const result=[];
  for(let n=0;n<=last;n++){
    if(n>L+1){result.push(0n);continue;}
    result.push(bareissDeterminant(Array.from({length:n},(_,i)=>
      Array.from({length:n},(_,j)=>moments[i+j]))));
  }
  return result;
}

export function centralWeightedMoment(n,d,c){
  if(n<0)return 0n;
  const m=Math.floor(n/2);
  const base=falling(m,d)*binomial(2*m,m);
  return n%2===0?base:BigInt(c)*BigInt(n)*base;
}
export function weightedJet(n,d,lambda,c){
  if(n<0)return 0n;
  const shift=BigInt(lambda);
  let sum=0n;
  for(let k=0;k<=n;k++){
    sum+=binomial(n,k)*shift**BigInt(n-k)*centralWeightedMoment(k,d,c);
  }
  return sum;
}
export function bareissDeterminant(input){
  const n=input.length;
  if(!n)return 1n;
  if(input.some(row=>row.length!==n))throw Error('Determinant matrix must be square.');
  const a=input.map(row=>row.map(BigInt));
  let sign=1n,denominator=1n;
  for(let k=0;k<n-1;k++){
    if(a[k][k]===0n){
      const pivot=a.findIndex((row,i)=>i>k&&row[k]!==0n);
      if(pivot===-1)return 0n;
      [a[k],a[pivot]]=[a[pivot],a[k]];
      sign=-sign;
    }
    const pivot=a[k][k];
    for(let i=k+1;i<n;i++){
      for(let j=k+1;j<n;j++){
        const numerator=pivot*a[i][j]-a[i][k]*a[k][j];
        if(numerator%denominator!==0n)throw Error('Fraction-free determinant division was not exact.');
        a[i][j]=numerator/denominator;
      }
      a[i][k]=0n;
    }
    denominator=pivot;
  }
  return sign*a[n-1][n-1];
}
export function weightedHankel(n,d,c){
  return bareissDeterminant(Array.from({length:n},(_,i)=>
    Array.from({length:n},(_,j)=>centralWeightedMoment(i+j,d,c))));
}

export function polynomialDifferentialMoment(n, weights, operator) {
  if(!Number.isSafeInteger(n)||n<0)throw Error('The moment index must be nonnegative.');
  let result=0n;
  for(let k=0;k<operator.length&&k<=n;k++){
    if((n-k)%2)continue;
    const m=(n-k)/2;
    let weighted=0n;
    for(let d=0;d<weights.length;d++)
      weighted+=BigInt(weights[d])*falling(m,d);
    result+=BigInt(operator[k])*falling(n,k)*weighted*binomial(2*m,m);
  }
  return result;
}

function exactPolynomialProduct(left,right){
  const values=Array(left.length+right.length-1).fill(0n);
  for(let i=0;i<left.length;i++)
    for(let j=0;j<right.length;j++)
      values[i+j]+=left[i]*right[j];
  return values;
}
function trimmedPolynomial(values){
  while(values.length>1&&values[values.length-1]===0n)values.pop();
  return values;
}
function _effectiveExactCoefficients(values){
  return trimmedPolynomial(values.map(value=>BigInt(value)));
}
export function differentialMomentGeneratingFunction(weights,operator){
  // Exact universal algebraic OGF for polynomially weighted moments.
  // M(z)=R(z)/(1-4z^2)^(D+r+1/2), deg R<=2(D+r).
  const a=_effectiveExactCoefficients(weights);
  const c=_effectiveExactCoefficients(operator);
  const D=a.length-1,r=c.length-1,h=[1n,0n,-4n];
  const powers=[[1n]];
  for(let j=1;j<=Math.max(D,r);j++)
    powers.push(exactPolynomialProduct(powers[j-1],h));
  let current=Array(2*D+1).fill(0n);
  for(let d=0;d<=D;d++){
    let factor=1n;
    for(let j=d+1;j<=2*d;j++)factor*=BigInt(j);
    const term=exactPolynomialProduct(
      Array(2*d).fill(0n).concat([a[d]*factor]),powers[D-d]);
    term.forEach((value,j)=>{current[j]+=value;});
  }
  const numerator=Array(2*(D+r)+1).fill(0n);
  for(let k=0;k<=r;k++){
    const term=exactPolynomialProduct(current,powers[r-k]);
    term.forEach((value,j)=>{numerator[j]+=c[k]*value;});
    if(k===r)break;
    const next=Array(current.length+3).fill(0n);
    current.forEach((value,j)=>{
      next[j+1]+=BigInt(j+1)*value;
      next[j+3]+=4n*BigInt(2*D+2*k-j)*value;
    });
    current=trimmedPolynomial(next);
  }
  const R=trimmedPolynomial(numerator);
  const twiceExponent=2*(D+r)+1;
  const initialZeroMoments=R.findIndex(value=>value!==0n);
  if(R.length>twiceExponent)
    throw Error('The moment generating numerator exceeded its derived degree bound.');
  function polynomialText(values){
    let output='';
    values.forEach((value,k)=>{
      if(value===0n)return;
      const negative=value<0n,amount=negative?-value:value;
      const factor=k===0?'':(k===1?'z':'z^'+k);
      const term=factor?(amount===1n?factor:String(amount)+'*'+factor):String(amount);
      if(output)output+=negative?' - ':' + ';
      else if(negative)output+='-';
      output+=term;
    });
    return output||'0';
  }
  return {
    numerator:R.map(String),twiceExponent,degreeBound:2*(D+r),
    weightDegree:D,operatorOrder:r,
    initialZeroMoments:initialZeroMoments<0?null:initialZeroMoments,
    regularizedRecurrenceOrderBound:initialZeroMoments<0?0:2*(D+r)-initialZeroMoments+2,
    expression:'M(z) = ('+polynomialText(R)+') / (1-4z^2)^('+twiceExponent+'/2)',
    meaning:'M(z) = sum_(n>=0) F_P[D_x x^n] z^n. The numerator is computed by finite integer polynomial arithmetic.'
  };
}


export function differentialMomentsFromAlgebraicRecurrence(weights,operator,last,generating=null){
  // Remove initial zero moments and reconstruct the full tail from
  // A(z)T'(z)=B(z)T(z) with A(0)=the first nonzero moment.
  // Every operation uses exact BigInt coefficients.
  if(!Number.isSafeInteger(last)||last<0||last>160)
    throw Error('The algebraic moment index must be between 0 and 160.');
  const formula=generating||differentialMomentGeneratingFunction(weights,operator);
  const R=formula.numerator.map(BigInt);
  const ell=formula.initialZeroMoments;
  if(ell===null||ell>last)return Array(last+1).fill(0n);
  const h=[1n,0n,-4n],reduced=R.slice(ell);
  const A=exactPolynomialProduct(reduced,h);
  const derivative=reduced.length>1
    ?reduced.slice(1).map((value,j)=>BigInt(j+1)*value):[0n];
  const B=exactPolynomialProduct(derivative,h);
  while(B.length<A.length)B.push(0n);
  reduced.forEach((value,j)=>{
    B[j+1]+=4n*BigInt(formula.twiceExponent)*value;
  });
  if(A[0]===0n)throw Error('The regularized recurrence retained a singular leading coefficient.');
  const tail=[A[0]];
  for(let n=0;n<last-ell;n++){
    let rhs=0n;
    for(let j=0;j<=Math.min(n,B.length-1);j++)rhs+=B[j]*tail[n-j];
    for(let j=1;j<=Math.min(n+1,A.length-1);j++)
      rhs-=A[j]*BigInt(n-j+1)*tail[n-j+1];
    const denominator=BigInt(n+1)*A[0];
    if(rhs%denominator!==0n)
      throw Error('The algebraic recurrence did not yield an exact integer moment.');
    tail.push(rhs/denominator);
  }
  return Array(ell).fill(0n).concat(tail);
}

export function differentialHankel(n,weights,operator) {
  if(!Number.isSafeInteger(n)||n<0||n>12)
    throw Error('The differential Hankel size must be between 0 and 12.');
  const moments=Array.from({length:Math.max(0,2*n-1)},(_,k)=>
    polynomialDifferentialMoment(k,weights,operator));
  return bareissDeterminant(Array.from({length:n},(_,i)=>
    Array.from({length:n},(_,j)=>moments[i+j])));
}

export function fourFthreeHankel(n,c){
  if(n===0)return 1n;
  let numerator=1n,denominator=1n;
  const C=BigInt(c);
  for(let k=1;k<=Math.floor(n/2);k++){
    const item=(k%2?-1n:1n)*BigInt((2*k-1)*n*(n-1))*
      binomial(n+2*k-2,4*k-2)*C**BigInt(2*k);
    [numerator,denominator]=addFraction(numerator,denominator,item,BigInt(4*k));
  }
  const scaled=(2n**BigInt(n-1))*numerator;
  if(scaled%denominator!==0n)throw Error('The terminating 4F3 has an unexpected noninteger result.');
  return scaled/denominator;
}
export function meixnerCoefficients(s,twox,last){
  if(!Number.isInteger(last)||last<0||last>96)throw Error('The requested index is outside the calculator limit.');
  const X=BigInt(twox),S=BigInt(s),result=[1n];
  if(last>=1)result.push(X);
  for(let n=1;n<last;n++){
    result.push(X*result[n]-BigInt(n)*(BigInt(n)+S-1n)*result[n-1]);
  }
  return result;
}
export function computeExactWindow(raw){
  if(!raw||typeof raw!=='object')throw Error('Choose an exact sequence family.');
  const mode=String(raw.mode||'sparse');
  if(!Object.hasOwn(MODE_LIMITS,mode))throw Error('Choose a supported exact family.');
  const limits=MODE_LIMITS[mode];
  const start=integer(raw.start,'First index',mode==='fourblock'?1:0,limits.maxIndex);
  const count=integer(raw.count,'Number of terms',1,limits.maxCount);
  const last=start+count-1;
  if(last>limits.maxIndex)throw Error('The last index must not exceed '+limits.maxIndex+' for this family.');
  const params={};
  for(const field of MODE_FIELDS[mode]){
    params[field]=integer(raw[field],field,...FIELD_LIMITS[field]);
  }
  let values,description,verification,generatingFunction;
  switch(mode){
    case 'sparse':{
      const {p,q,r,u,v}=params;
      values=sparseCoefficients(p,q,r,u,v,last);
      description='C(n) = [z^n](1-u z^p-v z^q)^(-r). Integer powers and weights, including negative r and zero weights.';
      verification='The coefficients use the exact differentiated generating-function recurrence.';
      break;
    }
    case 'padovan':{
      values=padovanCoefficients(params.h,last);
      description='Padovan convolution powers: [z^n]((1-z^2)/(1-z^2-z^3))^h.';
      verification='Exact finite numerator convolution against the two-delay denominator power.';
      break;
    }
    case 'fourblock':{
      values=fourBlockCoefficients(params.a,last);
      description='Four-block logarithmic polynomials T_m(a), indexed from m=1. The analytic source degree is 4m-1.';
      verification='Exact integer-polynomial recurrence with the preserved factorial normalization.';
      break;
    }
    case 'jet':{
      const {d,lambda,c}=params;
      values=Array.from({length:last+1},(_,n)=>weightedJet(n,d,lambda,c));
      description='Polynomially weighted binomial transform. lambda shifts the seed; c weights its odd derivative part.';
      verification='Values use the original finite binomial sum, with the zero prefix and lambda=0 endpoints intact.';
      break;
    }
    case 'hankel':{
      const {d,c}=params;
      values=Array.from({length:last+1},(_,n)=>weightedHankel(n,d,c));
      description='W_N^[d](c) = det[F_d(x^(i+j)) + c(i+j)F_d(x^(i+j-1))]. W_0 = 1.';
      if(d===0){
        for(let n=0;n<=last;n++)if(values[n]!==fourFthreeHankel(n,c)){
          throw Error('The determinant disagrees with the independent terminating 4F3.');
        }
        verification='Verified against both fraction-free determinants and the independent terminating 4F3.';
      }else{
        verification='Evaluated by exact fraction-free determinants. The general root-free Chebyshev formula is in the source note.';
      }
      break;
    }
    case 'beta_moments':{
      const {L,a,b}=params;
      if(a<1)throw Error('Beta shape a must be positive.');
      values=betaMomentCoefficients(L,a,b,last);
      description='Unnormalized beta-binomial integer moments U_n = sum_(k=0)^L k^n binom(L,k) (a)_k (b)_(L-k).';
      verification='Exact finite weighted sum. U_n is an integer and equals (a+b)_L times the normalized probability moment.';
      break;
    }
    case 'beta_hankel':{
      const {L,a,b}=params;
      if(a<1)throw Error('Beta shape a must be positive.');
      values=betaHankelCoefficients(L,a,b,last);
      description='Hankel determinants of unnormalized beta-binomial integer moments, with H_0=1 and H_N=0 for N>L+1.';
      verification='Exact fraction-free determinants, including the finite-support rank cutoff. The normalized product needs the factor (a+b)_L^N.';
      break;
    }
    case 'differential_hankel':{
      const weights=[params.a0,params.a1,params.a2,params.a3];
      const operator=[params.c0,params.c1,params.c2,params.c3];
      values=Array.from({length:last+1},(_,n)=>differentialHankel(n,weights,operator));
      generatingFunction=differentialMomentGeneratingFunction(weights,operator);
      description='Higher-order differential Hankel: P(m)=sum_(d=0)^3 a_d falling(m,d), L[p]=sum_(k=0)^3 c_k F_P[p^(k)].';
      verification='Exact fraction-free determinants. The general Chebyshev proof bounds separated-block rank by 2(degree(P)+operator order). Higher-size exact structured calculations use the Python source implementation.';
      break;
    }
    case 'differential_moments':{
      const weights=[params.a0,params.a1,params.a2,params.a3];
      const operator=[params.c0,params.c1,params.c2,params.c3];
      generatingFunction=differentialMomentGeneratingFunction(weights,operator);
      values=differentialMomentsFromAlgebraicRecurrence(
        weights,operator,last,generatingFunction);
      for(let n=0;n<=last;n++){
        if(values[n]!==polynomialDifferentialMoment(n,weights,operator))
          throw Error('The algebraic recurrence disagrees with the independent direct moment sum at index '+n+'.');
      }
      description='Underlying polynomial-weighted differential moments mu_n = F_P[D_x x^n], using the same parameters as the differential Hankel family.';
      verification='Exact algebraic forward recurrence independently checked against the direct finite moment sums, including singular initial blocks.';
      break;
    }
    case 'meixner':{
      const {s,twox}=params;
      values=meixnerCoefficients(s,twox,last);
      description='Q_(n+1) = (2x) Q_n - n(n+s-1) Q_(n-1), Q_0=1, Q_1=2x.';
      verification='Exact polynomial recurrence. The source hypergeometric form requires its separate parameter conditions.';
      break;
    }
  }
  return {mode,start,count,parameters:params,
    rows:values.slice(start,last+1).map((value,j)=>({index:start+j,value:value.toString()})),
    description,verification,...(generatingFunction?{generatingFunction}:{})};
}
function csvQuote(value){
  const s=String(value);
  return '"'+s.replace(/"/g,'""')+'"';
}
export function exactWindowCSV(report){
  if(!report||!Array.isArray(report.rows))throw Error('Calculate a window before exporting.');
  const metadata=JSON.stringify(report.parameters);
  return ['family,index,exact_integer,parameters',...report.rows.map(row=>
    [report.mode,row.index,row.value,metadata].map(csvQuote).join(','))].join('\r\n')+'\r\n';
}
export function exactViewURL(href,raw){
  const report=computeExactWindow(raw),url=new URL(href);
  for(const key of [...url.searchParams.keys()])if(key.startsWith('cf-'))url.searchParams.delete(key);
  url.searchParams.set('cf-version','1');
  url.searchParams.set('cf-mode',report.mode);
  url.searchParams.set('cf-start',String(report.start));
  url.searchParams.set('cf-count',String(report.count));
  for(const [key,value] of Object.entries(report.parameters))url.searchParams.set('cf-'+key,String(value));
  url.hash='closed-calculator-panel';
  return url.href;
}
export function readExactView(href){
  const url=new URL(href);
  if(!url.searchParams.has('cf-version'))return null;
  if(url.searchParams.getAll('cf-version').length!==1||url.searchParams.get('cf-version')!=='1')
    throw Error('Unsupported or duplicated calculator link version.');
  const mode=url.searchParams.get('cf-mode');
  if(!Object.hasOwn(MODE_FIELDS,mode))throw Error('The calculator link has an unknown family.');
  const keys=['mode','start','count',...MODE_FIELDS[mode]];
  const allowed=new Set(keys.map(k=>'cf-'+k).concat('cf-version'));
  for(const key of url.searchParams.keys())if(key.startsWith('cf-')&&!allowed.has(key))
    throw Error('The calculator link contains an unexpected setting.');
  const values={};
  for(const key of keys){
    if(url.searchParams.getAll('cf-'+key).length!==1)throw Error('The calculator link has a missing or repeated setting.');
    values[key]=url.searchParams.get('cf-'+key);
  }
  computeExactWindow(values);
  return values;
}
