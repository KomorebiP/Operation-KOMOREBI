// Read only requested Lean sources from the site's existing, checksum-bound ZIP.
// No archive paths are extracted to the host or used as worker filesystem paths.
const MAX_BUNDLE=64*1024*1024,MAX_SOURCE=4*1024*1024;
const utf8=new TextDecoder('utf-8',{fatal:true});
export async function sha256(bytes) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
}
function safePath(path) {
  if(typeof path!=='string'||!path||/[\\:\x00-\x1f]/.test(path)||path.split('/').some(p=>!p||p==='.'||p==='..'))throw new Error('Invalid source path.');
  return path;
}
export function zipDirectory(bytes) {
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  let end=-1;
  for(let p=bytes.length-22;p>=Math.max(0,bytes.length-65557);p--) {
    if(view.getUint32(p,true)===0x06054b50&&p+22+view.getUint16(p+20,true)===bytes.length){end=p;break;}
  }
  if(end<0||view.getUint16(end+4,true)||view.getUint16(end+6,true))throw new Error('Unsupported source archive.');
  const count=view.getUint16(end+10,true),length=view.getUint32(end+12,true),start=view.getUint32(end+16,true);
  if(count===65535||count>20000||start+length!==end||view.getUint16(end+8,true)!==count)throw new Error('Invalid source archive directory.');
  const entries=new Map();let p=start;
  for(let i=0;i<count;i++) {
    if(p+46>end||view.getUint32(p,true)!==0x02014b50)throw new Error('Invalid source archive entry.');
    const flags=view.getUint16(p+8,true),method=view.getUint16(p+10,true),compressed=view.getUint32(p+20,true),size=view.getUint32(p+24,true);
    const names=view.getUint16(p+28,true),extra=view.getUint16(p+30,true),comment=view.getUint16(p+32,true),offset=view.getUint32(p+42,true);
    if(p+46+names+extra+comment>end||flags&1||![0,8].includes(method))throw new Error('Unsupported source archive entry.');
    const name=safePath(utf8.decode(bytes.subarray(p+46,p+46+names)));
    if(entries.has(name))throw new Error('Duplicate source archive path.');
    entries.set(name,{offset,compressed,size,method});p+=46+names+extra+comment;
  }
  if(p!==end)throw new Error('Invalid source archive directory length.');
  return entries;
}
export async function readZipSource(bytes,entries,path,expected) {
  const entry=entries.get('inputs/'+safePath(path));
  if(!entry||entry.size!==expected.size||entry.size>MAX_SOURCE)throw new Error('Source is missing or exceeds the browser limit: '+path);
  const v=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength),p=entry.offset;
  if(p+30>bytes.length||v.getUint32(p,true)!==0x04034b50||v.getUint16(p+8,true)!==entry.method)throw new Error('Invalid source archive header.');
  const start=p+30+v.getUint16(p+26,true)+v.getUint16(p+28,true);
  if(start+entry.compressed>bytes.length)throw new Error('Truncated source archive.');
  let raw=bytes.slice(start,start+entry.compressed);
  if(entry.method===8) {
    const reader=new Blob([raw]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();
    const chunks=[];let length=0;
    for(;;){const {value,done}=await reader.read();if(done)break;length+=value.length;if(length>entry.size){await reader.cancel();throw new Error('Invalid expanded source length.');}chunks.push(value);}
    raw=new Uint8Array(length);let offset=0;for(const chunk of chunks){raw.set(chunk,offset);offset+=chunk.length;}
  }
  if(raw.length!==expected.size||await sha256(raw)!==expected.sha256)throw new Error('Retained source checksum mismatch: '+path);
  return raw;
}
let cachedBundle;
export async function loadSourceBundle(record,{signal,onProgress=()=>{}}={}) {
  signal?.throwIfAborted();
  if(!record||!Number.isInteger(record.size)||record.size<1||record.size>MAX_BUNDLE)throw new Error('Invalid source bundle record.');
  if(cachedBundle?.sha===record.sha256)return cachedBundle.value;
  const url=new URL(record.url,location.href);
  if(url.origin!==location.origin)throw new Error('Source bundle must come from this site.');
  onProgress('Downloading the retained source bundle…');
  const response=await fetch(url,{signal,cache:'no-cache',credentials:'omit'});
  if(!response.ok)throw new Error('Source bundle download failed: HTTP '+response.status);
  const bytes=new Uint8Array(await response.arrayBuffer());
  if(bytes.length!==record.size||await sha256(bytes)!==record.sha256)throw new Error('Source bundle checksum mismatch. Reload the page and try again.');
  signal?.throwIfAborted();
  const value={bytes,entries:zipDirectory(bytes)};cachedBundle={sha:record.sha256,value};return value;
}
export async function sourceWorkspace(catalog,entry,bundle,{signal}={}) {
  const files=[];
  for(const module of entry.library||[]) {
    signal?.throwIfAborted();
    const record=catalog.librarySources?.[module];
    if(!record||record.module!==module||record.path!==module.replaceAll('.','/')+'.lean'||record.revision!==catalog.mathlibRevision||!/^Mathlib(?:\.[A-Za-z_][A-Za-z_0-9]*)+$/.test(module)||!/^[0-9a-f]{40}$/.test(record.revision)||record.url!=='https://github.com/leanprover-community/mathlib4/blob/'+record.revision+'/'+record.path)throw new Error('Invalid pinned library source record.');
    if(record.syntaxCheck!==undefined&&record.syntaxCheck!=='frontend')throw new Error('Unsupported library source syntax check: '+module);
    const bytes=new TextEncoder().encode(record.source);
    if(bytes.length!==record.size||bytes.length>MAX_SOURCE||await sha256(bytes)!==record.sha256)throw new Error('Pinned library source checksum mismatch: '+module);
    files.push({module,path:record.path,text:record.source,originalBytes:bytes,sha256:record.sha256,library:true,revision:record.revision,inspect:record.url,...(record.syntaxCheck?{syntaxCheck:record.syntaxCheck}:{})});
  }
  if(entry.legacy) {
    const compatibility=catalog.legacy,bytes=new TextEncoder().encode(compatibility.source);
    if(await sha256(bytes)!==compatibility.sha256)throw new Error('Browser compatibility source checksum mismatch.');
    files.push({module:compatibility.module,text:compatibility.source,originalBytes:bytes,sha256:compatibility.sha256,generated:true,inspect:'version-compatibility.lean'});
  }
  if(entry.tactics) {
    const compatibility=catalog.compatibility,bytes=new TextEncoder().encode(compatibility.source);
    if(await sha256(bytes)!==compatibility.sha256)throw new Error('Browser compatibility source checksum mismatch.');
    files.push({module:compatibility.module,text:compatibility.source,originalBytes:bytes,sha256:compatibility.sha256,generated:true,inspect:'tactic-compatibility.lean'});
  }
  const routes=new Map(catalog.entries.map(e=>[e.path,e.inspect]));
  for(const file of entry.files) {
    signal?.throwIfAborted();
    const input=catalog.inputs[file.input];
    if(!input||input.work!==entry.work)throw new Error('Source dependency ownership mismatch.');
    const raw=await readZipSource(bundle.bytes,bundle.entries,input.path,input);
    files.push({module:file.module,path:input.path,sha256:input.sha256,originalBytes:raw,
      text:utf8.decode(raw).replace(/^\uFEFF/,'').replace(/\r\n/g,'\n'),inspect:routes.get(input.path)||null});
  }
  return {id:'source-'+entry.id,title:entry.label+' · '+entry.path.split('/').pop(),work:entry.work,files,
    exploratory:true,issues:entry.issues,library:entry.library||[],tactics:entry.tactics,legacy:entry.legacy?catalog.legacy.module:null};
}
