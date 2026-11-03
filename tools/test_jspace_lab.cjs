const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../website/assets/jspace-lab.js'), 'utf8');

function shell(hash = '') {
  const nodes = new Map(), timers = new Map();
  let nextTimer = 0, resets = 0, tab, demo, focus = 0;
  function node(id) {
    if (!nodes.has(id)) nodes.set(id, {hidden: true, disabled: true, dataset: {}, textContent: '',
      listeners: {}, addEventListener(event, fn) { this.listeners[event] = fn; },
      click() { this.listeners.click?.(); }, focus() { focus++; }});
    return nodes.get(id);
  }
  const buttons = ['edit', 'relay', 'persistence'].map(guide => {
    const b = node(guide); b.dataset.jlGuide = guide; return b;
  });
  node('j-lab').querySelectorAll = () => buttons;
  const frame = node('jl-frame'); frame.dataset.src = 'assets/j-space/causal-lab.html?v=frozen'; frame.contentWindow = {};
  const document = {getElementById: node};
  vm.runInNewContext(source, {document, window: {location: {hash}},
    setTimeout(fn) { const id = ++nextTimer; timers.set(id, fn); return id; },
    clearTimeout(id) { timers.delete(id); }});
  return {node, frame, buttons, timers,
    get result() { return {resets, tab, demo, focus}; },
    makeReady() {
      frame.contentWindow = {JCausalLab: {resetDemo() {resets++;}}, JRelayLab: {}, JChallengeLab: {},
        document: {querySelector(selector) {return {click() {tab = selector;}};}, getElementById(id) {return {click() {demo = id;}};}}};
      frame.onload();
    },
    tick() { const [id, fn] = timers.entries().next().value; timers.delete(id); fn(); }
  };
}

test('models load only on request; ordinary reopening preserves a run', () => {
  const s = shell();
  assert.equal(s.frame.src, undefined);
  assert.equal(s.node('jl-launch').disabled, false);
  s.node('jl-launch').click();
  assert.equal(s.frame.src, s.frame.dataset.src);
  s.makeReady();
  assert.equal(s.result.resets, 1);
  assert.equal(s.result.tab, '[data-tab="causal"]');
  s.node('jl-launch').click();
  assert.equal(s.result.resets, 1);
  assert.match(s.node('jl-status').textContent, /Lab ready/);
});

test('latest guided selection wins while the instrument is loading', () => {
  const s = shell();
  s.buttons[0].click(); s.buttons[1].click(); s.buttons[2].click();
  s.makeReady();
  assert.equal(s.result.resets, 1);
  assert.equal(s.result.tab, '[data-tab="challenge"]');
  assert.equal(s.result.demo, 'tDemo');
  s.buttons[1].click();
  assert.equal(s.result.resets, 2);
  assert.equal(s.result.tab, '[data-tab="relay"]');
  assert.equal(s.result.demo, 'mDemo');
});

test('network failure has a retry and old callbacks cannot reset a new run', () => {
  const s = shell();
  s.buttons[1].click(); const stale = s.frame.onload;
  s.frame.onerror();
  assert.match(s.node('jl-status').textContent, /Retry/);
  s.node('jl-launch').click();
  const current = s.frame.onload;
  s.makeReady(); stale();
  assert.equal(s.result.resets, 1);
  assert.notEqual(current, stale);
});

test('an unfinished model initialization times out instead of polling forever', () => {
  const s = shell(); s.node('jl-launch').click(); s.frame.onload();
  for (let i = 0; i < 300; i++) s.tick();
  assert.equal(s.timers.size, 0);
  assert.match(s.node('jl-status').textContent, /could not finish loading/);
  s.node('jl-launch').click(); s.makeReady();
  assert.equal(s.result.resets, 1);
});

test('only declared guide fragments can launch the app automatically', () => {
  for (const hash of ['#unknown', '#toString', '#__proto__']) {
    const s = shell(hash); assert.equal(s.frame.src, undefined);
  }
  const s = shell('#relay'); s.makeReady();
  assert.equal(s.result.demo, 'mDemo');
  assert.equal(s.result.focus, 0);
});
