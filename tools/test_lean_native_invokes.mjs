import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {
  rewriteTableAsImport, createNativeInvokeContext, prepareNativeInvokePair
} from '../website/assets/lean-wasm/native-invokes.js';
import {createRuntime} from '../website/assets/lean-wasm/runtime.js';

// Tiny Wasm fixtures; this suite needs no downloaded Lean artifact or libraries.
const I=0x7f, T={i:0x7f,j:0x7e,f:0x7d,d:0x7c};
const signatures=[
  'vi','iii','ii','vii','viii','iiii','v','viiii','viiiiii','iiiii','viiiii','i',
  'iiiiii','viiiiiii','iiiiiii','iiiiiiiiiii','iiiiiiiiiiiii','iiij','viiiiiiiiii',
  'iiiiiiiiiiii','vj','viiiiiiii','viiiiiiiiiiiiiii','jiiii','iiiiiiii','j','diii',
  'fiii','vid','iiiiiiiiii','iiiiiiiii','iid','iiiiid','viid','viif','iif','jiji','di','viij'
].map(s=>'invoke_'+s);
function u(n){const out=[];do{const b=n&127;n>>>=7;out.push(b|(n?128:0));}while(n);return out;}
const string=s=>{const b=new TextEncoder().encode(s);return [...u(b.length),...b];};
const section=(id,b)=>[id,...u(b.length),...b];
const type=(p,r)=>[0x60,...u(p.length),...p,...u(r.length),...r];
const body=b=>[...u(b.length+2),0,...b,0x0b];
const binary=(...sections)=>new Uint8Array([0,97,115,109,1,0,0,0,...sections.flat()]);

function fixture({start=false,maximum}={}){
  const types=[type([I],[I]),type([I,I],[I]),type([],[I]),type([I],[]),type([I,I],[]),type([],[])];
  const exports=[['recurse',0,2],['emscripten_stack_get_current',0,3],['_emscripten_stack_restore',0,4],['setThrew',0,5],['__indirect_function_table',1,0],['threw',3,1],['stack',3,0],['started',3,2]];
  const recurse=[0x20,0,0x45,0x04,I,0x41,42,0x05,0x20,0,0x41,1,0x46,0x04,I,0x10,1,0x05,0x41,0,0x20,0,0x41,1,0x6b,0x10,0,0x0b,0x0b];
  return binary(
    section(1,[types.length,...types.flat()]),
    section(2,[2,...string('env'),...string('invoke_ii'),0,1,...string('env'),...string('thrower'),0,2]),
    section(3,start?[5,0,2,3,4,5]:[4,0,2,3,4]),
    section(4,[1,0x70,...(maximum===undefined?[0,1]:[1,1,...u(maximum)])]),
    section(6,[3,I,1,0x41,23,0x0b,I,1,0x41,0,0x0b,I,1,0x41,0,0x0b]),
    section(7,[exports.length,...exports.flatMap(([n,k,i])=>[...string(n),k,i])]),
    start?section(8,[6]):[],
    section(9,[1,0,0x41,0,0x0b,1,2]),
    section(10,[start?5:4,...body(recurse),...body([0x23,0]),...body([0x20,0,0x24,0]),...body([0x20,0,0x24,1]),...(start?body([0x41,0,0x41,20,0x10,0,0x1a,0x41,1,0x24,2]):[])])
  );
}

function instantiateFixture(options={}){
  const rewritten=rewriteTableAsImport(fixture(options));
  const context=createNativeInvokeContext(rewritten.descriptor);
  const instance=new WebAssembly.Instance(new WebAssembly.Module(rewritten.bytes),{env:{__komorebi_native_table:context.table,...context.invokes,thrower:()=>42}});
  return {rewritten,context,instance};
}

function targetFunction(signature,stack,behavior,host,tag){
  const params=Array.from(signature.slice(1),s=>T[s]),results=signature[0]==='v'?[]:[T[signature[0]]];
  const imports=[...string('env'),...string('stack'),3,I,1];
  const code=[0x41,31,0x24,0]; // Deliberately change the linear-memory stack.
  if(behavior==='host'){
    imports.push(...string('env'),...string('host'),0,0);
    code.push(...params.flatMap((_,i)=>[0x20,...u(i)]),0x10,0);
  }else if(behavior==='native'){
    imports.push(...string('env'),...string('tag'),4,0,1);
    code.push(0x41,37,0x08,0);
  }else code.push(0x00); // Unreachable: native traps must never look successful.
  const bytes=binary(
    section(1,[2,...type(params,results),...type([I],[])]),
    section(2,[behavior==='trap'?1:2,...imports]),
    section(3,[1,0]),
    section(7,[1,...string('target'),0,behavior==='host'?1:0]),
    section(10,[1,...body(code)])
  );
  return new WebAssembly.Instance(new WebAssembly.Module(bytes),{env:{stack,host,tag}}).exports.target;
}

function glue(){
  return 'var wasmImports,wasmExports;function assignWasmImports(){wasmImports={invoke_ii,thrower:()=>42};}'
    +'function getWasmImports(){assignWasmImports();return {env:wasmImports};}'
    +'function receiveInstance(instance,module){wasmExports=instance.exports;return wasmExports;}'
    +'function invoke_ii(index,a1){var sp=stackSave();try{return getWasmTableEntry(index)(a1)}catch(e){stackRestore(sp);if(e!==e+0)throw e;_setThrew(1,0)}}';
}

test('native invoke tests run on an engine with JavaScript exception tags',()=>{
  assert.ok(WebAssembly.JSTag instanceof WebAssembly.Tag,'Run these fixtures with Node 24 or another JSTag-capable engine.');
});

test('rewritten module keeps recursion and runs its start exactly once after helpers bind',()=>{
  const {rewritten,context,instance}=instantiateFixture({start:true});
  assert.equal(instance.exports.started.value,0);
  context.bind(instance.exports);
  assert.equal(instance.exports.started.value,1);
  assert.equal(instance.exports.recurse(300),42);
  assert.equal(context.table.get(0),instance.exports.recurse);
  assert.equal(context.table.length,4);
  assert.equal(context.table.get(1),instance.exports.emscripten_stack_get_current);
  assert.throws(()=>context.bind(instance.exports),/already bound/);
  // Like a pthread: the same compiled artifact gets its own table and helpers.
  const other=createNativeInvokeContext(rewritten.descriptor);
  const second=new WebAssembly.Instance(new WebAssembly.Module(rewritten.bytes),{env:{__komorebi_native_table:other.table,...other.invokes,thrower:()=>42}});
  other.bind(second.exports);
  assert.notEqual(other.table,context.table);
  assert.equal(second.exports.recurse(300),42);
});

test('all 39 pinned signatures preserve values, stack restoration, and exception identity',()=>{
  const {instance}=instantiateFixture();
  const context=createNativeInvokeContext({table:{initial:1},signatures});
  context.bind({...instance.exports,__indirect_function_table:context.table});
  const stack=instance.exports.stack,tag=new WebAssembly.Tag({parameters:['i32']});
  for(const name of signatures){
    const sig=name.slice(7),args=Array.from(sig.slice(1),s=>s==='j'?7n:7);
    const value=sig[0]==='j'?19n:sig[0]==='v'?undefined:1.25;
    let error;
    const target=targetFunction(sig,stack,'host',(...received)=>{assert.deepEqual(received,args);if(error!==undefined)throw error;return value;});
    context.table.set(0,target);
    stack.value=23;
    assert.equal(context.invokes[name](0,...args),sig[0]==='i'?1:value,name);
    assert.equal(stack.value,31,'normal return retains target stack behavior');
    error=17;stack.value=23;instance.exports.threw.value=0;
    const caught=context.invokes[name](0,...args);
    if(sig[0]==='f'||sig[0]==='d')assert.ok(Number.isNaN(caught),name);
    else assert.equal(caught,sig[0]==='j'?0n:sig[0]==='v'?undefined:0,name);
    assert.equal(stack.value,23);assert.equal(instance.exports.threw.value,1);
    for(error of [new Error('identity'),'halt',new WebAssembly.Exception(tag,[91])]){
      stack.value=23;instance.exports.threw.value=0;
      assert.throws(()=>context.invokes[name](0,...args),e=>e===error,name);
      assert.equal(stack.value,23);assert.equal(instance.exports.threw.value,0);
    }
    context.table.set(0,targetFunction(sig,stack,'native',undefined,tag));
    stack.value=23;
    assert.throws(()=>context.invokes[name](0,...args),e=>e.is(tag)&&e.getArg(tag,0)===37,name);
    assert.equal(stack.value,23,'native tagged exception restores the stack');
    context.table.set(0,targetFunction(sig,stack,'trap'));
    stack.value=23;
    assert.throws(()=>context.invokes[name](0,...args),WebAssembly.RuntimeError,name);
    assert.equal(stack.value,31,'traps bypass EH; caller must discard the runtime');
  }
});

test('paired preparation executes patched glue and preserves originals on unsupported input',async()=>{
  const source=glue(),bytes=fixture({start:true}),prepared=prepareNativeInvokePair(source,bytes);
  assert.equal(prepared.applied,true);
  const sandbox=vm.createContext({WebAssembly,TextEncoder,TextDecoder});
  vm.runInContext(prepared.source,sandbox);
  const module=new WebAssembly.Module(prepared.bytes);
  const instance=new WebAssembly.Instance(module,sandbox.getWasmImports());
  sandbox.receiveInstance(instance,module);
  assert.equal(instance.exports.started.value,1);
  assert.equal(instance.exports.recurse(100),42);
  for(const [badSource,badBytes] of [
    [source.replace('function getWasmImports(){','function changed(){'),bytes],
    [source.replace('_setThrew(1,0)','_setThrew(2,0)'),bytes],
    [source,new Uint8Array([0,1,2])],
    [source,fixture({maximum:1})],
    [source,prepared.bytes]
  ]){
    const fallback=prepareNativeInvokePair(badSource,badBytes);
    assert.equal(fallback.applied,false);assert.equal(fallback.source,badSource);assert.equal(fallback.bytes,badBytes);assert.ok(fallback.reason);
  }
  const shim=await readFile(new URL('../website/assets/lean-wasm/native-invokes.js',import.meta.url),'utf8');
  const unsupported=vm.runInNewContext(shim.replace(/^export /gm,'')+'\nprepareNativeInvokePair',{WebAssembly:{},TextEncoder,TextDecoder});
  const fallback=unsupported(source,bytes);
  assert.equal(fallback.applied,false);assert.equal(fallback.bytes,bytes);assert.equal(fallback.source,source);
  assert.match(fallback.reason,/exception tags unavailable/);
});

test('worker distinguishes fatal escaped exceptions from retryable Lean IO errors',async()=>{
  const worker=await readFile(new URL('../website/assets/lean-wasm/worker.js',import.meta.url),'utf8');
  const start=worker.indexOf('function compileCode('),end=worker.indexOf('\n/**',start);
  const sandbox=vm.createContext({performance,mkLeanString:()=>0,Module:{_lean_wasm_compile:()=>0,getValue:()=>1,_lean_io_result_show_error(){}}});
  vm.runInContext('let moduleReady=true,compileBusy=false;'+worker.slice(start,end),sandbox);
  const io=sandbox.compileCode('bad import');assert.equal(io.success,false);assert.equal(io.fatal,undefined);
  sandbox.Module.getValue=()=>0;assert.equal(sandbox.compileCode('fixed import').success,true);
  sandbox.Module._lean_wasm_compile=()=>{throw new WebAssembly.RuntimeError('trap');};
  const fatal=sandbox.compileCode('trap');assert.equal(fatal.success,false);assert.equal(fatal.fatal,true);assert.equal(fatal.error,'trap');
  assert.match(sandbox.compileCode('cannot reuse').error,/not ready/);
});

test('runtime disposes a fatal worker before returning and permits retryable IO results',async()=>{
  const previous=globalThis.Worker,workers=[];
  class FakeWorker {
    constructor(){this.terminated=false;workers.push(this);}
    terminate(){this.terminated=true;}
    postMessage(message){
      const response=message.type==='start'?{type:'ready'}:{type:'result',id:message.id,success:message.code==='good',...(message.code==='fatal'?{fatal:true,error:'trap'}:{})};
      queueMicrotask(()=>this.onmessage({data:response}));
    }
  }
  globalThis.Worker=FakeWorker;
  const fatal=createRuntime({}),retry=createRuntime({});
  try {
    await fatal.start();const result=await fatal.compile('fatal');
    assert.equal(result.fatal,true);assert.equal(workers[0].terminated,true);
    await assert.rejects(fatal.compile('good'),/not running/);
    await retry.start();assert.equal((await retry.compile('IO error')).success,false);
    assert.equal(workers[1].terminated,false);assert.equal((await retry.compile('good')).success,true);
  } finally {
    fatal.dispose();retry.dispose();if(previous===undefined)delete globalThis.Worker;else globalThis.Worker=previous;
  }
});
