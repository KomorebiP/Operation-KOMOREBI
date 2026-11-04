// Keep the immutable book downloads off the Pages storage budget. Authenticate
// every bounded part and the complete file before opening or saving it.
const PREFIX = 'publication/machine-native-reasoning-reconstructed/2026-11-04/';
const HASHES = {
  pdf: '65a0a736e3422102f83bfc96883dcb81d2a7dacc42663c78e002718ebb7278db',
  source: '14e635a4e910ab3062e5618b084841eff2e0504f048130cfd336985a7c94ef25'
};
export async function sha256(bytes) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
}
export function validateAsset(kind, asset, revision) {
  if (!/^[0-9a-f]{40}$/.test(revision) || asset?.sha256 !== HASHES[kind]) throw Error('Unknown book edition');
  if (!Number.isSafeInteger(asset.bytes) || asset.bytes < 1 || asset.bytes > 32 * 1024 * 1024) throw Error('Invalid file size');
  if (!Array.isArray(asset.parts) || !asset.parts.length || asset.parts.length > 128) throw Error('Invalid file inventory');
  const seen = new Set();
  let total = 0;
  for (const p of asset.parts) {
    if (!p.path?.startsWith(PREFIX) || !/^(pdf|source)-\d{3}\.bin$/.test(p.path.slice(PREFIX.length)) ||
        seen.has(p.path) || !/^[0-9a-f]{64}$/.test(p.sha256) ||
        !Number.isSafeInteger(p.bytes) || p.bytes < 1 || p.bytes > 524288) throw Error('Invalid file part');
    seen.add(p.path); total += p.bytes;
  }
  if (total !== asset.bytes || !/^[A-Za-z0-9_.-]+$/.test(asset.filename)) throw Error('Changed file inventory');
}
export async function assembleAsset(kind, asset, { revision, fetcher = fetch, signal, onprogress = () => {} } = {}) {
  validateAsset(kind, asset, revision);
  const controller = new AbortController();
  const abort = () => controller.abort(signal?.reason);
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) abort();
  const parts = new Array(asset.parts.length);
  let next = 0, completed = 0;
  const worker = async () => {
    while (next < asset.parts.length) {
      controller.signal.throwIfAborted();
      const i = next++, p = asset.parts[i];
      const response = await fetcher('https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/' + revision + '/' + p.path, { signal: controller.signal, credentials: 'omit' });
      if (!response.ok) throw Error('A download could not be retrieved (' + response.status + ')');
      const raw = new Uint8Array(await response.arrayBuffer());
      if (raw.byteLength !== p.bytes || await sha256(raw) !== p.sha256) throw Error('Download integrity check failed');
      parts[i] = raw; completed += raw.byteLength; onprogress(completed / asset.bytes);
    }
  };
  try {
    await Promise.all(Array.from({ length: Math.min(4, parts.length) }, worker));
    controller.signal.throwIfAborted();
    const bytes = new Uint8Array(asset.bytes);
    let offset = 0;
    for (const part of parts) { bytes.set(part, offset); offset += part.byteLength; }
    if (await sha256(bytes) !== asset.sha256) throw Error('Complete download integrity check failed');
    return bytes;
  } catch (error) { controller.abort(); throw error; }
  finally { signal?.removeEventListener('abort', abort); }
}

async function startInterface(root) {
  const status = document.getElementById('mnr-status');
  const save = document.getElementById('mnr-save');
  const cancel = document.getElementById('mnr-cancel');
  const retry = document.getElementById('mnr-retry');
  const holder = document.getElementById('mnr-viewer');
  const buttons = ['mnr-pdf', 'mnr-source'].map(id => document.getElementById(id));
  const cache = new Map(), urls = [];
  let active, lastAction = 'reader', record;
  const loadRecord = async () => {
    if (!record) {
      const response = await fetch(root.dataset.record, { credentials: 'omit' });
      if (!response.ok) throw Error('The download record could not be loaded');
      record = await response.json();
    }
    return record;
  };
  const run = async action => {
    if (active) return;
    lastAction = action; active = new AbortController();
    const controller = active;
    const kind = action === 'source' ? 'source' : 'pdf';
    const label = action === 'reader' ? 'Loading book' : 'Preparing download';
    buttons.forEach(button => { button.disabled = true; });
    cancel.hidden = false; retry.hidden = true; save.hidden = true;
    status.textContent = label + '…';
    try {
      const info = await loadRecord(), asset = info.assets[kind];
      let bytes = cache.get(kind);
      if (!bytes) {
        bytes = await assembleAsset(kind, asset, { revision: info.revision, signal: controller.signal,
          onprogress: ratio => { status.textContent = label + ': ' + Math.round(100 * ratio) + '%'; } });
        cache.set(kind, bytes);
      }
      controller.signal.throwIfAborted();
      const url = URL.createObjectURL(new Blob([bytes], { type: kind === 'pdf' ? 'application/pdf' : 'application/zip' }));
      urls.push(url);
      if (action === 'reader') {
        const viewer = new URL(root.dataset.viewer, location.href);
        if (viewer.origin !== location.origin) throw Error('Unexpected PDF reader');
        viewer.searchParams.set('file', url);
        viewer.hash = /^#page=([1-9]\d{0,2})$/.test(location.hash) && Number(location.hash.slice(6)) <= 977 ? location.hash : '#page=1';
        const frame = document.createElement('iframe');
        frame.title = 'Machine-Native Reasoning — complete 977-page book';
        frame.className = 'pdf-reader'; frame.style.cssText = 'width:100%;height:85vh'; frame.src = viewer.href;
        holder.replaceChildren(frame);
        status.textContent = 'Book verified. All 977 pages are available in the reader below.';
      } else {
        save.href = url; save.download = asset.filename; save.textContent = 'Save ' + (kind === 'pdf' ? 'PDF' : 'editable TeX ZIP'); save.hidden = false;
        status.textContent = 'Download verified. Save the complete ' + (kind === 'pdf' ? 'PDF.' : 'editable TeX ZIP.');
        save.click();
      }
    } catch (error) {
      status.textContent = controller.signal.aborted ? 'Download cancelled. Select Retry to continue.' : error.message + '. Select Retry to try again.';
      retry.hidden = false;
    } finally {
      active = null; cancel.hidden = true; buttons.forEach(button => { button.disabled = false; });
    }
  };
  cancel.addEventListener('click', () => active?.abort());
  retry.addEventListener('click', () => run(lastAction));
  buttons[0].addEventListener('click', () => run('pdf'));
  buttons[1].addEventListener('click', () => run('source'));
  window.addEventListener('pagehide', () => { active?.abort(); urls.forEach(url => URL.revokeObjectURL(url)); });
  const requested = new URLSearchParams(location.search).get('download');
  await run(requested === 'pdf' || requested === 'source' ? requested : 'reader');
}
if (typeof document !== 'undefined') {
  const root = document.getElementById('mnr-delivery');
  if (root) startInterface(root);
}
