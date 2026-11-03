const {test}=require('node:test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const core=import(pathToFileURL(path.join(__dirname,'../website/assets/recovery-lab-core.mjs')));

test('starters distinguish recovery, lost questions, redundancy, and fractional rules',async()=>{
  const {analyzeRecovery,presetExperiment}=await core;
  const expected={sum:[1,1,0,1],sufficient:[2,1,1,0],partial:[2,1,1,1],redundant:[1,2,0,2],fractions:[2,1,1,0],invertible:[2,0,2,0]};
  for(const[name,values]of Object.entries(expected)){
    const r=analyzeRecovery(presetExperiment(name));
    assert.deepEqual([r.rank,r.nullity,r.recoverable,r.repair.additional],values,name);
  }
  const r=analyzeRecovery(presetExperiment('fractions'));
  assert.deepEqual(r.questions[0].weights,['1/2','1/2']);
  const lost=analyzeRecovery(presetExperiment('sum'));
  assert.deepEqual(lost.questions[0].witness,['1','-1']);
  assert.deepEqual(lost.motion.summary,lost.motion.movedSummary);
  assert.notDeepEqual(lost.motion.answers,lost.motion.movedAnswers);
});

test('no available measurements recover only zero questions',async()=>{
  const {analyzeRecovery,presetExperiment,repairExperiment}=await core;
  const state={...presetExperiment('partial'),enabled:[false,false],F:[['0','0','0'],['1','0','0']]};
  const r=analyzeRecovery(state);
  assert.equal(r.rank,0);assert.equal(r.nullity,3);assert.equal(r.recoverable,1);
  assert.deepEqual(r.questions[0].weights,['0','0']);
  assert.deepEqual(r.motion.summary,[]);assert.deepEqual(r.rref,[]);
  assert.equal(analyzeRecovery(repairExperiment(state)).recoverable,2);
});

test('the global obstruction remains when the inspected pair coincides at t zero',async()=>{
  const {analyzeRecovery,presetExperiment}=await core;
  const r=analyzeRecovery({...presetExperiment('sum'),t:0});
  assert.deepEqual(r.motion.x,r.motion.moved);
  assert.equal(r.questions[0].recoverable,false);
  assert.equal(r.questions[0].change,'1');
});

test('repair removes redundancy and adds only independent missing questions',async()=>{
  const {analyzeRecovery,presetExperiment,repairExperiment}=await core;
  const state={...presetExperiment('redundant'),F:[['1','0','0'],['2','0','0'],['0','0','1']]};
  const r=analyzeRecovery(state);
  assert.deepEqual(r.repair.retainedRows,[0]);assert.deepEqual(r.repair.addedQuestions,[0,2]);
  assert.deepEqual(repairExperiment(state).R,[['1','1','0'],['1','0','0'],['0','0','1']]);
  assert.equal(analyzeRecovery(repairExperiment(state)).recoverable,3);
  assert.deepEqual(state.R,presetExperiment('redundant').R);
});

test('every starter link preserves matrices, selections and the inspected collision',async()=>{
  const {PRESETS,presetExperiment,encodeRecovery,decodeRecovery,analyzeRecovery}=await core;
  for(const name of Object.keys(PRESETS)){
    const state=presetExperiment(name);state.t=-4;state.question=state.F.length-1;state.enabled[0]=false;
    const encoded=encodeRecovery(state);assert.match(encoded,/^[A-Za-z0-9_-]+$/);
    assert.deepEqual(decodeRecovery(encoded),state);
    assert.deepEqual(analyzeRecovery(decodeRecovery(encoded)),analyzeRecovery(state));
  }
});

test('untrusted settings are bounded and malformed or sparse entries are rejected',async()=>{
  const {presetExperiment,validateExperiment,decodeRecovery}=await core;
  const state=presetExperiment('sum');
  for(const change of [
    {v:2},{n:5},{R:[]},{F:[]},{R:Array(5).fill(['1','1'])},
    {F:Array(4).fill(['1','1'])},{R:[['1']]},{R:[['1',undefined]]},{R:[Array(2)]},
    {R:[['1','1/0']]},{R:[['1','1/100']]},{R:[['1','100']]},{R:[['1','0.5']]},
    {R:[['1','<img>']]},{R:[['1','1e2']]},{enabled:Array(1)},{x:Array(2)},
    {enabled:[1]},{x:[1,5]},{x:[0.5,0]},{t:5},{t:NaN},{question:1},
  ]) assert.throws(()=>validateExperiment({...state,...change}),RangeError,JSON.stringify(change));
  for(const encoded of ['',null,'A','a!','x'.repeat(4097),btoa('null'),btoa('{}')]) assert.throws(()=>decodeRecovery(encoded),RangeError);
});

test('canonical settings discard unknown properties and retain independent arrays',async()=>{
  const {presetExperiment,validateExperiment,decodeRecovery}=await core;
  const input={...presetExperiment('sum'),R:[['-0',' 2/4 ']],unused:true};
  const state=validateExperiment(input);
  assert.deepEqual(state.R,[['0','1/2']]);assert.equal(Object.hasOwn(state,'unused'),false);
  state.R[0][0]='3';assert.equal(input.R[0][0],'-0');
  const malicious=btoa('{"v":1,"n":2,"R":[["1","1"]],"F":[["1","0"]],"enabled":[true],"x":[1,0],"t":1,"question":0,"__proto__":{"polluted":true}}').replace(/=+$/,'');
  assert.equal(Object.hasOwn(decodeRecovery(malicious),'__proto__'),false);assert.equal({}.polluted,undefined);
});
