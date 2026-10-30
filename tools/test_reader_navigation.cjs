const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/reader.js'), 'utf8');

function page(hash = '#L50') {
  const events = {};
  const tasks = [];
  const body = {};
  const document = {
    body, documentElement: {}, activeElement: body,
    querySelector() { return null; }, querySelectorAll() { return []; },
    getElementById(id) { return targets[id] || null; },
    addEventListener() {}
  };
  const disclosure = {open: false, parentElement: null, matches: selector => selector === 'details'};
  function target(id, parentElement = null) {
    const attrs = {};
    return {id, parentElement, textContent: 'Passage', scrolls: 0,
      matches() { return false; },
      hasAttribute: key => key in attrs, setAttribute: (key, value) => { attrs[key] = value; },
      getAttribute: key => attrs[key],
      focus() { document.activeElement = this; }, scrollIntoView() { this.scrolls++; }};
  }
  const targets = {L50: target('L50', disclosure), L51: target('L51'), 'résumé': target('résumé')};
  const location = new URL('https://example.test/read/paper-iv/atlas/v03.html' + hash);
  let pushes = 0;
  const history = {pushState(a, b, value) { pushes++; location.hash = value; }};
  const window = {addEventListener(name, callback) { events[name] = callback; }};
  vm.runInNewContext(source, {document, location, history, window, setTimeout: callback => tasks.push(callback)});
  return {document, targets, disclosure, location, events, pushes: () => pushes,
    flush() { while (tasks.length) tasks.shift()(); }};
}

let p = page();
p.events.load();
assert.equal(p.document.activeElement, p.targets.L50, 'A direct drawing link focuses the drawing');
assert.equal(p.targets.L50.getAttribute('tabindex'), '-1', 'The passage does not add a Tab stop');
assert.equal(p.disclosure.open, true, 'An enclosing disclosure opens');
assert.equal(p.pushes(), 0, 'Opening a direct link does not add a history entry');

p.location.hash = '#L51';
p.events.hashchange();
p.flush();
assert.equal(p.document.activeElement, p.targets.L51, 'Forward navigation focuses the new passage');
p.location.hash = '#L50';
p.events.hashchange();
p.flush();
assert.equal(p.document.activeElement, p.targets.L50, 'Back navigation restores passage focus');
assert.equal(p.pushes(), 0, 'History navigation does not add duplicate entries');

p = page();
const search = {id: 'search'};
p.document.activeElement = search;
p.events.load();
assert.equal(p.document.activeElement, search, 'Page loading preserves an active reading control');
assert.equal(p.targets.L50.scrolls, 0);

for (const hash of ['', '#missing', '#%ZZ']) {
  p = page(hash);
  assert.doesNotThrow(() => p.events.load());
  assert.doesNotThrow(() => p.events.hashchange());
  assert.doesNotThrow(() => p.flush());
  assert.equal(p.document.activeElement, p.document.body, 'Unknown or malformed hashes leave focus alone');
}
p = page('#r%C3%A9sum%C3%A9');
p.events.load();
assert.equal(p.document.activeElement, p.targets['résumé'], 'Encoded heading IDs resolve');

p = page();
p.location.hash = '#L51';
p.events.hashchange();
p.location.hash = '#missing';
p.flush();
assert.equal(p.document.activeElement, p.document.body, 'A stale navigation task cannot move focus');

p = page();
p.events.hashchange();
const visiblePassage = p.targets.L51;
p.targets.L50 = visiblePassage;
p.flush();
assert.equal(p.document.activeElement, visiblePassage, 'Focus resolves after other filters reveal the target');

p = page('#alias');
const heading = p.targets.L51;
p.targets.alias = {textContent: '', parentElement: null, nextElementSibling: heading,
  matches: selector => selector === 'a:not([href])'};
heading.matches = selector => selector === 'h1,h2,h3,h4,h5,h6';
p.events.load();
assert.equal(p.document.activeElement, heading, 'An empty legacy anchor focuses its following heading');
console.log('PASS: direct passage focus, Back/Forward, disclosures, existing focus, safe hashes and legacy anchors');
