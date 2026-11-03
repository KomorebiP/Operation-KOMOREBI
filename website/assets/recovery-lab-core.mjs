// Exact rational linear algebra for small real-linear recovery questions.
// BigInt is used throughout the certificates; only the display plots round values.
const abs = n => n < 0n ? -n : n;
function gcd(a, b) { a = abs(a); b = abs(b); while (b) [a, b] = [b, a % b]; return a; }
function q(n, d = 1n) {
  if (!d) throw new RangeError('A denominator cannot be zero.');
  if (d < 0n) { n = -n; d = -d; }
  const g = gcd(n, d);
  return {n:n/g, d:d/g};
}
const zero = () => q(0n);
const add = (a,b) => q(a.n*b.d + b.n*a.d, a.d*b.d);
const neg = a => q(-a.n,a.d);
const sub = (a,b) => add(a,neg(b));
const mul = (a,b) => q(a.n*b.n,a.d*b.d);
const div = (a,b) => q(a.n*b.d,a.d*b.n);
const str = a => a.d === 1n ? String(a.n) : `${a.n}/${a.d}`;
const dot = (a,b) => a.reduce((s,v,i) => add(s,mul(v,b[i])),zero());
const strings = a => a.map(str);
const matrixStrings = a => a.map(strings);

function parse(value) {
  if (typeof value === 'number' && Number.isInteger(value)) value = String(value);
  if (typeof value !== 'string' || value.length > 9 || !/^-?\d{1,2}(?:\/[1-9]\d?)?$/.test(value.trim())) {
    throw new RangeError('Use an integer from −99 to 99, or a fraction such as −2/3 with denominator 1–99.');
  }
  const [n,d='1'] = value.trim().split('/');
  return q(BigInt(n),BigInt(d));
}
function matrix(value, columns, maxRows) {
  if (!Array.isArray(value) || value.length < 1 || value.length > maxRows) throw new RangeError('Invalid matrix size.');
  return Array.from(value,row => {
    if (!Array.isArray(row) || row.length !== columns) throw new RangeError('Every row needs one entry per input coordinate.');
    return Array.from(row,parse);
  });
}

export function validateExperiment(value) {
  if (!value || typeof value !== 'object' || value.v !== 1 || ![2,3,4].includes(value.n)) throw new RangeError('Unsupported recovery experiment.');
  const R = matrix(value.R,value.n,4), F = matrix(value.F,value.n,3);
  if (!Array.isArray(value.enabled) || value.enabled.length !== R.length ||
      Array.from(value.enabled).some(v => typeof v !== 'boolean')) throw new RangeError('Choose which measurements are available.');
  if (!Array.isArray(value.x) || value.x.length !== value.n ||
      Array.from(value.x).some(v => !Number.isInteger(v) || Math.abs(v)>4)) throw new RangeError('Input coordinates must be integers from −4 to 4.');
  if (!Number.isInteger(value.t) || Math.abs(value.t)>4 || !Number.isInteger(value.question) || value.question<0 || value.question>=F.length) throw new RangeError('Invalid inspection settings.');
  return {v:1,n:value.n,R:matrixStrings(R),F:matrixStrings(F),enabled:Array.from(value.enabled),x:Array.from(value.x),t:value.t,question:value.question};
}

function reduce(A,columns,trace=false) {
  const rows = A.map(row => row.slice()), size = rows.length;
  const transform = Array.from({length:size},(_,i) => Array.from({length:size},(_,j)=>q(i===j ? 1n : 0n)));
  const pivots=[], operations=[];
  let target=0;
  for (let col=0; col<columns && target<size; col++) {
    const selected = rows.findIndex((row,i)=>i>=target && row[col].n!==0n);
    if (selected<0) continue;
    if (selected!==target) {
      [rows[target],rows[selected]]=[rows[selected],rows[target]];
      [transform[target],transform[selected]]=[transform[selected],transform[target]];
      if (trace) operations.push(`Swap rows ${target+1} and ${selected+1}.`);
    }
    const scale = rows[target][col];
    if (scale.n!==scale.d) {
      rows[target]=rows[target].map(v=>div(v,scale));
      transform[target]=transform[target].map(v=>div(v,scale));
      if (trace) operations.push(`Divide row ${target+1} by ${str(scale)}.`);
    }
    for (let i=0;i<size;i++) {
      if (i===target || rows[i][col].n===0n) continue;
      const factor=rows[i][col];
      rows[i]=rows[i].map((v,j)=>sub(v,mul(factor,rows[target][j])));
      transform[i]=transform[i].map((v,j)=>sub(v,mul(factor,transform[target][j])));
      if (trace) operations.push(`Row ${i+1} ← row ${i+1} − (${str(factor)}) × row ${target+1}.`);
    }
    pivots.push(col); target++;
  }
  return {rows,transform,pivots,operations};
}
function primitive(vector) {
  const denominator=vector.reduce((d,v)=>d/gcd(d,v.d)*v.d,1n);
  const values=vector.map(v=>v.n*(denominator/v.d));
  const divisor=values.reduce(gcd,0n);
  const sign=values.find(v=>v!==0n)<0n ? -1n : 1n;
  return values.map(v=>q(v/divisor*sign));
}
function kernel(reduced,n) {
  return Array.from({length:n},(_,i)=>i).filter(i=>!reduced.pivots.includes(i)).map(col=>{
    const w=Array.from({length:n},zero); w[col]=q(1n);
    reduced.pivots.forEach((pivot,row)=>{w[pivot]=neg(reduced.rows[row][col]);});
    return primitive(w);
  });
}

export function analyzeRecovery(input) {
  const state=validateExperiment(input), n=state.n;
  const R=state.R.map(row=>row.map(parse)), F=state.F.map(row=>row.map(parse));
  const active=R.map((_,i)=>i).filter(i=>state.enabled[i]);
  const A=active.map(i=>R[i]), reduced=reduce(A,n,true), basis=kernel(reduced,n);
  const questions=F.map(f=>{
    let remainder=f.slice();
    const weights=R.map(zero);
    reduced.pivots.forEach((pivot,row)=>{
      const coefficient=remainder[pivot];
      remainder=remainder.map((v,j)=>sub(v,mul(coefficient,reduced.rows[row][j])));
      active.forEach((original,i)=>{weights[original]=add(weights[original],mul(coefficient,reduced.transform[row][i]));});
    });
    const recoverable=remainder.every(v=>v.n===0n);
    const witness=recoverable ? null : basis.find(w=>dot(f,w).n!==0n);
    return {recoverable,weights:recoverable ? strings(weights) : null,
      witness:witness ? strings(witness) : null,change:witness ? str(dot(f,witness)) : '0'};
  });
  // Preserve an independent subset of the available measurements, then add only
  // target rows that increase rank. This reaches rank([R;F]) in the fewest new rows.
  const independent=[], retainedRows=[], addedQuestions=[];
  let rank=0;
  active.forEach(i=>{
    const next=reduce([...independent,R[i]],n).pivots.length;
    if (next>rank) { independent.push(R[i]); retainedRows.push(i); rank=next; }
  });
  F.forEach((f,i)=>{
    const next=reduce([...independent,f],n).pivots.length;
    if (next>rank) { independent.push(f); addedQuestions.push(i); rank=next; }
  });
  const selected=questions[state.question];
  const direction=selected.witness ? selected.witness.map(v=>{
    const [a,b='1']=v.split('/');return q(BigInt(a),BigInt(b));
  }) : basis[0] || Array.from({length:n},zero);
  const x=state.x.map(v=>q(BigInt(v))), moved=x.map((v,i)=>add(v,mul(q(BigInt(state.t)),direction[i])));
  const apply=(M,v)=>strings(M.map(row=>dot(row,v)));
  return {state,active,rank:reduced.pivots.length,nullity:basis.length,
    kernel:matrixStrings(basis),rref:matrixStrings(reduced.rows),transform:matrixStrings(reduced.transform),operations:reduced.operations,
    questions,recoverable:questions.filter(v=>v.recoverable).length,
    repair:{retainedRows,addedQuestions,additional:addedQuestions.length,R:matrixStrings(independent)},
    motion:{direction:strings(direction),x:strings(x),moved:strings(moved),
      summary:apply(A,x),movedSummary:apply(A,moved),answers:apply(F,x),movedAnswers:apply(F,moved)}};
}

export function repairExperiment(input) {
  const result=analyzeRecovery(input);
  // A zero measurement represents the rank-zero summary when every question is zero.
  const R=result.repair.R.length ? result.repair.R : [Array(input.n).fill('0')];
  return validateExperiment({...result.state,R,enabled:R.map(()=>true)});
}

export function encodeRecovery(input) {
  return btoa(JSON.stringify(validateExperiment(input))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
export function decodeRecovery(encoded) {
  if (typeof encoded!=='string' || encoded.length>4096 || !/^[A-Za-z0-9_-]+$/.test(encoded)) throw new RangeError('Invalid recovery link.');
  try { return validateExperiment(JSON.parse(atob(encoded.replace(/-/g,'+').replace(/_/g,'/')))); }
  catch { throw new RangeError('This recovery link is invalid or uses an unsupported version.'); }
}

export const PRESETS = {
  sum:{title:'A sum loses a coordinate',n:2,R:[['1','1']],F:[['1','0']],x:[1,0]},
  sufficient:{title:'Recover without knowing x',n:3,R:[['1','1','0'],['0','1','1']],F:[['2','3','1']],x:[1,2,-1]},
  partial:{title:'Two questions, one obstruction',n:3,R:[['1','1','0'],['0','0','1']],F:[['2','2','0'],['1','-1','0']],x:[1,0,2]},
  redundant:{title:'More rows, no more information',n:3,R:[['1','1','0'],['2','2','0'],['0','0','0']],F:[['1','0','0'],['0','0','1']],x:[1,0,2]},
  fractions:{title:'An exact fractional rule',n:3,R:[['2','1','0'],['0','3','1']],F:[['1','2','1/2']],x:[2,1,-1]},
  invertible:{title:'Recover the whole input',n:2,R:[['1','1'],['1','-1']],F:[['1','0'],['0','1']],x:[2,1]}
};
export function presetExperiment(name) {
  const preset=PRESETS[name];
  if (!preset) throw new RangeError('Unknown recovery starter.');
  return validateExperiment({v:1,...preset,enabled:preset.R.map(()=>true),t:1,question:0});
}
