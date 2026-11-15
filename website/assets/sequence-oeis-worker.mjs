import {referenceQuery,referenceValues,referencePositions,referenceNameMatches} from './sequence-oeis-core.mjs';

const cache=new Map();
const versions={'stripped.gz':'__OEIS_TERMS_SHA256__','names.gz':'__OEIS_NAMES_SHA256__'};
async function bulk(name){
  if(cache.has(name))return cache.get(name);
  const promise=(async()=>{const response=await fetch(new URL('./oeis/'+name+'?v='+versions[name],import.meta.url));if(!response.ok)throw Error('The reference snapshot could not be downloaded. Try again or use its download links.');const reader=response.body.getReader(),chunks=[];let bytes=0,nextNotice=2*1048576;while(true){const part=await reader.read();if(part.done)break;bytes+=part.value.byteLength;if(bytes>50*1024*1024)throw Error('Reference file exceeded the 50 MiB compressed-file cap.');chunks.push(part.value);if(bytes>=nextNotice){nextNotice=bytes+2*1048576;self.postMessage({type:'progress',message:`Loading ${name}: ${(bytes/1048576).toFixed(1)} MiB received.`});}}return new Uint8Array(await new Blob(chunks).arrayBuffer());})();cache.set(name,promise);try{return await promise;}catch(error){cache.delete(name);throw error;}
}
async function* lines(bytes){
  let stream=new Blob([bytes]).stream();if(bytes[0]===31&&bytes[1]===139){if(typeof DecompressionStream!=='function')throw Error('This browser cannot unpack the snapshot. Download the files for local use or try a browser with gzip stream support.');stream=stream.pipeThrough(new DecompressionStream('gzip'));}
  const reader=stream.pipeThrough(new TextDecoderStream()).getReader();let carry='';
  try{while(true){const part=await reader.read();if(part.done)break;const chunks=(carry+part.value).split('\n');carry=chunks.pop();for(const line of chunks)if(line&&!line.startsWith('#'))yield line.trimEnd();}if(carry&&!carry.startsWith('#'))yield carry.trimEnd();}finally{reader.releaseLock();}
}
self.onmessage=async event=>{
  if(event.data.type!=='search')return;
  try{
    const query=referenceQuery(event.data.query),[stripped,names]=await Promise.all([bulk('stripped.gz'),bulk('names.gz')]);
    const results=[],wanted=new Map();let total=0,scanned=0,positions=0;
    if(query.type==='terms'){
      for await(const line of lines(stripped)){const row=referenceValues(line);if(!row)continue;scanned++;const at=referencePositions(row.values,query);if(at.length){total++;positions+=at.length;if(results.length<50){const start=Math.max(0,at[0]-2),hit={id:row.id,position:at[0],positions:at.length,sample_position:start,values:row.values.slice(start,start+Math.min(64,query.pattern.length+4)),matched_terms:query.pattern.length,known_terms:query.pattern.filter(v=>v!==null).length};results.push(hit);wanted.set(row.id,hit);}}if(scanned%16384===0)self.postMessage({type:'progress',message:`Compared ${scanned.toLocaleString()} OEIS records…`});}
      for await(const line of lines(names)){const space=line.indexOf(' '),id=line.slice(0,space);if(wanted.has(id))wanted.get(id).name=line.slice(space+1);}
    }else{
      for await(const line of lines(names)){const space=line.indexOf(' '),id=line.slice(0,space),name=line.slice(space+1);if(referenceNameMatches(id,name,query)){total++;if(results.length<50){const hit={id,name,position:null};results.push(hit);wanted.set(id,hit);}}}
      for await(const line of lines(stripped)){const id=line.slice(0,7);if(wanted.has(id)){const row=referenceValues(line);Object.assign(wanted.get(id),{values:row.values.slice(0,32),sample_position:0});}}
    }
    self.postMessage({type:'results',results,total,positions,scanned,query_type:query.type});
  }catch(error){self.postMessage({type:'error',message:error.message});}
};
