const test=require('node:test');
const assert=require('node:assert/strict');
const workspace=import('../website/assets/signal-lab-workspace.mjs');
const core=import('../website/assets/signal-lab-core.mjs');

test('fast forward and backward strokes fill every crossed address without mutating inputs',async()=>{
  const w=await workspace,values=Array(16).fill(0);
  const a=w.paintSegment(values,{index:2,value:-8},{index:10,value:8});
  assert.deepEqual(a.slice(2,11),[-8,-6,-4,-2,0,2,4,6,8]);
  assert.deepEqual(w.paintSegment(values,{index:10,value:8},{index:2,value:-8}),a);
  assert.deepEqual(values,Array(16).fill(0));
  assert.equal(w.paintSegment(values,{index:4,value:0},{index:4,value:64})[4],64);
  for(const point of [{index:-1,value:0},{index:16,value:0},{index:1,value:65},{index:.5,value:1},{index:1,value:NaN}])
    assert.throws(()=>w.paintSegment(values,{index:0,value:0},point),RangeError);
  assert.throws(()=>w.paintSegment(Array(16),{index:0,value:0},{index:1,value:0}),RangeError);
});

test('sample history groups strokes, bounds undo and discards obsolete redo branches',async()=>{
  const w=await workspace,h=new w.SampleHistory(),a=Array(16).fill(0),b=a.slice();b[0]=1;
  assert.equal(h.record(a,a),false);assert.equal(h.record(a,b),true);
  a[0]=9;
  const previous=h.undo(b);assert.equal(previous[0],0);assert.deepEqual(h.redo(previous),b);
  h.undo(b);const c=b.slice();c[1]=2;h.record(previous,c);assert.equal(h.redo(c),null);
  h.clear();for(let i=0;i<40;i++){const x=Array(16).fill(i),y=Array(16).fill(i+1);h.record(x,y);}
  assert.equal(h.past.length,32);assert.equal(h.undo(Array(16).fill(40))[0],39);
  h.clear();assert.equal(h.undo(c),null);assert.equal(h.future.length,0);
});

test('notebooks retain validated settings and names while ignoring stored result claims',async()=>{
  const w=await workspace,m=await core;
  const entries=[{label:'  First run  ',settings:m.defaults(),referenceError:-999}];
  const saved=w.readNotebook(w.writeNotebook(entries));assert.equal(saved[0].label,'First run');
  assert.deepEqual(Object.keys(saved[0]),['label','settings']);assert.deepEqual(saved[0].settings,m.defaults());
  const input={schema:w.NOTEBOOK_SCHEMA,entries:[{label:'Custom',settings:{...m.defaults(),shape:'custom',custom:Array(64).fill(12)},results:{error:0}}]};
  const decoded=w.readNotebook(JSON.stringify(input));input.entries[0].settings.custom[0]=64;
  assert.equal(decoded[0].settings.custom[0],12);
  const custom=w.customSettings({...m.defaults(),budget:50,address:60,coefficient:50},Array(16).fill(-64));
  assert.equal(custom.n,16);assert.equal(custom.address,15);assert.equal(custom.budget,16);assert.equal(custom.coefficient,15);
});

test('invalid or excessive notebook imports fail atomically',async()=>{
  const w=await workspace,m=await core,entry={label:'Run',settings:m.defaults()},entries=Array(12).fill(entry);
  for(const value of ['', '{}','x'.repeat(65537),JSON.stringify({schema:w.NOTEBOOK_SCHEMA,entries:[null]}),
    JSON.stringify({schema:w.NOTEBOOK_SCHEMA,entries:[{...entry,label:''}]}),JSON.stringify({schema:w.NOTEBOOK_SCHEMA,entries:[{...entry,label:'bad\nname'}]}),
    JSON.stringify({schema:w.NOTEBOOK_SCHEMA,entries:[{...entry,label:'a'.repeat(49)}]}),
    JSON.stringify({schema:w.NOTEBOOK_SCHEMA,entries:[{...entry,settings:{...m.defaults(),seed:-1}}]})])assert.throws(()=>w.readNotebook(value),RangeError);
  assert.throws(()=>w.appendRuns(entries,[entry]),RangeError);assert.equal(entries.length,12);
  assert.equal(w.readNotebook(w.writeNotebook(entries)).length,12);
  const largest=Array.from({length:12},()=>({label:'W'.repeat(48),settings:{...m.defaults(),n:256,shape:'custom',custom:Array(256).fill(-64)}}));
  const exported=w.writeNotebook(largest);assert.ok(Buffer.byteLength(exported)<65536);assert.equal(w.readNotebook(exported).length,12);
});

test('comparisons require identical data and CSV metrics come from recomputed experiments',async()=>{
  const w=await workspace,m=await core,a=m.experiment(m.defaults()),b=m.experiment({...m.defaults(),basis:'cosine',budget:8});
  assert.equal(w.sameObservation(a,b),true);
  assert.equal(w.sameObservation(a,m.experiment({...m.defaults(),seed:18})),false);
  assert.equal(w.sameObservation(a,m.experiment({...m.defaults(),shape:'wave'})),false);
  const zero=m.experiment({...m.defaults(),noise:0}),other=m.experiment({...m.defaults(),noise:0,seed:999});
  assert.equal(w.sameObservation(zero,other),true);
  const csv=w.notebookCsv([{label:'=formula',settings:a.config},{label:'A "quoted" name',settings:b.config}],[a,b]);
  assert.equal(csv.trim().split('\n').length,3);assert.ok(csv.includes('"\'=formula"'));assert.ok(csv.includes('"A ""quoted"" name"'));
  assert.equal(Number(csv.trim().split('\n')[1].split(',').at(-2)),a.analyses.haar.referenceError);
});

test('every starter produces two independent valid settings for identical observations',async()=>{
  const w=await workspace,m=await core;
  for(const id of ['edges','tone','noise','ranking']) {
    const entries=w.starterRuns(id);assert.equal(entries.length,2);
    entries.forEach(entry=>assert.deepEqual(m.settings(entry.settings),entry.settings));
    assert.equal(w.sameObservation(...entries.map(entry=>m.experiment(entry.settings))),true);
    entries[0].settings.seed=999;assert.equal(w.starterRuns(id)[0].settings.seed,17);
  }
  const ranked=w.starterRuns('ranking').map(entry=>m.experiment(entry.settings));
  assert.equal(ranked[0].analyses.haar.referenceError,272);assert.equal(ranked[1].analyses.haar.referenceError,288);
  assert.throws(()=>w.starterRuns('unknown'),RangeError);
});

test('signed comparison data and CSV agree with an exact zero-versus-full sample reconstruction',async()=>{
  const w=await workspace,m=await core,reference=Array.from({length:16},(_,i)=>i+1);
  const config={...m.defaults(),n:16,shape:'custom',custom:reference,basis:'samples',noise:0,budget:0,address:0};
  const a=m.experiment(config),b=m.experiment({...config,budget:16}),data=w.compareRuns(a,b);
  assert.equal(data.maximum,16);assert.equal(data.maximumAddress,15);
  for(let i=0;i<16;i++)assert.deepEqual(data.rows[i],{address:i,reference:i+1,observed:i+1,a:0,b:i+1,errorA:-(i+1),errorB:0,difference:i+1});
  const lines=w.comparisonCsv(a,b).trim().split('\n');assert.equal(lines.length,17);
  assert.equal(lines[1],'0,1,1,0,1,-1,0,1');assert.equal(lines.at(-1),'15,16,16,0,16,-16,0,16');
  assert.equal(a.analyses.samples.referenceError,1496);assert.equal(b.analyses.samples.referenceError,0);
  const same=w.compareRuns(a,a);assert.equal(same.maximum,0);assert.equal(same.maximumAddress,0);
});

test('comparison exports reject different data and cover the largest supported sample count',async()=>{
  const w=await workspace,m=await core,a=m.experiment(m.defaults()),b=m.experiment({...m.defaults(),seed:18});
  assert.throws(()=>w.compareRuns(a,b),RangeError);assert.throws(()=>w.comparisonCsv(a,b),RangeError);
  const large=m.experiment({...m.defaults(),n:256});assert.equal(w.compareRuns(large,large).rows.length,256);
  assert.equal(w.comparisonCsv(large,large).trim().split('\n').length,257);
});

test('comparison links round-trip both bounded runs, Unicode names, views and boundary addresses',async()=>{
  const w=await workspace,m=await core;
  for(const n of m.SIZES)for(const view of ['overlay','error','difference']) {
    const base={...m.defaults(),n,shape:'custom',custom:Array.from({length:n},(_,i)=>i%2?-64:64),noise:16,seed:4294967295,budget:n,address:n-1,coefficient:n-1};
    const raw={v:1,entries:[{label:'波形 A 🟢',settings:base},{label:'Cosinus é · B',settings:{...base,basis:'cosine',budget:0}}],view,address:n-1};
    const encoded=w.encodeComparison(raw);assert.ok(encoded.length<=8192);assert.match(encoded,/^[A-Za-z0-9_-]+$/);
    assert.deepEqual(w.decodeComparison(encoded),raw);
    const copy=w.decodeComparison(encoded);copy.entries[0].settings.custom[0]=0;assert.equal(w.decodeComparison(encoded).entries[0].settings.custom[0],64);
  }
  const boundary={v:1,entries:w.starterRuns('edges'),view:'overlay',address:0};assert.deepEqual(w.decodeComparison(w.encodeComparison(boundary)),boundary);
});

test('comparison links reject malformed or incompatible data without accepting stored result claims',async()=>{
  const w=await workspace,m=await core,base={v:1,entries:w.starterRuns('ranking'),view:'error',address:11};
  for(const raw of [null,[],{...base,v:2},{...base,entries:base.entries.slice(0,1)},{...base,entries:[...base.entries,base.entries[0]]},
    {...base,view:'unknown'},{...base,address:-1},{...base,address:16},{...base,address:.5},
    {...base,entries:[base.entries[0],{...base.entries[1],settings:{...base.entries[1].settings,noise:1}}]}])assert.throws(()=>w.encodeComparison(raw),RangeError);
  for(const value of ['', 'invalid!', 'a'.repeat(8193),btoa('not json'),btoa('\xff'),btoa(JSON.stringify({...base,v:2}))])assert.throws(()=>w.decodeComparison(value),RangeError);
  const claimed={...base,results:{error:-999},entries:base.entries.map(entry=>({...entry,results:{referenceError:-999},settings:{...entry.settings,unknown:true}}))};
  const clean=w.decodeComparison(w.encodeComparison(claimed));assert.deepEqual(Object.keys(clean),['v','entries','view','address']);
  assert.deepEqual(Object.keys(clean.entries[0]),['label','settings']);assert.equal(clean.entries[0].settings.unknown,undefined);
  assert.equal(m.experiment(clean.entries[0].settings).analyses.haar.referenceError,272);
  assert.equal(m.experiment(clean.entries[1].settings).analyses.haar.referenceError,288);
});

test('quality targets find exact first budgets for a sample-coordinate benchmark',async()=>{
  const w=await workspace,m=await core,config={...m.defaults(),n:16,shape:'custom',custom:Array.from({length:16},(_,i)=>i+1),basis:'samples',noise:0,address:0},r=m.experiment(config);
  const energy=w.targetBudgets(r,'energy',50),sample=energy.rows.find(row=>row.basis==='samples');
  assert.equal(energy.observedEnergy,1496);assert.equal(energy.threshold,748);assert.equal(sample.budget,4);
  assert.equal(r.analyses.samples.curve[3].observedError,819);assert.equal(r.analyses.samples.curve[4].observedError,650);
  assert.equal(w.targetBudgets(r,'reference',5).rows.find(row=>row.basis==='samples').budget,6);
  assert.equal(w.targetBudgets(r,'energy',0).rows.find(row=>row.basis==='samples').budget,0);
  assert.equal(w.targetBudgets(r,'energy',100).rows.find(row=>row.basis==='samples').budget,16);
});

test('reference targets handle an intermediate success, unreachable limits, and zero energy',async()=>{
  const w=await workspace,m=await core,r=m.experiment(m.defaults()),outcome=w.targetBudgets(r,'reference',2),haar=outcome.rows.find(row=>row.basis==='haar');
  assert.ok(haar.budget>0&&haar.budget<64);assert.ok(haar.referenceRms<=2);assert.ok(Math.sqrt(r.noiseEnergy/64)>2);
  assert.equal(w.targetBudgets(r,'reference',0).rows.filter(row=>row.budget!==null).length,0);
  const zero=m.experiment({...m.defaults(),shape:'custom',custom:Array(64).fill(0),noise:0});
  for(const metric of ['energy','reference'])for(const value of [0,metric==='energy'?100:64]){
    for(const row of w.targetBudgets(zero,metric,value).rows){assert.equal(row.budget,0);assert.equal(row.retainedPercent,100);assert.equal(row.referenceRms,0);}
  }
});

test('target results are minimal across supported sizes and selection policies; saved choices are independent',async()=>{
  const w=await workspace,m=await core;
  for(const n of m.SIZES)for(const policy of m.POLICIES){const r=m.experiment({...m.defaults(),n,policy,address:0});for(const [metric,value]of [['energy',95],['reference',2]]){
    const outcome=w.targetBudgets(r,metric,value),field=metric==='energy'?'observedError':'referenceError';
    for(const row of outcome.rows){const curve=r.analyses[row.basis].curve;if(row.budget===null)assert.ok(curve.every(point=>point[field]>outcome.threshold+outcome.tolerance));else{assert.ok(curve[row.budget][field]<=outcome.threshold+outcome.tolerance);assert.ok(curve.slice(0,row.budget).every(point=>point[field]>outcome.threshold+outcome.tolerance));}}
  }}
  const r=m.experiment({...m.defaults(),shape:'custom',custom:Array(64).fill(4)}),entries=w.targetRuns(r,'energy',95);assert.equal(entries.length,3);assert.equal(new Set(entries.map(entry=>entry.settings.basis)).size,3);
  assert.equal(w.sameObservation(...entries.slice(0,2).map(entry=>m.experiment(entry.settings))),true);entries[0].settings.custom[0]=9;assert.equal(entries[1].settings.custom[0],4);assert.equal(r.config.custom[0],4);
  assert.deepEqual(w.targetRuns(m.experiment(m.defaults()),'reference',0),[]);
  for(const [metric,value]of [['unknown',1],['energy',-1],['energy',100.1],['reference',64.1],['reference',NaN],['energy',Infinity]])assert.throws(()=>w.targetBudgets(r,metric,value),RangeError);
});

test('regional metrics and CSV use inclusive original addresses and exact sample-coordinate errors',async()=>{
  const w=await workspace,m=await core,config={...m.defaults(),n:16,shape:'custom',custom:Array.from({length:16},(_,i)=>i+1),basis:'samples',noise:0,budget:0,address:0};
  const a=m.experiment(config),b=m.experiment({...config,budget:16}),data=w.compareRegion(a,b,[4,7]);
  assert.deepEqual([data.start,data.end,data.count],[4,7,4]);assert.deepEqual(data.rows.map(row=>row.address),[4,5,6,7]);
  assert.deepEqual(data.a,{rms:Math.sqrt(43.5),bias:-6.5,maximum:8,maximumAddress:7});
  assert.deepEqual(data.b,{rms:0,bias:0,maximum:0,maximumAddress:4});assert.equal(data.maximum,8);assert.equal(data.maximumAddress,7);
  assert.equal(w.comparisonCsv(a,b,[4,7]),'address,reference,observed,a_reconstruction,b_reconstruction,a_error_to_reference,b_error_to_reference,b_minus_a\n4,5,5,0,5,-5,0,5\n5,6,6,0,6,-6,0,6\n6,7,7,0,7,-7,0,7\n7,8,8,0,8,-8,0,8\n');
  const single=w.compareRegion(b,a,[15,15]);assert.equal(single.count,1);assert.equal(single.b.rms,16);assert.equal(single.b.bias,-16);assert.equal(single.rows[0].difference,-16);assert.equal(single.maximumAddress,15);
  const same=w.compareRegion(a,a,[8,12]);assert.equal(same.maximum,0);assert.equal(same.maximumAddress,8);
  assert.deepEqual(w.compareRegion(a,b).rows,w.compareRuns(a,b).rows);
});

test('regional partitions recover whole-signal squared errors at every supported size and basis',async()=>{
  const w=await workspace,m=await core;
  for(const n of m.SIZES)for(const basis of m.BASES){
    const a=m.experiment({...m.defaults(),n,basis,address:0}),b=m.experiment({...m.defaults(),n,basis,budget:n,address:0});
    const left=w.compareRegion(a,b,[0,n/2-1]),right=w.compareRegion(a,b,[n/2,n-1]);
    for(const [key,result]of [['a',a],['b',b]]){
      const sum=left[key].rms**2*left.count+right[key].rms**2*right.count;
      assert.ok(Math.abs(sum-result.analyses[basis].referenceError)<1e-8);
    }
    assert.equal(w.comparisonCsv(a,b,[n-1,n-1]).trim().split('\n').length,2);
    for(const region of [[],[0],[0,1,2],[-1,0],[0,n],[4,3],[0,.5],[NaN,2],'0,1',{}]){
      assert.throws(()=>w.compareRegion(a,b,region),RangeError);assert.throws(()=>w.comparisonCsv(a,b,region),RangeError);
    }
  }
  assert.throws(()=>w.compareRegion(m.experiment(m.defaults()),m.experiment({...m.defaults(),seed:18}),[0,1]),RangeError);
});

test('shared regions preserve a bounded range and reject invalid or out-of-region selected samples',async()=>{
  const w=await workspace,base={v:1,entries:w.starterRuns('ranking'),view:'difference',address:11};
  for(const region of [[0,15],[8,11],[11,11]]){
    const state={...base,region},clean=w.decodeComparison(w.encodeComparison(state));assert.deepEqual(clean,state);
    clean.region[0]=3;assert.deepEqual(w.decodeComparison(w.encodeComparison(state)).region,region);
  }
  for(const region of [null,[],[0],[0,16],[-1,15],[12,15],[0,10],[12,11],[1.5,15]])assert.throws(()=>w.encodeComparison({...base,region}),RangeError);
  assert.deepEqual(w.decodeComparison(w.encodeComparison(base)),base);
});
