import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {WORKBENCH_DEFAULTS,validateWorkbench,localSource,familySource,referenceSource,workbenchRows,agreements,readWorkbenchLink,workbenchLink,comparisonCSV} from '../website/assets/sequence-workbench-core.mjs';
import {COMPARISON_CHART_DEFAULTS,validateComparisonChart,comparisonChartTitle,comparisonXAxisTitle,comparisonYAxisTitle,comparisonYAxisTick,comparisonScaleExplanation} from '../website/assets/sequence-comparison-chart.mjs';
import {readSaved,writeSaved,STORAGE_KEY} from '../website/assets/sequence-atlas-saved.mjs';
import {referenceQuery,referenceValues,referencePositions,referenceNameMatches} from '../website/assets/sequence-oeis-core.mjs';
import {identifyInput,discoveryProbes,matchProbe} from '../website/assets/sequence-discovery-core.mjs';
const entry=(id,offset,terms)=>({id,title:id,offset,terms:terms.map(String),url:'records/'+id+'.html',collection:'atlas'});
const a=entry('KSEQ-000001',2,[0,-1,'9007199254740993',7]),b=entry('KOM085',3,[0,-1,'9007199254740992',7]);
test('windows preserve exact arithmetic and stored prefix transformations',()=>{
  let r=workbenchRows([localSource(a)],{skip:1,count:2,transform:'sum'});assert.deepEqual(r.series[0].rows.map(r=>r.value),['-1','9007199254740992']);assert.deepEqual(r.series[0].rows.map(r=>r.index),[3,4]);
  r=workbenchRows([localSource(a)],{skip:1,count:1,transform:'difference'});assert.equal(r.series[0].rows[0].value,'-1');
  assert.equal(workbenchRows([localSource(a)],{transform:'difference'}).series[0].rows[0].value,null);
  assert.equal(workbenchRows([localSource(a)],{view:'mod',modulus:7}).series[0].rows[1].value,'6');
  assert.equal(workbenchRows([localSource(a)],{skip:50}).series[0].rows.length,0);
});
test('finite agreement joins use exact integers and the selected alignment',()=>{
  let r=workbenchRows([localSource(a),localSource(b)]);let c=agreements(r)[0];assert.equal(c.compared,4);assert.equal(c.equal,3);assert.equal(c.firstMismatch.x,2);
  r=workbenchRows([localSource(a),localSource(b)],{alignment:'indices'});c=agreements(r)[0];assert.equal(c.compared,3);assert.equal(c.equal,0);
  const ref=referenceSource({id:'A000001',sample_position:8,values:['0','-1']},'snapshot');assert.throws(()=>workbenchRows([ref],{alignment:'indices'}),/omit mathematical offsets/);
  assert.equal(workbenchRows([ref],{skip:1}).series[0].rows[0].index,9);
});
test('shared references require explicit restoration against the same snapshot',()=>{
  const ref=referenceSource({id:'A000001',sample_position:8,values:['0','-1'],name:'Test'},'snapshot');
  const href=workbenchLink('https://example.test/sequence-library.html?q=old',[localSource(a),ref],{...WORKBENCH_DEFAULTS,view:'mod',modulus:11});
  const restored=readWorkbenchLink(href,[a,b],'snapshot');assert.equal(restored.state.modulus,11);assert.equal(restored.sources[1].pending,true);assert.equal(restored.sources[1].descriptor.position,8);assert.equal(new URL(href).searchParams.has('q'),false);
  assert.throws(()=>readWorkbenchLink(href,[a,b],'other'),/reference data/);assert.throws(()=>readWorkbenchLink(href,[b],'snapshot'),/unavailable/);
  assert.throws(()=>readWorkbenchLink(workbenchLink(href,[localSource(a),localSource(a)],{}),[a],'snapshot'),/duplicate/);
  for(const value of [{skip:''},{count:0},{count:1.1},{modulus:1},{scale:'invented'}])assert.throws(()=>validateWorkbench(value));
  for(const values of [['-0'],['01'],[],['1.2']])assert.throws(()=>referenceSource({id:'A000001',sample_position:0,values},'snapshot'));
});
test('second-generation comparison links pin exact local source prefixes',()=>{
  const pinnedA={...a,record_sha256:'a'.repeat(64)},pinnedB={...b,record_sha256:'b'.repeat(64)};
  const link=workbenchLink('https://example.test/sequence-library.html?old=true',
    [localSource(pinnedA),localSource(pinnedB)],{...WORKBENCH_DEFAULTS,transform:'sum',skip:1,count:2,alignment:'indices'});
  const url=new URL(link),payload=JSON.parse(url.searchParams.get('wb'));
  assert.equal(url.hash,'#comparison');
  assert.equal(payload.schema,2);
  assert.deepEqual(payload.sources.map(item=>[item.id,item.offset,item.count,item.sha256]),[
    ['KSEQ-000001',2,4,'a'.repeat(64)],['KOM085',3,4,'b'.repeat(64)]
  ]);
  const restored=readWorkbenchLink(link,[pinnedA,pinnedB],'snapshot');
  assert.equal(restored.schema,2);
  assert.equal(restored.state.transform,'sum');
  assert.equal(restored.state.skip,1);
  assert.equal(restored.sources.length,2);
  assert.equal(restored.sources[0].terms[2],'9007199254740993');
  assert.deepEqual(workbenchRows(restored.sources,restored.state).series[0].rows.map(row=>row.value),
    ['-1','9007199254740992']);
  const altered={...pinnedA,record_sha256:'c'.repeat(64),terms:['0','-1','9007199254740994','7']};
  assert.throws(()=>readWorkbenchLink(link,[altered,pinnedB],'snapshot'),/no longer matches its exact stored data/);
  assert.throws(()=>readWorkbenchLink(link,[{...pinnedA,offset:3},pinnedB],'snapshot'),/no longer matches/);
  assert.throws(()=>readWorkbenchLink(link,[{...pinnedA,terms:pinnedA.terms.slice(0,3)},pinnedB],'snapshot'),/no longer matches/);
  const forged=new URL(link),bad=JSON.parse(forged.searchParams.get('wb'));
  bad.sources[0].sha256='0'.repeat(64);forged.searchParams.set('wb',JSON.stringify(bad));
  assert.throws(()=>readWorkbenchLink(forged.href,[pinnedA,pinnedB],'snapshot'),/no longer matches/);
  bad.sources[0].sha256='invalid';forged.searchParams.set('wb',JSON.stringify(bad));
  assert.throws(()=>readWorkbenchLink(forged.href,[pinnedA,pinnedB],'snapshot'),/missing its exact source receipt/);
  const duplicate=new URL(link);duplicate.searchParams.append('wb',url.searchParams.get('wb'));
  assert.throws(()=>readWorkbenchLink(duplicate.href,[pinnedA,pinnedB],'snapshot'),/one set of comparison settings/);
});
test('legacy comparison URLs remain usable without data pinning',()=>{
  const v1=workbenchLink('https://example.test/sequence-compare.html',[localSource(a),localSource(b)],WORKBENCH_DEFAULTS);
  assert.equal(JSON.parse(new URL(v1).searchParams.get('wb')).schema,1);
  const restored=readWorkbenchLink(v1,[{...a,record_sha256:'a'.repeat(64)},{...b,record_sha256:'b'.repeat(64)}],'snapshot');
  assert.equal(restored.schema,1);
  assert.equal(restored.sources.length,2);
  assert.equal(restored.sources[0].receipt,'a'.repeat(64));
  // Old links carry no SHA-256 receipt, so they do not claim to pin the source.
  assert.deepEqual(restored.sources[0].terms,a.terms);
});

test('signed logarithmic tick labels show approximate original values rather than log coordinates',()=>{
  const state={...WORKBENCH_DEFAULTS};
  const settings={view:'values',scale:'signed-log',ticks:'magnitude'};
  assert.equal(comparisonYAxisTick(0,settings),'0');
  assert.equal(comparisonYAxisTick(1.62,settings),'≈41');
  assert.equal(comparisonYAxisTick(3.24,settings),'≈1.7K');
  assert.equal(comparisonYAxisTick(6.48,settings),'≈3M');
  assert.equal(comparisonYAxisTick(-6.48,settings),'≈−3M');
  assert.equal(comparisonYAxisTick(6.48,{...settings,ticks:'log'}),'6.48');
  assert.equal(comparisonYAxisTick(4,{view:'mod',scale:'signed-log'}),'4');
  assert.equal(comparisonYAxisTick(1234567,{view:'values',scale:'linear'}),'≈1.2M');
  assert.equal(comparisonXAxisTitle(state,COMPARISON_CHART_DEFAULTS),'Window position');
  assert.match(comparisonYAxisTitle(state,COMPARISON_CHART_DEFAULTS),/signed log/);
  assert.match(comparisonScaleExplanation(state,COMPARISON_CHART_DEFAULTS),/approximate the original values/);
  assert.match(comparisonScaleExplanation(state,{...COMPARISON_CHART_DEFAULTS,ticks:'log'}),/not sequence values/);
});
test('scientific plot labels retain mantissa notation for huge exact-sequence magnitudes',()=>{
  const settings={view:'values',scale:'signed-log',ticks:'scientific'};
  assert.equal(comparisonYAxisTick(18.5,settings),'≈3.2×10^18');
  assert.equal(comparisonYAxisTick(-100.25,settings),'≈−1.8×10^100');
  assert.equal(comparisonYAxisTick(1000.3,settings),'≈2×10^1000');
  assert.equal(comparisonYAxisTick(20.999,settings),'≈1×10^21',
    'Rounded mantissas should normalize their exponent');
  assert.equal(comparisonYAxisTick(-5,{view:'values',scale:'log',ticks:'magnitude'}),'≈1×10^-5');
  assert.equal(comparisonYAxisTick(-15.2,{view:'values',scale:'log',ticks:'magnitude'}),'≈6.3×10^-16');
  assert.equal(comparisonYAxisTick(-15.2,{view:'values',scale:'log',ticks:'scientific'}),'≈6.3×10^-16');
  assert.equal(comparisonYAxisTick(20.999,{view:'values',scale:'log',ticks:'scientific'}),'≈1×10^21');
  assert.equal(comparisonYAxisTick(18.5,{...settings,ticks:'magnitude'}),'≈10^18.5');
  assert.equal(comparisonYAxisTick(18.5,{...settings,ticks:'log'}),'18.5');
  assert.equal(workbenchRows([localSource(a)],WORKBENCH_DEFAULTS).series[0].rows[2].raw,'9007199254740993');
});
test('automatic comparison titles identify the selected records and displayed transform',()=>{
  const names=[{id:'KSEQ-000025',title:'Fibonacci numbers'},{id:'KSEQ-000037',title:'Lucas numbers'}];
  assert.equal(comparisonChartTitle(WORKBENCH_DEFAULTS,COMPARISON_CHART_DEFAULTS,names),
    'Original terms · Fibonacci vs Lucas');
  assert.equal(comparisonChartTitle({...WORKBENCH_DEFAULTS,transform:'sum'},COMPARISON_CHART_DEFAULTS,names),
    'Partial sums · Fibonacci vs Lucas');
  assert.equal(comparisonChartTitle({...WORKBENCH_DEFAULTS,view:'mod',modulus:7,transform:'difference'},COMPARISON_CHART_DEFAULTS,names),
    'Residues mod 7 · First differences · Fibonacci vs Lucas');
  assert.equal(comparisonChartTitle(WORKBENCH_DEFAULTS,COMPARISON_CHART_DEFAULTS,names.slice(0,1)),
    'Original terms · Fibonacci');
  assert.equal(comparisonChartTitle(WORKBENCH_DEFAULTS,COMPARISON_CHART_DEFAULTS,[...names,names[0]]),
    'Original terms · 3 sequences');
  assert.equal(comparisonChartTitle(WORKBENCH_DEFAULTS,{...COMPARISON_CHART_DEFAULTS,title:'Author chart'},names),
    'Author chart');
});

test('custom chart and legend text round trip with exact pinned comparisons',()=>{
  const pinned={...a,record_sha256:'a'.repeat(64)};
  const chartLabels=validateComparisonChart({
    title:'Fibonacci and Lucas · coefficient comparison',
    xTitle:'Stored local index',yTitle:'Magnitude of coefficient',
    titleDisplay:'show',xTitleDisplay:'hide',yTitleDisplay:'show',
    titleSize:'22',xTitleSize:'14',yTitleSize:'18',titleAlign:'right',
    titleColor:'#7c2d12',titleFont:'serif',titleWeight:'bold',titleStyle:'italic',
    xTitleColor:'#075985',xTitleFont:'mono',xTitleWeight:'normal',yTitleStyle:'italic',
    legend:'show',legendPosition:'bottom',ticks:'log',seriesLabels:['First family','Second family']
  });
  assert.equal(comparisonChartTitle(WORKBENCH_DEFAULTS,chartLabels),chartLabels.title);
  const url=workbenchLink('https://example.test/sequence-compare.html',[localSource(pinned),localSource({...b,record_sha256:'b'.repeat(64)})],WORKBENCH_DEFAULTS,chartLabels);
  const payload=JSON.parse(new URL(url).searchParams.get('wb'));
  assert.equal(payload.schema,2);
  assert.deepEqual(payload.chartLabels,chartLabels);
  const restored=readWorkbenchLink(url,[pinned,{...b,record_sha256:'b'.repeat(64)}],'snapshot');
  assert.deepEqual(restored.chartLabels,chartLabels);
  assert.equal(restored.sources[0].terms[2],'9007199254740993');
  const old=new URL(url),oldData=JSON.parse(old.searchParams.get('wb'));
  delete oldData.chartLabels;oldData.schema=1;oldData.sources=oldData.sources.map(({type,id})=>({type,id}));
  old.searchParams.set('wb',JSON.stringify(oldData));
  assert.deepEqual(readWorkbenchLink(old,[pinned,b],'snapshot').chartLabels,validateComparisonChart());
  const oldLabels=new URL(url),older=JSON.parse(oldLabels.searchParams.get('wb'));
  for(const key of ['titleDisplay','xTitleDisplay','yTitleDisplay','titleSize','xTitleSize','yTitleSize','titleAlign'])delete older.chartLabels[key];
  for(const key of ['title','xTitle','yTitle'])for(const property of ['Color','Font','Weight','Style'])delete older.chartLabels[key+property];
  oldLabels.searchParams.set('wb',JSON.stringify(older));
  const restoredOlder=readWorkbenchLink(oldLabels,[pinned,{...b,record_sha256:'b'.repeat(64)}],'snapshot');
  assert.equal(restoredOlder.chartLabels.title,chartLabels.title);
  assert.equal(restoredOlder.chartLabels.titleDisplay,'show');assert.equal(restoredOlder.chartLabels.xTitleDisplay,'show');
  assert.equal(restoredOlder.chartLabels.titleSize,'auto');assert.equal(restoredOlder.chartLabels.titleAlign,'center');
  assert.equal(restoredOlder.chartLabels.titleColor,'auto');assert.equal(restoredOlder.chartLabels.titleFont,'sans');
  assert.equal(restoredOlder.chartLabels.titleWeight,'auto');assert.equal(restoredOlder.chartLabels.titleStyle,'normal');
});
test('chart text customization rejects invalid labels and does not change data',()=>{
  for(const bad of [{title:'x'.repeat(91)},{xTitle:'x'.repeat(65)},{yTitle:'line\n2'},
    {legend:'unknown'},{legendPosition:'left'},{ticks:'numbers'}, {seriesLabels:['a','b','c','d','e']},
    {seriesLabels:['a\nnewline']},{seriesLabels:['x'.repeat(61)]},
    {titleDisplay:'none'},{xTitleDisplay:false},{yTitleDisplay:'auto'},{titleSize:26},
    {titleSize:'27'},{xTitleSize:'26'},{yTitleSize:'0'},{titleAlign:'justify'},
    {titleColor:'red'},{titleColor:'#fff'},{xTitleColor:'#00000000'},{yTitleColor:'url(https://invalid.test/a.svg)'},
    {titleColor:'var(--ink)'},{titleFont:'External font'},{xTitleFont:'url(font.woff)'},{titleWeight:'900'},
    {yTitleWeight:700},{titleStyle:'oblique'},{xTitleStyle:true}]){
    assert.throws(()=>validateComparisonChart(bad));
  }
  const state=validateComparisonChart({legend:'hide',seriesLabels:['One','Two']});
  assert.equal(state.legend,'hide');
  assert.equal(validateComparisonChart({titleColor:'#ABCDEF'}).titleColor,'#abcdef');
  assert.equal(workbenchRows([localSource(a)],WORKBENCH_DEFAULTS).series[0].rows[2].raw,'9007199254740993');
});
test('comparison CSV retains exact values, source positions and attribution',()=>{
  const ref=referenceSource({id:'A000001',sample_position:8,values:['9007199254740993']},'sha');const csv=comparisonCSV(workbenchRows([ref]));
  for(const text of ['9007199254740993','mathematical offset unknown','"8"','CC-BY-SA-4.0','OEIS Foundation','"sha"'])assert.ok(csv.includes(text),text);
});
test('Appell column comparisons retain the readout and its exact values through sharing',()=>{
  const source=familySource('appell',{N:3,j:0,r:1,appellMode:'column',column:2,count:4});
  assert.match(source.title,/column=2/);assert.doesNotMatch(source.title,/x=/);
  assert.deepEqual(source.terms,['1','-10','532','-83215']);
  const restored=readWorkbenchLink(workbenchLink('https://example.test/sequence-library.html',[source],WORKBENCH_DEFAULTS),[],'snapshot').sources[0];
  assert.equal(restored.familyDescriptor.params.appellMode,'column');
  assert.equal(restored.title,source.title);assert.deepEqual(restored.terms,source.terms);
});
test('legacy comparison aliases restore once when inactive family parameters normalize away',()=>{
  const url=new URL('https://example.test/sequence-library.html');
  url.searchParams.set('wb',JSON.stringify({schema:1,state:WORKBENCH_DEFAULTS,sources:[
    {type:'family',engine:'linear',params:{k:2,r:1,c:1,count:4,N:3}},
    {type:'family',engine:'linear',params:{k:2,r:1,c:1,count:4,N:4}},
  ]}));
  const restored=readWorkbenchLink(url.href,[],'snapshot');
  assert.equal(restored.sources.length,1);assert.deepEqual(restored.sources[0].terms,['1','1','2','3']);
});
test('scoped saves preserve other collections and reject oversized writes',()=>{
  let raw='[]';const storage={getItem:()=>raw,setItem:(key,value)=>{assert.equal(key,STORAGE_KEY);raw=value;}};
  writeSaved(storage,['KFOR-S-catalan-03-01','KOM085','KSEQ-000001']);
  writeSaved(storage,[],new Set(['KSEQ-000001']));assert.deepEqual(readSaved(storage).ids,['KFOR-S-catalan-03-01','KOM085']);
  writeSaved(storage,['KSEQ-000002'],new Set(['KSEQ-000001','KSEQ-000002']));assert.equal(readSaved(storage).ids.length,3);
  const before=raw;assert.equal(writeSaved(storage,Array.from({length:501},(_,i)=>'KFOR-test-'+i)),false);assert.equal(raw,before);
  assert.equal(readSaved({getItem:()=>{throw Error('denied');}}).available,false);
});
test('worker restores selected slices and rejects absent or malformed excerpts',async()=>{
  // Run the actual worker body over bounded exported-line fixtures, without a network request.
  const code=fs.readFileSync(new URL('../website/assets/sequence-oeis-worker.mjs',import.meta.url),'utf8').replace(/^import .*;\r?\n/gm,'').replaceAll('import.meta.url',"'https://example.test/assets/sequence-oeis-worker.mjs'");
  const messages=[],files={'stripped.gz':'A000001 ,99,0,-1,9007199254740993,7,\nA000045 ,99,0,1,1,2,3,5,8,13,21,34,\n','names.gz':'A000001 Test reference\nA000045 Fibonacci numbers\n'};
  const self={postMessage:data=>messages.push(data)},context=vm.createContext({self,referenceQuery,referenceValues,referencePositions,referenceNameMatches,identifyInput,discoveryProbes,matchProbe,URL,Blob,TextDecoderStream,DecompressionStream,Uint8Array,fetch:async url=>new Response(files[new URL(url).pathname.split('/').pop()])});
  vm.runInContext(code,context);
  await self.onmessage({data:{type:'records',records:[{id:'A000001',position:2,count:2}]}});assert.equal(messages.at(-1).type,'results');assert.deepEqual(Array.from(messages.at(-1).results[0].values),['-1','9007199254740993']);
  for(const records of [[{id:'A000001',position:99,count:1}],[{id:'A999999',position:0,count:1}],[],[{id:'bad',position:0,count:1}],[{id:'A000001',position:0,count:257}]]){await self.onmessage({data:{type:'records',records}});assert.equal(messages.at(-1).type,'error');}
  files['stripped.gz']='A000045 ,99,0,1,1,2,3,5,8,13,21,34,\n';files['names.gz']='A000045 Fibonacci numbers\n';
  await self.onmessage({data:{type:'discover',text:'0,2,2,4,6,10,16,26'}});assert.equal(messages.at(-1).type,'results');const hit=messages.at(-1).results.find(r=>r.id==='A000045');assert.ok(hit);assert.equal(messages.at(-1).license,'CC-BY-SA-4.0');assert.ok(messages.at(-1).snapshot.stripped_sha256);assert.match(hit.inputOperation,/gcd 2/);assert.equal(hit.targetIndex,1);assert.equal(hit.sample_position,0);assert.equal(hit.title,'Fibonacci numbers');assert.deepEqual(Array.from(hit.inputPositions),[0,1,2,3,4,5,6,7]);
});
