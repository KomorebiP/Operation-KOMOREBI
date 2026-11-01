const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/reading-tools.js'), 'utf8');
const key = 'komorebi.reading.text';

function chapter(storage, present = true) {
  function control(value = 'default') {
    const events = {};
    return {value, addEventListener: (name, fn) => {events[name] = fn;},
      fire(name) {events[name]();}};
  }
  const size = control(), font = control(), reset = control();
  const article = {dataset:{}};
  const settings = {hidden:true, querySelector(selector) {
    return {'#reading-text-size':size, '#reading-text-font':font, '.reading-display-reset':reset}[selector];
  }};
  const events = {};
  const document = {
    querySelectorAll: () => [], addEventListener() {},
    querySelector: selector => present ? {'.reading-display':settings,'#chapter-text':article}[selector] : null
  };
  vm.runInNewContext(source, {document, localStorage:storage, Event:class {},
    window:{dispatchEvent() {}, addEventListener(name, fn) {events[name] = fn;}}});
  return {settings, article, size, font, reset, storageChanged: event => events.storage(event)};
}

const values = new Map();
const storage = {getItem: name => values.get(name) ?? null,
  setItem: (name, value) => values.set(name,value), removeItem: name => values.delete(name)};
let page = chapter(storage);
assert.equal(page.settings.hidden,false);
assert.equal(page.article.dataset.textSize,'default');
assert.equal(values.size,0,'Opening a chapter does not store a choice');
page.size.value = 'larger';page.size.fire('change');
page.font.value = 'serif';page.font.fire('change');
page = chapter(storage);
assert.equal(page.size.value,'larger','The size survives navigation to another paper');
assert.equal(page.font.value,'serif');
page.reset.fire('click');
assert.equal(page.article.dataset.textSize,'default');
assert.equal(page.article.dataset.textFont,'default');
assert.equal(values.has(key),false,'Reset removes the saved preference');
for (const invalid of ['bad JSON','null','42','"large"','{"size":"huge","font":"unknown"}']) {
  values.set(key,invalid);page = chapter(storage);
  assert.equal(page.article.dataset.textSize,'default');
  assert.equal(page.article.dataset.textFont,'default');
}
values.set(key,'{"size":"large","font":"serif"}');
page.storageChanged({key});
assert.equal(page.size.value,'large','Another open reader can update the preference');
values.clear();page.storageChanged({key:null});
assert.equal(page.font.value,'default','Cleared storage restores the defaults');
const blocked = {getItem() {throw Error('blocked');},setItem() {throw Error('blocked');},removeItem() {throw Error('blocked');}};
page = chapter(blocked);page.size.value = 'larger';
assert.doesNotThrow(() => page.size.fire('change'));
assert.equal(page.article.dataset.textSize,'larger','Text settings work even without storage');
assert.doesNotThrow(() => page.reset.fire('click'));
assert.doesNotThrow(() => chapter(blocked,false),'Pages without text controls remain usable');
console.log('PASS: text settings, cross-paper persistence, reset, malformed and blocked storage');
