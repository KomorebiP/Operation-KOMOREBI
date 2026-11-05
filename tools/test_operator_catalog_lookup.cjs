const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/operator-catalog.js'), 'utf8');

function lookupPage(suffix = '#browse-by-family') {
  const events = {};
  const timers = new Map();
  let nextTimer = 0;
  const nodes = {};
  const document = {activeElement: null, querySelector: key => nodes[key]};
  function node(id, extra = {}) {
    return {id, hidden: true, value: '', ...extra,
      addEventListener(event, callback) { events[id + ':' + event] = callback; },
      focus() { document.activeElement = this; },
      scrollIntoView() { this.scrolled = true; }};
  }
  function entry(id, name, family, checks, text) {
    return node('operator-result-' + id.toLowerCase(), {dataset: {
      operatorId: id, name, family, checks: String(checks), search: id + ' ' + name + ' ' + text}});
  }
  const entries = [
    entry('OP-098', 'Adaptive filter weight update', 'E', 0, 'Nonlinear state updates.'),
    entry('OP-003', 'Coordinate projection', 'A', 2, 'Linear projector in R².'),
    entry('OP-176', 'Falling-factorial degree operator', 'C', 0, 'Polynomial degree in falling factorial coordinates.'),
    entry('OP-175', 'Falling-factorial raising operator', 'C', 2, 'Shift and raise the polynomial basis.'),
    entry('OP-104', 'Faà di Bruno composition', 'F', 2, 'Composition derivatives and set partitions.'),
    entry('OP-047', 'Forward finite difference', 'C', 2, 'Delta \\Delta Translation and polynomial differences.'),
    entry('OP-025', 'Residue projector', 'B', 1, 'Cyclic degree selection by residues.')
  ];
  const list = node('operator-catalog-results', {children: entries.slice(), append(child) {
    this.children.splice(this.children.indexOf(child), 1); this.children.push(child);
  }});
  for (const id of ['operator-catalog-lookup', 'operator-catalog-form', 'operator-catalog-query',
    'operator-catalog-family', 'operator-catalog-checks', 'operator-catalog-status',
    'operator-catalog-matches', 'operator-catalog-results-title']) nodes['#' + id] = node(id);
  nodes['#operator-catalog-results'] = list;
  nodes['#operator-catalog-family'].options = ['', 'A', 'B', 'C', 'E', 'F'].map(value => ({value}));
  nodes['#operator-catalog-checks'].options = ['', 'linked', 'unlinked'].map(value => ({value}));
  const location = new URL('https://example.test/collection/operators/catalog/README.html' + suffix);
  const history = {replaceState(a, b, url) { location.href = String(url); }};
  vm.runInNewContext(source, {document, location, history, URL,
    window: {addEventListener(name, callback) { events[name] = callback; }},
    setTimeout(callback) { timers.set(++nextTimer, callback); return nextTimer; },
    clearTimeout(id) { timers.delete(id); }});
  return {nodes, document, location, entries,
    event(id, name) { events[id + ':' + name]({preventDefault() {}}); },
    historyChange() { events.popstate(); },
    fragment(value) { location.hash = value; events.hashchange(); },
    search(value) { nodes['#operator-catalog-query'].value = value; this.event('operator-catalog-query', 'input'); },
    filter(name, value) { nodes['#operator-catalog-' + name].value = value; this.event('operator-catalog-' + name, 'change'); },
    flush() { for (const fn of timers.values()) fn(); timers.clear(); },
    visible() { return list.children.filter(row => !row.hidden).map(row => row.dataset.operatorId); }};
}

let p = lookupPage();
assert.equal(p.nodes['#operator-catalog-form'].hidden, false);
assert.equal(p.nodes['#operator-catalog-matches'].hidden, true);
assert.match(p.nodes['#operator-catalog-status'].textContent, /Search all 7 entries/);
assert.equal(p.document.activeElement, null, 'Loading the catalog does not steal keyboard focus');

p.document.activeElement = p.nodes['#operator-catalog-query'];
p.search('falling factorial');
assert.deepEqual(p.visible(), ['OP-176', 'OP-175'], 'Word matches preserve the name ordering');
assert.equal(p.document.activeElement, p.nodes['#operator-catalog-query']);
assert.equal(p.location.searchParams.get('q'), 'falling factorial');
assert.equal(p.location.hash, '#browse-by-family', 'Filtering preserves unrelated section fragments');
p.flush();
assert.equal(p.nodes['#operator-catalog-status'].textContent, '2 matching entries out of 7.');
p.event('operator-catalog-form', 'submit');
assert.equal(p.document.activeElement, p.nodes['#operator-catalog-results-title']);
assert.equal(p.nodes['#operator-catalog-results-title'].scrolled, true);

p.filter('checks', 'linked');
assert.deepEqual(p.visible(), ['OP-175']);
p.filter('family', 'B');
assert.deepEqual(p.visible(), []);
assert.match(p.nodes['#operator-catalog-status'].textContent, /No matching entries/);
assert.equal(p.nodes['#operator-catalog-matches'].hidden, true);
p.event('operator-catalog-form', 'reset');
assert.equal(p.nodes['#operator-catalog-family'].value, '');
assert.equal(p.nodes['#operator-catalog-checks'].value, '');
assert.equal(p.nodes['#operator-catalog-matches'].hidden, true);
assert.equal(p.location.search, '');
assert.equal(p.document.activeElement, p.nodes['#operator-catalog-query']);

for (const value of ['OP-025', 'op25', 'op 025', 'OP025']) {
  p.search(value);
  assert.deepEqual(p.visible(), ['OP-025'], 'OP identifiers accept ordinary spacing and zero padding');
}
p.search('OP-999');
assert.deepEqual(p.visible(), [], 'Unknown identifiers do not return incidental number matches');
for (const value of ['faa di bruno', 'Faà di Bruno', 'FAÀ–DI–BRUNO']) {
  p.search(value);
  assert.deepEqual(p.visible(), ['OP-104'], 'Names match accent and dash variants');
}
p.search('Δ');
assert.deepEqual(p.visible(), ['OP-047'], 'A Greek symbol matches its formula spelling');
p.search('r2');
assert.deepEqual(p.visible(), ['OP-003'], 'Compatibility characters are searchable');
p.search('');
p.filter('checks', 'linked');
assert.equal(p.visible().length, 5);
p.filter('checks', 'unlinked');
assert.deepEqual(p.visible(), ['OP-098', 'OP-176']);
p.filter('family', 'C');
assert.deepEqual(p.visible(), ['OP-176'], 'Family and fixture filters combine without a text query');
p.event('operator-catalog-form', 'reset');
p.search('raising');
p.search('unknown phrase');
p.flush();
assert.match(p.nodes['#operator-catalog-status'].textContent, /No matching entries/, 'A stale delayed count cannot replace the latest result');

p = lookupPage('?q=falling&family=c&checks=linked&ref=shared#browse-by-family');
assert.deepEqual(p.visible(), ['OP-175']);
assert.equal(p.nodes['#operator-catalog-family'].value, 'C');
assert.equal(p.location.searchParams.get('family'), 'C');
assert.equal(p.document.activeElement, null);
p.location.search = '?q=cyclic&family=B';
p.historyChange();
assert.deepEqual(p.visible(), ['OP-025']);
assert.equal(p.nodes['#operator-catalog-checks'].value, '');
assert.equal(p.document.activeElement, null, 'History restores the lookup without stealing passage focus');
p.location.search = '?q=projection&family=unknown&checks=verified';
p.historyChange();
assert.equal(p.nodes['#operator-catalog-family'].value, '');
assert.equal(p.nodes['#operator-catalog-checks'].value, '');
assert.deepEqual(p.visible(), ['OP-003'], 'Unsupported filters are ignored rather than silently hiding all results');
p.location.search = '?q=%3Cscript%3E&family=F';
p.historyChange();
assert.deepEqual(p.visible(), [], 'Query strings remain text');

p = lookupPage('?q=falling&family=C&checks=unlinked#op-025');
assert.deepEqual(p.visible(), ['OP-025'], 'A direct entry fragment reveals its target despite conflicting filters');
assert.equal(p.nodes['#operator-catalog-family'].value, '');
assert.equal(p.nodes['#operator-catalog-checks'].value, '');
assert.equal(p.entries.find(entry => entry.dataset.operatorId === 'OP-025').scrolled, true);
assert.equal(p.document.activeElement, null);
assert.equal(p.location.hash, '#op-025');
p.search('falling');
assert.equal(p.location.hash, '', 'A new lookup replaces an old result fragment');
assert.deepEqual(p.visible(), ['OP-176', 'OP-175']);
p.fragment('operator-result-op-104');
assert.deepEqual(p.visible(), ['OP-104']);
p.fragment('%E0%A4%A');
assert.deepEqual(p.visible(), ['OP-104'], 'A malformed fragment does not break the active lookup');

p = lookupPage('?q=falling&family=C&checks=linked&ref=shared#browse-by-family');
p.event('operator-catalog-form', 'reset');
assert.equal(p.location.search, '?ref=shared', 'Reset preserves unrelated URL parameters');
assert.equal(p.location.hash, '#browse-by-family');
vm.runInNewContext(source, {document: {querySelector: () => null}});
console.log('PASS: operator names, OP identifiers, source vocabulary, family and fixture filters, URL state, fragments, focus, reset and accessible counts');
