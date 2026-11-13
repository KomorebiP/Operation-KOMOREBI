const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/glossary.js'), 'utf8');

function page(address = '', saved = 'long', storageAvailable = true) {
  const ids = {}, events = {}, storage = new Map([['glossary-view', saved]]);
  const document = {activeElement: null,
    querySelector: selector => ids[selector.slice(1)] || null,
    getElementById: id => ids[id] || null,
    createElement: tag => node('', {tagName: tag.toUpperCase()}),
    addEventListener: (name, callback) => { events['document:' + name] = callback; }};
  function node(id, extra = {}) {
    const listeners = {}, attributes = {};
    const item = {id, dataset: {}, hidden: false, tagName: 'DIV', parentElement: null,
      value: '', textContent: '', rect: {top: 1000, bottom: 1200}, ...extra,
      setAttribute: (key, value) => { attributes[key] = value; },
      getAttribute: key => attributes[key], hasAttribute: key => key in attributes,
      addEventListener: (key, callback) => { listeners[key] = callback; },
      emit: (key, event = {}) => listeners[key]?.(event),
      replaceChildren: (...children) => { item.children = children; },
      focus: () => { document.activeElement = item; }, scrollIntoView: () => {},
      getBoundingClientRect: () => item.rect,
      closest(selector) {
        if (selector === '[data-glossary-panel]') return item.dataset.glossaryPanel ? item : item.parentElement?.closest(selector);
        if (selector === '[data-glossary-term]') return item.dataset.glossaryTerm ? item : item.parentElement?.closest(selector);
        if (selector === 'a[href]') return item.href ? item : null;
        return item.interactive ? item : null;
      }};
    if (id) ids[id] = item;
    return item;
  }
  const groups = [['linear', 'Linear foundations', ['scalar', 'kernel']], ['operators', 'Operators', ['seed', 'projector']]].map(([id, title, terms]) => {
    const panel = node('panel-' + id, {dataset: {glossaryPanel: id, title}});
    const heading = node('heading-' + id, {tagName: 'H2', parentElement: panel});
    node(id, {parentElement: panel});
    panel.terms = terms.map(key => {
      const term = node('term-' + key, {dataset: {glossaryTerm: key, title: key}, parentElement: panel});
      const heading = node('heading-' + key, {tagName: 'H3', parentElement: term});
      node(key, {parentElement: term});
      term.querySelector = () => heading;
      return term;
    });
    panel.querySelectorAll = () => panel.terms;
    panel.querySelector = () => heading;
    return panel;
  });
  const navs = [0, 1].map(index => {
    const previous = node('previous-' + index), next = node('next-' + index);
    const nav = node('nav-' + index);
    nav.querySelector = selector => selector.includes('previous') ? previous : next;
    return nav;
  });
  for (const id of ['glossary-controls', 'glossary-overview', 'glossary-panels', 'glossary-reading-controls',
    'glossary-section', 'glossary-term', 'glossary-position', 'glossary-search', 'glossary-view-long',
    'glossary-view-slides', 'glossary-sections']) node(id);
  ids['glossary-panels'].querySelectorAll = () => groups;
  const browser = node('glossary-browser', {classList: {add() {}}});
  browser.querySelectorAll = () => navs;
  const guide = node('guide', {tagName: 'DETAILS'});
  node('alphabetical-index', {parentElement: guide});
  const location = new URL('https://example.test/collection/GLOSSARY.html' + address);
  const history = {pushState(a, b, url) { location.href = String(url); }, replaceState(a, b, url) { location.href = String(url); }};
  vm.runInNewContext(source, {document, location, history, URL,
    window: {innerHeight: 800, addEventListener(name, callback) { events[name] = callback; }},
    localStorage: {getItem(key) { if (!storageAvailable) throw Error('blocked'); return storage.get(key); },
      setItem(key, value) { if (!storageAvailable) throw Error('blocked'); storage.set(key, value); }}});
  return {ids, groups, document, location, storage,
    select(section) { ids['glossary-section'].value = section; ids['glossary-section'].emit('change'); },
    jump(term) { ids['glossary-term'].value = term; ids['glossary-term'].emit('change'); },
    mode(mode) { ids['glossary-view-' + mode].emit('click'); },
    step(direction) { ids[(direction > 0 ? 'next-' : 'previous-') + '0'].emit('click'); },
    restore(url) { location.href = new URL(url, location).href; events.popstate(); },
    link(hash, modifiers = {}) {
      const target = node('', {href: new URL(hash, location).href});
      events['document:click']({target, ...modifiers});
    },
    key(key, target = document.activeElement) { ids['glossary-panels'].emit('keydown', {key, target, preventDefault() {}}); },
    visible() { return groups.filter(group => !group.hidden).flatMap(group => group.terms.filter(term => !term.hidden).map(term => term.dataset.glossaryTerm)); }};
}

test('the landing page presents section choices and Long shows only its chosen subject', () => {
  const p = page();
  assert.equal(p.ids['glossary-overview'].hidden, false);
  assert.equal(p.ids['glossary-panels'].hidden, true);
  assert.equal(p.ids['glossary-controls'].hidden, false);
  assert.deepEqual(p.visible(), []);
  p.select('linear');
  assert.deepEqual(p.visible(), ['scalar', 'kernel']);
  assert.equal(p.document.activeElement.id, 'heading-linear');
  assert.equal(p.ids['previous-0'].disabled, true);
  p.step(1);
  assert.deepEqual(p.visible(), ['seed', 'projector']);
  assert.equal(p.ids['next-0'].disabled, true);
  p.select('');
  assert.equal(p.ids['glossary-overview'].hidden, false);
  assert.equal(p.document.activeElement.id, 'glossary-sections');
});

test('slides retain one term, cross section boundaries, and return to the same entry in Long', () => {
  const p = page('?view=slides#scalar');
  assert.deepEqual(p.visible(), ['scalar']);
  p.step(1);
  assert.deepEqual(p.visible(), ['kernel']);
  assert.equal(p.document.activeElement.id, 'heading-kernel');
  assert.equal(p.location.hash, '#kernel');
  p.step(1);
  assert.deepEqual(p.visible(), ['seed']);
  assert.equal(p.ids['glossary-section'].value, 'operators');
  p.step(-1);
  assert.deepEqual(p.visible(), ['kernel']);
  p.mode('long');
  assert.deepEqual(p.visible(), ['scalar', 'kernel']);
  assert.equal(p.location.hash, '#kernel');
  p.mode('slides');
  assert.deepEqual(p.visible(), ['kernel']);
  p.jump('scalar');
  assert.deepEqual(p.visible(), ['scalar']);
  assert.equal(p.ids['previous-0'].disabled, true);
});

test('direct links, cross-subject search links, routes and history reveal their targets', () => {
  const p = page('?q=lost&view=slides&section=linear#projector');
  assert.deepEqual(p.visible(), ['projector'], 'A canonical term link wins over a stale section parameter');
  assert.equal(p.ids['glossary-search'].open, true);
  p.link('#kernel');
  assert.deepEqual(p.visible(), ['kernel'], 'Capture reveals before the shared reader focuses its destination');
  assert.equal(p.ids['glossary-search'].open, false);
  assert.equal(p.location.hash, '#projector', 'Capture leaves history and the query to the normal link handler');
  p.link('#seed', {ctrlKey: true});
  assert.deepEqual(p.visible(), ['kernel'], 'Modified clicks retain native browser behavior');
  p.restore('?view=long#seed');
  assert.deepEqual(p.visible(), ['seed', 'projector']);
  p.restore('?view=slides#kernel');
  assert.deepEqual(p.visible(), ['kernel']);
  p.link('#alphabetical-index');
  assert.equal(p.ids.guide.open, true);
  assert.equal(p.ids['glossary-overview'].hidden, false);
  p.restore('?view=slides#%E0%A4%A');
  assert.equal(p.ids['glossary-overview'].hidden, false, 'Malformed anchors leave a usable section browser');
});

test('mode preference is optional, visible term is preserved, and arrow keys leave controls alone', () => {
  const p = page('#linear', 'slides');
  assert.deepEqual(p.visible(), ['scalar']);
  assert.equal(p.location.searchParams.get('view'), 'slides', 'A saved view becomes part of the shareable address');
  p.mode('long');
  p.groups[0].terms[1].rect = {top: 100, bottom: 400};
  p.mode('slides');
  assert.deepEqual(p.visible(), ['kernel']);
  assert.equal(p.storage.get('glossary-view'), 'slides');
  p.key('ArrowRight', p.ids['heading-kernel']);
  assert.deepEqual(p.visible(), ['seed']);
  p.key('ArrowRight', {closest: () => ({})});
  assert.deepEqual(p.visible(), ['seed'], 'Selects, links and text fields keep their own keys');
  const noStorage = page('?view=unknown#kernel', 'slides', false);
  assert.deepEqual(noStorage.visible(), ['scalar', 'kernel']);
  noStorage.mode('slides');
  assert.deepEqual(noStorage.visible(), ['kernel']);
});
