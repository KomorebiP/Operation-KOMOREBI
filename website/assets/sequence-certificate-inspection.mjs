/* Read-only exploration of previously independently verified finite certificates.
   This module does not certify any input. Call verifyComparisonCertificate first. */
export const CERTIFICATE_INSPECTION_PAGE_SIZE=12;

function collectVerifiedInspectionRows(certificate,{seriesIndex=-1,onlyDifferences=false}={}){
  if(!certificate||!Array.isArray(certificate.series)||!Array.isArray(certificate.sources)||
    certificate.series.length!==certificate.sources.length||certificate.series.length<1||
    certificate.series.length>4)throw Error('A verified comparison certificate is required to inspect its rows.');
  if(!Number.isSafeInteger(seriesIndex)||seriesIndex < -1||seriesIndex>=certificate.series.length)
    throw RangeError('Select a recorded certificate series.');
  if(typeof onlyDifferences!=='boolean')throw Error('Choose whether to show only finite differences.');
  const baseline=certificate.series[0].rows;
  const baselineMap=new Map(baseline.filter(row=>row.displayed!==null)
    .map(row=>[row.alignmentKey,row]));
  const rows=[];
  for(const [i,series] of certificate.series.entries()){
    const source=certificate.sources[i];
    if(i!==seriesIndex&&seriesIndex!==-1)continue;
    for(const row of series.rows){
      const matched=i>0?baselineMap.get(row.alignmentKey):null;
      const status=row.displayed===null?'undefined':
        i===0?'baseline':
        !matched?'no-overlap':
        matched.displayed===row.displayed?'equal':'different';
      if(onlyDifferences&&status!=='different')continue;
      rows.push({
        seriesIndex:i,sourceId:source.id,sourceType:source.type,
        indexConvention:source.indexConvention,
        windowPosition:row.windowPosition,storedPosition:row.storedPosition,
        recordedIndex:row.recordedIndex,
        sourceDegree:source.sourceDegrees===null?null:source.sourceDegrees[row.storedPosition],
        alignmentKey:row.alignmentKey,raw:row.raw,displayed:row.displayed,
        baselineDisplayed:matched?.displayed??null,
        status
      });
    }
  }
  rows.sort((a,b)=>a.alignmentKey-b.alignmentKey||a.seriesIndex-b.seriesIndex||
    a.storedPosition-b.storedPosition);
  return rows;
}
export function certificateInspectionWindow(certificate,{seriesIndex=-1,onlyDifferences=false,page=0,pageSize=CERTIFICATE_INSPECTION_PAGE_SIZE}={}){
  if(!Number.isSafeInteger(page)||page<0||
    !Number.isSafeInteger(pageSize)||pageSize<1||pageSize>100)
    throw RangeError('Choose a bounded inspection page and page size.');
  const rows=collectVerifiedInspectionRows(certificate,{seriesIndex,onlyDifferences});
  const total=rows.length,pages=Math.max(1,Math.ceil(total/pageSize)),
    selectedPage=Math.min(page,pages-1),start=selectedPage*pageSize;
  return {total,pages,page:selectedPage,pageSize,rows:rows.slice(start,start+pageSize),
    different:rows.filter(row=>row.status==='different').length};
}

/** Export every matching verified row, not just the current twelve-row page.
 * Values remain literal exact decimal strings in the CSV bytes. Spreadsheet
 * programs may still coerce long integers; import integer columns as text.
 * Keep the original JSON certificate for independent replay.
 */
export function certificateInspectionCSV(certificate,{seriesIndex=-1,onlyDifferences=false}={}){
  const rows=collectVerifiedInspectionRows(certificate,{seriesIndex,onlyDifferences});
  if(typeof certificate.certificateSha256!=='string'||!/^[a-f0-9]{64}$/.test(certificate.certificateSha256))
    throw Error('A verified certificate SHA-256 receipt is required for inspection export.');
  const header=[
    'certificate_sha256','source_id','source_type','source_receipt_sha256',
    'index_convention','index_symbol','window_position','stored_prefix_position',
    'recorded_index_or_export_position','source_degree_if_recorded',
    'alignment_key','original_exact_integer','displayed_exact_integer',
    'baseline_displayed_exact_integer','comparison_status'
  ];
  const escapeCell=(value,isMetadata=false)=>{
    let safe=String(value??'');
    // Prevent untrusted source IDs or conventions being interpreted as
    // formulas when a CSV is opened in a spreadsheet application.
    if(isMetadata&&/^[=+@-]/.test(safe)&&!/^-?[0-9]+$/.test(safe))safe="'"+safe;
    return '"'+safe.replaceAll('"','""')+'"';
  };
  const data=[header.map(h=>escapeCell(h)).join(',')];
  for(const row of rows){
    const source=certificate.sources[row.seriesIndex];
    const values=[
      certificate.certificateSha256,row.sourceId,row.sourceType,source.catalogueReceipt??'',
      row.indexConvention,source.indexSymbol,row.windowPosition,row.storedPosition,
      row.recordedIndex,row.sourceDegree??'',row.alignmentKey,row.raw,
      row.displayed??'',row.baselineDisplayed??'',row.status
    ];
    data.push(values.map((v,i)=>escapeCell(v,[1,2,4,5,14].includes(i))).join(','));
  }
  return data.join('\r\n')+'\r\n';
}
