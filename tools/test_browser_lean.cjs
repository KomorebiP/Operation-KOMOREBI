const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/lean-playground.js'), 'utf8');

test('legacy Lean bookmarks open our general workspace and replace the old history entry', () => {
  for (const href of ['https://example.test/lean/playground.html',
    'https://example.test/project/lean/playground.html?example=paper-xii#code=old']) {
    let destination;
    vm.runInNewContext(source, {URL, window: {location: {href, replace: value => { destination = value; }}}});
    assert.equal(destination, new URL('browser/index.html', href).href);
    assert.equal(new URL(destination).origin, new URL(href).origin);
    assert.equal(new URL(destination).search, '');
    assert.equal(new URL(destination).hash, '');
  }
});
