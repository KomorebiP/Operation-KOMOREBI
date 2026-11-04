/* Static-site isolation, following the MIT coi-serviceworker approach:
 * https://github.com/gzuidhof/coi-serviceworker (Guido Zuidhof and contributors).
 * Installed only under lean/browser/. It never stores reader proof text.
 */
'use strict';
const CACHE = 'komorebi-lean-62b6a229-v2';
const PREFIX = 'komorebi-lean-';
const engine = new URL('engine/', self.registration.scope);
let manifest;
const MAX_TRANSFER_BYTES = 1024 * 1024;
const MAX_TRANSFER_TASKS = 8;
const transferIndexes = new WeakMap(), transferPending = new Map(), transferFailed = new Set(), transferVolatile = new Map();
let transferSerial = 0, transferEpoch = 0, transferActive = 0;
const transferWaiters = [];

function artifactPath(path) {
  return typeof path === 'string' && !/[\\:\x00-\x1f]/.test(path) && path.split('/').every(p => p && p !== '.' && p !== '..') &&
    (/^lean-mathlib\/(?:modules|proof-path-modules)\/[0-9a-f]{64}\.pack$/.test(path) || path.startsWith('loose/') && path.endsWith('.gz'));
}
function transferIndex(source) {
  if (transferIndexes.has(source)) return transferIndexes.get(source);
  let index = null;
  try {
    const plan = source.transfer_groups;
    if (plan?.schema !== 1 || plan.max_bytes !== MAX_TRANSFER_BYTES || !Array.isArray(plan.groups) || plan.groups.length > 128) throw Error('No bounded transfer plan');
    index = new Map(); const files = new Set(), serial = ++transferSerial;
    for (const item of plan.groups) {
      const record = source.remote_files?.[item.file];
      if (!/^transfers\/[0-9a-f]{64}\.bundle$/.test(item.file) || files.has(item.file) ||
          !record || !/^[0-9a-f]{64}$/.test(record.sha256) || item.file !== `transfers/${record.sha256}.bundle` ||
          !Number.isSafeInteger(record.size) || record.size < 1 || record.size > MAX_TRANSFER_BYTES ||
          !/^https:\/\/raw\.githubusercontent\.com\/KomorebiP\/Operation-KOMOREBI\/[0-9a-f]{40}\/lean-transfer-bundles\/[0-9a-f]{64}\.bundle$/.test(record.url) ||
          !Array.isArray(item.members) || item.members.length < 2 || item.members.length > 1024) throw Error('Invalid transfer');
      const group = {key:`${serial}:${item.file}`,file:item.file,record,members:[]}; let offset = 0;
      for (const path of item.members) {
        const member = source.remote_files?.[path];
        if (!artifactPath(path) || source.files?.[path] || index.has(path) || !member ||
            !/^[0-9a-f]{64}$/.test(member.sha256) || !Number.isSafeInteger(member.size) || member.size < 1 ||
            offset + member.size > record.size || index.size >= 1024) throw Error('Invalid transfer member');
        const entry = {path,record:member,offset,group}; group.members.push(entry); index.set(path,entry); offset += member.size;
      }
      if (offset !== record.size) throw Error('Invalid transfer length'); files.add(item.file);
    }
  } catch { index = null; }
  transferIndexes.set(source,index); return index;
}
async function cachedAsset(cache,key) {
  try { return await cache?.match(key); } catch { return undefined; }
}
function artifactKey(path,record) { return new Request(new URL(path+'?sha256='+record.sha256,engine)); }
async function transferSlot(work) {
  if (transferActive >= 2) await new Promise(resolve => transferWaiters.push(resolve));
  else transferActive++;
  try { return await work(); }
  finally { const next = transferWaiters.shift(); if (next) next(); else transferActive--; }
}
async function exactTransfer(response,size) {
  const reader = response.body?.getReader(); if (!reader) throw Error('Empty transfer');
  const bytes = new Uint8Array(size); let offset = 0;
  try {
    for (;;) {
      const {done,value} = await reader.read(); if (done) break;
      if (offset + value.byteLength > size) throw Error('Oversized transfer');
      bytes.set(value,offset); offset += value.byteLength;
    }
    if (offset !== size) throw Error('Truncated transfer');
    return bytes;
  } catch (error) { try { await reader.cancel(); } catch {} throw error; }
}
async function digest(bytes) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)), b => b.toString(16).padStart(2,'0')).join('');
}
async function transferBytes(group,cache) {
  if (transferFailed.has(group.key)) return null;
  if (transferVolatile.has(group.key)) {
    const bytes = transferVolatile.get(group.key); transferVolatile.delete(group.key); transferVolatile.set(group.key,bytes); return bytes;
  }
  if (transferPending.has(group.key)) return transferPending.get(group.key);
  if (transferPending.size >= MAX_TRANSFER_TASKS) return null;
  const epoch = transferEpoch;
  const task = (async () => {
    const present = await Promise.all(group.members.map(m => cachedAsset(cache,artifactKey(m.path,m.record))));
    let missing = 0, missingBytes = 0;
    present.forEach((response,i) => { if (!response) {missing++; missingBytes += group.members[i].record.size;} });
    // A mostly warm group keeps its individual cache keys and avoids bulk overfetch.
    if (missing < 2 || missingBytes * 2 < group.record.size) return null;
    return transferSlot(async () => {
      const response = await fetch(group.record.url,{credentials:'omit',mode:'cors'});
      if (!response.ok) throw Error('Transfer HTTP '+response.status);
      const bytes = await exactTransfer(response,group.record.size);
      if (await digest(bytes) !== group.record.sha256) throw Error('Transfer checksum mismatch');
      // Check every member before any member is admitted to the shared cache.
      for (const member of group.members) {
        const data = bytes.subarray(member.offset,member.offset+member.record.size);
        if (await digest(data) !== member.record.sha256) throw Error('Transfer member checksum mismatch');
      }
      let retained = !!cache;
      for (const member of group.members) {
        try {
          if (!cache) throw Error('Cache unavailable');
          await cache.put(artifactKey(member.path,member.record),new Response(bytes.subarray(member.offset,member.offset+member.record.size)));
        } catch { retained = false; }
      }
      // Quota failure keeps at most two bounded encoded groups in service-worker
      // memory. This is separate from the compiler worker and stores no proof text.
      if (!retained && epoch === transferEpoch) {
        transferVolatile.set(group.key,bytes);
        while (transferVolatile.size > 2) transferVolatile.delete(transferVolatile.keys().next().value);
      }
      return bytes;
    });
  })().catch(() => { transferFailed.add(group.key); return null; });
  transferPending.set(group.key,task);
  try { return await task; }
  finally { if (transferPending.get(group.key) === task) transferPending.delete(group.key); }
}
self.addEventListener('install', event => event.waitUntil(self.skipWaiting()));
self.addEventListener('activate', event => event.waitUntil((async () => {
  for (const name of await caches.keys()) if (name.startsWith(PREFIX) && name !== CACHE) await caches.delete(name);
  await self.clients.claim();
})()));
function isolated(response) {
  if (!response || response.status === 0) return response;
  const headers = new Headers(response.headers);
  headers.set('Cross-Origin-Opener-Policy', 'same-origin');
  headers.set('Cross-Origin-Embedder-Policy', 'require-corp');
  headers.set('Cross-Origin-Resource-Policy', 'same-origin');
  return new Response(response.body, {status:response.status,statusText:response.statusText,headers});
}
async function responseFor(request) {
  const url = new URL(request.url);
  // A deployment may replace pack bytes. Refresh the record on each navigation;
  // cache keys include its checksums, so older packs cannot satisfy a new record.
  if(request.mode==='navigate') {manifest=null;transferEpoch++;transferVolatile.clear();transferFailed.clear();}
  if (request.method !== 'GET' || url.origin !== engine.origin || !url.pathname.startsWith(engine.pathname)) {
    return isolated(await fetch(request));
  }
  const relative = url.pathname.slice(engine.pathname.length);
  // Absent optional snapshots and plain-file probes remain ordinary 404s.
  manifest ??= fetch(new URL('SOURCE.json',engine), {cache:'no-cache'}).then(async r => {
    if (!r.ok) throw new Error('Compiler download record is unavailable.');
    return r.json();
  }).catch(e => { manifest = null; throw e; });
  const source=await manifest;
  const record = source.files[relative] || source.remote_files?.[relative];
  if (!record) return isolated(await fetch(request));
  let cache; try {cache = await caches.open(CACHE);} catch {}
  const key = artifactKey(relative,record);
  const cached = await cachedAsset(cache,key);
  if (cached) return isolated(cached);
  const member = transferIndex(source)?.get(relative);
  if (member) {
    const bytes = await transferBytes(member.group,cache);
    if (bytes) return isolated(new Response(bytes.subarray(member.offset,member.offset+record.size)));
    const installed = await cachedAsset(cache,key); if (installed) return isolated(installed);
  }
  const response = record.url ? await fetch(record.url,{credentials:'omit',mode:'cors'}) : await fetch(request);
  if (!response.ok) return isolated(response);
  const bytes = await response.clone().arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)), b => b.toString(16).padStart(2,'0')).join('');
  if (bytes.byteLength !== record.size || hash !== record.sha256) throw new Error('Compiler asset checksum mismatch: '+relative);
  // A full browser cache must not prevent proof checking.
  try { await cache?.put(key,response.clone()); } catch { /* continue without a persistent copy */ }
  return isolated(response);
}
self.addEventListener('fetch', event => {
  if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') return;
  event.respondWith(responseFor(event.request).catch(error => new Response(String(error),{status:503})));
});
