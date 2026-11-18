/* Read-only exploration of previously independently verified finite certificates.
   This module does not certify any input. Call verifyComparisonCertificate first. */
export const CERTIFICATE_INSPECTION_PAGE_SIZE=12;

export function certificateInspectionWindow(certificate,{seriesIndex=-1,onlyDifferences=false,page=0,pageSize=CERTIFICATE_INSPECTION_PAGE_SIZE}={}){
  if(!certificate||!Array.isArray(certificate.series)||!Array.isArray(certificate.sources)||
    certificate.series.length!==certificate.sources.length||certificate.series.length<1||
    certificate.series.length>4)throw Error('A verified comparison certificate is required to inspect its rows.');
  if(!Number.isSafeInteger(seriesIndex)||seriesIndex < -1||seriesIndex>=certificate.series.length)
    throw RangeError('Select a recorded certificate series.');
  if(typeof onlyDifferences!=='boolean')throw Error('Choose whether to show only finite differences.');
  if(!Number.isSafeInteger(page)||page<0||
    !Number.isSafeInteger(pageSize)||pageSize<1||pageSize>100)
    throw RangeError('Choose a bounded inspection page and page size.');

  const baseline=certificate.series[0].rows;
  const baselineMap=new Map(baseline.filter(row=>row.displayed!==null)
    .map(row=>[row.alignmentKey,row]));
  const rows=[];
  for(const [i,series] of certificate.series.entries()){
    const source=certificate.sources[i];
    if(i!==seriesIndex&&seriesIndex!==-1)continue;
    for(const row of series.rows){
      const matched=i>0?baselineMap.get(row.alignmentKey):null;
      const status=i===0?'baseline':
        row.displayed===null?'undefined':
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
  const total=rows.length,pages=Math.max(1,Math.ceil(total/pageSize)),
    selectedPage=Math.min(page,pages-1),start=selectedPage*pageSize;
  return {total,pages,page:selectedPage,pageSize,rows:rows.slice(start,start+pageSize),
    different:rows.filter(row=>row.status==='different').length};
}
