/* Explicit bookmarks only. No automatic browsing history or network requests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.start(root);
})(typeof window === 'undefined' ? null : window, function () {
  'use strict';
  const KEY = 'komorebi.saved-reading.v1';
  const LIMIT = 200;
  const clean = (value, limit) => typeof value === 'string' ? value.trim().slice(0, limit) : '';
  const storageKey = base => KEY + ':' + new URL(base).pathname;

  function target(value, base) {
    if (typeof value !== 'string' || !value || value.length > 4096) return null;
    try {
      const home = new URL(base), url = new URL(value, home);
      if (url.origin !== home.origin || url.username || url.password || !url.pathname.startsWith(home.pathname)) return null;
      const path = url.pathname.slice(home.pathname.length);
      const decoded = decodeURIComponent(path);
      if (!path.endsWith('.html') || /[\\\x00-\x1f]/.test(decoded) || decoded.split('/').some(part => part === '..' || part === '.')) return null;
      if (/^(assets|documents|downloads)\//.test(decoded)) return null;
      const fragment = url.hash ? '#' + encodeURIComponent(decodeURIComponent(url.hash.slice(1))) : '';
      return path + url.search + fragment;
    } catch { return null; }
  }

  function parse(raw, base) {
    if (typeof raw !== 'string' || raw.length > 1000000) return [];
    try {
      const data = JSON.parse(raw);
      if (data.schema !== 1 || !Array.isArray(data.items)) return [];
      const seen = new Set(), items = [];
      for (const entry of data.items.slice(0, LIMIT)) {
        if (!entry || typeof entry !== 'object') continue;
        const url = target(entry.url, base), title = clean(entry.title, 300);
        if (!url || !title || seen.has(url)) continue;
        seen.add(url);
        items.push({url, title, section: clean(entry.section, 300), work: clean(entry.work, 300)});
      }
      return items;
    } catch { return []; }
  }

  function edit(items, entry) {
    if (items.some(item => item.url === entry.url)) return items.filter(item => item.url !== entry.url);
    if (items.length >= LIMIT) throw new Error('Your reading list is full. Remove a saved place before adding another.');
    return [entry, ...items];
  }

  function start(window) {
    const document = window.document;
    const bar = document.querySelector('[data-reading-save]');
    const list = document.querySelector('[data-reading-list]');
    if (!bar && !list) return;
    const rootLink = document.querySelector('.brand');
    if (!rootLink) return;
    const base = new URL('./', rootLink.href).href;
    const key = storageKey(base);
    let storage;
    try { storage = window.localStorage; } catch {}
    const read = () => { try { return parse(storage.getItem(key), base); } catch { return []; } };
    let items = read();
    const buttons = [];
    const icon = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false"><path d="M5 3h10v14l-5-3-5 3z"/></svg>';
    const status = bar ? bar.querySelector('.reading-save-status') : list.querySelector('.reading-list-status');
    function announce(message) { status.textContent = message; }
    function pageEntry(hash = window.location.hash, section = '') {
      const url = new URL(window.location.href);
      url.hash = hash;
      const work = document.querySelector('.reading-position a');
      return {url: target(url.href, base), title: bar.dataset.pageTitle, section,
        work: work ? clean(work.textContent, 300) : ''};
    }
    function currentEntry() {
      let node;
      try { node = document.getElementById(decodeURIComponent(window.location.hash.slice(1))); } catch {}
      if (!node) return pageEntry('');
      const heading = node.matches('h2,h3,h4') ? node : node.querySelector('h2,h3,h4');
      return pageEntry(window.location.hash, heading ? clean(heading.dataset.savedTitle || heading.textContent, 300) : 'Linked passage');
    }
    function save(entry, removeOnly = false) {
      if (!entry.url) { announce('This location cannot be saved.'); return; }
      const latest = read();
      let next;
      try {
        next = removeOnly ? latest.filter(item => item.url !== entry.url) : edit(latest, entry);
        storage.setItem(key, JSON.stringify({schema: 1, items: next}));
      } catch (error) {
        announce(error.message && latest.length >= LIMIT ? error.message : 'Browser storage is unavailable. Use your browser’s bookmarks to keep this place.');
        return;
      }
      items = next;
      refresh();
      announce(next.some(item => item.url === entry.url) ? 'Saved in this browser.' : 'Removed from saved reading.');
    }
    function syncButtons() {
      for (const record of buttons) {
        const entry = record.entry(), saved = items.some(item => item.url === entry.url);
        record.button.setAttribute('aria-pressed', String(saved));
        if (record.heading) {
          record.button.setAttribute('aria-label', (saved ? 'Remove saved passage: ' : 'Save passage: ') + entry.section);
          record.button.title = saved ? 'Remove saved passage' : 'Save this passage';
        } else record.button.querySelector('span').textContent = saved ? 'Saved' : entry.section ? 'Save passage' : 'Save page';
      }
      const link = bar && bar.querySelector('[data-saved-reading-link]');
      if (link) link.textContent = items.length ? 'Saved reading (' + items.length + ')' : 'Saved reading';
    }
    function renderList() {
      if (!list) return;
      const query = list.querySelector('input').value.trim().toLocaleLowerCase();
      const visible = items.filter(item => [item.title, item.section, item.work].join(' ').toLocaleLowerCase().includes(query));
      const output = list.querySelector('ol');
      output.replaceChildren();
      for (const entry of visible) {
        const row = document.createElement('li'), content = document.createElement('div');
        const label = document.createElement('p'), link = document.createElement('a'), title = document.createElement('h2');
        label.className = 'saved-reading-context';
        label.textContent = entry.work || (entry.section ? 'Saved passage' : 'Saved page');
        link.href = new URL(entry.url, base).href;
        link.textContent = entry.section || entry.title;
        title.append(link); content.append(label, title);
        if (entry.section) { const parent = document.createElement('p'); parent.textContent = entry.title; content.append(parent); }
        const remove = document.createElement('button');
        remove.type = 'button'; remove.className = 'saved-reading-remove'; remove.textContent = 'Remove';
        remove.setAttribute('aria-label', 'Remove ' + (entry.section || entry.title) + ' from saved reading');
        remove.addEventListener('click', () => {
          const index = visible.findIndex(item => item.url === entry.url);
          save(entry, true);
          const remaining = output.querySelectorAll('button');
          (remaining[Math.min(index, remaining.length - 1)] || list.querySelector('input')).focus();
        });
        row.append(content, remove); output.append(row);
      }
      list.querySelector('.saved-reading-count').textContent = query
        ? visible.length + ' of ' + items.length + ' saved places match'
        : items.length + (items.length === 1 ? ' saved place' : ' saved places');
      const empty = list.querySelector('.reading-list-empty');
      empty.hidden = items.length !== 0;
      if (query && items.length && !visible.length) {
        const message = document.createElement('li');
        message.className = 'reading-list-no-match'; message.textContent = 'No saved places match. Try another title or section.';
        output.append(message);
      }
    }
    function refresh() { syncButtons(); renderList(); }
    if (bar) {
      bar.hidden = false;
      const button = bar.querySelector('[data-save-page]');
      buttons.push({button, entry: currentEntry});
      button.addEventListener('click', () => save(currentEntry()));
      const headings = document.querySelectorAll('main article h2[id], main article h3[id]');
      for (const heading of headings) {
        const title = clean(heading.textContent, 300);
        heading.dataset.savedTitle = title;
        // Keep the heading name intact when its bookmark button is announced.
        if (!heading.getAttribute('aria-label')) heading.setAttribute('aria-label', title);
        const button = document.createElement('button');
        button.type = 'button'; button.className = 'save-passage'; button.innerHTML = icon;
        const entry = () => pageEntry('#' + encodeURIComponent(heading.id), title);
        buttons.push({button, entry, heading: true});
        button.addEventListener('click', () => save(entry()));
        heading.append(button);
      }
      window.addEventListener('hashchange', syncButtons);
      window.addEventListener('popstate', syncButtons);
      // The shared reader uses pushState for section links, which has no hashchange event.
      document.addEventListener('click', () => window.setTimeout(syncButtons, 0));
    }
    if (list) { list.hidden = false; list.querySelector('input').addEventListener('input', renderList); }
    window.addEventListener('storage', event => {
      if (event.key === key || event.key === null) { items = read(); refresh(); }
    });
    refresh();
  }
  return {KEY, LIMIT, storageKey, target, parse, edit, start};
});
