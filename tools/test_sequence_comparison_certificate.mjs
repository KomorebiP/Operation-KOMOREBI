import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {COMPARISON_CERTIFICATE_SCHEMA,createComparisonCertificate,verifyComparisonCertificate,assessCertificateCatalogue} from '../website/assets/sequence-comparison-certificate.mjs';
import {localSource,customSource,referenceSource,WORKBENCH_DEFAULTS} from '../website/assets/sequence-workbench-core.mjs';
import {certificateInspectionWindow,CERTIFICATE_INSPECTION_PAGE_SIZE} from '../website/assets/sequence-certificate-inspection.mjs';

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
