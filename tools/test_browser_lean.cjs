const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function fixture() {
  const nodes = {};
  for (const id of ['open', 'close', 'external', 'slot', 'status', 'original', 'help']) {
    nodes[id] = {hidden: true, listeners: {}, textContent: '', children: [],
      addEventListener(name, fn) {this.listeners[name] = fn;},
      replaceChildren(...children) {this.children = children;},
      focus() {this.focused = true;}};
  }
  nodes.external.href = 'https://live.lean-lang.org/#project=MathlibDemo&code=original';
  const root = {querySelector: s => nodes[s.match(/data-lean-(.*)\]/)[1]]};
  const created = [];
  const document = {querySelector: () => root, createElement(tag) {
    const el = {tag, attributes: {}, setAttribute(k, v) {this.attributes[k] = v;},
      remove() {this.removed = true;}};
    created.push(el); return el;
  }};
  vm.runInNewContext(fs.readFileSync('website/assets/lean-playground.js', 'utf8'), {document});
  return {nodes, created, click: key => nodes[key].listeners.click()};
}

test('external editor is opt-in and loading never assigns a successful proof result', () => {
  const f = fixture();
  assert.equal(f.created.length, 0);
  assert.equal(f.nodes.open.hidden, false);
  f.click('open');
  const frame = f.created[0];
  assert.equal(frame.tag, 'iframe');
  assert.equal(frame.src, f.nodes.external.href);
  assert.equal(frame.referrerPolicy, 'no-referrer');
  assert.match(frame.title, /Paper XII/);
  assert.equal(f.nodes.slot.hidden, false);
  assert.equal(f.nodes.original.open, false);
  assert.match(f.nodes.status.textContent, /All Messages/);
  assert.doesNotMatch(f.nodes.status.textContent, /accepted|verified|success|passed/i);
});

test('restore replaces the session and close releases it and returns keyboard focus', () => {
  const f = fixture();f.click('open');f.click('open');
  assert.equal(f.created[0].removed, true);
  assert.equal(f.created.length, 2);
  assert.equal(f.created[1].src, f.nodes.external.href);
  f.click('close');
  assert.equal(f.created[1].removed, true);
  assert.equal(f.nodes.slot.hidden, true);
  assert.equal(f.nodes.slot.children.length, 0);
  assert.equal(f.nodes.original.open, true);
  assert.equal(f.nodes.close.hidden, true);
  assert.equal(f.nodes.open.focused, true);
});
