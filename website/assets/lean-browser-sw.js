/* Static-site isolation, following the MIT coi-serviceworker approach:
 * https://github.com/gzuidhof/coi-serviceworker (Guido Zuidhof and contributors).
 * Installed only under lean/browser/. It never stores reader proof text.
 */
'use strict';
const CACHE = 'komorebi-lean-62b6a229-v2';
const PREFIX = 'komorebi-lean-';
const engine = new URL('engine/', self.registration.scope);
let manifest;
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
  if(request.mode==='navigate')manifest=null;
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
  const cache = await caches.open(CACHE);
  const key = new Request(new URL(relative+'?sha256='+record.sha256,engine));
  const cached = await cache.match(key);
  if (cached) return isolated(cached);
  const response = record.url ? await fetch(record.url,{credentials:'omit',mode:'cors'}) : await fetch(request);
  if (!response.ok) return isolated(response);
  const bytes = await response.clone().arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)), b => b.toString(16).padStart(2,'0')).join('');
  if (bytes.byteLength !== record.size || hash !== record.sha256) throw new Error('Compiler asset checksum mismatch: '+relative);
  // A full browser cache must not prevent proof checking.
  try { await cache.put(key,response.clone()); } catch { /* continue without a persistent copy */ }
  return isolated(response);
}
self.addEventListener('fetch', event => {
  if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') return;
  event.respondWith(responseFor(event.request).catch(error => new Response(String(error),{status:503})));
});
