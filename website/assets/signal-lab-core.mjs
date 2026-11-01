// Bounded, known-reference experiments. No inference about unknown real data.
export const SIZES = [16,32,64,128,256];
export const BASES = ['haar','cosine','samples'];
export const POLICIES = ['energy','magnitude','prefix'];
const SHAPES = ['steps','wave','chirp','spikes','triangle','mixed','custom'];
const invalid = message => { throw new RangeError(message); };
const size = n => { if (!SIZES.includes(n)) invalid('Choose 16, 32, 64, 128, or 256 samples.'); return n; };
function integer(value,low,high,label) {
  if (!Number.isInteger(value) || value < low || value > high) invalid(label);
  return value || 0;
}
function signal(values,bound=128) {
  if (!Array.isArray(values)) invalid('A sample array is required.');
  size(values.length);
  if (Array.from(values).some(v=>!Number.isFinite(v)||Math.abs(v)>bound)) invalid('Samples are outside the supported range.');
}
export const defaults = () => ({v:1,n:64,shape:'steps',amplitude:16,cycles:3,noise:4,seed:17,
  budget:12,policy:'energy',basis:'haar',coefficient:1,address:32});
export function settings(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw) || raw.v !== 1) invalid('Unsupported experiment format.');
  const n = size(raw.n);
  if (!SHAPES.includes(raw.shape)||!BASES.includes(raw.basis)||!POLICIES.includes(raw.policy)) invalid('Unknown signal, representation, or selection rule.');
  const value = {v:1,n,shape:raw.shape,
    amplitude:integer(raw.amplitude,1,24,'Amplitude must be a whole number from 1 to 24.'),
    cycles:integer(raw.cycles,1,Math.min(16,n/4),'Frequency is outside the range for this sample count.'),
    noise:integer(raw.noise,0,16,'Noise must be a whole number from 0 to 16.'),
    seed:integer(raw.seed,0,4294967295,'Seed must be a whole number from 0 to 4294967295.'),
    budget:integer(raw.budget,0,n,'Coefficient budget is outside the sample count.'),
    policy:raw.policy,basis:raw.basis,
    coefficient:integer(raw.coefficient,0,n-1,'Coefficient index is outside the sample count.'),
    address:integer(raw.address,0,n-1,'Sample address is outside the sample count.')};
  if (raw.shape === 'custom') {
    if (!Array.isArray(raw.custom)||raw.custom.length!==n) invalid('Custom samples must match the sample count.');
    value.custom = Array.from(raw.custom,v=>integer(v,-64,64,'Imported reference samples must be whole numbers from −64 to 64.'));
  }
  return value;
}
export function referenceSignal(config) {
  const s = settings(config), {n,amplitude:a,cycles:f} = s;
  if (s.shape === 'custom') return s.custom.slice();
  return Array.from({length:n},(_,i)=>{
    const t = (i+.5)/n;
    let v;
    if (s.shape === 'steps') v = a*(t<.25 ? .25 : t<.5 ? .75 : t<.75 ? -.5 : .5)+(i===Math.floor(.62*n) ? 1.5*a : 0);
    if (s.shape === 'wave') v = a*Math.cos(Math.PI*f*(i+.5)/n);
    if (s.shape === 'chirp') v = a*Math.sin(Math.PI*f*t*t);
    if (s.shape === 'spikes') v = i===Math.floor(.2*n) ? a : i===Math.floor(.53*n) ? -a : i===Math.floor(.77*n) ? .6*a : 0;
    if (s.shape === 'triangle') v = a*(1-4*Math.abs(t-.5));
    if (s.shape === 'mixed') v = a*(.55*Math.cos(Math.PI*f*t)+.25*(t<.5 ? -1 : 1)+(i===Math.floor(.6*n) ? .2 : 0));
    return Math.round(v)||0;
  });
}
export function noiseSignal(n,amplitude,seed) {
  size(n); integer(amplitude,0,16,'Invalid noise amplitude.'); integer(seed,0,4294967295,'Invalid seed.');
  let state = seed >>> 0;
  return Array.from({length:n},()=>{
    state = (Math.imul(1664525,state)+1013904223) >>> 0;
    return Math.floor(state/4294967296*(2*amplitude+1))-amplitude;
  });
}
const cosineCache = new Map();
function cosineRows(n) {
  if (!cosineCache.has(n)) cosineCache.set(n,Array.from({length:n},(_,k)=>
    Float64Array.from({length:n},(_,i)=>(k===0 ? 1/Math.sqrt(n) : Math.sqrt(2/n))*Math.cos(Math.PI*k*(i+.5)/n))));
  return cosineCache.get(n);
}
export function basisVector(n,basis,index) {
  size(n); integer(index,0,n-1,'Invalid coefficient index.');
  if (basis==='samples') return Array.from({length:n},(_,i)=>Number(i===index));
  if (basis==='cosine') return Array.from(cosineRows(n)[index]);
  if (basis!=='haar') invalid('Unknown representation.');
  if (index===0) return Array(n).fill(1);
  const group = Math.floor(Math.log2(index)), width = n/2**group, start = (index-2**group)*width;
  return Array.from({length:n},(_,i)=>i<start||i>=start+width ? 0 : i<start+width/2 ? 1 : -1);
}
export function analyze(values,basis) {
  signal(values); const n=values.length;
  if (basis==='samples') return {values:values.slice(),weights:Array(n).fill(1),metadata:values.map((_,i)=>({label:'Sample '+i,start:i,end:i,kind:'sample'}))};
  if (basis==='cosine') {
    // Orthonormal DCT-II, including the distinct normalization of k=0.
    // Convention: https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dct.html
    const coefficients = cosineRows(n).map(row=>row.reduce((sum,v,i)=>sum+v*values[i],0)||0);
    return {values:coefficients,weights:Array(n).fill(1),metadata:coefficients.map((_,k)=>({label:k===0 ? 'DC / mean mode' : 'Cosine mode '+k,start:0,end:n-1,kind:'cosine'}))};
  }
  if (basis!=='haar') invalid('Unknown representation.');
  let averages=values.slice(); const levels=[];
  for(let level=1;averages.length>1;level++) {
    const next=[],details=[];
    for(let i=0;i<averages.length;i+=2) {next.push((averages[i]+averages[i+1])/2);details.push((averages[i]-averages[i+1])/2);}
    levels.push({level,details}); averages=next;
  }
  const coefficients=[averages[0]],weights=[n],metadata=[{label:'Global mean',start:0,end:n-1,kind:'mean'}];
  for(const {level,details} of levels.reverse()) details.forEach((v,i)=>{
    coefficients.push(v||0);weights.push(2**level);
    metadata.push({label:`Level ${level}, detail ${i}`,start:i*2**level,end:(i+1)*2**level-1,kind:'detail'});
  });
  return {values:coefficients,weights,metadata};
}
export function synthesize(coefficients,basis) {
  if(!Array.isArray(coefficients))invalid('A coefficient array is required.');
  const n=size(coefficients.length);
  if (Array.from(coefficients).some(v=>!Number.isFinite(v)||Math.abs(v)>4096)) invalid('Invalid coefficients.');
  if (basis==='samples') return coefficients.slice();
  if (basis==='cosine') {
    const rows=cosineRows(n);
    return Array.from({length:n},(_,i)=>coefficients.reduce((sum,c,k)=>sum+c*rows[k][i],0)||0);
  }
  if (basis!=='haar') invalid('Unknown representation.');
  let result=[coefficients[0]],offset=1;
  while(result.length<n) {
    const next=[];
    for(const average of result) {const d=coefficients[offset++];next.push(average+d,average-d);}
    result=next;
  }
  return result.map(v=>v||0);
}
export function rankCoefficients(analysis,policy) {
  if (!POLICIES.includes(policy)) invalid('Unknown selection rule.');
  const score = i => policy==='energy' ? analysis.weights[i]*analysis.values[i]**2 : Math.abs(analysis.values[i]);
  return analysis.values.map((_,i)=>i).sort((a,b)=>policy==='prefix' ? a-b : score(b)-score(a)||a-b);
}
export function errorCurve(observed,reference,order) {
  const n=observed.values.length,observedTail=Array(n+1).fill(0),referenceTail=Array(n+1).fill(0);
  for(let k=n-1;k>=0;k--) {
    const i=order[k],w=observed.weights[i];
    observedTail[k]=observedTail[k+1]+w*observed.values[i]**2;
    referenceTail[k]=referenceTail[k+1]+w*reference.values[i]**2;
  }
  let keptNoise=0;
  return Array.from({length:n+1},(_,k)=>{
    if(k>0){const i=order[k-1];keptNoise+=observed.weights[i]*(observed.values[i]-reference.values[i])**2;}
    return {budget:k,observedError:observedTail[k],referenceError:referenceTail[k]+keptNoise};
  });
}
export function squaredError(a,b) {return a.reduce((sum,v,i)=>sum+(v-b[i])**2,0);}
export function experiment(raw) {
  const config=settings(raw),reference=referenceSignal(config),noise=noiseSignal(config.n,config.noise,config.seed);
  const observed=reference.map((v,i)=>v+noise[i]),analyses={};
  for(const basis of BASES) {
    const a=analyze(observed,basis),r=analyze(reference,basis),order=rankCoefficients(a,config.policy);
    const curve=errorCurve(a,r,order),chosen=new Set(order.slice(0,config.budget));
    const kept=a.values.map((v,i)=>chosen.has(i)?v:0),reconstruction=synthesize(kept,basis);
    const minimum=Math.min(...curve.map(p=>p.referenceError));
    const tolerance=1e-10*Math.max(1,squaredError(reference,Array(config.n).fill(0)));
    const bestBudget=curve.find(p=>p.referenceError<=minimum+tolerance).budget;
    analyses[basis]={...a,order,curve,chosen:Array.from({length:config.n},(_,i)=>chosen.has(i)),reconstruction,bestBudget,
      referenceError:curve[config.budget].referenceError,observedError:curve[config.budget].observedError};
  }
  return {config,reference,observed,noise,noiseEnergy:noise.reduce((sum,v)=>sum+v*v,0),analyses};
}
export function encodeSettings(raw) {return btoa(JSON.stringify(settings(raw))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
export function decodeSettings(encoded) {
  if(typeof encoded!=='string'||encoded.length>4096||!/^[A-Za-z0-9_-]+$/.test(encoded))invalid('This lab link is invalid or too large.');
  try {return settings(JSON.parse(atob(encoded.replace(/-/g,'+').replace(/_/g,'/'))));}
  catch {invalid('This lab link could not be restored.');}
}
export function parseSamples(text) {
  if(typeof text!=='string'||text.length>65536)invalid('Use a numeric CSV or text file under 64 KiB.');
  const lines=text.trim().split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
  if(!lines.length)invalid('Paste or import some samples first.');
  if(lines.some(line=>/(?:^|[,;\t]) *(?=[,;\t]|$)/.test(line)))invalid('A sample is missing between delimiters.');
  const cells=line=>line.split(/[,;\t]/).map(v=>v.trim().replace(/^"(.*)"$/,'$1'));
  let values;
  if(lines.length===1 || lines.every(line=>cells(line).length===1 && !/[a-zA-Z]/.test(line))) values=text.trim().split(/[\s,;]+/).map(Number);
  else {
    const first=cells(lines[0]),header=first.some(v=>/[a-zA-Z]/.test(v));
    if(header) {
      const column=first.findIndex(v=>['reference','value','sample'].includes(v.toLowerCase()));
      if(column<0)invalid('CSV headers need a reference, value, or sample column.');
      values=lines.slice(1).map(line=>{const value=cells(line)[column];if(value===undefined||value==='')invalid('A CSV row is missing its sample.');return Number(value);});
    } else {
      const rows=lines.map(cells);
      const numeric=value=>{if(value==='')invalid('A CSV row is missing its sample.');return Number(value);};
      values=rows.every((row,i)=>row.length===2&&Number(row[0])===i) ? rows.map(row=>numeric(row[1])) : rows.flat().map(numeric);
    }
  }
  size(values.length);
  return values.map(v=>integer(v,-64,64,'Reference samples must be whole numbers from −64 to 64.'));
}
export function signalCsv(result) {
  const a=result.analyses[result.config.basis];
  return 'address,reference,observed,reconstruction,discarded_residual\n'+result.reference.map((v,i)=>[i,v,result.observed[i],a.reconstruction[i],result.observed[i]-a.reconstruction[i]].join(',')).join('\n')+'\n';
}
export function curvesCsv(result) {
  const header=['budget',...BASES.map(b=>b+'_reference_error'),...BASES.map(b=>b+'_observed_error')];
  return header.join(',')+'\n'+Array.from({length:result.config.n+1},(_,k)=>[k,...BASES.map(b=>result.analyses[b].curve[k].referenceError),...BASES.map(b=>result.analyses[b].curve[k].observedError)].join(',')).join('\n')+'\n';
}
export function experimentJson(result) {
  const a=result.analyses[result.config.basis];
  return JSON.stringify({schema:'komorebi-signal-lab-v1',settings:result.config,reference:result.reference,observed:result.observed,
    reconstruction:a.reconstruction,comparison:BASES.map(b=>({basis:b,referenceError:result.analyses[b].referenceError,observedError:result.analyses[b].observedError}))},null,2)+'\n';
}
export function importExperiment(text) {
  if(typeof text!=='string'||text.length>65536)invalid('Use an experiment JSON file under 64 KiB.');
  let parsed;try{parsed=JSON.parse(text);}catch{invalid('This is not valid experiment JSON.');}
  if(parsed?.schema!=='komorebi-signal-lab-v1')invalid('This is not a Signal Laboratory experiment file.');
  return settings(parsed.settings);
}
