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
