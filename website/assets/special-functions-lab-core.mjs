// Exact rational coefficients and local series bounds. Plot conversion is separate.
const abs = n => n < 0n ? -n : n;
const gcd = (a, b) => { a = abs(a); b = abs(b); while (b) [a, b] = [b, a % b]; return a; };
export function rational(n, d = 1n) {
  if (!d) throw new RangeError('The denominator must be positive.');
  if (d < 0n) { n = -n; d = -d; }
  const g = gcd(n, d); return {n:n/g, d:d/g};
}
export const add = (a,b) => rational(a.n*b.d+b.n*a.d,a.d*b.d);
export const sub = (a,b) => rational(a.n*b.d-b.n*a.d,a.d*b.d);
export const mul = (a,b) => rational(a.n*b.n,a.d*b.d);
export const div = (a,b) => rational(a.n*b.d,a.d*b.n);
export const pow = (a,n) => rational(a.n**BigInt(n),a.d**BigInt(n));
export const text = a => a.d === 1n ? String(a.n) : `${a.n}/${a.d}`;
export const less = (a,b) => a.n*b.d < b.n*a.d;
export function decimal(a) {
  // Avoid Infinity/Infinity for exact fractions with thousands of digits.
  if (!a.n) return 0;
  const ns = abs(a.n).toString(), ds = a.d.toString();
  const k = Math.min(ns.length,16), j = Math.min(ds.length,16);
  return (a.n < 0n ? -1 : 1) * (Number(ns.slice(0,k))/Number(ds.slice(0,j))) * 10**(ns.length-k-ds.length+j);
}
export function parse(value) {
  if (typeof value !== 'string' || value.length > 16 || !/^[+-]?\d{1,3}(?:\/[1-9]\d{0,2})?$/.test(value.trim())) {
    throw new RangeError('Enter a whole number or a fraction such as 2/3, with denominator at most 100.');
  }
  const [n,d='1'] = value.trim().split('/');
  if (BigInt(d)>100n) throw new RangeError('Use a denominator from 1 to 100.');
  return rational(BigInt(n),BigInt(d));
}
export function parameters(values) {
  if (!Array.isArray(values) || values.length !== 4) throw new RangeError('Supply q, r, a and b.');
  return Array.from(values, (v,i) => {
    const x = parse(v);
    if (x.n <= 0n || x.n >= x.d) throw new RangeError(`${['q','r','a','b'][i]} must be strictly between 0 and 1.`);
    return x;
  });
}
export function validateState(value) {
  if (!value || value.v !== 1 || typeof value.compare !== 'boolean') throw new RangeError('Unsupported experiment link.');
  const current=parameters(value.current).map(text), comparison=parameters(value.comparison).map(text);
  const count=value.count, term=value.term, radius=parse(value.radius);
  if (!Number.isInteger(count) || count < 1 || count > 16) throw new RangeError('Keep between 1 and 16 coefficients per component.');
  if (radius.n < 0n || less(rational(4n,3n),radius)) throw new RangeError('The radius must be between 0 and 4/3.');
  if (!Number.isInteger(term) || term < 0 || term >= count) throw new RangeError('Choose a retained coefficient index.');
  return {v:1,current,comparison,compare:value.compare,count,radius:text(radius),term};
}
export function defaultState() {
  return {v:1,current:['1/3','2/3','1/2','3/4'],comparison:['1/2','1/2','1/2','1/2'],compare:false,count:12,radius:'1',term:2};
}
export function coefficients(values,count) {
  if (!Number.isInteger(count) || count<1 || count>16) throw new RangeError('Keep between 1 and 16 coefficients.');
  const [q,r,a,b]=parameters(values), u=[rational(1n)],v=[rational(1n)];
  const powers=[q,r,a,b].map(x=>Array.from({length:count},(_,i)=>pow(x,2*i+1)));
  for (let n=1;n<count;n++) {
    let su=rational(0n),sv=rational(0n);
    for (let i=0;i<n;i++) {
      const j=n-1-i, uv=mul(u[i],v[j]);
      su=add(su,mul(mul(powers[0][i],powers[1][j]),uv));
      sv=add(sv,mul(mul(powers[2][i],powers[3][j]),uv));
    }
    u.push(div(su,rational(BigInt(2*n+1))));v.push(div(sv,rational(BigInt(2*n+1))));
  }
  return {u,v};
}
export function contributions(values,result,n) {
  if (!Number.isInteger(n) || n<0 || n>=result.u.length) throw new RangeError('Invalid coefficient index.');
  if (n===0) return [];
  const [q,r,a,b]=parameters(values), rows=[];
  for(let i=0;i<n;i++) {
    const j=n-1-i, shared=mul(result.u[i],result.v[j]), denominator=rational(BigInt(2*n+1));
    rows.push({i,j,shared,u:div(mul(mul(pow(q,2*i+1),pow(r,2*j+1)),shared),denominator),
      v:div(mul(mul(pow(a,2*i+1),pow(b,2*j+1)),shared),denominator)});
  }
  return rows;
}
export function tailBound(radius,count) {
  const r=parse(radius);
  if (r.n<0n || less(rational(4n,3n),r) || !Number.isInteger(count) || count<1 || count>16) throw new RangeError('Outside the laboratory domain.');
  const rho=div(mul(r,r),rational(2n));
  return div(mul(r,pow(rho,count)),sub(rational(1n),rho));
}
export function evaluateExact(row,x) {
  let sum=rational(0n);const square=mul(x,x);
  for(let i=row.length-1;i>=0;i--) sum=add(mul(sum,square),row[i]);
  return mul(sum,x);
}
export function evaluatePlot(row,x) {
  let sum=0;
  for(let i=row.length-1;i>=0;i--) sum=sum*x*x+decimal(row[i]);
  return sum*x;
}
export function encodeState(value) { return 'sf='+encodeURIComponent(JSON.stringify(validateState(value))); }
export function decodeState(hash) {
  if (typeof hash!=='string' || hash.length>2500) throw new RangeError('The experiment link is too long.');
  const raw=hash.replace(/^#/,'');
  if (!raw.startsWith('sf=')) throw new RangeError('This link does not contain a coupled-function experiment.');
  return validateState(JSON.parse(decodeURIComponent(raw.slice(3))));
}
export function coefficientCSV(value) {
  const s=validateState(value), sets=[['current',s.current]];
  if(s.compare)sets.push(['comparison',s.comparison]);
  const rows=['experiment,q,r,a,b,retained_count,radius,tail_bound,index,degree,u,v'];
  for(const [name,scales] of sets){const c=coefficients(scales,s.count);for(let n=0;n<s.count;n++)rows.push([name,...scales,s.count,s.radius,text(tailBound(s.radius,s.count)),n,2*n+1,text(c.u[n]),text(c.v[n])].join(','));}
  return rows.join('\n')+'\n';
}
