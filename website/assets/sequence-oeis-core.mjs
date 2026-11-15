import {termPattern,matchTerms,normalizeText} from './sequence-atlas-search.mjs';

export function referenceQuery(value){
  const text=String(value).replace(/\u2212/g,'-').trim();if(!text||text.length>20000)throw Error('Enter an A-number, sequence-name words, or 3–1,000 exact terms.');
  const id=/^a(\d{1,6})$/i.exec(text);if(id)return {type:'id',id:'A'+id[1].padStart(6,'0')};
  if(/^[-+?\d\s,;]+$/.test(text)){const pattern=termPattern(text);if(pattern.length<3)throw Error('Use at least three terms for this full-snapshot comparison.');return {type:'terms',pattern};}
  return {type:'name',words:normalizeText(text).split(' ')};
}
export function referenceValues(line){
  const match=/^(A\d{6})\s+,?(.*?)[,\s]*$/.exec(line);if(!match)return null;
  return {id:match[1],values:match[2].split(',').filter(Boolean).map(raw=>{const negative=raw.startsWith('-'),digits=raw.replace(/^[-+]/,'').replace(/^0+/,'')||'0';return (negative&&digits!=='0'?'-':'')+digits;})};
}
export function referencePositions(values,query){return query.type==='terms'?matchTerms(values,query.pattern):[];}
export function referenceNameMatches(id,name,query){return query.type==='id'?id===query.id:query.type==='name'&&query.words.every(word=>normalizeText(name).includes(word));}
