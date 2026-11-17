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
function witnessParts(rows,j,tex,direction){
  const first=direction==='inverse'?'inverse':'kernel';
  const second=direction==='inverse'?'target':'source';
  const pieces=[];
  for(let i=0;i<=j;i++){
    const a=parseExactRational(rows[i][first]),b=parseExactRational(rows[j-i][second]);
    const negative=a.negative!==b.negative;
    const left=absoluteCoefficient(a,tex),right=absoluteCoefficient(b,tex);
    const term=tex?'\\left('+left+'\\right)\\left('+right+'\\right)':'('+left+')*('+right+')';
    pieces.push((pieces.length?(negative?' - ':' + '):(negative?'-':''))+term);
  }
  return pieces.join('');
}
function witness(rows,j,tex,direction='forward') {
  if(!Array.isArray(rows)||!Number.isSafeInteger(j)||j<0||j>=rows.length)throw Error('Witness index is outside the coefficient window.');
  if(!['forward','inverse'].includes(direction))throw Error('Choose a forward or inverse witness.');
  const inverse=direction==='inverse',row=rows[j],sum=witnessParts(rows,j,tex,direction);
  const letter=inverse?'a':'b',kernel=inverse?'k':'h',other=inverse?'b':'a';
  const value=inverse?row.recovered:row.forward,stored=inverse?row.source:row.target;
  if(tex)return '\\begin{aligned}'+letter+'_{'+j+'}&=\\sum_{i=0}^{'+j+'}'+kernel+'_i '+other+'_{'+j+'-i}\\\\&='+sum+'\\\\&='+rationalTeX(value)+'\\qquad(\\mathrm{stored\\ '+(inverse?'source':'target')+'}='+rationalTeX(stored)+(inverse?'':',\\;\\mathrm{residual}='+rationalTeX(row.residual))+')\\end{aligned}';
  return letter+'_'+j+' = sum(i=0..'+j+') '+kernel+'_i*'+other+'_('+j+'-i) = '+sum+' = '+value+'; '+(inverse?'source':'target')+'='+stored+(inverse?'':'; residual='+row.residual);
}
export function transferWitnessTeX(rows,j,direction='forward'){return witness(rows,j,true,direction);}
export function transferWitnessPlain(rows,j,direction='forward'){return witness(rows,j,false,direction);}
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
    if(typeof value!=='string')throw Error('Expected an exact rational coefficient string.');
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

/** Exact finite matrix-vector actions. Index shifts remain external metadata. */
export function transferActionEquations(rows,size){
  if(!Array.isArray(rows)||!Number.isSafeInteger(size)||size<1||size>8||rows.length<size){
    throw Error('Choose 1 to 8 stored coefficients for the matrix action.');
  }
  const selected=rows.slice(0,size);
  for(const row of selected)if(row.forward!==row.target||row.recovered!==row.source){
    throw Error('Matrix action requires an exact forward and inverse certificate.');
  }
  const vector=(values,tex)=>{
    const cells=values.map(value=>{
      if(typeof value!=='string')throw Error('Matrix action requires exact coefficient strings.');
      return tex?rationalTeX(value):value;
    });
    return tex?'\\begin{pmatrix}'+cells.join('\\\\')+'\\end{pmatrix}':'['+cells.join(', ')+']';
  };
  const source=selected.map(row=>row.source),target=selected.map(row=>row.target);
  const forward={
    plain:'L_'+size+'(H) '+vector(source,false)+' = '+vector(target,false),
    tex:'L_{'+size+'}(H)'+vector(source,true)+'='+vector(target,true)
  };
  const inverse={
    plain:'L_'+size+'(K) '+vector(target,false)+' = '+vector(source,false),
    tex:'L_{'+size+'}(K)'+vector(target,true)+'='+vector(source,true)
  };
  return {forward,inverse};
}

/** Render an independently evaluated finite product entry without altering data. */
export function transferProductMath(witness){
  if(!witness||!['HK','KH'].includes(witness.order)||!Number.isSafeInteger(witness.row)||
     !Number.isSafeInteger(witness.column)||!Array.isArray(witness.terms)||
     !['0','1'].includes(witness.expected)){
    throw Error('Expected a valid finite matrix-product witness.');
  }
  const {row,column,order,terms,value,expected}=witness;
  if(!witness.verified||value!==expected)throw Error('The exact matrix product entry failed its identity check.');
  const [first,second]=order==='HK'?['H','K']:['K','H'];
  const lhs='\\bigl(L('+first+')L('+second+')\\bigr)_{'+row+','+column+'}';
  const plainLhs='(L('+first+')L('+second+'))['+row+','+column+']';
  if(!terms.length){
    if(row<=column&&row!==column){
      return {plain:plainLhs+' = 0 = delta('+row+','+column+')',
        tex:lhs+'=0=\\delta_{'+row+','+column+'}'};
    }
    throw Error('The lower-triangular witness has no recorded summands.');
  }
  const products=terms.map(term=>{
    if(typeof term.left!=='string'||typeof term.right!=='string')throw Error('Missing exact rational summands.');
    return {plain:'('+term.left+')*('+term.right+')',
      tex:'\\left('+rationalTeX(term.left)+'\\right)\\left('+rationalTeX(term.right)+'\\right)'};
  });
  const formula=first.toLowerCase()+'_{'+row+'-\\ell}'+second.toLowerCase()+'_{\\ell-'+column+'}';
  const tex='\\begin{aligned}'+lhs+'&=\\sum_{\\ell='+column+'}^{'+row+'}'+formula+
    '\\\\&='+products.map(term=>term.tex).join('+')+'\\\\&='+rationalTeX(value)+
    '=\\delta_{'+row+','+column+'}\\end{aligned}';
  const plain=plainLhs+' = '+products.map(term=>term.plain).join(' + ')+
    ' = '+value+' = delta('+row+','+column+')';
  return {plain,tex};
}

/** Local coefficient position is distinct from either sequence's source index. */
export function transferIndexMath(map){
  const a=map?.sourceAnchor?.index,b=map?.targetAnchor?.index,n=map?.count;
  if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||!Number.isSafeInteger(n)||
    n<1||map.indexShift!==b-a)throw Error('Expected consistent integer transfer anchors.');
  return {
    plain:'source index = '+a+'+j; target index = '+b+'+j; original index shift = '+(b-a)+'; 0<=j<'+n,
    tex:'\\begin{aligned}i_{\\mathrm{source}}(j)&='+a+'+j\\\\i_{\\mathrm{target}}(j)&='+b+
      '+j\\\\\\Delta i&='+String(b-a)+',\\quad 0\\le j<'+n+'\\end{aligned}'
  };
}
