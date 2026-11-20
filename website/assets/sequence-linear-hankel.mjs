// Linear-weight Hankel determinants and the uniform order-nine recurrence.
// Author: Komorebi P. All coefficient arithmetic uses BigInt.
function exact(value){
  if(typeof value==='bigint')return value;
  if(typeof value==='number'&&!Number.isSafeInteger(value))
    throw Error('Linear Hankel parameters must be exact integers without rounding.');
  if(!/^-?(0|[1-9][0-9]*)$/.test(String(value)))
    throw Error('Linear Hankel parameters must be integers.');
  return BigInt(value);
}
function multiply(a,b){
  const out=Array(a.length+b.length-1).fill(0n);
  for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)out[i+j]+=a[i]*b[j];
  return out;
}
function text(values,variable='z'){
  let output='';
  values.forEach((value,k)=>{
    if(value===0n)return;
    const negative=value<0n,magnitude=negative?-value:value;
    const power=k?(k===1?variable:variable+'^'+k):'';
    const term=power?(magnitude===1n?power:magnitude+'*'+power):String(magnitude);
    output+=(output?(negative?' - ':' + '):(negative?'-':''))+term;
  });
  return output||'0';
}
export function linearHankelGeneratingFunction(first,slope){
  const a=exact(first),b=exact(slope);
  const numerator=[
    1n,-17n*a+12n*b,2n*(64n*a*a-77n*a*b+24n*b*b),
    -8n*(70n*a**3n-105n*a*a*b+51n*a*b*b-7n*b**3n),
    8n*a*(196n*a**3n-315n*a*a*b+168n*a*b*b-30n*b**3n),
    -32n*a*(91n*a**4n-140n*a**3n*b+66n*a*a*b*b-8n*a*b**3n-2n*b**4n),
    32n*a**3n*(112n*a**3n-147n*a*a*b+48n*a*b*b+2n*b**3n),
    -128n*a**4n*(2n*a-b)*(11n*a*a-5n*a*b-b*b),
    640n*a**7n*(2n*a-b),-256n*a**9n
  ];
  const factor=multiply([1n,-2n*a],[1n,-4n*(a-b),4n*a*a]);
  const denominator=multiply(multiply(factor,factor),factor);
  return {numerator,denominator};
}
export function linearHankelCoefficients(a,b,last){
  if(!Number.isInteger(last)||last<0||last>256)
    throw Error('The linear Hankel index must be between 0 and 256.');
  const {numerator,denominator}=linearHankelGeneratingFunction(a,b),values=[];
  for(let n=0;n<=last;n++){
    let value=numerator[n]||0n;
    for(let j=1;j<=Math.min(n,denominator.length-1);j++)value-=denominator[j]*values[n-j];
    values.push(value);
  }
  return values;
}
export function linearHankelFormula(a,b){
  const {numerator,denominator}=linearHankelGeneratingFunction(a,b);
  return {
    kind:'rational-hankel',recurrenceOrderBound:9,
    numerator:numerator.map(String),denominator:denominator.map(String),
    expression:'P(m) = '+exact(a)+' + ('+exact(b)+')*m; D_x = 1.\n'+
      'H(z) = ('+text(numerator)+') / ('+text(denominator)+').\n\n'+
      'For every n >= 1, with S W_n = W_(n+1):\n'+
      '[(S-2*a)*(S^2-4*(a-b)*S+4*a^2)]^3 W_n = 0.\n'+
      'The denominator has constant term 1; no singular-pivot division is used.\n'+
      'Order 9 is minimal generically and at a=b=1; special parameters can reduce the order.'
  };
}
