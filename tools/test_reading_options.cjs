const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/reader.js'), 'utf8');
const key = 'komorebi.reading.showPassageTools';

function openChapter(storage, present = true) {
  const groups = [{hidden: false}, {hidden: false}];
  const options = {hidden: true};
  const events = {};
  const checkbox = {checked: false, addEventListener: (event, handler) => { events[event] = handler; }};
  const document = {
    querySelector(selector) {
      if (!present) return null;
      if (selector === '.reading-options') return options;
      if (selector === '#show-passage-tools') return checkbox;
      return null;
    },
    querySelectorAll(selector) { return selector === '.readable-chapter .passage-tools' ? groups : []; },
    addEventListener() {}
  };
  vm.runInNewContext(source, {document, localStorage: storage, window: {addEventListener() {}},
    requestAnimationFrame: callback => callback()});
  return {groups, options, checkbox, change(show) { checkbox.checked = show; events.change(); }};
}

const saved = new Map();
const storage = {getItem: key => saved.get(key) ?? null, setItem: (key, value) => saved.set(key, value)};
let chapter = openChapter(storage);
assert.equal(chapter.options.hidden, false);
assert.equal(chapter.checkbox.checked, false);
assert.ok(chapter.groups.every(group => group.hidden));
assert.equal(saved.size, 0, 'Opening a chapter does not write a preference');
chapter.change(true);
assert.ok(chapter.groups.every(group => !group.hidden));
assert.equal(saved.get(key), 'true');
chapter = openChapter(storage);
assert.equal(chapter.checkbox.checked, true);
assert.ok(chapter.groups.every(group => !group.hidden));
chapter.change(false);
assert.equal(saved.get(key), 'false');
assert.ok(openChapter(storage).groups.every(group => group.hidden));

const unavailable = {getItem() { throw new Error('Storage blocked'); }, setItem() { throw new Error('Storage blocked'); }};
chapter = openChapter(unavailable);
assert.equal(chapter.options.hidden, false);
assert.ok(chapter.groups.every(group => group.hidden));
chapter.change(true);
assert.ok(chapter.groups.every(group => !group.hidden));
chapter.change(false);
assert.ok(chapter.groups.every(group => group.hidden));
assert.doesNotThrow(() => openChapter(unavailable, false), 'Pages without reading controls remain usable');
console.log('PASS: reading view, both toggles, cross-chapter preference and blocked storage');
