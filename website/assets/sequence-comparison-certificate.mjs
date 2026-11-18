/* Standalone finite exact-data comparison certificate and verifier.
   All arithmetic below is independent of the workbench's plot/transform routine. */
import {workbenchRows,agreements,validateWorkbench} from './sequence-workbench-core.mjs';
import {validateAppearance} from './sequence-plot-options.mjs';
import {validateComparisonChart} from './sequence-comparison-chart.mjs';

export const COMPARISON_CERTIFICATE_SCHEMA=1;
export const COMPARISON_CERTIFICATE_KIND='komorebi-sequence-comparison-certificate';
const SOURCE_TYPES=new Set(['local','family','custom','oeis']);
const EXACT_INTEGER=/^(?:0|-?[1-9][0-9]*)$/;
const DIGEST=/^[0-9a-f]{64}$/;
const MAX_CERTIFICATE_CHARS=8000000;
const MAX_SOURCE_TERMS=4096;
const MAX_TOTAL_DIGITS=3000000;

function check(ok,message){if(!ok)throw Error(message);}
function jsonEqual(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function fingerprintParts(source){
  return [source.id,source.collection,source.offset,source.indexSymbol,source.terms,source.sourceDegrees];
}
async function sha256(value){
  const subtle=globalThis.crypto?.subtle;
  check(Boolean(subtle),'SHA-256 is unavailable. Export a plain exact CSV instead.');
  const bytes=new TextEncoder().encode(JSON.stringify(value));
  const hash=new Uint8Array(await subtle.digest('SHA-256',bytes));
  return Array.from(hash,byte=>byte.toString(16).padStart(2,'0')).join('');
}
function normalSource(source){
  check(source&&SOURCE_TYPES.has(source.type)&&typeof source.key==='string'&&source.key.length>0,
    'The comparison contains an unsupported source.');
  const id=String(source.id||'');
  check(id.length>0&&id.length<=128,'A comparison source has an invalid identifier.');
  const offset=source.offset;
  check(Number.isSafeInteger(offset)&&Math.abs(offset)<=1000000,'The source offset is not an exact bounded integer.');
  const terms=source.terms;
  check(Array.isArray(terms)&&terms.length>0&&terms.length<=MAX_SOURCE_TERMS,
    'Source terms exceed the finite certificate limit. Export exact CSV or a smaller comparison.');
  check(terms.every(term=>typeof term==='string'&&term.length<=10000&&EXACT_INTEGER.test(term)),
    'Source terms must be canonical exact integer strings.');
  const degrees=source.sourceDegrees??source.source_degrees??null;
  check(degrees===null||(Array.isArray(degrees)&&degrees.length===terms.length&&degrees.every(Number.isSafeInteger)),
    'A source has an incomplete or invalid degree map.');
  const collection=source.collection??null;
  const indexSymbol=source.indexSymbol||source.index_symbol||(source.type==='oeis'?'OEIS export position':
    String(source.indexKind||'').includes('flat index j')?'j':'n');
  const receipt=source.catalogueReceipt??source.receipt??null;
  check(receipt===null||DIGEST.test(receipt),'A local source has an invalid catalogue SHA-256 receipt.');
  return {
    type:source.type,key:source.key,id,title:String(source.title||source.id),
    indexConvention:String(source.indexConvention??source.indexKind??'stored index'),
    indexSymbol,collection,offset,url:String(source.url||''),
    referenceSnapshot:source.referenceSnapshot??source.snapshot??null,
    familyParameters:source.familyParameters??source.familyDescriptor??null,
    catalogueReceipt:receipt,sourceDegrees:degrees===null?null:degrees.slice(),
    terms:terms.slice()
  };
}
function pureRows(source,state){
  const values=source.terms.map(BigInt),end=Math.min(values.length,state.skip+state.count);
  const rows=[];let total=0n;
  for(let i=0;i<end;i++){
    total+=values[i];if(i<state.skip)continue;
    const exact=state.transform==='sum'?total:state.transform==='difference'?
      (i===0?null:values[i]-values[i-1]):values[i];
    const residue=exact===null?null:((exact%BigInt(state.modulus))+BigInt(state.modulus))%BigInt(state.modulus);
    const displayed=exact===null?null:String(state.view==='mod'?residue:exact);
    const recordedIndex=source.offset+i,windowPosition=i-state.skip;
    rows.push({windowPosition,storedPosition:i,recordedIndex,
      alignmentKey:state.alignment==='indices'?recordedIndex:windowPosition,
      raw:source.terms[i],displayed});
  }
  return {key:source.key,rows};
}
function pureAgreements(series){
  if(!series.length)return [];
  const baseline=series[0],lookup=new Map(baseline.rows.filter(row=>row.displayed!==null).map(row=>[row.alignmentKey,row]));
  return series.slice(1).map(target=>{
    let compared=0,equal=0,firstMismatch=null;
    for(const row of target.rows){
      const left=lookup.get(row.alignmentKey);
      if(!left||row.displayed===null)continue;
      compared++;
      if(left.displayed===row.displayed)equal++;
      else if(firstMismatch===null)firstMismatch={
        x:row.alignmentKey,left:left.recordedIndex,right:row.recordedIndex,
        leftValue:left.displayed,rightValue:row.displayed
      };
    }
    return {source:target.key,baseline:baseline.key,compared,equal,firstMismatch};
  });
}
function displayRows(result){
  return result.series.map(({source,rows})=>({key:source.key,rows:rows.map(row=>({
    windowPosition:row.position,storedPosition:row.storedPosition,
    recordedIndex:row.index,alignmentKey:row.x,raw:row.raw,displayed:row.value
  }))}));
}
function bodySize(body){return JSON.stringify(body).length;}
function validateInputSources(sources,state){
  check(Array.isArray(sources)&&sources.length>=1&&sources.length<=4,'A certificate needs one to four exact sources.');
  const result=sources.map(normalSource);
  check(new Set(result.map(source=>source.key)).size===result.length,'A certificate contains duplicate sources.');
  if(state.alignment==='indices')check(!result.some(source=>source.type==='oeis'),
    'OEIS export positions do not provide mathematical index offsets. Use position alignment.');
  const digits=result.reduce((total,source)=>total+source.terms.reduce((sum,term)=>sum+term.length,0),0);
  check(digits<=MAX_TOTAL_DIGITS,'The certificate exceeds the exact-data size limit. Export a smaller comparison.');
  return result;
}
/* Build from visible workbench sources. Include the entire stored prefixes, so
   partial sums are independently reproducible even when the plotted window skips terms. */
export async function createComparisonCertificate(sources,settings,presentation={}){
  const state=validateWorkbench(settings),inputs=validateInputSources(sources,state);
  for(const source of inputs){
    source.dataSha256=await sha256(fingerprintParts(source));
    if(source.type==='local'&&source.catalogueReceipt)
      check(source.dataSha256===source.catalogueReceipt,
        'A local source does not match its indexed catalogue receipt: '+source.id);
  }
  const result=workbenchRows(sources,state);
  check(result.series.some(series=>series.rows.length>0),'Select a window containing stored values.');
  const body={
    schema:COMPARISON_CERTIFICATE_SCHEMA,kind:COMPARISON_CERTIFICATE_KIND,
    scope:'Finite stored-prefix integer calculations only; not a proof of an infinite identity or of historical novelty.',
    coordinateNote:'Position alignment matches stored window positions. Index alignment uses recorded local indices, not source Taylor degrees. OEIS indexes are export positions.',
    sourceReceiptNote:'Local catalogue receipts identify published indexed data. Other input hashes attest only to embedded finite data, not external source authority.',
    state,
    presentation:{
      chartLabels:validateComparisonChart(presentation.chartLabels||{}),
      appearance:validateAppearance(presentation.appearance||{})
    },
    sources:inputs,
    series:displayRows(result),
    finiteAgreements:agreements(result)
  };
  check(bodySize(body)<=MAX_CERTIFICATE_CHARS,'The exact certificate is too large. Export CSV or a smaller comparison.');
  const certificate={...body,certificateSha256:await sha256(body)};
  await verifyComparisonCertificate(certificate);
  return certificate;
}
/* The verifier does not call workbenchRows, agreements, transform, or coordinate.
   It recomputes every finite row and overlap from the embedded BigInt inputs. */
export async function verifyComparisonCertificate(certificate){
  check(certificate&&typeof certificate==='object'&&!Array.isArray(certificate),
    'The certificate must be a JSON object.');
  const {certificateSha256,...body}=certificate;
  check(DIGEST.test(certificateSha256||''),'Missing or malformed certificate SHA-256 digest.');
  check(bodySize(body)<=MAX_CERTIFICATE_CHARS,'The certificate exceeds the supported size limit.');
  check(body.schema===COMPARISON_CERTIFICATE_SCHEMA&&body.kind===COMPARISON_CERTIFICATE_KIND,
    'Unsupported exact comparison certificate version.');
  check(typeof body.scope==='string'&&typeof body.coordinateNote==='string'&&typeof body.sourceReceiptNote==='string',
    'The certificate is missing its finite-proof and indexing limitations.');
  check(await sha256(body)===certificateSha256,'The comparison certificate digest does not match its contents.');
  const state=validateWorkbench(body.state);
  check(jsonEqual(state,body.state),'The comparison settings contain unexpected fields or are not normalized.');
  const sources=validateInputSources(body.sources,state);
  check(Array.isArray(body.series)&&Array.isArray(body.finiteAgreements),'The comparison results are missing.');
  for(const source of sources){
    const saved=body.sources.find(entry=>entry.key===source.key);
    check(jsonEqual({...source,dataSha256:saved.dataSha256},saved),
      'Source metadata is not in the normalized certificate format.');
    const sha=await sha256(fingerprintParts(source));
    check(sha===saved.dataSha256,'Source data SHA-256 mismatch for '+source.id);
    if(source.type==='local'&&source.catalogueReceipt)
      check(sha===source.catalogueReceipt,'Local catalogue receipt mismatch for '+source.id);
  }
  check(body.presentation&&jsonEqual(validateComparisonChart(body.presentation.chartLabels),body.presentation.chartLabels),
    'Invalid chart presentation settings.');
  check(jsonEqual(validateAppearance(body.presentation.appearance),body.presentation.appearance),
    'Invalid plot appearance settings.');
  const expected=sources.map(source=>pureRows(source,state));
  check(jsonEqual(expected,body.series),'The certificate rows differ from independently recomputed exact integers.');
  const expectedAgreements=pureAgreements(expected);
  check(jsonEqual(expectedAgreements,body.finiteAgreements),
    'The finite comparison agreements do not match independently recomputed values.');
  return {
    ok:true,schema:body.schema,sources:sources.length,
    exactRows:expected.reduce((sum,series)=>sum+series.rows.length,0),
    finiteChecks:expectedAgreements.length,
    comparedPositions:expectedAgreements.reduce((sum,check)=>sum+check.compared,0),
    certificateSha256
  };
}

/** Compare independently verified embedded local sources with this site's currently
 * published catalogue receipts. This is a separate check from finite arithmetic.
 * Other providers and generated sources have no local catalogue attestation.
 */
export function assessCertificateCatalogue(certificate,entries){
  check(certificate&&Array.isArray(certificate.sources)&&Array.isArray(entries),
    'Cannot compare certificate sources against the current catalogue.');
  const catalogue=new Map(entries.filter(entry=>entry&&typeof entry.id==='string')
    .map(entry=>[entry.id,entry]));
  const sources=certificate.sources.map(source=>{
    const id=String(source.id||'');
    if(source.type!=='local')return {id,type:source.type,status:'embedded-only'};
    const expected=source.catalogueReceipt;
    if(!DIGEST.test(expected||''))return {id,type:'local',status:'no-receipt'};
    const current=catalogue.get(id);
    if(!current)return {id,type:'local',status:'not-in-catalogue'};
    if(!DIGEST.test(current.record_sha256||'')||current.record_sha256!==expected)
      return {id,type:'local',status:'different'};
    return {id,type:'local',status:'matches'};
  });
  const local=sources.filter(source=>source.type==='local');
  return {
    localSources:local.length,
    matched:local.filter(source=>source.status==='matches').length,
    different:local.filter(source=>source.status==='different').length,
    unavailable:local.filter(source=>source.status==='not-in-catalogue').length,
    withoutReceipt:local.filter(source=>source.status==='no-receipt').length,
    sources
  };
}
