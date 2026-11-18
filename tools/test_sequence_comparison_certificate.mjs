import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {COMPARISON_CERTIFICATE_SCHEMA,createComparisonCertificate,verifyComparisonCertificate,assessCertificateCatalogue} from '../website/assets/sequence-comparison-certificate.mjs';
import {localSource,customSource,familySource,referenceSource,WORKBENCH_DEFAULTS} from '../website/assets/sequence-workbench-core.mjs';
import {certificateInspectionWindow,certificateInspectionCSV,CERTIFICATE_INSPECTION_PAGE_SIZE} from '../website/assets/sequence-certificate-inspection.mjs';

const sha=data=>createHash('sha256').update(JSON.stringify(data),'utf8').digest('hex');
const a={id:'KSEQ-TEST',title:'Exact reference',collection:'atlas',index_symbol:'n',offset:2,
  terms:['0','-1','9007199254740993','7'],url:'sequences/KSEQ-TEST.html'};
a.record_sha256=sha([a.id,a.collection,a.offset,a.index_symbol,a.terms,null]);
const second=customSource({title:'Local unreviewed input',offset:2,terms:['0','-1','9007199254740993','8']});
const pinned=localSource(a,'https://example.test/');

async function resign(certificate){
  const body=structuredClone(certificate);
  delete body.certificateSha256;
  return {...body,certificateSha256:sha(body)};
}
test('certificates are self-contained with exact source receipts, indices and finite agreement',async()=>{
  const state={...WORKBENCH_DEFAULTS,skip:1,count:3,scale:'signed-log'};
  const cert=await createComparisonCertificate([pinned,second],state,{
    appearance:{palette:'ink',theme:'white'},
    chartLabels:{title:'Exact finite prefix comparison',seriesLabels:['Reference','Input']}
  });
  assert.equal(cert.kind,'komorebi-sequence-comparison-certificate');
  assert.equal(cert.schema,COMPARISON_CERTIFICATE_SCHEMA);
  assert.equal(cert.sources[0].catalogueReceipt,a.record_sha256);
  assert.equal(cert.sources[0].dataSha256,a.record_sha256);
  assert.deepEqual(cert.sources[0].terms,a.terms);
  assert.equal(cert.sources[0].offset,2);
  assert.equal(cert.sources[0].indexSymbol,'n');
  assert.equal(cert.sources[0].indexConvention,'local index n');
  assert.equal(cert.sources[1].sourceDegrees,null);
  assert.equal(cert.presentation.chartLabels.title,'Exact finite prefix comparison');
  assert.equal(cert.presentation.appearance.palette,'ink');
  assert.deepEqual(cert.series[0].rows.map(row=>[row.recordedIndex,row.windowPosition,row.raw,row.displayed]),[
    [3,0,'-1','-1'],[4,1,'9007199254740993','9007199254740993'],[5,2,'7','7']
  ]);
  assert.deepEqual(cert.finiteAgreements,[{
    source:second.key,baseline:pinned.key,compared:3,equal:2,
    firstMismatch:{x:2,left:5,right:5,leftValue:'7',rightValue:'8'}
  }]);
  const verification=await verifyComparisonCertificate(JSON.parse(JSON.stringify(cert)));
  assert.equal(verification.ok,true);
  assert.equal(verification.exactRows,6);
  assert.equal(verification.comparedPositions,3);
  assert.equal(verification.certificateSha256,cert.certificateSha256);
});
test('certificates issued before title typography controls retain their original digest and exact verification',async()=>{
  const legacyLabels={title:'Saved finite comparison',xTitle:'Recorded index',yTitle:'Value',
    legend:'show',legendPosition:'bottom',legendStyle:'id',ticks:'scientific',seriesLabels:['Reference','Input']};
  const current=await createComparisonCertificate([pinned,second],{skip:1,count:3},{chartLabels:legacyLabels});
  current.presentation.chartLabels=legacyLabels;
  const legacy=await resign(current),before=JSON.stringify(legacy);
  // Captured from the previous generator before typography fields were added.
  assert.equal(legacy.certificateSha256,'b35a31b3182b3e4cc9fdb43c19d51df2087c2551e7d3ab0c4f3070c944171f97');
  const verified=await verifyComparisonCertificate(legacy);
  assert.equal(verified.ok,true);assert.equal(verified.exactRows,6);
  assert.equal(JSON.stringify(legacy),before,'Verification must not normalize or rewrite a saved certificate');
  for(const change of [
    labels=>{labels.titleSize='26';},
    labels=>{labels.unrecognized='show';},
    labels=>{delete labels.ticks;},
    labels=>{labels.title=' Saved finite comparison ';}
  ]){
    const malformed=structuredClone(legacy);change(malformed.presentation.chartLabels);
    await assert.rejects(verifyComparisonCertificate(await resign(malformed)),/Invalid chart presentation settings/);
  }
});
test('full title typography survives certificates while partial or invalid presentation settings are rejected',async()=>{
  const certificate=await createComparisonCertificate([pinned,second],{skip:1,count:3},{chartLabels:{
    title:'Finite values',titleDisplay:'hide',xTitleDisplay:'show',yTitleDisplay:'hide',
    titleSize:'26',xTitleSize:'18',yTitleSize:'16',titleAlign:'right'
  }});
  assert.equal(certificate.presentation.chartLabels.titleSize,'26');
  assert.equal(certificate.presentation.chartLabels.yTitleDisplay,'hide');
  assert.equal((await verifyComparisonCertificate(certificate)).ok,true);
  for(const change of [
    labels=>{delete labels.xTitleSize;},
    labels=>{labels.extra='unknown';},
    labels=>{labels.titleSize='27';},
    labels=>{labels.titleAlign='justify';}
  ]){
    const malformed=structuredClone(certificate);change(malformed.presentation.chartLabels);
    await assert.rejects(verifyComparisonCertificate(await resign(malformed)),/chart|setting/i);
  }
});
test('in-browser catalogue check distinguishes matching, changed, missing and unpinned local receipts',async()=>{
  const certificate=await createComparisonCertificate([pinned,second],{skip:1,count:2});
  const before=JSON.stringify(certificate);
  const matched=assessCertificateCatalogue(certificate,[a]);
  assert.equal(matched.localSources,1);
  assert.equal(matched.matched,1);
  assert.equal(matched.different,0);
  assert.equal(matched.sources[0].status,'matches');
  assert.equal(matched.sources[1].status,'embedded-only');
  assert.equal(matched.sources[1].type,'custom');
  assert.equal(JSON.stringify(certificate),before,'The site lookup must not mutate the exact certificate');
  const changed=assessCertificateCatalogue(certificate,[{...a,record_sha256:'f'.repeat(64)}]);
  assert.equal(changed.different,1);
  assert.equal(changed.sources[0].status,'different');
  const missing=assessCertificateCatalogue(certificate,[]);
  assert.equal(missing.unavailable,1);
  assert.equal(missing.sources[0].status,'not-in-catalogue');
  const unpinned={...certificate,sources:certificate.sources.map(src=>src.type==='local'?
    {...src,catalogueReceipt:null}:src)};
  const withoutReceipt=assessCertificateCatalogue(unpinned,[a]);
  assert.equal(withoutReceipt.withoutReceipt,1);
  assert.equal(withoutReceipt.sources[0].status,'no-receipt');
  const onlyCustom=await createComparisonCertificate([second],{count:2});
  const external=assessCertificateCatalogue(onlyCustom,[]);
  assert.equal(external.localSources,0);
  assert.equal(external.sources[0].status,'embedded-only');
  assert.throws(()=>assessCertificateCatalogue(null,[]),/Cannot compare certificate sources/);
});
test('verified certificate window pages exact rows and isolates genuine finite disagreements',async()=>{
  const certificate=await createComparisonCertificate([pinned,second],{skip:1,count:3});
  const original=JSON.stringify(certificate);
  assert.equal((await verifyComparisonCertificate(certificate)).ok,true);
  assert.equal(CERTIFICATE_INSPECTION_PAGE_SIZE,12);
  const view=certificateInspectionWindow(certificate,{pageSize:2});
  assert.equal(view.total,6);
  assert.equal(view.pages,3);
  assert.equal(view.rows.length,2);
  assert.deepEqual(view.rows.map(row=>[row.seriesIndex,row.windowPosition,row.recordedIndex,row.raw,row.displayed,row.status]),[
    [0,0,3,'-1','-1','baseline'],[1,0,3,'-1','-1','equal']
  ]);
  const end=certificateInspectionWindow(certificate,{pageSize:2,page:500});
  assert.equal(end.page,2);
  assert.deepEqual(end.rows.map(row=>[row.seriesIndex,row.status]),[[0,'baseline'],[1,'different']]);
  const mismatches=certificateInspectionWindow(certificate,{onlyDifferences:true});
  assert.equal(mismatches.total,1);
  assert.equal(mismatches.rows[0].raw,'8');
  assert.equal(mismatches.rows[0].displayed,'8');
  assert.equal(mismatches.rows[0].baselineDisplayed,'7');
  assert.equal(mismatches.rows[0].recordedIndex,5);
  assert.equal(mismatches.rows[0].alignmentKey,2);
  assert.equal(mismatches.rows[0].sourceDegree,null);
  assert.equal(certificateInspectionWindow(certificate,{seriesIndex:0,onlyDifferences:true}).total,0);
  assert.equal(certificateInspectionWindow(certificate,{seriesIndex:1,onlyDifferences:true}).total,1);
  assert.equal(JSON.stringify(certificate),original,'Read-only inspection must not change verified source data');
});

test('filtered certificate CSV exports ALL exact rows and their baseline, indices and receipt',async()=>{
  const cert=await createComparisonCertificate([pinned,second],{skip:1,count:3});
  const before=JSON.stringify(cert);
  const window=certificateInspectionWindow(cert,{pageSize:1});
  assert.equal(window.rows.length,1);
  assert.equal(window.total,6);
  const csv=certificateInspectionCSV(cert);
  const lines=csv.trimEnd().split(/\r?\n/);
  assert.equal(lines.length,7,'Export every verified displayed row, not just the current page');
  assert.match(lines[0],/certificate_sha256/);
  assert.match(lines[0],/baseline_displayed_exact_integer/);
  assert.match(lines[0],/alignment_key/);
  assert.match(lines[0],/recorded_index_or_export_position/);
  assert.match(lines[0],/source_degree_if_recorded/);
  assert.ok(lines[1].startsWith('"'+cert.certificateSha256+'",'));
  assert.ok(csv.includes('"9007199254740993"'));
  assert.ok(csv.includes('"9007199254740993","9007199254740993"'));
  assert.equal((csv.match(/"different"\r?\n/g)||[]).length,1);
  const justDifferences=certificateInspectionCSV(cert,{onlyDifferences:true});
  assert.equal(justDifferences.trimEnd().split(/\r?\n/).length,2);
  assert.match(justDifferences,/"8","8","7","different"\r?\n/);
  assert.doesNotMatch(justDifferences,/"baseline"/);
  assert.equal(certificateInspectionCSV(cert,{seriesIndex:0,onlyDifferences:true}).trimEnd().split(/\r?\n/).length,1,
    'The baseline has no pairwise disagreements of its own');
  const secondOnly=certificateInspectionCSV(cert,{seriesIndex:1});
  assert.equal(secondOnly.trimEnd().split(/\r?\n/).length,4);
  assert.ok(secondOnly.includes('"PASTED"'));
  const a2={...a,source_degrees:[0,2,4,6]};
  a2.record_sha256=sha([a2.id,a2.collection,a2.offset,a2.index_symbol,a2.terms,a2.source_degrees]);
  const indexed=await createComparisonCertificate([localSource(a2)],{skip:1,count:2});
  const indexedCSV=certificateInspectionCSV(indexed);
  assert.match(indexedCSV,/"local index n","n","0","1","3","2","0","-1","-1",""/);
  assert.equal(JSON.stringify(cert),before,'Export must never change the independently verified certificate');
  assert.throws(()=>certificateInspectionCSV(cert,{seriesIndex:2}),/Select a recorded certificate series/);
});
test('certificate CSV preserves distinct source identities when display identifiers repeat',async()=>{
  const sources=[
    customSource({title:'Baseline input',offset:0,terms:['1','2','3']}),
    customSource({title:'Another input',offset:0,terms:['1','4','6']}),
    familySource('linear',{k:2,c:1,count:3}),
    familySource('linear',{k:2,c:2,count:3})
  ];
  const cert=await createComparisonCertificate(sources,{count:3});
  assert.equal((await verifyComparisonCertificate(cert)).ok,true);
  assert.deepEqual(cert.sources.map(source=>source.id),['PASTED','PASTED','FAMILY-linear','FAMILY-linear']);
  assert.equal(new Set(cert.sources.map(source=>source.dataSha256)).size,4);
  const before=JSON.stringify(cert);
  // These fixtures contain no embedded quotes or newlines in CSV fields.
  const records=csv=>{
    const [header,...rows]=csv.trimEnd().split(/\r?\n/).map(line=>line.slice(1,-1).split('","'));
    return rows.map(row=>Object.fromEntries(header.map((key,index)=>[key,row[index]])));
  };
  const all=records(certificateInspectionCSV(cert));
  assert.equal(all.length,12);
  for(const [index,source]of cert.sources.entries()){
    const rows=all.filter(row=>row.source_number===String(index+1));
    assert.equal(rows.length,3);
    for(const row of rows){
      assert.equal(row.source_id,source.id);
      assert.equal(row.source_data_sha256,source.dataSha256);
      assert.equal(row.certificate_sha256,cert.certificateSha256);
    }
    assert.deepEqual(rows.map(row=>[row.recorded_index_or_export_position,row.original_exact_integer,row.displayed_exact_integer]),
      cert.series[index].rows.map(row=>[String(row.recordedIndex),row.raw,row.displayed]));
  }
  // All four sources start with 1, so values and display IDs alone cannot
  // distinguish the two pasted inputs or the two family parameter choices.
  const first=all.filter(row=>row.window_position==='0');
  assert.equal(new Set(first.map(row=>row.source_number)).size,4);
  assert.equal(new Set(first.map(row=>row.source_data_sha256)).size,4);
  const differences=records(certificateInspectionCSV(cert,{onlyDifferences:true}));
  assert.equal(differences.length,cert.finiteAgreements.reduce((count,item)=>count+item.compared-item.equal,0));
  assert.ok(differences.every(row=>row.comparison_status==='different'));
  assert.deepEqual(differences,all.filter(row=>row.comparison_status==='different'));
  for(let seriesIndex=0;seriesIndex<cert.sources.length;seriesIndex++){
    const selected=row=>row.source_number===String(seriesIndex+1);
    assert.deepEqual(records(certificateInspectionCSV(cert,{seriesIndex})),all.filter(selected));
    assert.deepEqual(records(certificateInspectionCSV(cert,{seriesIndex,onlyDifferences:true})),differences.filter(selected));
  }
  assert.equal(JSON.stringify(cert),before);
});
test('certificate source numbers distinguish parameter choices with identical finite data digests',async()=>{
  const sources=[
    familySource('linear',{k:2,c:1,count:2}),
    familySource('linear',{k:3,c:1,count:2})
  ];
  const cert=await createComparisonCertificate(sources,{count:2});
  assert.equal((await verifyComparisonCertificate(cert)).ok,true);
  assert.notEqual(cert.sources[0].key,cert.sources[1].key);
  assert.equal(cert.sources[0].id,cert.sources[1].id);
  assert.deepEqual(cert.sources[0].terms,cert.sources[1].terms);
  assert.equal(cert.sources[0].dataSha256,cert.sources[1].dataSha256);
  const rows=certificateInspectionCSV(cert).trimEnd().split(/\r?\n/).slice(1);
  assert.equal(rows.length,4);
  assert.deepEqual(rows.map(line=>line.split(',')[1]),['"1"','"2"','"1"','"2"']);
  const selected=certificateInspectionCSV(cert,{seriesIndex:1}).trimEnd().split(/\r?\n/).slice(1);
  assert.deepEqual(selected,rows.filter(line=>line.startsWith('"'+cert.certificateSha256+'","2",')));
  for(const row of selected)assert.ok(row.includes('"'+cert.sources[1].dataSha256+'"'));
  assert.equal(certificateInspectionCSV(cert,{onlyDifferences:true}).trimEnd().split(/\r?\n/).length,1);
});
test('inspection distinguishes absent overlap, undefined first differences and stored source degrees',async()=>{
  const offsetSource=customSource({title:'Shifted index',offset:5,terms:['0','-1','9007199254740993','8']});
  const aligned=await createComparisonCertificate([pinned,offsetSource],{alignment:'indices',count:4});
  const view=certificateInspectionWindow(aligned,{seriesIndex:1});
  assert.deepEqual(view.rows.map(row=>row.status),['different','no-overlap','no-overlap','no-overlap']);
  const differences=certificateInspectionWindow(aligned,{onlyDifferences:true});
  assert.equal(differences.total,1);
  const diffCert=await createComparisonCertificate([pinned,offsetSource],
    {alignment:'indices',transform:'difference',count:4});
  const first=certificateInspectionWindow(diffCert,{seriesIndex:1}).rows[0];
  assert.equal(certificateInspectionWindow(diffCert,{seriesIndex:0}).rows[0].status,'undefined');
  assert.equal(first.status,'undefined');
  assert.equal(first.displayed,null);
  assert.equal(first.recordedIndex,5);
  const withDegrees={...a,source_degrees:[0,2,4,6]};
  withDegrees.record_sha256=sha([withDegrees.id,withDegrees.collection,withDegrees.offset,
    withDegrees.index_symbol,withDegrees.terms,withDegrees.source_degrees]);
  const degreeCert=await createComparisonCertificate([localSource(withDegrees)],{skip:1,count:2});
  assert.deepEqual(certificateInspectionWindow(degreeCert).rows.map(row=>row.sourceDegree),[2,4]);
  assert.equal(certificateInspectionWindow(degreeCert).rows[0].recordedIndex,3);
  for(const options of [{seriesIndex:2},{seriesIndex:-2},{page:-1},{pageSize:0},{pageSize:101},{onlyDifferences:'yes'}])
    assert.throws(()=>certificateInspectionWindow(degreeCert,options));
});

test('independent replay covers partial sums, missing initial differences and Euclidean residues',async()=>{
  const sum=await createComparisonCertificate([pinned],{transform:'sum',skip:2,count:2});
  assert.deepEqual(sum.series[0].rows.map(row=>row.displayed),['9007199254740992','9007199254740999']);
  assert.equal((await verifyComparisonCertificate(sum)).exactRows,2);
  const diffs=await createComparisonCertificate([pinned],{transform:'difference',skip:0,count:3});
  assert.deepEqual(diffs.series[0].rows.map(row=>row.displayed),[null,'-1','9007199254740994']);
  const residue=await createComparisonCertificate([pinned,second],{view:'mod',transform:'raw',modulus:7,skip:0,count:2});
  assert.deepEqual(residue.series[0].rows.map(row=>row.displayed),['0','6']);
  assert.equal((await verifyComparisonCertificate(residue)).finiteChecks,1);
  const indexed=await createComparisonCertificate([pinned,second],{alignment:'indices',count:4});
  assert.deepEqual(indexed.series[0].rows.map(row=>row.alignmentKey),[2,3,4,5]);
  assert.equal((await verifyComparisonCertificate(indexed)).sources,2);
});
test('reference excerpts retain export positions rather than claiming mathematical offsets',async()=>{
  const source=referenceSource({id:'A000045',sample_position:11,values:['0','1','1','2']},'retained-reference-sha');
  const certificate=await createComparisonCertificate([source],{count:3,alignment:'positions'});
  assert.match(certificate.sources[0].indexConvention,/mathematical offset unknown/);
  assert.equal(certificate.sources[0].referenceSnapshot,'retained-reference-sha');
  assert.deepEqual(certificate.series[0].rows.map(row=>row.recordedIndex),[11,12,13]);
  assert.equal((await verifyComparisonCertificate(certificate)).ok,true);
  await assert.rejects(createComparisonCertificate([source],{alignment:'indices'}),/Use position alignment/);
});
test('independent verifier rejects changed results even when an attacker recomputes the outer digest',async()=>{
  const original=await createComparisonCertificate([pinned,second],{skip:1,count:3});
  const corruptResult=structuredClone(original);
  corruptResult.series[0].rows[1].displayed='9007199254740994';
  await assert.rejects(verifyComparisonCertificate(await resign(corruptResult)),/rows differ/);
  const corruptAgreements=structuredClone(original);
  corruptAgreements.finiteAgreements[0].equal=3;
  await assert.rejects(verifyComparisonCertificate(await resign(corruptAgreements)),/agreements do not match/);
  const alteredInput=structuredClone(original);
  alteredInput.sources[0].terms[0]='1';
  await assert.rejects(verifyComparisonCertificate(await resign(alteredInput)),/Source data SHA-256 mismatch/);
  const forgedCatalogue={...a,record_sha256:'f'.repeat(64)};
  await assert.rejects(createComparisonCertificate([localSource(forgedCatalogue)]),/does not match its indexed catalogue receipt/);
  const mismatchedDigest=structuredClone(original);mismatchedDigest.state.skip=0;
  await assert.rejects(verifyComparisonCertificate(mismatchedDigest),/digest does not match/);
});
test('certificate rejects out-of-bounds data or invalid exact integers and never changes the source',async()=>{
  const before=JSON.stringify(a);
  await assert.rejects(createComparisonCertificate([customSource({title:'One',offset:0,terms:['1','2']})],{skip:999}),/Select a window containing stored values/);
  await assert.rejects(createComparisonCertificate([{...pinned,terms:['01']}]),/canonical exact integer strings/);
  await assert.rejects(createComparisonCertificate([pinned,pinned]),/duplicate sources/);
  await assert.rejects(createComparisonCertificate([pinned],{transform:'new'}),/Choose a listed transform/);
  assert.equal(JSON.stringify(a),before);
});

test('offline Node checker verifies a downloaded file and exits nonzero on corruption',async()=>{
  const certificate=await createComparisonCertificate([pinned,second],{skip:1,count:3});
  const folder=mkdtempSync(join(tmpdir(),'komorebi-sequence-certificate-'));
  const filename=join(folder,'verified.json');
  try{
    writeFileSync(filename,JSON.stringify(certificate,null,2)+'\n','utf8');
    const run=()=>spawnSync(process.execPath,
      [new URL('./verify_sequence_comparison_certificate.mjs',import.meta.url).pathname,filename],
      {encoding:'utf8'});
    const accepted=run();
    assert.equal(accepted.status,0,accepted.stderr);
    const report=JSON.parse(accepted.stdout);
    assert.equal(report.ok,true);
    assert.equal(report.exactRows,6);
    assert.equal(report.finiteChecks,1);
    assert.match(report.scope,/not a proof of infinite identity/);
    const broken=structuredClone(certificate);
    broken.series[1].rows[0].displayed='wrong';
    writeFileSync(filename,JSON.stringify(broken,null,2)+'\n','utf8');
    const rejected=run();
    assert.equal(rejected.status,1);
    assert.match(rejected.stderr,/CERTIFICATE VERIFICATION FAILED/);
  }finally{rmSync(folder,{recursive:true,force:true});}
});
