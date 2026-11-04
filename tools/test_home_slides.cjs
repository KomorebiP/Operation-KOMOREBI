const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/home-slides.js'), 'utf8');

function page(hash = '') {
  const targets = {};
  const document = {activeElement: null, getElementById: id => targets[id] || null};
  function element(id, textContent = '') {
    const listeners = {};
    const attributes = {};
    const node = {id, textContent, hidden: false, attributes,
      setAttribute: (key, value) => { attributes[key] = value; },
      addEventListener: (name, callback) => { (listeners[name] ||= []).push(callback); },
      emit: (name, event = {}) => { (listeners[name] || []).forEach(callback => callback(event)); },
      focus: () => { document.activeElement = node; },
      contains: target => target === node || target?.parent === node};
    if (id) targets[id] = node;
    return node;
  }
  function showcase(prefix, names) {
    const tabs = names.map(name => element(prefix + '-topic-' + name, name));
    const slides = names.map(name => element(prefix + '-' + name));
    const topics = element();
    topics.hidden = true;
    topics.querySelectorAll = () => tabs;
    const controls = element();
    controls.hidden = true;
    const position = element();
    const previous = element();
    const next = element();
    const feature = element();
    const classes = new Set();
    const nodes = {'.home-topics': topics, '.home-slide-controls': controls,
      '.home-slide-position': position, '[data-slide-previous]': previous,
      '[data-slide-next]': next, '.home-feature, .home-entry-feature': feature};
    return {tabs, slides, topics, controls, position, previous, next, feature, classes,
      querySelector: selector => nodes[selector], querySelectorAll: () => slides,
      classList: {add: name => classes.add(name)}};
  }
  const entry = showcase('home-entry', ['Introduction', 'Mathematics', 'Proofs', 'Software']);
  const research = showcase('home-research', ['Wavelets', 'Euler', 'Factorials', 'Quantum', 'Counting', 'Polynomials']);
  const nested = element('nested-proof-link');
  nested.parent = entry.slides[2];
  const instances = [entry, research];
  document.querySelectorAll = () => instances;
  const location = {hash};
  const windowEvents = {};
  const window = {addEventListener: (name, callback) => { (windowEvents[name] ||= []).push(callback); }};
  vm.runInNewContext(source, {document, location, window});
  return {entry, research, document,
    hash: value => { location.hash = value; windowEvents.hashchange.forEach(callback => callback()); }};
}

function selected(showcase) {
  return showcase.slides.findIndex(slide => !slide.hidden);
}

test('entry and research tabs and arrows operate independently', () => {
  const {entry, research} = page();
  assert.equal(selected(entry), 0);
  assert.equal(selected(research), 0);
  entry.tabs[2].emit('click');
  assert.equal(selected(entry), 2);
  assert.equal(selected(research), 0);
  research.next.emit('click');
  assert.equal(selected(research), 1);
  assert.equal(selected(entry), 2);
  assert.match(entry.position.textContent, /^03 \/ 04 · Proofs$/);
  assert.match(research.position.textContent, /^02 \/ 06 · Euler$/);
  entry.next.emit('click');
  entry.next.emit('click');
  assert.equal(selected(entry), 0);
  entry.previous.emit('click');
  assert.equal(selected(entry), 3);
});

test('keyboard selection wraps and keeps one tab in the tab order per selector', () => {
  const {entry, research, document} = page();
  const key = value => entry.topics.emit('keydown', {key: value, preventDefault() {}});
  key('ArrowLeft');
  assert.equal(selected(entry), 3);
  assert.equal(document.activeElement, entry.tabs[3]);
  assert.deepEqual(entry.tabs.map(tab => tab.tabIndex), [-1, -1, -1, 0]);
  assert.deepEqual(entry.tabs.map(tab => tab.attributes['aria-selected']), ['false', 'false', 'false', 'true']);
  key('Home');
  assert.equal(selected(entry), 0);
  key('End');
  assert.equal(selected(entry), 3);
  key('ArrowRight');
  assert.equal(selected(entry), 0);
  entry.topics.emit('keydown', {key: 'ArrowRight', ctrlKey: true});
  assert.equal(selected(entry), 0);
  assert.equal(selected(research), 0);
});

test('a linked panel or its contents is revealed only in its own selector', () => {
  const p = page('#home-research-Quantum');
  assert.equal(selected(p.research), 3);
  assert.equal(selected(p.entry), 0);
  p.hash('#nested-proof-link');
  assert.equal(selected(p.entry), 2);
  assert.equal(selected(p.research), 3);
  p.hash('#not-a-panel');
  p.hash('#%invalid');
  assert.equal(selected(p.entry), 2);
  assert.equal(selected(p.research), 3);
});

test('touch swipes switch their own panel while vertical scroll and links stay alone', () => {
  const {entry, research} = page();
  const touch = (x, y, interactive = false) => ({isPrimary: true, pointerType: 'touch',
    pointerId: 1, clientX: x, clientY: y, target: {closest: () => interactive}});
  entry.feature.emit('pointerdown', touch(200, 100));
  entry.feature.emit('pointerup', touch(100, 100));
  assert.equal(selected(entry), 1);
  assert.equal(selected(research), 0);
  entry.feature.emit('pointerdown', touch(200, 100));
  entry.feature.emit('pointerup', touch(180, 200));
  assert.equal(selected(entry), 1);
  entry.feature.emit('pointerdown', touch(200, 100, true));
  entry.feature.emit('pointerup', touch(100, 100));
  assert.equal(selected(entry), 1);
  entry.feature.emit('pointerdown', touch(200, 100));
  entry.feature.emit('pointercancel');
  entry.feature.emit('pointerup', touch(100, 100));
  assert.equal(selected(entry), 1);
});

test('enhancement supplies accessible roles and reveals both selectors', () => {
  const {entry, research} = page();
  for (const instance of [entry, research]) {
    assert.equal(instance.topics.hidden, false);
    assert.equal(instance.controls.hidden, false);
    assert.equal(instance.topics.attributes.role, 'tablist');
    assert.equal(instance.classes.has('home-slides-ready'), true);
    for (let i = 0; i < instance.slides.length; i++) {
      assert.equal(instance.tabs[i].attributes.role, 'tab');
      assert.equal(instance.slides[i].attributes.role, 'tabpanel');
      assert.equal(instance.slides[i].attributes['aria-labelledby'], instance.tabs[i].id);
    }
  }
});

test('other pages can load the script without a homepage selector', () => {
  vm.runInNewContext(source, {document: {querySelectorAll: () => []}});
});
