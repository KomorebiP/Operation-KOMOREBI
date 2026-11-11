/* Byte-preserving delivery for generated indexes. Native exports stay downloadable. */
(() => {
  'use strict';
  const script = document.currentScript;
  const base = new URL('../', script.src);
  const nativeFetch = globalThis.fetch.bind(globalThis);
  let manifestPromise, fallbackPromise;
  const selected = path => /^(?:notation\/(?:data|reader)\/[a-z0-9-]+\.json|notation\/(?:index|search)\.json|side-reader-index\.json|downloads\/selection\.json|search-index\.json)$/.test(path);
  function manifest() {
    manifestPromise ||= nativeFetch(new URL('delivery.json', base), {cache: 'no-cache'}).then(async response => {
      if (!response.ok) throw new Error('Reader download record unavailable');
      const value = await response.json();
      if (value.schema !== 1 || !/^[0-9a-f]{40}$/.test(value.revision)) throw new Error('Invalid reader download record');
      return value;
    }).catch(error => { manifestPromise = null; throw error; });
    return manifestPromise;
  }
  async function authenticated(raw, expected) {
    if (globalThis.crypto?.subtle) {
      const digest = await crypto.subtle.digest('SHA-256', raw);
      const actual = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
      if (actual !== expected) throw new Error('Reader data checksum mismatch');
    }
    return raw;
  }
  async function fallback(record) {
    if (globalThis.fflate?.gunzipSync) return globalThis.fflate;
    fallbackPromise ||= new Promise((resolve, reject) => {
      const tag = document.createElement('script');
      tag.src = new URL('assets/vendor/fflate-0.8.3.js', base).href;
      tag.integrity = record.fallback_integrity;
      tag.onload = () => globalThis.fflate?.gunzipSync ? resolve(globalThis.fflate) : reject(new Error('Reader decompressor unavailable'));
      tag.onerror = () => reject(new Error('Reader decompressor unavailable'));
      document.head.append(tag);
    }).catch(error => { fallbackPromise = null; throw error; });
    return fallbackPromise;
  }
  async function read(input, init) {
    const url = new URL(input, document.baseURI);
    const path = url.origin === base.origin && url.pathname.startsWith(base.pathname) ? decodeURIComponent(url.pathname.slice(base.pathname.length)) : '';
    if (!selected(path) || init?.method && init.method.toUpperCase() !== 'GET') return nativeFetch(input, init);
    const catalog = await manifest(), record = catalog.files[path];
    if (!record?.gzip || record.gzip !== path+'.gz') throw new Error('Reader data is missing from its download record');
    const target = new URL(record.gzip, base); target.search = url.search;
    target.searchParams.set('delivery', catalog.revision);
    const response = await nativeFetch(target, init);
    if (!response.ok) throw new Error('Reader data could not be loaded');
    const packed = new Uint8Array(await response.arrayBuffer());
    // Some hosts transparently decode Content-Encoding before exposing bytes.
    if (packed[0] !== 31 || packed[1] !== 139) {
      if (packed.byteLength !== record.bytes) throw new Error('Incomplete reader index');
      await authenticated(packed, record.sha256);
      return new Response(packed, {headers: {'Content-Type': 'application/json; charset=utf-8'}});
    }
    if (packed.byteLength !== record.gzip_bytes) throw new Error('Incomplete reader data');
    await authenticated(packed, record.gzip_sha256);
    let raw;
    if (typeof DecompressionStream === 'function') {
      try {
        raw = new Uint8Array(await new Response(new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
      } catch (error) {
        if (init?.signal?.aborted) throw error;
        raw = (await fallback(catalog)).gunzipSync(packed);
      }
    } else raw = (await fallback(catalog)).gunzipSync(packed);
    if (init?.signal?.aborted) throw new DOMException('The operation was aborted', 'AbortError');
    if (raw.byteLength !== record.bytes) throw new Error('Incomplete reader index');
    await authenticated(raw, record.sha256);
    return new Response(raw, {headers: {'Content-Type': 'application/json; charset=utf-8'}});
  }
  globalThis.KomorebiReaderData = {fetch: read};
  // Old bookmarked download routes retain an automatic browser handoff. The
  // ordinary release links on the 404 page also work with JavaScript disabled.
  document.addEventListener('DOMContentLoaded', async () => {
    if (!document.querySelector('#retained-downloads')) return;
    const url = new URL(location.href);
    if (!url.pathname.startsWith(base.pathname)) return;
    const path = decodeURIComponent(url.pathname.slice(base.pathname.length));
    if (!selected(path) && !/^downloads\/[a-z0-9-]+\.zip$/.test(path)) return;
    try {
      const record = (await manifest()).files[path];
      if (record) location.replace(record.export_url);
    } catch { /* Native download links remain available. */ }
  });
})();
