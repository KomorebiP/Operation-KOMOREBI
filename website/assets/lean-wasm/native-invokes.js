// Replace the pinned Emscripten invoke trampolines with Wasm calls so recursive
// Lean evaluation does not spend a JavaScript stack frame on every invocation.
// Original function indices, table entries, code, and proof inputs are unchanged.
// Unsupported engines or artifact shapes retain the original runtime pair.
const encoder = new TextEncoder();
function uleb(n) { const a=[]; do { let b=n&127;n=Math.floor(n/128);a.push(b|(n?128:0)); } while(n); return a; }
function str(s) { const a=encoder.encode(s);return [...uleb(a.length),...a]; }
function section(id,payload) { return concat([new Uint8Array([id,...uleb(payload.length)]),payload]); }
function concat(parts) { const out=new Uint8Array(parts.reduce((n,p)=>n+p.length,0));let o=0;for(const p of parts){out.set(p,o);o+=p.length;}return out; }
function reader(bytes) {
  let p=0;
  return {get pos(){return p;},set pos(v){p=v;},byte(){if(p>=bytes.length)throw Error('Truncated Wasm');return bytes[p++];},uint(){let n=0,m=1;for(let i=0;i<5;i++){const b=this.byte();n+=(b&127)*m;if(!(b&128))return n;m*=128;}throw Error('Invalid u32');},string(){const n=this.uint(),end=p+n;if(end>bytes.length)throw Error('Truncated name');const s=new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(p,end));p=end;return s;},end(){if(p!==bytes.length)throw Error('Unexpected section bytes');}};
}
function limits(r,table=false) {
  const flags=r.uint();
  if(table && flags>1)throw Error('Unsupported table flags');
  if(!table && flags>3)throw Error('Unsupported memory flags');
  const initial=r.uint(),maximum=flags&1?r.uint():undefined;
  return {flags,initial,...(maximum===undefined?{}:{maximum})};
}
const wasmTypes={i:0x7f,j:0x7e,f:0x7d,d:0x7c};
export function rewriteTableAsImport(bytes) {
  bytes=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes);
  if(bytes.length<8||[0,97,115,109,1,0,0,0].some((v,i)=>bytes[i]!==v))throw Error('Invalid Wasm header');
  const cursor=reader(bytes);cursor.pos=8;const sections=[];let table,tableRaw,imports,types,importCount,startFunction,exportPayload;const signatures=[];
  const startExport='__komorebi_deferred_start';
  while(cursor.pos<bytes.length){const id=cursor.byte(),length=cursor.uint(),start=cursor.pos,end=start+length;if(end>bytes.length)throw Error('Truncated section');const payload=bytes.subarray(start,end);sections.push({id,payload});cursor.pos=end;
    if(id===1){const r=reader(payload),count=r.uint();types=[];for(let i=0;i<count;i++){if(r.byte()!==0x60)throw Error('Unsupported function type');const params=Array.from({length:r.uint()},()=>r.byte()),results=Array.from({length:r.uint()},()=>r.byte());types.push({params,results});}r.end();}
    if(id===2){imports=payload;const r=reader(payload);importCount=r.uint();for(let i=0;i<importCount;i++){const module=r.string(),name=r.string(),kind=r.byte();if(kind===0){const type=r.uint();if(name.startsWith('invoke_')){if(module!=='env'||!/^invoke_[vijfd][ijfd]*$/.test(name))throw Error('Unsupported invoke import');signatures.push({name,type});}}else if(kind===1)throw Error('Artifact already imports a table');else if(kind===2)limits(r);else if(kind===3){r.byte();r.byte();}else if(kind===4){if(r.byte()!==0)throw Error('Unsupported tag');r.uint();}else throw Error('Unsupported import kind');if(name==='__komorebi_native_table')throw Error('Reserved table name');}r.end();}
    if(id===4){const r=reader(payload);if(r.uint()!==1||r.byte()!==0x70)throw Error('Expected one funcref table');const before=1;tableRaw=payload.subarray(before);table=limits(r,true);r.end();}
    if(id===7){exportPayload=payload;const r=reader(payload),count=r.uint();for(let i=0;i<count;i++){if(r.string()===startExport)throw Error('Reserved start export');r.byte();r.uint();}r.end();}
    if(id===8){const r=reader(payload);startFunction=r.uint();r.end();}
  }
  if(!table||!imports||!types||!signatures.length)throw Error('Missing pinned artifact structures');
  for(const {name,type} of signatures){const sig=name.slice(7),expected={params:[0x7f,...Array.from(sig.slice(1),x=>wasmTypes[x])],results:sig[0]==='v'?[]:[wasmTypes[sig[0]]]};if(JSON.stringify(types[type])!==JSON.stringify(expected))throw Error('Invoke signature mismatch: '+name);}
  const oldCount=reader(imports);oldCount.uint();
  const extra=[...str('env'),...str('__komorebi_native_table'),1,...tableRaw];
  const newImports=concat([new Uint8Array(uleb(importCount+1)),imports.subarray(oldCount.pos),new Uint8Array(extra)]);
  let newExports=exportPayload;
  if(startFunction!==undefined){
    if(!exportPayload)throw Error('Expected export section for deferred start');
    const r=reader(exportPayload),count=r.uint();
    newExports=concat([new Uint8Array(uleb(count+1)),exportPayload.subarray(r.pos),new Uint8Array([...str(startExport),0,...uleb(startFunction)])]);
  }
  const output=concat([bytes.subarray(0,8),...sections.filter(s=>s.id!==4&&s.id!==8).map(s=>section(s.id,s.id===2?newImports:s.id===7?newExports:s.payload))]);
  // Compile validates section ordering, table bounds, and unchanged reference indices.
  new WebAssembly.Module(output);
  return {bytes:output,descriptor:{table,signatures:signatures.map(s=>s.name),...(startFunction===undefined?{}:{startExport})}};
}

// This factory is self-contained so the same source can be embedded in every
// pthread's patched Emscripten glue. Each thread gets its own corresponding table.
export function createNativeInvokeContext(descriptor) {
  if(typeof WebAssembly.Tag!=='function'||!(WebAssembly.JSTag instanceof WebAssembly.Tag))throw Error('Native JavaScript exception tags unavailable');
  function u(n){const a=[];do{const b=n&127;n=Math.floor(n/128);a.push(b|(n?128:0));}while(n);return a;}
  function text(s){const b=new TextEncoder().encode(s);return [...u(b.length),...b];}
  function sec(id,a){return [id,...u(a.length),...a];}
  const T={i:0x7f,j:0x7e,f:0x7d,d:0x7c};const types=[];
  function type(params,results){const key=JSON.stringify([params,results]);let i=types.findIndex(t=>t.key===key);if(i<0){i=types.length;types.push({key,bytes:[0x60,...u(params.length),...params,...u(results.length),...results]});}return i;}
  const saveType=type([], [T.i]),restoreType=type([T.i],[]),threwType=type([T.i,T.i],[]),exceptionType=type([0x6f],[]);
  const functionTypes=[],exports=[],bodies=[];
  descriptor.signatures.forEach((name,index)=>{
    if(!/^invoke_[vijfd][ijfd]*$/.test(name))throw Error('Unsupported invoke signature');
    const sig=name.slice(7),result=sig[0]==='v'?[]:[T[sig[0]]],params=Array.from(sig.slice(1),s=>T[s]),allParams=[T.i,...params];
    const calleeType=type(params,result),invokeType=type(allParams,result),saved=allParams.length;
    functionTypes.push(invokeType);exports.push([...text(name),0,...u(index+1)]);
    const body=[1,1,T.i, // One i32 local for the saved Emscripten linear-memory stack.
      0x23,0,0x11,...u(saveType),0,0x21,...u(saved),
      0x06,...(result.length?result:[0x40])]; // try (result ...)
    params.forEach((_,i)=>body.push(0x20,...u(i+1)));
    body.push(0x20,0,0x11,...u(calleeType),0,
      0x07,0, // Ordinary JS throws, including Emscripten numeric C++ pointers.
      0x20,...u(saved),0x23,1,0x11,...u(restoreType),0,
      0x10,0, // JS only on exceptions: rethrow anything except numeric C++ pointer.
      0x41,1,0x41,0,0x23,2,0x11,...u(threwType),0);
    if(sig[0]==='i')body.push(0x41,0);
    else if(sig[0]==='j')body.push(0x42,0);
    else if(sig[0]==='f')body.push(0x43,0,0,0xc0,0x7f); // Undefined coerces to NaN.
    else if(sig[0]==='d')body.push(0x44,0,0,0,0,0,0,0xf8,0x7f);
    // Native tagged exceptions also restore the linear-memory stack and keep
    // their original tag/payload. Wasm traps are uncatchable and must terminate
    // the runtime; worker.js marks escaped compile exceptions as fatal.
    body.push(0x19, 0x20,...u(saved),0x23,1,0x11,...u(restoreType),0,0x09,0, 0x0b,0x0b);bodies.push([...u(body.length),...body]);
  });
  const {initial,maximum}=descriptor.table;
  if(maximum!==undefined&&maximum<initial+3)throw Error('Wasm table cannot reserve three native helper slots');
  const table=new WebAssembly.Table({element:'anyfunc',initial,...(maximum===undefined?{}:{maximum})});
  const slots=Array.from({length:3},()=>new WebAssembly.Global({value:'i32',mutable:true},-1));
  const imports=[
    [...text('env'),...text('table'),1,0x70,0,...u(initial)],
    [...text('env'),...text('save'),3,0x7f,1],
    [...text('env'),...text('restore'),3,0x7f,1],
    [...text('env'),...text('setThrew'),3,0x7f,1],
    [...text('env'),...text('jsException'),0,...u(exceptionType)],
    [...text('env'),...text('JSTag'),4,0,...u(exceptionType)]
  ];
  const binary=new Uint8Array([0,97,115,109,1,0,0,0,
    ...sec(1,[...u(types.length),...types.flatMap(t=>t.bytes)]),
    ...sec(2,[...u(imports.length),...imports.flat()]),
    ...sec(3,[...u(functionTypes.length),...functionTypes.flatMap(u)]),
    ...sec(7,[...u(exports.length),...exports.flat()]),
    ...sec(10,[...u(bodies.length),...bodies.flat()])]);
  const instance=new WebAssembly.Instance(new WebAssembly.Module(binary),{env:{table,save:slots[0],restore:slots[1],setThrew:slots[2],JSTag:WebAssembly.JSTag,jsException(e){if(e!==e+0)throw e;}}});
  let bound=false;
  return {table,invokes:instance.exports,shimBytes:binary,
    bind(exports){
      if(bound)throw Error('Native invoke helpers already bound');
      if(exports.__indirect_function_table!==table)throw Error('Native invoke table mismatch');
      const names=['emscripten_stack_get_current','_emscripten_stack_restore','setThrew'];
      const functions=names.map(name=>{if(typeof exports[name]!=='function')throw Error('Missing native stack helper '+name);return exports[name];});
      const start=table.grow(3);functions.forEach((f,i)=>{table.set(start+i,f);slots[i].value=start+i;});bound=true;
      // Preserve the original start's execution before all Emscripten receive
      // side effects, but after invoke imports can access native stack helpers.
      if(descriptor.startExport){if(typeof exports[descriptor.startExport]!=='function')throw Error('Missing deferred Wasm start');exports[descriptor.startExport]();}
    }
  };
}

export function patchLeanGlue(source,descriptor) {
  const get='function getWasmImports(){assignWasmImports();';
  const receive='function receiveInstance(instance,module){wasmExports=instance.exports;';
  if(source.split(get).length!==2||source.split(receive).length!==2)throw Error('Pinned Emscripten glue shape changed');
  // The exceptional return coercion must match this exact Emscripten artifact.
  // In particular its i64 wrappers explicitly return 0n; float wrappers return
  // undefined, which the original Wasm import conversion turns into NaN.
  for(const name of descriptor.signatures){
    const sig=name.slice(7),args=Array.from({length:sig.length-1},(_,i)=>'a'+(i+1));
    const wrapper='function '+name+'('+['index',...args].join(',')+'){var sp=stackSave();try{'+(sig[0]==='v'?'':'return ')+'getWasmTableEntry(index)('+args.join(',')+')}catch(e){stackRestore(sp);if(e!==e+0)throw e;_setThrew(1,0)'+(sig[0]==='j'?';return 0n':'')+'}}';
    if(source.split(wrapper).length!==2)throw Error('Pinned invoke wrapper changed: '+name);
  }
  const prelude='var __komorebiNativeInvokeContext;var __komorebiNativeInvokeDescriptor='+JSON.stringify(descriptor)+';var __komorebiCreateNativeInvoke='+createNativeInvokeContext.toString()+';\n';
  return prelude+source.replace(get,get+'__komorebiNativeInvokeContext??=__komorebiCreateNativeInvoke(__komorebiNativeInvokeDescriptor);Object.assign(wasmImports,__komorebiNativeInvokeContext.invokes);wasmImports.__komorebi_native_table=__komorebiNativeInvokeContext.table;')
    .replace(receive,receive+'__komorebiNativeInvokeContext.bind(wasmExports);');
}

// Treat the original verified script and Wasm as one indivisible pair. Call
// before allocating either runtime Blob URL. Unsupported engines/artifacts
// retain the complete original pair and explicitly report the reason.
export function prepareNativeInvokePair(source,bytes) {
  try {
    if(typeof WebAssembly.Tag!=='function'||!(WebAssembly.JSTag instanceof WebAssembly.Tag))throw Error('Native JavaScript exception tags unavailable');
    const rewritten=rewriteTableAsImport(bytes);
    const patched=patchLeanGlue(source,rewritten.descriptor);
    // This validates the engine's EH support and table limits before committing.
    createNativeInvokeContext(rewritten.descriptor);
    return {source:patched,bytes:rewritten.bytes,applied:true,descriptor:rewritten.descriptor};
  } catch(error) {
    return {source,bytes,applied:false,reason:String(error?.message||error)};
  }
}
