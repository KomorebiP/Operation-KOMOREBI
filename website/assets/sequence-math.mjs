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

/**
 * Transcribe a complete stored triangle row. The original indexed integer
 * values remain in the table and exports; this never extrapolates a row.
 */
export function triangleRowExpressions(entry,cells) {
  if(!entry?.triangle||!Array.isArray(cells)||!cells.length)throw Error('Expected one complete coefficient row.');
  const n=cells[0].n,expected=entry.triangle.row_lengths?.[n];
  if(!Number.isSafeInteger(n)||!Number.isSafeInteger(expected)||cells.length!==expected||cells.some((cell,k)=>cell.n!==n||cell.k!==k))throw Error('The row coefficients do not match the recorded index map.');
  const x=entry.triangle.variable==='r'?'r':'x';
  let texLabel,plainLabel;
  if(entry.id.startsWith('KFOR-TRI-P-')) {
    texLabel='P_{'+entry.N+','+n+'}('+x+')';
    plainLabel='P_('+entry.N+','+n+')('+x+')';
  } else if(entry.id==='KFOR-TRI-H') {
    texLabel='\\Theta_{'+(2*n)+'}('+x+')';
    plainLabel='Theta_('+(2*n)+')('+x+')';
  } else if(entry.id.startsWith('KFOR-TRI-A-')) {
    texLabel='E_{'+n+'}('+x+')';
    plainLabel='E_'+n+'('+x+')';
  } else {
    // For matrix kernels R_n is just a polynomial encoding of row n.
    texLabel='R_{'+n+'}('+x+')';
    plainLabel='R_'+n+'('+x+')';
  }
  const terms=[];
  for(const cell of cells) {
    const c=parseExactRational(cell.raw);
    if(c.denominator)throw Error('Triangle rows must contain exact integers.');
    if(c.numerator==='0')continue;
    const negative=c.negative,unit=c.numerator==='1'&&cell.k>0;
    const value=unit?'':c.numerator;
    const texPower=cell.k===0?'':cell.k===1?x:x+'^{'+cell.k+'}';
    const plainPower=cell.k===0?'':cell.k===1?x:x+'^'+cell.k;
    terms.push({
      sign:negative?'-':'+',
      tex:value+(value&&texPower?'\\,':'')+texPower,
      plain:value+plainPower
    });
  }
  const makeExpr=key=>{
    if(!terms.length)return '0';
    return terms.map((term,i)=>(i===0?(term.sign==='-'?'-':''):term.sign==='-'?' - ':' + ')+term[key]).join('');
  };
  return {plain:plainLabel+' = '+makeExpr('plain'),tex:texLabel+'='+makeExpr('tex')};
}

/**
 * Display a leading principal block of the exact lower-triangular
 * convolution operator. Matrix entries are already certified rationals.
 * This is presentation only and does not change the transfer certificate.
 */
function matrixFormula(values,symbol,tex){
  if(!['H','K'].includes(symbol)||!Array.isArray(values)||!values.length||values.length>8||
      values.some(row=>!Array.isArray(row)||row.length!==values.length)){
    throw Error('Expected a square matrix of 1 to 8 exact coefficients.');
  }
  const rows=values.map(row=>row.map(value=>{
    const parsed=parseExactRational(value);
    if(tex)return rationalTeX(value);
    return (parsed.negative?'-':'')+absoluteCoefficient(parsed,false);
  }));
  return tex
    ?'L('+symbol+')=\\begin{pmatrix}'+rows.map(row=>row.join(' & ')).join(' \\\\ ')+'\\end{pmatrix}'
    :'L('+symbol+') = ['+rows.map(row=>'['+row.join(', ')+']').join(', ')+']';
}
export function transferMatrixTeX(values,symbol){return matrixFormula(values,symbol,true);}
export function transferMatrixPlain(values,symbol){return matrixFormula(values,symbol,false);}
