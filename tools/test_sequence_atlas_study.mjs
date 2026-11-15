import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {analyzeStudy,readStudyURL,studyURL,validateStudy,studyCSV,studyIndexed} from '../website/assets/sequence-atlas-study.mjs';

const root=fileURLToPath(new URL('..',import.meta.url));
test('all 38 entries agree with independent Fraction and binomial-difference oracles in 1482 study windows',()=>{
  const fixtures=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','-c',`
import sys,json
sys.path.insert(0,'tools')
from sequence_atlas import catalogue
from sequence_atlas_study import study_model,MODES
result=[]
for entry in catalogue():
    cases=[]
    for mode,modulus in [(mode,7) for mode in MODES]+[('mod',2),('mod',128)]:
        for start,count in [(0,12),(9,16),(52,12)]:
            options=dict(transform=mode,start=start,count=count,modulus=modulus)
            cases.append(dict(options=options,expected=study_model(entry,mode,start,count,modulus)))
    result.append(dict(id=entry['id'],terms=entry['terms'],cases=cases))
print(json.dumps(result,separators=(',',':')))
`],{cwd:root,encoding:'utf8',maxBuffer:32*1024*1024}));
  let windows=0;
  for(const entry of fixtures)for(const {options,expected}of entry.cases){const result=analyzeStudy(entry.terms,options);for(const key of ['rows','facts','ladder'])assert.deepEqual(result[key],expected[key],`${entry.id} ${JSON.stringify(options)} ${key}`);windows++;}
  assert.equal(fixtures.length,38);assert.equal(windows,1482);
});
test('backward differences retain original n and report only adequately sampled finite observations',()=>{
  const squares=Array.from({length:64},(_,n)=>BigInt(n)**2n);
  const first=analyzeStudy(squares,{transform:'second-difference'});
  assert.deepEqual(first.rows.slice(0,4),[{n:0,value:null},{n:1,value:null},{n:2,value:'2'},{n:3,value:'2'}]);
  assert.deepEqual(first.observation,{order:2,value:'2',count:10,start:2,end:11});
  const later=analyzeStudy(squares,{start:9,count:16,transform:'sum'});assert.equal(later.rows[0].value,'285');assert.equal(later.ladder[1][0],'17');
  assert.equal(analyzeStudy(squares,{count:4}).observation,null);
  assert.deepEqual(analyzeStudy(Array(64).fill(0n)).facts,{defined:12,undefined:0,integers:12,zero:12,positive:0,negative:0,even:12,odd:0,gcd:'0'});
});
test('fractions, zero denominators, signs, parity and gcd stay exact',()=>{
  const result=analyzeStudy([0n,1n,1n,2n,3n,5n],{transform:'ratio',count:6});
  assert.deepEqual(result.rows.map(row=>row.value),[null,null,'1','2','3/2','5/3']);
  assert.equal(result.facts.gcd,null);assert.equal(result.facts.integers,2);assert.equal(result.facts.undefined,2);
  const residues=analyzeStudy([-1n,-8n,0n,2n],{transform:'mod',count:4,modulus:7});assert.deepEqual(residues.rows.map(row=>row.value),['6','6','0','2']);assert.equal(residues.facts.gcd,'2');
});
test('linked integers never cross undefined or fractional values, or exceed target input caps',()=>{
  const result=analyzeStudy([1n,2n,0n,4n,8n,16n],{transform:'ratio',count:6});assert.deepEqual(result.search,['2','0']);assert.deepEqual(result.discovery,[]);assert.equal(result.searchStart,1);
  assert.deepEqual(analyzeStudy([2n,1n,2n,4n],{transform:'ratio',count:4}).search,[]);
  const enormous=10n**301n;const large=analyzeStudy(Array(12).fill(enormous));assert.equal(large.search.length,8);assert.deepEqual(large.discovery,[]);
  assert.deepEqual(analyzeStudy(Array(12).fill(10n**2001n)).search,[]);
});
test('study links round-trip, recover invalid input and preserve other entry query options',()=>{
  const state={transform:'sum',start:52,count:12,modulus:11};
  const link=studyURL('https://example.test/sequences/KSEQ-000001.html?other=kept#data',state);
  assert.equal(link.hash,'#analysis');assert.equal(link.searchParams.get('other'),'kept');assert.deepEqual(readStudyURL(link).state,state);
  for(const options of [{start:-1},{start:''},{start:NaN},{count:1},{count:33},{modulus:129},{transform:'__proto__'},{start:60,count:12}])assert.throws(()=>validateStudy(options));
  const invalid=readStudyURL('https://example.test/entry?study=bad&from=999');assert.ok(invalid.error);assert.equal(invalid.state.transform,'raw');
});
test('CSV and indexed copies retain missing values, signs, fractions and every large-integer digit',()=>{
  const huge=9007199254740993n,model=analyzeStudy([huge,2n*huge,0n,-huge],{transform:'ratio',count:4});
  assert.equal(studyCSV(model),'n,value,defined\n0,,false\n1,2,true\n2,0,true\n3,,false\n');
  assert.equal(studyIndexed(model),'0 undefined\n1 2\n2 0\n3 undefined');
  assert.ok(studyCSV(analyzeStudy([huge,huge+1n],{count:2})).includes('9007199254740993'));
});
test('study plot scale retains huge samples and avoids overflow of a signed linear span',()=>{
  assert.equal(analyzeStudy(Array(64).fill(10n**600n),{start:52,count:12}).plotScale,'signed-log');
  assert.equal(analyzeStudy([10n**308n,-(10n**308n)],{count:2}).plotScale,'signed-log');
  assert.equal(analyzeStudy(Array(64).fill(10n**600n),{transform:'mod',start:52,count:12}).plotScale,'linear');
  assert.equal(analyzeStudy([0n,1n,3n,6n],{count:4}).plotScale,'linear');
});
