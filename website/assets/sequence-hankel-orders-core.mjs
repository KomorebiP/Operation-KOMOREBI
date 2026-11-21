// Exact rational arithmetic for Theorem N. No numerical root finding.
const abs=x=>x<0n?-x:x;
const igcd=(a,b)=>{a=abs(a);b=abs(b);while(b)[a,b]=[b,a%b];return a;};
class R{
  constructor(n,d=1n){
    if(!d)throw Error('A denominator cannot be zero.');
    if(d<0n){n=-n;d=-d;}const g=igcd(n,d);this.n=n/g;this.d=d/g;Object.freeze(this);
  }
}
const zero=new R(0n),one=new R(1n);
function bounded(n,d=1n){
  const value=new R(n,d);
  if(abs(value.n).toString().length>32||value.d.toString().length>32)throw Error('Use at most 32 digits in the numerator and denominator.');
  return value;
}
export function rational(value){
  if(value instanceof R)return value;
  if(typeof value==='bigint')return new R(value);
  if(typeof value==='number'){
    if(!Number.isSafeInteger(value))throw Error('Use an exact integer, fraction or decimal.');
    return new R(BigInt(value));
  }
  const text=String(value).trim();if(!text||text.length>70)throw Error('Use an integer, fraction, or finite decimal within 32 digits per numerator and denominator.');
  let match=text.match(/^([+-]?\d+)(?:\/(\d+))?$/);
  if(match)return bounded(BigInt(match[1]),BigInt(match[2]||'1'));
  match=text.match(/^([+-]?)(\d*)\.(\d*)$/);
  if(match&&(match[2]||match[3]))return bounded((match[1]==='-'?-1n:1n)*BigInt((match[2]||'0')+match[3]),10n**BigInt(match[3].length));
  throw Error('Use an integer, fraction, or finite decimal.');
}
const add=(a,b)=>new R(a.n*b.d+b.n*a.d,a.d*b.d);
const neg=a=>new R(-a.n,a.d);
const sub=(a,b)=>add(a,neg(b));
const mul=(a,b)=>new R(a.n*b.n,a.d*b.d);
const div=(a,b)=>new R(a.n*b.d,a.d*b.n);
const pow=(a,k)=>k<0?new R(a.d**BigInt(-k),a.n**BigInt(-k)):new R(a.n**BigInt(k),a.d**BigInt(k));
export const text=value=>{const a=rational(value);return a.d===1n?String(a.n):a.n+'/'+a.d;};
const trim=p=>{p=p.slice();while(p.length&&!p.at(-1).n)p.pop();return p;};
const derivative=p=>trim(p.slice(1).map((v,i)=>mul(rational(i+1),v)));
function primitive(p){
  p=p.slice();while(p.length&&p.at(-1)===0n)p.pop();if(!p.length)return p;
  let content=0n;for(const c of p)content=igcd(content,c);
  if(p.at(-1)<0n)content=-content;return p.map(c=>c/content);
}
function integral(p){
  let denominator=1n;for(const c of p)denominator=denominator/igcd(denominator,c.d)*c.d;
  return primitive(p.map(c=>c.n*(denominator/c.d)));
}
function pseudoRemainder(a,b){
  a=a.slice();
  while(a.length>=b.length&&a.length){
    const shift=a.length-b.length,c=a.at(-1),leading=b.at(-1);
    a=a.map(x=>x*leading);
    for(let j=0;j<b.length;j++)a[shift+j]-=c*b[j];
    a=primitive(a);
  }return a;
}
function gcd(first,second){
  let a=integral(first),b=integral(second);
  while(b.length)[a,b]=[b,pseudoRemainder(a,b)];
  return a.map(x=>new R(x,a.at(-1)));
}
export function coefficients(data){
  const rows=data.first_eight_with_unit;
  if(data.schema_version!==1||!Array.isArray(rows)||rows.length!==9)throw Error('Invalid coefficient resource.');
  rows.forEach((row,k)=>{
    const seen=new Set();if(!Array.isArray(row))throw Error('Invalid coefficient list.');
    for(const [i,j,c]of row){
      const key=i+','+j;
      if(!Number.isInteger(i)||!Number.isInteger(j)||i<0||j<0||i>k||j>Math.floor(k/2)||seen.has(key))throw Error('Invalid coefficient degree.');
      seen.add(key);rational(c);
    }
  });
  if(JSON.stringify(rows[0])!==JSON.stringify([[0,0,'1']]))throw Error('Invalid leading coefficient.');
  return rows;
}
function characteristic(t,q,rows){
  const first=rows.map(row=>row.reduce((s,[i,j,c])=>add(s,mul(rational(c),mul(pow(t,i),pow(q,j)))),zero));
  return [...first,...first.slice(0,-1).reverse()];
}
export function classify(tValue,qValue,rows){
  const t=rational(tValue),q=rational(qValue);
  if(!t.n||!q.n)throw Error('Choose nonzero t and q. Theorem M covers the coordinate boundary.');
  const c=characteristic(t,q,rows),f=c.slice().reverse(),h=16-(gcd(f,derivative(f)).length-1);
  const T=n=>rational(n),q2=mul(q,q);
  const H=[sub(T(16),mul(T(8),t)),mul(q,sub(mul(T(6),t),T(4))),mul(q,sub(mul(T(2),t),T(8))),q2,q2];
  const G=gcd(H,derivative(H)),g=G.length-1;
  const B=add(add(q2,mul(add(sub(mul(T(36),mul(t,t)),mul(T(16),t)),T(32)),q)),mul(T(64),pow(sub(t,T(2)),2)));
  const delta=!B.n;let rootType,order;
  if(g===0){rootType='1+1+1+1';order=7*h-Number(delta);}
  else if(g===1){rootType='2+1+1';order=7*h+4-Number(delta);}
  else if(g===2&&gcd(G,derivative(G)).length===1){rootType='2+2';order=69;if(h!==9||delta)throw Error('Inconsistent double-root invariants.');}
  else if(g===2){rootType='3+1';order=64;if(h!==8||delta)throw Error('Inconsistent triple-root invariants.');}
  else throw Error('The nonzero quartic identities exclude this multiplicity.');
  return {t:text(t),q:text(q),order,root_type:rootType,distinct_bases:h,negative_full_collision:delta,root_gcd_degree:g,recurrence_starts_at:1};
}
function choose(n,k){let c=1n;for(let j=1;j<=k;j++)c=c*BigInt(n-j+1)/BigInt(j);return c;}
export function normalizedTerms(tValue,qValue,count=8){
  const t=rational(tValue),q=rational(qValue);
  if(!q.n)throw Error('Choose q nonzero.');
  if(!Number.isInteger(count)||count<0||count>13)throw Error('Choose at most thirteen terms.');
  function moment(k){
    const m=Math.floor(k/2);let v=div(mul(add(one,mul(t,rational(m))),rational(choose(2*m,m))),pow(q,m));
    return k%2?mul(rational(2*m+1),v):v;
  }
  const values=[];
  for(let N=0;N<count;N++){
    const M=Array.from({length:N},(_,i)=>Array.from({length:N},(_,j)=>moment(i+j)));
    let sign=one,previous=one,singular=false;
    for(let k=0;k<N-1;k++){
      let row=k;while(row<N&&!M[row][k].n)row++;
      if(row===N){singular=true;break;}
      if(row!==k){[M[row],M[k]]=[M[k],M[row]];sign=neg(sign);}
      const pivot=M[k][k];
      for(let i=k+1;i<N;i++)for(let j=k+1;j<N;j++)M[i][j]=div(sub(mul(pivot,M[i][j]),mul(M[i][k],M[k][j])),previous);
      for(let i=k+1;i<N;i++)M[i][k]=zero;previous=pivot;
    }
    const d=singular?zero:N?mul(sign,M[N-1][N-1]):one;
    values.push(text(mul(pow(q,N*(N-1)/2),d)));
  }return values;
}
