import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import {createHash,webcrypto} from 'node:crypto';

const script=await readFile(new URL('../website/assets/lean-browser-sw.js',import.meta.url),'utf8');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const engine='https://example.test/lean/browser/engine/';
function fixture({groups=1,perGroup=4,quota=false,openFailure=false,delay=false,edit,body}={}) {
  const source={files:{},remote_files:{},transfer_groups:{schema:1,max_bytes:1048576,groups:[]}};
  const raw=new Map(),paths=[],groupURLs=[],stored=new Map(),events={},downloads=[],gates=[];
  let active=0,maxActive=0;
  for(let g=0;g<groups;g++) {
    const members=[],parts=[];
    for(let i=0;i<perGroup;i++) {
      const path=`loose/Batteries/Test${g}_${i}.olean.gz`,bytes=Buffer.from(`original-${g}-${i}-encoded-artifact`);
      const url=`https://raw.githubusercontent.com/live-codes/browser-lean/${'a'.repeat(40)}/public/${path}`;
      source.remote_files[path]={size:bytes.length,sha256:sha(bytes),url};raw.set(url,bytes);members.push(path);parts.push(bytes);
    }
    const bytes=Buffer.concat(parts),digest=sha(bytes),file=`transfers/${digest}.bundle`;
    const url=`https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/${'b'.repeat(40)}/lean-transfer-bundles/${digest}.bundle`;
    source.remote_files[file]={size:bytes.length,sha256:digest,url};raw.set(url,bytes);groupURLs.push(url);
    source.transfer_groups.groups.push({file,members});paths.push([...members]);
  }
  edit?.(source);
  vm.runInNewContext(script,{
    self:{registration:{scope:'https://example.test/lean/browser/'},addEventListener:(name,fn)=>events[name]=fn},
    URL,Request,Response,Headers,crypto:webcrypto,
    caches:{open:async()=>{
      if(openFailure)throw Error('Cache unavailable');
      return {match:async key=>stored.get(key.url)?.clone(),put:async(key,response)=>{
        if(quota)throw Error('Quota exceeded');stored.set(key.url,response.clone());
      }};
    }},
    fetch:async(input,options)=>{
      const url=typeof input==='object'&&input.url?input.url:String(input);
      if(url.endsWith('SOURCE.json'))return Response.json(source);
      if(!raw.has(url))return new Response('',{status:404});
      assert.equal(options.credentials,'omit');assert.equal(options.mode,'cors');downloads.push(url);
      if(groupURLs.includes(url)&&delay){active++;maxActive=Math.max(maxActive,active);await new Promise(resolve=>gates.push(resolve));active--;}
      return new Response(body?.(url,raw.get(url))??raw.get(url));
    }
  });
  const key=path=>engine+path+'?sha256='+source.remote_files[path].sha256;
  async function request(path){let answer;events.fetch({request:new Request(engine+path),respondWith:p=>answer=p});return answer;}
  const seed=path=>stored.set(key(path),new Response(raw.get(source.remote_files[path].url)));
  return {source,raw,paths,groupURLs,stored,downloads,gates,request,seed,key,get maxActive(){return maxActive;}};
}
async function until(check){for(let i=0;i<200&&!check();i++)await new Promise(setImmediate);assert.ok(check(),'condition completed');}

test('one bounded transfer fills unchanged per-file cache keys and verifies every response',async()=>{
  const f=fixture();
  const responses=await Promise.all(f.paths[0].slice(0,2).map(f.request));
  for(let i=0;i<responses.length;i++){
    assert.equal(responses[i].status,200);assert.equal(await responses[i].text(),`original-0-${i}-encoded-artifact`);
    assert.equal(responses[i].headers.get('Cross-Origin-Embedder-Policy'),'require-corp');
  }
  assert.deepEqual(f.downloads,f.groupURLs);
  for(const path of f.paths[0])assert.ok(f.stored.has(f.key(path)));
  await f.request(f.paths[0][3]);assert.equal(f.downloads.length,1);
});

test('a mostly warm group fetches only its one missing member',async()=>{
  const f=fixture();for(const path of f.paths[0].slice(0,3))f.seed(path);
  assert.equal((await f.request(f.paths[0][3])).status,200);
  assert.deepEqual(f.downloads,[f.source.remote_files[f.paths[0][3]].url]);
});

test('few small missing bytes do not trigger a much larger transfer',async()=>{
  const f=fixture({perGroup:5});for(const path of f.paths[0].slice(0,3))f.seed(path);
  await Promise.all(f.paths[0].slice(3).map(f.request));
  assert.equal(f.downloads.filter(url=>f.groupURLs.includes(url)).length,0);assert.equal(f.downloads.length,2);
});

test('legacy records retain direct verified delivery',async()=>{
  const f=fixture({edit:source=>delete source.transfer_groups});const response=await f.request(f.paths[0][0]);
  assert.equal(await response.text(),'original-0-0-encoded-artifact');assert.equal(f.downloads.length,1);
  assert.ok(!f.groupURLs.includes(f.downloads[0]));
});

for(const bad of ['oversize','unknown','duplicate','length','url','code'])test(`invalid ${bad} plan cannot authorize bulk delivery`,async()=>{
  const f=fixture({edit:source=>{
    const group=source.transfer_groups.groups[0],record=source.remote_files[group.file];
    if(bad==='oversize')record.size=1048577;
    if(bad==='unknown')group.members[0]='loose/Missing.gz';
    if(bad==='duplicate')group.members[1]=group.members[0];
    if(bad==='length')record.size++;
    if(bad==='url')record.url='https://example.com/unpinned.bundle';
    if(bad==='code'){source.remote_files['lean-wasm/lean.js']=source.remote_files[group.members[0]];group.members[0]='lean-wasm/lean.js';}
  }});
  assert.equal((await f.request(f.paths[0][0])).status,200);assert.equal(f.downloads.filter(u=>u.endsWith('.bundle')).length,0);
});

for(const bad of ['short','long','checksum'])test(`${bad} bundle falls back once to independently verified files`,async()=>{
  const f=fixture({body:(url,raw)=>url.endsWith('.bundle')?(bad==='short'?raw.subarray(1):bad==='long'?Buffer.concat([raw,Buffer.from('x')]):Buffer.alloc(raw.length)):raw});
  assert.equal(await (await f.request(f.paths[0][0])).text(),'original-0-0-encoded-artifact');
  await f.request(f.paths[0][1]);
  assert.equal(f.downloads.filter(u=>u.endsWith('.bundle')).length,1);
  assert.equal(f.downloads.length,3);
});

test('wrong member ranges cannot enter the cache even with a correct bundle hash',async()=>{
  const f=fixture({edit:source=>source.transfer_groups.groups[0].members.reverse()});
  assert.equal(await (await f.request(f.paths[0][0])).text(),'original-0-0-encoded-artifact');
  assert.equal(f.stored.size,1);assert.ok(f.stored.has(f.key(f.paths[0][0])));
});

test('a forged member checksum cannot be made clean by a valid outer transfer',async()=>{
  const f=fixture({edit:source=>source.remote_files[Object.keys(source.remote_files)[0]].sha256='0'.repeat(64)});
  const response=await f.request(f.paths[0][0]);assert.equal(response.status,503);assert.match(await response.text(),/checksum mismatch/);
  assert.equal(f.stored.size,0);
});

for(const mode of ['quota','openFailure'])test(`${mode} preserves checking with two bounded volatile groups`,async()=>{
  const f=fixture({groups:3,[mode]:true});
  await f.request(f.paths[0][0]);await f.request(f.paths[0][1]);assert.equal(f.downloads.length,1);
  await f.request(f.paths[1][0]);await f.request(f.paths[2][0]);assert.equal(f.downloads.length,3);
  await f.request(f.paths[0][2]);assert.equal(f.downloads.length,4);
});

test('only two group downloads run concurrently and excess work stays bounded',async()=>{
  const f=fixture({groups:3,delay:true});const tasks=f.paths.map(paths=>f.request(paths[0]));
  await until(()=>f.gates.length===2);assert.equal(f.downloads.length,2);assert.equal(f.maxActive,2);
  f.gates.shift()();f.gates.shift()();await until(()=>f.gates.length===1);f.gates.shift()();
  const responses=await Promise.all(tasks);assert.ok(responses.every(r=>r.status===200));assert.equal(f.maxActive,2);
});

test('a full group queue falls back to individual files instead of growing without bound',async()=>{
  const f=fixture({groups:10,perGroup:2,delay:true});const tasks=f.paths.map(paths=>f.request(paths[0]));
  await until(()=>f.downloads.filter(u=>!u.endsWith('.bundle')).length===2);
  let done=false;const all=Promise.all(tasks).finally(()=>{done=true;});
  for(let i=0;i<300&&!done;i++){f.gates.shift()?.();await new Promise(setImmediate);}
  assert.ok(done);assert.ok((await all).every(r=>r.status===200));
  assert.equal(f.downloads.filter(u=>u.endsWith('.bundle')).length,8);assert.equal(f.maxActive,2);
});
