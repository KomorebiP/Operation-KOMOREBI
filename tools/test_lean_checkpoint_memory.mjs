import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import vm from 'node:vm';
const source=await readFile(resolve(process.argv[2],'assets/lean-wasm/worker.js'),'utf8');
const start=source.indexOf('const MAX_PAGES = 65536;'),end=source.indexOf('async function gunzip(',start);
assert.ok(start>=0&&end>start);
const pick=source.slice(start,end);
let checks=0;
function trial({initial=1024,maximum=65536,fail=0}={}){
  const calls=[],events=[];
  const context=vm.createContext({declaredMemory:{initial,maximum},post:message=>events.push(message),
    WebAssembly:{Memory:class{
      constructor(options){calls.push({...options});if(calls.length<=fail)throw Error('Injected allocation refusal');}
    }}});
  const result=vm.runInContext(pick+'\npickMemory();',context);
  return {calls,events,result};
}
const normal=trial();
assert.equal(normal.calls.length,1);assert.deepEqual(normal.calls[0],{initial:16384,maximum:65536,shared:true});
assert.equal(normal.result.bytes,1024*1024*1024);checks++;
const fallback=trial({fail:1});
assert.equal(fallback.calls.length,2);assert.equal(fallback.calls[1].initial,12288);
assert.equal(fallback.events.filter(e=>e.type==='memory'&&e.failed).length,1);
assert.equal(fallback.result.bytes,768*1024*1024);checks++;
const refused=trial({fail:2});assert.equal(refused.result,null);assert.equal(refused.calls.length,2);checks++;
const ceiling=trial({maximum:8192});assert.equal(ceiling.result,null);assert.equal(ceiling.calls.length,0);checks++;
const floor=trial({initial:20000});assert.equal(floor.calls[0].initial,20000);assert.equal(floor.result.bytes,20000*65536);checks++;
console.log(JSON.stringify({result:'PASS',checks,scope:'Generated reservation selection using mocked WebAssembly.Memory. No real allocation, peak memory, source execution or growth claim.'}));
