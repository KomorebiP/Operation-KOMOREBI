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
