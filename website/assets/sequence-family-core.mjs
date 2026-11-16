// Exact family coefficients. Floating conversion belongs only to the chart.
import {binom,fraction,exact,generate} from './sequence-atlas-core.mjs';
export const ENGINE_NAMES=Object.freeze({linear:'Weighted k-step powers',kbonacci:'Zero-seeded k-bonacci',reciprocal:'Transfer secant powers',congruential:'Congruential inverse sections',appell:'Block-Appell coefficients',secancy:'Secancy parameter columns',theta:'Theta specializations','theta-column':'Theta coefficient columns',tangent:'Transfer tangents',section:'Classical multisections'});
export const FAMILY_ENGINES=Object.freeze({'GF-LINEAR':'linear','GF-KBONACCI':'kbonacci','GF-RECIPROCAL':'reciprocal','GF-CONGRUENTIAL':'congruential','GF-APPELL':'appell','GF-SECANCY':'secancy','GF-THETA':'theta','GF-THETA-COLUMN':'theta-column','GF-TANGENT':'tangent','GF-SECTIONS':'section'});
export const FAMILY_DEFAULTS=Object.freeze({k:3,r:1,c:1,N:3,j:1,x:2,column:2,count:24,component:'numerator',appellMode:'value',seedMode:'tail',seeds:'0, 0, 1',parent:'fibonacci'});
const integer=(v,name,min,max)=>{if(!['number','string'].includes(typeof v)||String(v).trim()===''||!Number.isSafeInteger(Number(v))||Number(v)<min||Number(v)>max)throw Error(`${name} must be an integer from ${min} to ${max}.`);return Number(v);};
export const Q=(a,b=1n)=>{const value=fraction(BigInt(a),BigInt(b));if(!value)throw Error('A denominator is zero.');return value;};
export const qadd=(a,b)=>Q(a.a*b.b+b.a*a.b,a.b*b.b),qmul=(a,b)=>Q(a.a*b.a,a.b*b.b),qdiv=(a,b)=>Q(a.a*b.b,a.b*b.a),qneg=a=>Q(-a.a,a.b);
export function readQ(value){const parts=String(value).split('/');if(parts.length>2||parts.some(p=>!/^[-+]?\d+$/.test(p)))throw Error('Expected an exact rational value.');return Q(parts[0],parts[1]??1);}
export function factorial(n){let value=1n;for(let i=2;i<=n;i++)value*=BigInt(i);return value;}
function parameterObject(options){if(!options||typeof options!=='object'||Array.isArray(options)||![Object.prototype,null].includes(Object.getPrototypeOf(options)))throw Error('Family parameters must be an object.');}
function appellMode(options){
  // Old record links supplied a coefficient column without x. Saved scalar
  // explorations contained x and must retain their point-evaluation meaning.
  const mode=Object.hasOwn(options,'appellMode')?options.appellMode:Object.hasOwn(options,'column')&&!Object.hasOwn(options,'x')?'column':'value';
  if(!['value','column'].includes(mode))throw Error('Choose Appell point values or a coefficient column.');return mode;
}
export function familyParameterKeys(engine,options={}){
  if(!Object.hasOwn(ENGINE_NAMES,engine))throw Error('Choose an available exact family.');parameterObject(options);
  if(engine==='linear'){
    const mode=Object.hasOwn(options,'seedMode')?options.seedMode:FAMILY_DEFAULTS.seedMode;
    if(!['tail','zero','custom'].includes(mode))throw Error('Choose a listed seed convention.');
    return ['k','c','count','seedMode',...(mode==='tail'?['r']:mode==='custom'?['seeds']:[])];
  }
  if(engine==='appell')return ['N','j','r','appellMode',appellMode(options)==='column'?'column':'x','component','count'];
  return ({kbonacci:['k','count'],reciprocal:['N','r','count'],congruential:['N','j','r','component','count'],secancy:['N','column','count'],theta:['x','count'],'theta-column':['column','count'],tangent:['N','count'],section:['N','j','parent','count']})[engine].slice();
}
export function validateFamily(engine,options={}){
  const keys=familyParameterKeys(engine,options),p={...FAMILY_DEFAULTS,...Object.fromEntries(keys.filter(k=>Object.hasOwn(options,k)).map(k=>[k,options[k]]))};
  if(engine==='appell')p.appellMode=appellMode(options);
  for(const [name,min,max]of [['k',2,16],['r',1,8],['c',1,5],['N',1,16],['j',0,15],['x',engine==='theta'?-12:-8,engine==='theta'?12:8],['column',engine==='appell'?0:1,engine==='theta-column'?12:8],['count',2,['linear','kbonacci'].includes(engine)?64:32]])if(keys.includes(name))p[name]=integer(p[name],name,min,max);
  if(!['linear','kbonacci','section','theta','theta-column'].includes(engine)&&p.N<2)throw Error('Block spacing N must be at least 2 for this construction.');
  if(['congruential','appell','section'].includes(engine)&&p.j>=p.N)throw Error('The residue j must satisfy 0 <= j < N.');
  if(keys.includes('component')&&!['numerator','denominator'].includes(p.component))throw Error('Choose the reduced numerator or positive denominator.');
  if(keys.includes('parent')&&!['fibonacci','lucas','pell','factorial','catalan','central-binomial','triangular','square','cube','power-two','power-three','bell','fubini'].includes(p.parent))throw Error('Choose a listed classical parent.');
  if(keys.includes('seeds')&&(typeof p.seeds!=='string'||p.seeds.length>2000))throw Error('Keep the seed vector below 2,000 characters.');
  if(engine==='kbonacci'){p.seedMode='zero';p.r=1;p.c=1;}
  if(['linear','kbonacci'].includes(engine)&&p.seedMode!=='tail'){
    p.r=1;
    if(p.seedMode==='custom'){
      const values=p.seeds.trim().split(/[\s,;]+/);if(values.length!==p.k||values.some(v=>!/^[-+]?\d{1,100}$/.test(v)))throw Error(`Supply exactly ${p.k} integer seeds, up to 100 digits each.`);
      p.seeds=values.map(v=>String(BigInt(v))).join(', ');
    }
  }
  return p;
}
export function linearCoefficients(k,r,c,count){const a=[1n];for(let n=1;n<count;n++){let sum=0n;for(let j=1;j<=Math.min(k,n);j++)sum+=BigInt(c*(n+(r-1)*j))*a[n-j];if(sum%BigInt(n))throw Error('A k-step coefficient is not integral.');a.push(sum/BigInt(n));}return a;}
function binomialH(k,r,c,m){if(m<0)return 0n;let sum=0n;for(let j=0;j<=Math.floor(m/(k+1));j++)sum+=(-BigInt(c))**BigInt(j)*binom(r+m-k*j-1,m-k*j)*binom(m-k*j,j)*BigInt(c+1)**BigInt(m-(k+1)*j);return sum;}
export function linearBinomial(k,r,c,n){let sum=0n;for(let ell=0;ell<=Math.min(r,n);ell++)sum+=(ell%2?-1n:1n)*binom(r,ell)*binomialH(k,r,c,n-ell);return sum;}
export function finiteHyperH(k,r,c,m){
  if(m<0)return Q(0);const argument=Q(BigInt(c)*BigInt(k+1)**BigInt(k+1),BigInt(c+1)**BigInt(k+1)*BigInt(k)**BigInt(k));let total=Q(1),term=Q(1);
  for(let j=1;j<=Math.floor(m/(k+1));j++){term=qmul(term,qdiv(argument,Q(j)));for(let i=0;i<=k;i++)term=qmul(term,Q(i-m+(j-1)*(k+1),k+1));for(let i=0;i<k;i++)term=qdiv(term,Q(i+1-r-m+(j-1)*k,k));total=qadd(total,term);}
  return qmul(Q(BigInt(c+1)**BigInt(m)*binom(r+m-1,m)),total);
}
export function linearHyper(k,r,c,n){let sum=Q(0);for(let ell=0;ell<=Math.min(r,n);ell++)sum=qadd(sum,qmul(Q((ell%2?-1n:1n)*binom(r,ell)),finiteHyperH(k,r,c,n-ell)));return sum;}
export function secancyRows(N,count){
  const rows=[[1n]];for(let n=1;n<count;n++){const row=Array(n+1).fill(0n);for(let k=1;k<=n;k++){let value=0n;for(let i=1;i<=n;i++)value+=(i%2?1n:-1n)*binom(N*n,N*i)*(BigInt(n-i)*(rows[n-i][k]??0n)+BigInt(i)*(rows[n-i][k-1]??0n));if(value%BigInt(n))throw Error('A polynomial coefficient is not integral.');row[k]=value/BigInt(n);}rows.push(row);}return rows;
}
export function thetaRows(count){const p=secancyRows(2,count),s=p.map(row=>row.reduce((a,b)=>a+b,0n));return p.map((_,n)=>Array.from({length:2*n+1},(_,k)=>{let sum=0n;for(let j=0;j<=n;j++)if(k>=2*j)sum+=binom(2*n,2*j)*s[j]*(p[n-j][k-2*j]??0n);return (n%2?-1n:1n)*sum;}));}
function inverseSection(N,j,r,count,alternating=false){const d=Array.from({length:count},(_,n)=>Q((alternating&&n%2?-1n:1n)*factorial(j),factorial(N*n+j))),h=[Q(1)];for(let n=1;n<count;n++){let sum=Q(0);for(let k=1;k<=n;k++)sum=qadd(sum,qmul(Q(n+(r-1)*k),qmul(d[k],h[n-k])));h.push(qneg(qdiv(sum,Q(n))));}return h.map((v,n)=>qmul(v,Q(factorial(N*n))));}
function linearSeeds(p){if(p.seedMode==='tail')return null;return p.seedMode==='custom'?p.seeds.split(', ').map(BigInt):[...Array(p.k-1).fill(0n),1n];}
function seedNumerator(p,seeds){return seeds.map((value,n)=>value-BigInt(p.c)*seeds.slice(0,n).reduce((a,b)=>a+b,0n));}
function seededLinear(p){const seeds=linearSeeds(p);if(!seeds)return linearCoefficients(p.k,p.r,p.c,p.count);const a=seeds.slice(0,p.count);for(let n=p.k;n<p.count;n++)a.push(BigInt(p.c)*a.slice(n-p.k,n).reduce((a,b)=>a+b,0n));return a;}
export function generateFamily(engine,options={}){
  const p=validateFamily(engine,options);let terms,raw=null,offset=0,degrees,formula,normalization='Exact ordinary coefficients, without factorial scaling.';
  if(['linear','kbonacci'].includes(engine)){
    terms=seededLinear(p);const seeds=linearSeeds(p),numerator=seeds?seedNumerator(p,seeds):[1n];formula=`sum_(n>=0) a(n)z^n = (${numerator.map((v,i)=>v===0n?'':i?`(${v})z^${i}`:String(v)).filter(Boolean).join('+')||'0'})/(1-${p.c} sum_(j=1)^${p.k} z^j)^${p.r}`;degrees=terms.map((_,n)=>n);
    normalization+=p.seedMode==='tail'?' The constant coefficient is one.':` The ${p.k} initial values are ${seeds.join(', ')}; recurrence a(n)=${p.c} sum_(j=1)^${p.k} a(n-j) begins at n=${p.k}.`;
  }else if(engine==='reciprocal'){
    terms=generate({kind:'reciprocal',N:p.N,power:p.r,cap:32},p.count);degrees=terms.map((_,n)=>p.N*n);formula=`sum_(n>=0) a(n)z^(${p.N}n)/(${p.N}n)! = (sum_(m>=0) (-1)^m z^(${p.N}m)/(${p.N}m)!)^(-${p.r})`;normalization=`Compressed EGF values: source degree ${p.N}n, factorial (${p.N}n)!.`;
  }else if(engine==='congruential'||engine==='appell'){
    const column=engine==='appell'&&p.appellMode==='column',q=inverseSection(p.N,p.j,p.r,p.count);
    raw=engine==='congruential'?q:column?q.map((value,n)=>qmul(Q(binom(p.N*n+p.column,p.column)),value)):Array.from({length:p.count},(_,n)=>{let sum=Q(0);for(let k=0;k<=Math.floor(n/p.N);k++)sum=qadd(sum,qmul(Q(binom(n,p.N*k)*BigInt(p.x)**BigInt(n-p.N*k)),q[k]));return sum;});
    terms=raw.map(q=>p.component==='numerator'?q.a:q.b);degrees=terms.map((_,n)=>engine==='congruential'?p.N*n:column?p.N*n+p.column:n);
    const denominator=`(sum_(m>=0) ${factorial(p.j)} z^(${p.N}m)/(${p.N}m+${p.j})!)^(-${p.r})`;
    formula=engine==='congruential'?`q(n)=(${p.N}n)! [z^(${p.N}n)] ${denominator}`:column?`q(n)=[x^${p.column}] P_(${p.N}n+${p.column})(x) = binom(${p.N}n+${p.column},${p.column}) (${p.N}n)! [z^(${p.N}n)] ${denominator}`:`q(n)=n! [z^n] exp(${p.x}z) ${denominator}`;
    normalization=`The displayed integers give the reduced ${p.component} of each q(n), with a positive denominator. The original rational values remain in the table. `+(column?`This is the ordinary coefficient of x^${p.column}, without ${p.column}! scaling. Local n begins at 0 and selects Appell polynomial row ${p.N}n+${p.column}; other rows of this column vanish.`:`Source degree ${engine==='congruential'?p.N+'n':'n'}, with its factorial normalization.`);
  }else if(engine==='secancy'){
    offset=p.column;const rows=secancyRows(p.N,p.count+offset);terms=rows.slice(offset).map(row=>row[p.column]??0n);degrees=terms.map((_,i)=>p.N*(offset+i));formula=`a(n)=[r^${p.column}] P_(${p.N},n)(r)`;normalization=`Ordinary polynomial coefficient of r^${p.column}, without ${p.column}! scaling. The stored window begins at n=${offset}; source degree ${p.N}n.`;
  }else if(engine==='theta'||engine==='theta-column'){
    if(engine==='theta-column')offset=Math.ceil(p.column/2);const rows=thetaRows(p.count+offset);terms=rows.slice(offset).map(row=>engine==='theta-column'?(row[p.column]??0n):row.reduce((sum,v,k)=>sum+v*BigInt(p.x)**BigInt(k),0n));degrees=terms.map((_,i)=>2*(offset+i));formula=engine==='theta'?`a(n)=Theta_(2n)(${p.x}); sum_(n>=0) a(n)z^(2n)/(2n)! = sech(${p.x}z) sech(z)^${p.x}`:`a(n)=[x^${p.column}] Theta_(2n)(x)`;normalization=`${engine==='theta-column'?'Ordinary x-column coefficient, without k! scaling.':'Signed theta specialization.'} Source degree 2n; local window begins at n=${offset}.`;
  }else if(engine==='tangent'){
    const pRows=secancyRows(p.N,p.count+1);terms=pRows.slice(1).map(row=>row[1]);degrees=terms.map((_,n)=>p.N*(n+1)-1);formula=`a(n)=(${p.N}(n+1)-1)! [z^(${p.N}(n+1)-1)] (-D_${p.N}'(z)/D_${p.N}(z))`;normalization=`Logarithmic derivative EGF values; source degree ${p.N}(n+1)-1. These equal the r-column coefficients at polynomial row n+1.`;
  }else{
    const count=p.N*(p.count-1)+p.j+1,values=generate({kind:p.parent,cap:512},count);terms=Array.from({length:p.count},(_,n)=>values[p.N*n+p.j]);degrees=terms.map((_,n)=>p.N*n+p.j);formula=`a(n)=b(${p.N}n+${p.j})`;normalization=`Classical ${p.parent} subsequence. Local n selects original source index ${p.N}n+${p.j}.`;
  }
  return {engine,params:p,title:ENGINE_NAMES[engine],offset,terms:terms.map(String),rationalTerms:raw?.map(exact)||null,degrees,formula,normalization};
}
export function workedFamily(result,index=3){
  const {engine,params:p}=result;const position=Math.min(index,result.terms.length-1),n=result.offset+position,value=result.terms[position];let alternative=null,method='';
  if(['linear','kbonacci'].includes(engine)){
    const seeds=linearSeeds(p),numerator=seeds?seedNumerator(p,seeds):[1n];let binomial=0n,hyper=Q(0);for(let ell=0;ell<numerator.length&&ell<=n;ell++){binomial+=numerator[ell]*linearBinomial(p.k,p.r,p.c,n-ell);hyper=qadd(hyper,qmul(Q(numerator[ell]),linearHyper(p.k,p.r,p.c,n-ell)));}
    alternative=String(binomial);if(exact(hyper)!==value||alternative!==value)throw Error('The independent finite formula disagrees.');method='The recurrence, finite binomial formula, and finite hypergeometric sum agree. The hypergeometric cutoff is applied before parameter cancellation.';
  }else if(engine==='reciprocal'){
    const q=inverseSection(p.N,0,p.r,n+1,true)[n];alternative=exact(q);if(alternative!==value)throw Error('The reciprocal coefficient constructions disagree.');method='The integer reciprocal-power recurrence and ordinary rational differential recurrence agree after multiplication by the source-degree factorial.';
  }else if(engine==='theta'){
    const factors=generate({kind:'reciprocal',N:2,power:Math.abs(p.x),cap:64},n+1); // x<0 uses the signed-power polynomial construction instead.
    if(p.x>0){const sec=generate({kind:'reciprocal',N:2,power:1,cap:64},n+1);let sum=0n;for(let j=0;j<=n;j++)sum+=binom(2*n,2*j)*sec[j]*BigInt(p.x)**BigInt(2*j)*factors[n-j];alternative=String((n%2?-1n:1n)*sum);if(alternative!==value)throw Error('The theta constructions disagree.');method='The polynomial specialization and the product of the two signed EGF factors agree.';}
  }
  return {position,index:n,value,alternative,method:method||'This value is evaluated from the defining exact coefficient construction. Its source degree and normalization are shown alongside it.'};
}
export function familyCSV(result){return ['local_n,source_degree,integer_component,original_rational',...result.terms.map((v,i)=>[result.offset+i,result.degrees[i],v,result.rationalTerms?.[i]??''].join(','))].join('\r\n')+'\r\n';}
export function familyURL(href,family,params,plot){
  if(!Object.hasOwn(FAMILY_ENGINES,family))throw Error('Choose a supported exact family.');
  const url=new URL(href),normalized=validateFamily(FAMILY_ENGINES[family],params);
  url.pathname=url.pathname.replace(/\/generalized-families\/GF-[^/]+\.html$/,`/generalized-families/${family}.html`);
  for(const key of ['family','parameters','family-view','family-modulus'])url.searchParams.delete(key);
  url.hash='family-explorer';url.searchParams.set('family',family);url.searchParams.set('parameters',JSON.stringify(normalized));if(plot){url.searchParams.set('family-view',plot.view);url.searchParams.set('family-modulus',String(plot.modulus));}return url.href;
}
export function familyDescriptor(engine,params){return {type:'family',engine,params:validateFamily(engine,params)};}
export function constantRecurrence(options={}){
  const p=validateFamily('linear',options);let denominator=[1n];const base=[1n,...Array(p.k).fill(-BigInt(p.c))];for(let r=0;r<p.r;r++){const next=Array(denominator.length+p.k).fill(0n);for(let i=0;i<denominator.length;i++)for(let j=0;j<base.length;j++)next[i+j]+=denominator[i]*base[j];denominator=next;}
  const coefficients=denominator.slice(1).map(v=>-v),order=coefficients.length;let seeds=linearSeeds(p);if(!seeds){seeds=[1n];for(let n=1;n<order;n++){let value=0n;for(let j=1;j<=n;j++)value+=coefficients[j-1]*seeds[n-j];seeds.push(value);}}
  return {params:p,order,coefficients:coefficients.map(String),seeds:seeds.map(String)};
}
export function familyRepresentations(result){
  const p=result.params,forms=[{title:'Defining generating or coefficient formula',expression:result.formula,note:result.normalization}];
  if(['linear','kbonacci'].includes(result.engine)){
    const k=p.k,r=p.r,c=p.c,top=Array.from({length:k+1},(_,i)=>`(${i}-m)/${k+1}`).join(', '),bottom=Array.from({length:k},(_,i)=>`(${i+1-r}-m)/${k}`).join(', '),argument=exact(Q(BigInt(c)*BigInt(k+1)**BigInt(k+1),BigInt(c+1)**BigInt(k+1)*BigInt(k)**BigInt(k))),outer=`b(n)=sum_(ell=0)^min(${r},n) (-1)^ell binom(${r},ell) H(n-ell)`;
    forms.push({title:'Finite binomial closed form',expression:outer+`\nH(m)=sum_(j=0)^floor(m/${k+1}) (-${c})^j binom(${r}+m-${k}j-1,m-${k}j) binom(m-${k}j,j) ${c+1}^(m-${k+1}j)`,note:'H(m)=0 for m<0. For a declared seed vector, convolve b with the displayed generating-function numerator; for the nonzero tail, a=b.'},{title:'Finite hypergeometric closed form',expression:outer+`\nH(m)=${c+1}^m binom(${r}+m-1,m) ${k+1}F${k}(${top}; ${bottom}; ${argument})`,note:`The hypergeometric symbol means exactly j=0..floor(m/${k+1}), before parameter cancellation. H(m)=0 for m<0. The seed numerator acts by finite convolution.`},{title:'Recurrence and seeds',expression:p.seedMode==='tail'?`a(0)=1; n a(n)=${c} sum_(j=1)^min(${k},n) (n+(${r}-1)j)a(n-j)`:`a(n)=${c} sum_(j=1)^${k} a(n-j), n>=${k}`,note:p.seedMode==='tail'?'Applies for n>=1. The division by n is exact.':result.normalization});
  }else if(['reciprocal','congruential','appell'].includes(result.engine))forms.push({title:'Ordinary differential coefficient recurrence',expression:`h(0)=1; h(n)=-sum_(k=1)^n (n+(${p.r}-1)k)d(k)h(n-k)/n`,note:`For the reciprocal tower d(k)=(-1)^k/(${p.N}k)!. For the positive congruential section d(k)=${factorial(p.j)}/(${p.N}k+${p.j})!. `+(result.engine==='appell'&&p.appellMode==='column'?`The ordinary x^${p.column} column is h(n) times (${p.N}n)! binom(${p.N}n+${p.column},${p.column}), at polynomial row ${p.N}n+${p.column}.`:'Restore the displayed factorial normalization; Appell point values then use the finite exponential-product coefficient sum.')});
  else if(result.engine==='secancy')forms.push({title:'Exact polynomial coefficient recurrence',expression:`n P(n,k)=-sum_(i=1)^n (-1)^i binom(${p.N}n,${p.N}i) ((n-i)P(n-i,k)+i P(n-i,k-1))`,note:'P(0,0)=1; coefficients outside the polynomial row are zero. This follows by differentiating D_N(z)^(-r) and comparing powers of r.'});
  return forms;
}
