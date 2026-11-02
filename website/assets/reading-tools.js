/* Progressive enhancements shared by the twelve core reading editions. */
(() => {
  'use strict';
  const normalize = value => value.normalize('NFKD').replace(/\p{M}/gu, '').toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  for (const [index, container] of Array.from(document.querySelectorAll('.reading-menu-panel, .reading-contents-index')).entries()) {
    const links = Array.from(container.querySelectorAll('a[data-reading-entry]'));
    if (!links.length) continue;
    const rows = links.map(link => ({link, row: link.closest('li'), text: normalize(link.textContent)}));
    const groups = Array.from(container.querySelectorAll('.reading-contents-group'));
    let savedGroups;
    const form = element('form', undefined, 'reading-chapter-filter');
    form.setAttribute('role', 'search');form.setAttribute('aria-label', 'Chapters in this paper');
    const id = 'reading-chapter-query-'+index;
    const label = element('label', 'Find a chapter');label.htmlFor = id;
    const input = element('input');input.id = id;input.type = 'search';
    input.placeholder = 'Title or reading-page number';input.autocomplete = 'off';
    const clear = element('button', 'Clear search');clear.type = 'reset';clear.hidden = true;
    const status = element('p', undefined, 'reading-chapter-count');
    status.setAttribute('role', 'status');input.setAttribute('aria-describedby', id+'-status');status.id = id+'-status';
    form.append(label, input, clear, status);
    function apply() {
      const query = normalize(input.value), words = query.split(/\s+/).filter(Boolean);
      if (query && !savedGroups) savedGroups = groups.map(group => group.open);
      let shown = 0;
      for (const {link, row, text} of rows) {
        const match = /^\d+$/.test(query) ? link.dataset.readingEntry === query : words.every(word => text.includes(word));
        row.hidden = !match;shown += Number(match);
      }
      groups.forEach((group, i) => {
        group.hidden = !Array.from(group.querySelectorAll('li')).some(row => !row.hidden);
        if (query) group.open = !group.hidden;
        else if (savedGroups) group.open = savedGroups[i];
      });
      if (!query) savedGroups = undefined;
      clear.hidden = !query;
      status.textContent = query ? (shown ? shown+' of '+rows.length+' reading pages' : 'No matching chapters. Try fewer words or clear the search.') : rows.length+' reading pages';
    }
    form.addEventListener('submit', event => {event.preventDefault();apply();});
    form.addEventListener('reset', event => {event.preventDefault();input.value = '';apply();input.focus();});
    input.addEventListener('input', apply);
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape' && input.value) {
        event.preventDefault();event.stopPropagation();input.value = '';apply();
      }
    });
    container.prepend(form);apply();
  }

  for (const [index, container] of Array.from(document.querySelectorAll('.statement-navigation, .reading-statement-directory')).entries()) {
    const engine = window.KomorebiStatementSearch;
    if (!engine) continue;
    const entries = Array.from(container.querySelectorAll('[data-statement-entry]')).map(row => ({row,
      text:row.querySelector('[data-statement-target]').textContent,kind:row.dataset.statementKind,
      name:row.dataset.statementName,number:row.dataset.statementNumber,labels:row.dataset.statementLabels,
      hasProof:!!row.querySelector('.statement-proof-link')}));
    if (!entries.length) continue;
    const directory = container.classList.contains('reading-statement-directory');
    const groups = Array.from(container.querySelectorAll('.statement-chapter-group'));
    const form = element('form', undefined, 'reading-chapter-filter reading-statement-filter');
    form.setAttribute('role','search');form.setAttribute('aria-label',directory ? 'Statements in this paper' : 'Statements in this chapter');
    const id = 'reading-statement-query-'+index;
    const label = element('label',directory ? 'Find a statement in this paper' : 'Find a statement');label.htmlFor = id;
    const input = element('input');input.id = id;input.type = 'search';input.autocomplete = 'off';
    input.placeholder = 'Title, number, type or source label';
    const clear = element('button','Clear');clear.type = 'reset';clear.hidden = true;
    clear.setAttribute('aria-label','Clear statement search');
    const proofLabel = element('label',undefined,'reading-statement-proof-filter');
    const proof = element('input');proof.type = 'checkbox';proof.id = id+'-proof';
    proofLabel.htmlFor = proof.id;proofLabel.append(proof,document.createTextNode('Proof links only'));
    const status = element('p',undefined,'reading-chapter-count');status.id = id+'-status';
    status.setAttribute('role','status');input.setAttribute('aria-describedby',status.id);
    form.append(label,input,clear,proofLabel,status);
    function apply(updateUrl = true) {
      const found = new Set(engine.search(entries,input.value,proof.checked));
      for (const entry of entries) entry.row.hidden = !found.has(entry);
      for (const group of groups) group.hidden = !Array.from(group.querySelectorAll('[data-statement-entry]')).some(row=>!row.hidden);
      clear.hidden = !input.value && !proof.checked;
      status.textContent = found.size ? found.size+' of '+entries.length+' statements' : 'No matching statements. Try fewer words or clear the filters.';
      if (directory && updateUrl) {
        try {
          const url = engine.filterUrl(location.href,input.value,proof.checked);
          if (url !== location.href) history.replaceState(history.state,'',url);
        } catch {} // Searching still works when browser history is unavailable.
      }
    }
    function restoreFilters() {
      const filters = engine.readFilters(location.search);
      input.value = filters.query;proof.checked = filters.proofOnly;apply(false);
    }
    function reset(focus = false) {input.value = '';proof.checked = false;apply();if (focus) input.focus();}
    form.addEventListener('submit',event=>{event.preventDefault();apply();});
    form.addEventListener('reset',event=>{event.preventDefault();reset(true);});
    input.addEventListener('input',apply);proof.addEventListener('change',apply);
    container.addEventListener('keydown',event=>{
      if (event.key === 'Escape' && (input.value || proof.checked)) {
        event.preventDefault();event.stopPropagation();reset();
      } else if (event.key === 'Escape' && !directory && container.open) {
        event.preventDefault();event.stopPropagation();container.open = false;container.querySelector('summary').focus();
      }
    });
    container.querySelector(directory ? 'h2' : 'summary').after(form);
    if (directory) {
      window.addEventListener('pageshow',restoreFilters);window.addEventListener('popstate',restoreFilters);
      restoreFilters();
    } else apply();
  }

  const bibliography = document.querySelector('.reading-bibliography');
  const references = bibliography ? Array.from(bibliography.querySelectorAll('section[id^="ref-"]')) : [];
  if (references.length) {
    const texts = new Map();
    let previousAuthors = '';
    for (const reference of references) {
      let text = Array.from(reference.children).filter(child => !child.matches('.reference-uses'))
        .map(child => child.textContent).join(' ');
      // An em dash repeats the preceding author list in the retained BBL.
      // Include that explicit convention in search without changing the entry.
      const paragraph = reference.querySelector('p');
      const title = paragraph?.querySelector('em');
      if (title?.parentElement === paragraph) {
        let prefix = '';
        for (const node of paragraph.childNodes) {if (node === title) break;prefix += node.textContent;}
        if (/^\s*[—–]\s*,/.test(prefix)) text = previousAuthors+' '+text;
        else previousAuthors = prefix.trim();
      } else previousAuthors = '';
      texts.set(reference, normalize(text));
    }
    const form = element('form', undefined, 'reading-chapter-filter reading-reference-filter');
    form.setAttribute('role', 'search');form.setAttribute('aria-label', 'Bibliography');
    const label = element('label', 'Find a reference');label.htmlFor = 'reading-reference-query';
    const input = element('input');input.id = 'reading-reference-query';input.type = 'search';
    input.placeholder = 'Author, title, year or citation key';input.autocomplete = 'off';
    input.setAttribute('aria-describedby', 'reading-reference-count');
    const clear = element('button', 'Clear reference search');clear.type = 'reset';clear.hidden = true;
    const status = element('p', undefined, 'reading-chapter-count');status.id = 'reading-reference-count';
    status.setAttribute('role', 'status');
    form.append(label, input, clear, status);
    function apply() {
      const words = normalize(input.value).split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const reference of references) {
        const match = words.every(word => texts.get(reference).includes(word));
        reference.hidden = !match;shown += Number(match);
      }
      clear.hidden = !input.value;
      status.textContent = words.length ? (shown ? shown+' of '+references.length+' references' : 'No matching references. Try fewer words or clear the search.') : references.length+' references';
    }
    function reset(focus = false) {input.value = '';apply();if (focus) input.focus();}
    function revealLinkedReference() {
      let id;
      try {id = decodeURIComponent(location.hash.slice(1));} catch {return;}
      const target = references.find(reference => reference.id === id);
      if (target?.hidden) reset();
    }
    form.addEventListener('submit', event => {event.preventDefault();apply();});
    form.addEventListener('reset', event => {event.preventDefault();reset(true);});
    input.addEventListener('input', apply);
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape' && input.value) {event.preventDefault();event.stopPropagation();reset();}
    });
    window.addEventListener('hashchange', revealLinkedReference);
    // A local permalink uses pushState in reader.js, so reveal its target before
    // the delegated focus handler runs as well as on Back/Forward navigation.
    document.addEventListener('click', event => {
      const link = event.target.closest('a[href]');
      if (!link || event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search) return;
      let id;
      try {id = decodeURIComponent(url.hash.slice(1));} catch {return;}
      if (references.some(reference => reference.id === id && reference.hidden)) reset();
    }, true);
    bibliography.prepend(form);apply();
  }

  // Every disclosure retains its native, script-free operation. Escape and an
  // outside click dismiss the floating panels without losing keyboard focus.
  const menus = Array.from(document.querySelectorAll('.reading-menu, .reading-paper-menu, .reading-display, .chapter-toolbar .reading-resources'));
  for (const menu of menus) {
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) {
        event.preventDefault();menu.open = false;menu.querySelector('summary').focus();
      }
    });
    menu.addEventListener('toggle', () => {
      if (menu.open) for (const other of menus) if (other !== menu) other.open = false;
    });
  }
  document.addEventListener('click', event => {
    for (const menu of menus) if (menu.open && !menu.contains(event.target)) menu.open = false;
  });

  const settings = document.querySelector('.reading-display');
  const article = document.querySelector('#chapter-text');
  if (!settings || !article) return;
  const size = settings.querySelector('#reading-text-size');
  const font = settings.querySelector('#reading-text-font');
  const key = 'komorebi.reading.text';
  function applySettings(value = {}) {
    size.value = ['large','larger'].includes(value.size) ? value.size : 'default';
    font.value = value.font === 'serif' ? 'serif' : 'default';
    article.dataset.textSize = size.value;article.dataset.textFont = font.value;
    window.dispatchEvent(new Event('resize')); // Refresh the section tracker after reflow.
  }
  function save() {
    const value = {size:size.value, font:font.value};applySettings(value);
    try {localStorage.setItem(key, JSON.stringify(value));} catch {}
  }
  function restore() {
    let value;
    try {value = JSON.parse(localStorage.getItem(key));} catch {}
    applySettings(value && typeof value === 'object' ? value : {});
  }
  size.addEventListener('change', save);font.addEventListener('change', save);
  settings.querySelector('.reading-display-reset').addEventListener('click', () => {
    applySettings();try {localStorage.removeItem(key);} catch {}
  });
  window.addEventListener('storage', event => {if (event.key === key || event.key === null) restore();});
  restore();settings.hidden = false;
})();
