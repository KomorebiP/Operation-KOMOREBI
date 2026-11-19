// Exact Chebyshev–Schur prefixes for finite differential Hankel determinants.
// Author: Komorebi P.
// The fixed-width state has size 2*(degree(P)+operator order). Singular
// leading minors use exact block lookahead; integer bit sizes still grow.

const ZERO=Object.freeze([0n,1n]),ONE=Object.freeze([1n,1n]);
function abs(x){return x<0n?-x:x;}
function gcd(a,b){a=abs(a);b=abs(b);while(b){[a,b]=[b,a%b];}return a;}
function rational(n,d=1n){
  if(d===0n)throw Error('The structured determinant attempted division by zero.');
  if(n===0n)return ZERO;
  if(d<0n){n=-n;d=-d;}
  const g=gcd(n,d);
  return [n/g,d/g];
}
function add(a,b){
  if(a[0]===0n)return b;
  if(b[0]===0n)return a;
  const g=gcd(a[1],b[1]),ad=a[1]/g,bd=b[1]/g;
  const n=a[0]*bd+b[0]*ad,t=gcd(n,g);
  return n===0n?ZERO:[n/t,ad*(b[1]/t)];
}
function neg(a){return a[0]===0n?ZERO:[-a[0],a[1]];}
function sub(a,b){return add(a,neg(b));}
function mul(a,b){
  if(a[0]===0n||b[0]===0n)return ZERO;
  const g=gcd(a[0],b[1]),h=gcd(b[0],a[1]);
  return [(a[0]/g)*(b[0]/h),(a[1]/h)*(b[1]/g)];
}
function div(a,b){
  if(b[0]===0n)throw Error('The structured determinant attempted division by zero.');
  return mul(a,b[0]<0n?[-b[1],-b[0]]:[b[1],b[0]]);
}
function dot(a,b){
  let result=ZERO;
  for(let i=0;i<a.length;i++)result=add(result,mul(a[i],b[i]));
  return result;
}
function integerValue(a){
  if(a[1]!==1n)throw Error('The structured Hankel determinant is not an exact integer.');
  return a[0];
}
function coefficients(values,label){
  if(!Array.isArray(values))throw Error(label+' requires an array of integer coefficients.');
  const result=(values.length?values:[0n]).map(value=>{
    if(typeof value==='number'&&!Number.isSafeInteger(value))
      throw Error(label+' coefficients must be exact integers.');
    if(typeof value!=='bigint'&&!/^-?(0|[1-9][0-9]*)$/.test(String(value)))
      throw Error(label+' coefficients must be exact integers.');
    return BigInt(value);
  });
  while(result.length>1&&result.at(-1)===0n)result.pop();
  if(result.length>4)throw Error(label+' supports degree or order at most 3 in the browser.');
  return result;
}
function factorial(n){let value=1n;for(let j=2;j<=n;j++)value*=BigInt(j);return value;}
function binomial(n,k){
  if(k>n)return 0n;
  let value=1n;
  for(let j=1;j<=k;j++)value=value*BigInt(n-j+1)/BigInt(j);
  return value;
}

function derivativePolynomial(d,k){
  // Ascending b_h for t*sum_h b_h*t^(2h), at matching positive indices.
  if(d===0&&k===0)return [ZERO];
  const squares=[];
  if(k===0){
    for(let j=1;j<d;j++)squares.push(BigInt((2*j)**2));
  }else if(k%2){
    const half=(k-1)/2;
    for(let j=1;j<=half;j++)squares.push(BigInt((2*j-1)**2),BigInt((2*j-1)**2));
    for(let j=half+1;j<=half+d;j++)squares.push(BigInt((2*j-1)**2));
  }else{
    const half=k/2;
    squares.push(0n);
    for(let j=1;j<half;j++)squares.push(BigInt((2*j)**2),BigInt((2*j)**2));
    for(let j=half;j<half+d;j++)squares.push(BigInt((2*j)**2));
  }
  let polynomial=[1n];
  for(const square of squares){
    const next=Array(polynomial.length+1).fill(0n);
    polynomial.forEach((value,j)=>{next[j]-=square*value;next[j+1]+=value;});
    polynomial=next;
  }
  const denominator=4n**BigInt(d+k-1)*factorial(d+k-1);
  return polynomial.map(value=>rational(value,denominator));
}
function jetPolynomials(a,c){
  const even=[],odd=[];
  for(let d=0;d<a.length;d++)for(let k=0;k<c.length;k++){
    if(a[d]===0n||c[k]===0n)continue;
    const polynomial=derivativePolynomial(d,k),target=k%2?odd:even;
    while(target.length<polynomial.length)target.push(ZERO);
    polynomial.forEach((value,j)=>{target[j]=add(target[j],mul(rational(a[d]*c[k]),value));});
  }
  return [even,odd];
}
function oddValue(polynomial,n){
  const x=BigInt(n),square=rational(x*x);
  let value=ZERO;
  for(let j=polynomial.length-1;j>=0;j--)value=add(mul(value,square),polynomial[j]);
  return mul(rational(x),value);
}
function generators(a,c,size){
  const half=a.length+c.length-2,[even,odd]=jetPolynomials(a,c);
  const rows=[],cols=[],diagonal=[];
  for(let i=0;i<size;i++){
    const x=BigInt(i),sign=i%2?-1n:1n,powers=[1n];
    for(let j=1;j<=2*half+1;j++)powers.push(powers.at(-1)*x);
    function part(polynomial,k){
      let value=ZERO;
      for(let h=k;h<polynomial.length;h++)
        value=add(value,mul(polynomial[h],rational(binomial(2*h+1,2*k)*powers[2*h+1-2*k])));
      return value;
    }
    const A=Array.from({length:half},(_,k)=>part(even,k));
    const B=Array.from({length:half},(_,k)=>part(odd,k));
    rows.push(A.map((value,k)=>add(value,B[k])).concat(
      A.map((value,k)=>mul(rational(sign),sub(value,B[k])))));
    cols.push(Array.from({length:half},(_,k)=>rational(powers[2*k])).concat(
      Array.from({length:half},(_,k)=>rational(sign*powers[2*k]))));
    diagonal.push(i===0?rational(4n*a[0]*c[0]):
      add(rational(2n*a[0]*c[0]),oddValue(even,2*i)));
  }
  function gram(i,j){
    if(i===j)return diagonal[i];
    const polynomial=(i-j)%2===0?even:odd;
    return add(oddValue(polynomial,i+j),oddValue(polynomial,Math.abs(i-j)));
  }
  return {rows,cols,gram};
}
function inverseAndDeterminant(matrix){
  const n=matrix.length,a=matrix.map(row=>row.slice());
  const inverse=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?ONE:ZERO));
  let determinant=ONE;
  for(let k=0;k<n;k++){
    const pivotRow=a.findIndex((row,i)=>i>=k&&row[k][0]!==0n);
    if(pivotRow<0)return {determinant:ZERO,inverse:null};
    if(pivotRow!==k){
      [a[k],a[pivotRow]]=[a[pivotRow],a[k]];
      [inverse[k],inverse[pivotRow]]=[inverse[pivotRow],inverse[k]];
      determinant=neg(determinant);
    }
    const pivot=a[k][k];
    determinant=mul(determinant,pivot);
    a[k]=a[k].map(value=>div(value,pivot));
    inverse[k]=inverse[k].map(value=>div(value,pivot));
    for(let i=0;i<n;i++){
      if(i===k||a[i][k][0]===0n)continue;
      const factor=a[i][k];
      for(let j=0;j<n;j++){
        a[i][j]=sub(a[i][j],mul(factor,a[k][j]));
        inverse[i][j]=sub(inverse[i][j],mul(factor,inverse[k][j]));
      }
    }
  }
  return {determinant,inverse};
}

export function structuredDifferentialHankel(weights,operator,maxSize){
  if(!Number.isSafeInteger(maxSize)||maxSize<0||maxSize>64)
    throw Error('The structured Hankel size must be between 0 and 64.');
  const a=coefficients(weights,'Polynomial weight'),c=coefficients(operator,'Differential operator');
  const result=Array(maxSize+1).fill(0n);result[0]=1n;
  const nu=a.findIndex(value=>value!==0n),kappa=c.findIndex(value=>value!==0n);
  if(nu<0||kappa<0)return result;
  const ell=2*nu+kappa,initialSize=ell+1;
  if(initialSize>maxSize)return result;
  const mass=a[nu]*c[kappa]*factorial(ell)/factorial(nu);
  const expected=(ell*(ell+1)/2%2?-1n:1n)*mass**BigInt(initialSize);
  const {rows,cols,gram}=generators(a,c,maxSize),width=rows[0].length;
  const initial=Array.from({length:initialSize},(_,i)=>
    Array.from({length:initialSize},(_,j)=>gram(i,j)));
  const first=inverseAndDeterminant(initial);
  let determinant=first.determinant;
  if(determinant[0]===0n||integerValue(div(determinant,rational(4n)))!==expected)
    throw Error('The first nonzero Hankel block failed its exact anti-diagonal check.');
  result[initialSize]=expected;
  const solved=first.inverse.map(row=>Array.from({length:width},(_,q)=>
    dot(row,cols.slice(0,initialSize).map(column=>column[q]))));
  let state=Array.from({length:width},(_,p)=>Array.from({length:width},(_,q)=>
    dot(cols.slice(0,initialSize).map(column=>column[p]),solved.map(row=>row[q]))));
  let m=initialSize;
  while(m<maxSize){
    // Keep already computed Schur entries while extending a singular block.
    const transformed=[],schur=[];
    let advanced=false;
    for(let length=1;length<=maxSize-m;length++){
      const index=m+length-1;
      transformed.push(state.map(row=>dot(row,rows[index])));
      const added=Array.from({length},(_,j)=>
        sub(gram(index,m+j),dot(rows[index],transformed[j])));
      for(let j=0;j<schur.length;j++)schur[j].push(added[j]);
      schur.push(added);
      const block=inverseAndDeterminant(schur);
      if(block.determinant[0]===0n)continue;
      const w=transformed.map((row,i)=>row.map((value,p)=>sub(value,cols[m+i][p])));
      const solvedBlock=block.inverse.map(row=>Array.from({length:width},(_,q)=>
        dot(row,w.map(vector=>vector[q]))));
      const next=state.map(row=>row.slice());
      for(let p=0;p<width;p++)for(let q=p;q<width;q++){
        const update=dot(w.map(row=>row[p]),solvedBlock.map(row=>row[q]));
        next[p][q]=next[q][p]=add(state[p][q],update);
      }
      state=next;
      determinant=mul(determinant,block.determinant);
      result[m+length]=integerValue(div(determinant,rational(4n)));
      m+=length;advanced=true;break;
    }
    if(!advanced)break;
  }
  return result;
}
