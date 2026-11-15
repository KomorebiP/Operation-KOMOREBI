// Exact integer and rational operations; floating conversion only at the plot boundary.
export const mod = (a, m) => ((a % BigInt(m)) + BigInt(m)) % BigInt(m);
export function binom(n, k) {
  k = Math.min(k, n-k); let result = 1n;
  for (let i=1; i<=k; i++) result = result*BigInt(n-k+i)/BigInt(i);
  return result;
}
const cache = new Map();
export function generate(entry, count) {
  if (!Number.isInteger(count) || count < 1 || count > entry.cap) throw Error(`This family supports 1–${entry.cap} terms.`);
  const key = [entry.kind, entry.N, entry.power, count].join(':');
  if (cache.has(key)) return cache.get(key).slice();
  let result = [];
  if (entry.kind === 'reciprocal' || entry.kind === 'euler') {
    const N = entry.N || 2, power = entry.power || 1, base = [1n];
    for (let n=1; n<count; n++) {
      let value = 0n;
      for (let k=1; k<=n; k++) value += (k%2 ? 1n : -1n)*binom(N*n,N*k)*base[n-k];
      base.push(value);
    }
    result = [1n, ...Array(count-1).fill(0n)];
    for (let r=0; r<power; r++) result = result.map((_,n) => {
      let value=0n; for(let k=0;k<=n;k++) value += binom(N*n,N*k)*result[k]*base[n-k]; return value;
    });
    if (entry.kind === 'euler') result = result.map((v,n)=>n%2 ? -v : v);
  } else if (entry.kind === 'factorial') {
    let v=1n; for(let n=0;n<count;n++){if(n) v*=BigInt(n); result.push(v);}
  } else if (entry.kind === 'fibonacci') {
    let a=0n,b=1n; for(let n=0;n<count;n++){result.push(a); [a,b]=[b,a+b];}
  } else if (entry.kind === 'bell' || entry.kind === 'fubini') {
    let row=[1n];
    for(let n=0;n<count;n++) {
      let weight=1n, total=0n;
      row.forEach((v,k)=>{if(k) weight*=BigInt(k);total+=v*(entry.kind==='fubini'?weight:1n);}); result.push(total);
      row=[0n,...Array.from({length:n+1},(_,i)=>BigInt(i+1)*(row[i+1]||0n)+row[i])];
    }
  } else throw Error('Unknown sequence definition.');
  cache.set(key,result); return result.slice();
}
export function parseTerms(text) {
  if(text.length>20000) throw Error('Use at most 20,000 characters.');
  const tokens=text.trim().split(/[\s,;]+/).filter(Boolean);
  if(!tokens.length || tokens.length>1000 || tokens.some(v=>!/^[-+]?\d{1,300}$/.test(v))) throw Error('Enter 1–1,000 integers, with at most 300 digits per term.');
  return tokens.map(v=>BigInt(v));
}
const abs = x=>x<0n?-x:x;
function gcd(a,b){a=abs(a);b=abs(b);while(b)[a,b]=[b,a%b];return a;}
export function fraction(a,b=1n){if(!b)return null;if(b<0n){a=-a;b=-b;}const g=gcd(a,b);return {a:a/g,b:b/g};}
export const exact = v=>v===null?'undefined':v.b===1n?String(v.a):`${v.a}/${v.b}`;
export function transform(values, mode='raw') {
  let sum=0n;
  return values.map((v,n)=>{sum+=v;switch(mode){
    case 'difference': return n ? fraction(v-values[n-1]) : null;
    case 'sum': return fraction(sum);
    case 'ratio': return n ? fraction(v,values[n-1]) : null;
    case 'average': return fraction(sum,BigInt(n+1));
    case 'raw': return fraction(v);
    default: throw Error('Unknown transform.');
  }});
}
export function logAbs(value){const s=String(abs(value));return Math.log10(Number(s.slice(0,15)))+s.length-Math.min(s.length,15);}
export function coordinate(v,scale){
  if(!v)return null;
  if(scale==='log')return v.a>0n?logAbs(v.a)-logAbs(v.b):null;
  if(scale==='signed-log')return v.a===0n?0:(v.a<0n?-1:1)*(logAbs(abs(v.a)+v.b)-logAbs(v.b));
  // Scale numerator/denominator separately to avoid Infinity/Infinity.
  const a=String(abs(v.a)), b=String(v.b), value=Number(a.slice(0,15))/Number(b.slice(0,15))*10**((a.length-Math.min(a.length,15))-(b.length-Math.min(b.length,15)));
  return Number.isFinite(value)?(v.a<0n?-value:value):null;
}
export function rowsFor(values, state, name) {
  const transformed=transform(values,state.transform), rows=[];
  for(let n=state.start;n<Math.min(values.length,state.start+state.count);n++) {
    const v=transformed[n], residue=v&&v.b===1n?Number(mod(v.a,state.modulus)):null;
    let x=n,y=coordinate(v,state.scale);
    if(['mod','grid','frequency'].includes(state.view)){
      if(v&&v.b!==1n)throw Error('Modular views require integer-valued transforms. Choose original terms, differences, or partial sums.');
      y=residue;if(state.view==='grid')x=n%state.modulus;
    }
    if(state.view==='pairs'){x=coordinate(v,state.scale);y=n+1<transformed.length?coordinate(transformed[n+1],state.scale):null;}
    rows.push({name,n,raw:String(values[n]),value:exact(v),residue,x,y});
  }
  return rows;
}
export function candidatePeriod(residues){
  if(residues.length<4 || residues.some(x=>x===null))return null;
  for(let p=1;p<=Math.floor(residues.length/3);p++)if(residues.every((v,i)=>i<p||v===residues[i-p]))return p;
  return null;
}
export function findMatches(entries, query, filter='all'){
  const q=query.trim().toLowerCase();let needle=null;
  if(q && /^[-+\d\s,;]+$/.test(q)){needle=parseTerms(q).map(String);}
  return entries.filter(entry=>{
    if(filter==='reference'&&!entry.status.startsWith('Known'))return false;
    if(filter==='family'&&entry.kind!=='reciprocal')return false;
    if(needle)return entry.terms.some((_,i)=>needle.every((v,k)=>entry.terms[i+k]===v));
    return (entry.id+' '+entry.title+' '+entry.formula+' '+entry.tags.join(' ')+' '+(entry.oeis||'')+' '+(entry.matches||[]).map(m=>m.id+' '+m.name).join(' ')).toLowerCase().includes(q);
  });
}
