import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {generate,binomialTransform,transform,exact} from '../website/assets/sequence-atlas-core.mjs';
import {discover,analyzeInput} from '../website/assets/sequence-atlas-discovery.mjs';
const root=fileURLToPath(new URL('..',import.meta.url));
const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','tools/sequence_atlas.py'],{cwd:root,encoding:'utf8',maxBuffer:12*1024*1024}));

test('binomial transforms invert exactly for signed integers far above 2^53',()=>{
  const values=Array.from({length:64},(_,n)=>(n%2?-1n:1n)*(BigInt(n)**5n+10n**80n));
  assert.deepEqual(binomialTransform(binomialTransform(values),true),values);
  assert.deepEqual(binomialTransform([1n,1n,1n,1n,1n]),[1n,2n,4n,8n,16n]);
  assert.deepEqual(transform([1n,-2n,3n],'alternating').map(exact),['1','2','3']);
  assert.deepEqual(transform([1n,-2n,3n],'absolute').map(exact),['1','2','3']);
});
test('unknown square terms discover the odd differences with both index origins reported',()=>{
  const report=discover(entries,'0,1,4,9,16,25,36,49',{both:true,limit:500});
  assert.ok(report.results.some(r=>r.id==='KSEQ-000030'&&r.inputOperation==='raw'&&r.targetOperation==='raw'&&r.length===8));
  assert.ok(report.results.some(r=>r.id==='KSEQ-000028'&&r.inputOperation==='difference'&&r.targetOperation==='raw'&&r.inputStart===1&&r.targetStart===0&&r.length===7));
  const triangular=discover(entries,'0,1,3,6,10,15,21,28',{both:true,limit:500});
  assert.ok(triangular.results.some(r=>r.id==='KSEQ-000027'&&r.inputOperation==='raw'&&r.targetOperation==='sum'));
});
test('matching uses the complete transformed input and can omit initial input terms',()=>{
  const unknown='999,0,1,1,2,3,5,8';
  const report=discover(entries,unknown,{limit:500});
  assert.ok(report.results.some(r=>r.id==='KSEQ-000025'&&r.inputOperation==='drop-1'&&r.inputStart===1&&r.length===7));
  const mismatch=discover(entries,'0,1,1,2,3,5,999');
  assert.ok(!mismatch.results.some(r=>r.id==='KSEQ-000025'&&r.inputOperation==='raw'));
});
test('signed Euler and secant connections are not confused with unsigned identity',()=>{
  const euler=entries.find(e=>e.kind==='euler');
  const report=discover(entries,euler.terms.slice(0,10).join(','),{limit:500});
  assert.ok(report.results.some(r=>r.id==='KSEQ-000001'&&r.inputOperation==='alternating'));
  assert.ok(!report.results.some(r=>r.id==='KSEQ-000001'&&r.inputOperation==='raw'));
});
test('new partition and Catalan generators agree with independent identities beyond the stored prefix',()=>{
  const catalan=generate(entries.find(e=>e.kind==='catalan'),100);
  for(let n=1;n<100;n++)assert.equal(catalan[n],catalan.slice(0,n).reduce((sum,v,k)=>sum+v*catalan[n-1-k],0n));
  const parts=generate(entries.find(e=>e.kind==='partition'),100),dp=[1n,...Array(99).fill(0n)];
  for(let k=1;k<100;k++)for(let n=k;n<100;n++)dp[n]+=dp[n-k];
  assert.deepEqual(parts,dp);
});
test('discovery rejects incomplete, fractional and excessive input and accepts Unicode minus',()=>{
  for(const text of ['1,2,3','1,2,3,4,5,1/2',Array(65).fill('1').join(','),'9'.repeat(301)+',1,2,3,4,5'])assert.throws(()=>analyzeInput(text));
  assert.deepEqual(analyzeInput('−1,0,1,2,3,4'),[-1n,0n,1n,2n,3n,4n]);
});
test('repeated target positions are grouped and redundant shortened-input matches are omitted',()=>{
  const flat=discover([{id:'flat',title:'Flat fixture',terms:Array(64).fill('2')}],'2,2,2,2,2,2');
  assert.equal(flat.results.length,1);assert.equal(flat.results[0].targetStarts.length,59);assert.equal(flat.results[0].constant,true);
  const square=discover(entries,'0,1,4,9,16,25,36,49',{limit:500});
  assert.ok(!square.results.some(r=>r.id==='KSEQ-000030'&&r.inputOperation.startsWith('drop-')&&r.targetOperation==='raw'));
});
test('the coverage counter excludes short and identity-equivalent input forms',()=>{
  assert.equal(discover(entries,'0,1,4,9,16,25,36,49').testedOperations,9);
  assert.equal(discover(entries,'1,2,4,8,16,32').testedOperations,5);
  assert.equal(discover(entries,'0,0,0,0,0,0').testedOperations,1);
});
