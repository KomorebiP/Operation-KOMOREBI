/* Canonical, self-contained links to one exact Sequence Library inspection window.
   The stored index is not assumed to be the source Taylor degree. */
export const INSPECTION_WINDOW_SIZE=8;

function validRecord(record) {
  return Boolean(record&&typeof record.id==='string'&&record.id.length>0&&record.id.length<=128&&
    Number.isSafeInteger(record.offset)&&record.offset>=0&&
    Array.isArray(record.terms)&&record.terms.length>0&&
    Number.isSafeInteger(record.offset+record.terms.length-1));
}
function readUnsigned(value) {
  if(typeof value!=='string'||value.length>15||!/^(?:0|[1-9][0-9]*)$/.test(value))return null;
  const n=Number(value);
  return Number.isSafeInteger(n)?n:null;
}
function validStart(record,start) {
  return Number.isSafeInteger(start)&&start>=record.offset&&
    start<record.offset+record.terms.length&&
    (start-record.offset)%INSPECTION_WINDOW_SIZE===0;
}

/** Make an independent record link, not a URL to a transient filtered result page. */
export function createInspectionLink(baseUrl,record,variantIndex,startIndex,variantCount=record?.formulas?.length||1) {
  if(!validRecord(record)||!Number.isSafeInteger(variantCount)||variantCount<1||
    !Number.isSafeInteger(variantIndex)||variantIndex<0||variantIndex>=variantCount||
    !validStart(record,startIndex))throw new RangeError('Invalid exact inspection parameters.');
  const url=new URL('sequence-library.html',baseUrl);
  url.search='';
  url.searchParams.set('q','id:'+record.id);
  url.searchParams.set('sl-record',record.id);
  url.searchParams.set('sl-formula',String(variantIndex));
  url.searchParams.set('sl-start',String(startIndex));
  url.hash='sl-results';
  return url.href;
}

/** Invalid or stale state fails closed without applying the wrong formula or window. */
export function readInspectionLink(rawUrl,record,variantCount) {
  if(!validRecord(record)||!Number.isSafeInteger(variantCount)||variantCount<1)return null;
  try {
    const params=new URL(rawUrl).searchParams;
    const single=key=>params.getAll(key).length===1;
    if(!single('q')||params.get('q')!=='id:'+record.id||
      !single('sl-record')||params.get('sl-record')!==record.id||
      !single('sl-formula')||!single('sl-start')||
      (params.has('scope')&&(!single('scope')||params.get('scope')!=='records')))return null;
    const variantIndex=readUnsigned(params.get('sl-formula'));
    const startIndex=readUnsigned(params.get('sl-start'));
    if(variantIndex===null||variantIndex>=variantCount||
      startIndex===null||!validStart(record,startIndex))return null;
    return {variantIndex,startPosition:startIndex-record.offset};
  }catch{return null;}
}
