// Display-only transcription helpers. Exact sequence values and exports are unchanged.
// Keep these functions independent of MathJax so coefficient identities can be tested in Node.
export function parseExactRational(value) {
  const match=/^(-?)(\d+)(?:\/(\d+))?$/.exec(String(value));
  if(!match || match[3]==='0')throw Error('Expected an exact rational coefficient.');
  return {negative:match[1]==='-'&&match[2]!=='0',numerator:match[2],denominator:match[3]||null};
}
function absoluteCoefficient(parsed,tex) {
  return parsed.denominator?(tex?'\\frac{'+parsed.numerator+'}{'+parsed.denominator+'}':parsed.numerator+'/'+parsed.denominator):parsed.numerator;
}
export function rationalTeX(value) {
  const parsed=parseExactRational(value);
  return (parsed.negative?'-':'')+absoluteCoefficient(parsed,true);
}
function polynomial(rows,key,symbol,maxTerms,tex) {
  if(!Array.isArray(rows)||!rows.length||!Number.isSafeInteger(maxTerms)||maxTerms<1)throw Error('Expected a nonempty coefficient window.');
  const bound=Math.min(rows.length,maxTerms),terms=[];
  for(let j=0;j<bound;j++){
    const parsed=parseExactRational(rows[j][key]);
    if(parsed.numerator==='0')continue;
    const unit=parsed.numerator==='1'&&!parsed.denominator&&j>0;
    const coefficient=unit?'':absoluteCoefficient(parsed,tex);
    const variable=j===0?'':j===1?'z':tex?'z^{'+j+'}':'z^'+j;
    const term=[coefficient,variable].filter(Boolean).join(tex?'\\,':'');
    terms.push((terms.length?(parsed.negative?' - ':' + '):(parsed.negative?'-':''))+term);
  }
  const rhs=terms.join('')||'0';
  return symbol+'(z)'+(tex?'\\equiv ':' = ')+rhs+(tex?'\\pmod{z^{'+bound+'}}':' (mod z^'+bound+')');
}
export function transferPolynomialTeX(rows,key,symbol,maxTerms=4) {
  return polynomial(rows,key,symbol,maxTerms,true);
}
export function transferPolynomialPlain(rows,key,symbol,maxTerms=4) {
  return polynomial(rows,key,symbol,maxTerms,false);
}
function witnessParts(rows,j,tex){
  const pieces=[];
  for(let i=0;i<=j;i++){
    const a=parseExactRational(rows[i].kernel),b=parseExactRational(rows[j-i].source);
    const negative=a.negative!==b.negative;
    const first=absoluteCoefficient(a,tex),second=absoluteCoefficient(b,tex);
    const term=tex?'\\left('+first+'\\right)\\left('+second+'\\right)':'('+first+')*('+second+')';
    pieces.push((pieces.length?(negative?' - ':' + '):(negative?'-':''))+term);
  }
  return pieces.join('');
}
function witness(rows,j,tex) {
  if(!Array.isArray(rows)||!Number.isSafeInteger(j)||j<0||j>=rows.length)throw Error('Witness index is outside the coefficient window.');
  const row=rows[j],sum=witnessParts(rows,j,tex);
  if(tex)return '\\begin{aligned}b_{'+j+'}&=\\sum_{i=0}^{'+j+'}h_i a_{'+j+'-i}\\\\&='+sum+'\\\\&='+rationalTeX(row.forward)+'\\qquad(\\mathrm{target}='+rationalTeX(row.target)+',\\;\\mathrm{residual}='+rationalTeX(row.residual)+')\\end{aligned}';
  return 'b_'+j+' = sum(i=0..'+j+') h_i*a_('+j+'-i) = '+sum+' = '+row.forward+'; target='+row.target+'; residual='+row.residual;
}
export function transferWitnessTeX(rows,j){return witness(rows,j,true);}
export function transferWitnessPlain(rows,j){return witness(rows,j,false);}
export function mathLine(source,tex,className='sr-transfer-equation'){
  const element=document.createElement('p');
  element.className='sar-formula '+className;
  element.textContent=source;
  element.setAttribute('data-math-latex',tex);
  return element;
}
