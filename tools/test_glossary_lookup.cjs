const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/glossary.js'), 'utf8');

function lookupPage(search = '') {
  const events = {};
  const timers = new Map();
  let nextTimer = 0;
  const document = {activeElement: null, querySelector: key => nodes[key]};
  function node(id, extra = {}) {
    return {id, hidden: true, value: '', ...extra,
      addEventListener(event, callback) { events[id+':'+event] = callback; },
      focus() { document.activeElement = this; }, scrollIntoView() { this.scrolled = true; }};
  }
  const entries = [
    node('cokernel', {dataset: {term: 'Cokernel', search: 'Cokernel Quotient by the image of a linear map.', subject: 'linear'}}),
    node('kernel', {dataset: {term: 'Kernel', search: 'Kernel Vectors sent to zero by a linear map.', subject: 'linear'}}),
    node('kernel-pair', {dataset: {term: 'Kernel pair', search: 'Kernel pair Two inputs with the same image.', subject: 'linear'}}),
    node('seed-rank', {dataset: {term: 'Seed rank', search: 'Seed rank Least generating family.', subject: 'operators'}}),
    node('ulp', {dataset: {term: 'ULP', search: 'ULP Spacing at precision 3 in R².', subject: 'arithmetic'}})
  ];
  const list = node('glossary-results', {children: entries.slice(), append(child) {
    this.children.splice(this.children.indexOf(child), 1); this.children.push(child);
  }});
  const nodes = {};
  for (const id of ['glossary-lookup','glossary-form','glossary-query','glossary-subject','glossary-status','glossary-matches','glossary-results-title']) nodes['#'+id] = node(id);
  nodes['#glossary-results'] = list;
  nodes['#glossary-subject'].options = ['', 'linear', 'operators', 'arithmetic'].map(value => ({value}));
  const location = new URL('https://example.test/collection/GLOSSARY.html'+search+'#power-series');
  const history = {replaceState(a, b, url) { location.href = String(url); }};
  vm.runInNewContext(source, {document, location, history, URL,
    window: {addEventListener(name, callback) { events[name] = callback; }},
    setTimeout(callback) { timers.set(++nextTimer, callback); return nextTimer; },
    clearTimeout(id) { timers.delete(id); }});
  return {nodes, document, location, entries,
    backOrForward() { events.popstate(); },
    event(id, event) { events[id+':'+event]({preventDefault() {}}); },
    search(text) { nodes['#glossary-query'].value = text; this.event('glossary-query','input'); },
    flush() { for (const fn of timers.values()) fn(); timers.clear(); },
    visible() { return list.children.filter(entry => !entry.hidden).map(entry => entry.id); }};
}

let p = lookupPage();
assert.equal(p.nodes['#glossary-form'].hidden, false);
assert.equal(p.nodes['#glossary-matches'].hidden, true);
assert.equal(p.document.activeElement, null, 'Opening lookup does not steal focus from a direct definition');
p.document.activeElement = p.nodes['#glossary-query'];
p.search('kernel');
assert.deepEqual(p.visible(), ['kernel', 'kernel-pair', 'cokernel'], 'Exact names and prefixes precede definition matches');
assert.equal(p.document.activeElement, p.nodes['#glossary-query'], 'Typing preserves input focus');
p.flush();
assert.equal(p.nodes['#glossary-status'].textContent, '3 matching terms.');
assert.equal(p.location.searchParams.get('q'), 'kernel');
assert.equal(p.location.hash, '#power-series', 'Lookup preserves a definition anchor');
p.event('glossary-form','submit');
assert.equal(p.document.activeElement, p.nodes['#glossary-results-title']);

p.search('sent zero');
assert.deepEqual(p.visible(), ['kernel'], 'Readers can search using words from a definition');
p.nodes['#glossary-subject'].value = 'operators';
p.event('glossary-subject','change');
assert.deepEqual(p.visible(), [], 'The subject and word filters combine');
assert.match(p.nodes['#glossary-status'].textContent, /No matching terms/);
p.search('');
assert.deepEqual(p.visible(), ['seed-rank'], 'Selecting a subject alone lists its entries');
p.event('glossary-form','reset');
assert.equal(p.nodes['#glossary-subject'].value, '');
assert.equal(p.nodes['#glossary-matches'].hidden, true);
assert.equal(p.document.activeElement, p.nodes['#glossary-query']);
assert.equal(p.location.search, '');

for (const query of ['SEED-RANK', 'seed–rank']) {
  p.search(query);
  assert.deepEqual(p.visible(), ['seed-rank']);
}
p.search('r2');
assert.deepEqual(p.visible(), ['ulp'], 'Compatibility characters match ordinary keyboard spellings');
p.search('kernel');
p.search('zzzz');
p.flush();
assert.match(p.nodes['#glossary-status'].textContent, /No matching terms/, 'Only the latest delayed count is announced');

p = lookupPage('?q=kernel&subject=linear');
assert.deepEqual(p.visible(), ['kernel', 'kernel-pair', 'cokernel'], 'Shared lookup addresses restore query and subject');
assert.equal(p.document.activeElement, null);
p.location.search = '?q=least&subject=operators';
p.backOrForward();
assert.equal(p.nodes['#glossary-query'].value, 'least');
assert.deepEqual(p.visible(), ['seed-rank'], 'Back and Forward restore the lookup described by the address');
assert.equal(p.document.activeElement, null, 'History restores filters without stealing passage focus');
p = lookupPage('?subject=unknown&q=%3Cscript%3E');
assert.equal(p.nodes['#glossary-subject'].value, '');
assert.deepEqual(p.visible(), []);
console.log('PASS: glossary ranking, definition search, subjects, keyboard focus, clear, safe shared addresses and announcements');
