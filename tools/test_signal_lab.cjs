const {test}=require('node:test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const core=import(pathToFileURL(path.join(__dirname,'../website/assets/signal-lab-core.mjs')));
const close=(actual,expected,scale=1)=>assert.ok(Math.abs(actual-expected)<=1e-9*Math.max(1,scale),`${actual} differs from ${expected}`);
const energy=values=>values.reduce((sum,v)=>sum+v*v,0);
const error=(a,b)=>a.reduce((sum,v,i)=>sum+(v-b[i])**2,0);

test('all signal generators and noise sequences are bounded and reproducible',async()=>{
  const m=await core;
  for(const n of m.SIZES)for(const shape of ['steps','wave','chirp','spikes','triangle','mixed']) {
    const config={...m.defaults(),n,shape,amplitude:24,cycles:Math.min(16,n/4),budget:0,address:0,coefficient:0};
    const reference=m.referenceSignal(config);
    assert.equal(reference.length,n);assert.ok(reference.every(v=>Number.isInteger(v)&&Math.abs(v)<=24));
    assert.deepEqual(m.referenceSignal(config),reference);
    const noise=m.noiseSignal(n,16,4294967295);
    assert.ok(noise.every(v=>Number.isInteger(v)&&Math.abs(v)<=16));
    assert.deepEqual(m.noiseSignal(n,16,4294967295),noise);
    assert.notDeepEqual(m.noiseSignal(n,16,1),noise);
    assert.deepEqual(m.noiseSignal(n,0,1),Array(n).fill(0));
  }
});

test('analysis and synthesis preserve samples and weighted energy at every supported size',async()=>{
  const m=await core;
  for(const n of m.SIZES)for(let seed=0;seed<4;seed++) {
    const values=Array.from({length:n},(_,i)=>(i*i+seed*17*i+seed)%129-64);
    for(const basis of m.BASES) {
      const a=m.analyze(values,basis),rebuilt=m.synthesize(a.values,basis);
      if(basis==='cosine')rebuilt.forEach((v,i)=>close(v,values[i],64));else assert.deepEqual(rebuilt,values);
      close(a.values.reduce((sum,c,i)=>sum+a.weights[i]*c*c,0),energy(values),energy(values));
    }
    const expected=[],weights=[];
    expected.push(values.reduce((sum,v)=>sum+v,0)/n);weights.push(n);
    for(let width=n;width>=2;width/=2)for(let start=0;start<n;start+=width) {
      let difference=0;
      for(let i=start;i<start+width;i++)difference+=(i<start+width/2?1:-1)*values[i];
      expected.push(difference/width);weights.push(width);
    }
    assert.deepEqual(m.analyze(values,'haar').values,expected);
    assert.deepEqual(m.analyze(values,'haar').weights,weights);
  }
  const n=16,constant=m.analyze(Array(n).fill(3),'cosine');
  close(constant.values[0],12);constant.values.slice(1).forEach(v=>close(v,0));
});

test('error curves agree with explicit reconstructions and the known-noise endpoint',async()=>{
  const m=await core;
  for(const n of m.SIZES)for(const policy of m.POLICIES) {
    const e=m.experiment({...m.defaults(),n,cycles:3,policy,address:0,coefficient:0,budget:Math.min(12,n)});
    const budgets=n<=32?Array.from({length:n+1},(_,k)=>k):[0,1,n/4,n/2,n-1,n];
    for(const basis of m.BASES) {
      const a=e.analyses[basis];
      assert.equal(a.curve.length,n+1);
      for(const k of budgets) {
        const selected=new Set(a.order.slice(0,k)),values=m.synthesize(a.values.map((c,i)=>selected.has(i)?c:0),basis);
        close(a.curve[k].referenceError,error(values,e.reference),energy(e.observed));
        close(a.curve[k].observedError,error(values,e.observed),energy(e.observed));
      }
      close(a.curve[n].referenceError,e.noiseEnergy,energy(e.observed));assert.equal(a.curve[n].observedError,0);
      for(let k=1;k<=n;k++)assert.ok(a.curve[k].observedError<=a.curve[k-1].observedError+1e-9);
      const minimum=Math.min(...a.curve.map(p=>p.referenceError)),tolerance=1e-10*Math.max(1,energy(e.reference));
      assert.ok(a.curve[a.bestBudget].referenceError<=minimum+tolerance);
      assert.ok(a.curve.slice(0,a.bestBudget).every(p=>p.referenceError>minimum+tolerance));
    }
  }
});

test('weighted-energy selection is optimal among all 65536 masks for the 16-sample benchmark',async()=>{
  const m=await core,values=[2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4];
  const e=m.experiment({...m.defaults(),n:16,shape:'custom',custom:values,noise:0,budget:1,address:0,coefficient:0});
  for(const basis of m.BASES) {
    const a=e.analyses[basis],vectors=a.values.map((c,i)=>m.basisVector(16,basis,i).map(v=>c*v));
    const best=Array(17).fill(Infinity),rebuilt=Array(16).fill(0);
    let previous=0,count=0;
    for(let mask=0;mask<65536;mask++) {
      const gray=mask^(mask>>>1);
      if(mask){const bit=Math.log2(gray^previous),sign=(gray&(1<<bit))?1:-1;count+=sign;for(let i=0;i<16;i++)rebuilt[i]+=sign*vectors[bit][i];}
      best[count]=Math.min(best[count],error(rebuilt,values));previous=gray;
    }
    best.forEach((v,k)=>close(a.curve[k].observedError,v,energy(values)));
  }
  assert.equal(e.analyses.haar.order[0],0);assert.equal(e.analyses.haar.observedError,272);
  const magnitude=m.experiment({...e.config,policy:'magnitude'});
  assert.equal(magnitude.analyses.haar.order[0],13);assert.equal(magnitude.analyses.haar.observedError,288);
});

test('saved links and numeric exports round-trip without trusting exported results',async()=>{
  const m=await core;
  for(const n of m.SIZES) {
    const config={...m.defaults(),n,shape:'custom',custom:Array.from({length:n},(_,i)=>i%2?64:-64),seed:4294967295,budget:n,coefficient:n-1,address:n-1};
    const encoded=m.encodeSettings(config);assert.ok(encoded.length<=4096);
    assert.deepEqual(m.decodeSettings(encoded),config);
    const e=m.experiment(config);
    assert.deepEqual(m.parseSamples(m.signalCsv(e)),e.reference);
    assert.equal(m.curvesCsv(e).trim().split('\n').length,n+2);
    const saved=JSON.parse(m.experimentJson(e));saved.reconstruction=['untrusted'];
    assert.deepEqual(m.importExperiment(JSON.stringify(saved)),config);
    assert.ok(m.experimentJson(e).length<65536);
  }
  assert.deepEqual(m.parseSamples(Array(16).fill(-2).join(', ')),Array(16).fill(-2));
  assert.deepEqual(m.parseSamples('value\n'+Array(16).fill(2).join('\n')),Array(16).fill(2));
});

test('malformed settings, unsupported lengths and missing CSV values are rejected',async()=>{
  const m=await core,base=m.defaults();
  for(const config of [null,{}, {...base,v:2},{...base,n:24},{...base,seed:-1},{...base,seed:2**32},
    {...base,noise:.5},{...base,budget:65},{...base,coefficient:64},{...base,address:-1},{...base,shape:'custom',custom:Array(64)},
    {...base,shape:'custom',custom:Array(64).fill(65)},{...base,basis:'unknown'},{...base,policy:'unknown'}])assert.throws(()=>m.settings(config),RangeError);
  for(const value of ['', '1,,2', '1,2,',Array(15).fill(0).join(','),Array(16).fill(.5).join(','), 'value\n0\n\n,', 'x'.repeat(65537)])assert.throws(()=>m.parseSamples(value),RangeError);
  for(const value of ['','broken!', 'x'.repeat(4097)])assert.throws(()=>m.decodeSettings(value),RangeError);
  assert.throws(()=>m.importExperiment('{"schema":"unknown"}'),RangeError);
  assert.throws(()=>m.analyze(Array(16),'haar'),RangeError);
  assert.throws(()=>m.synthesize(null,'cosine'),RangeError);
});
