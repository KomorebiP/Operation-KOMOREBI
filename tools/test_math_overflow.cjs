const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/reader.js'), 'utf8');

function fixture(withObservers = true) {
  const events = {}, tasks = [], formulas = [], observed = new Set();
  let resized, mutated;
  const body = {};
  const document = {body, querySelector: () => null,
    querySelectorAll: selector => selector === 'span.arithmatex' ? formulas.filter(f => f.isConnected) : [],
    addEventListener() {}};
  const window = {addEventListener: (name, callback) => { events[name] = callback; }};
  const context = {document, window, requestAnimationFrame: callback => tasks.push(callback)};
  if (withObservers) {
    context.ResizeObserver = class {
      constructor(callback) { resized = callback; }
      observe(formula) { observed.add(formula); }
      unobserve(formula) { observed.delete(formula); }
    };
    context.MutationObserver = class {
      constructor(callback) { mutated = callback; }
      observe() {}
    };
  }
  function formula(width, contentWidth, attrs = {}) {
    const classes = new Set();
    const result = {clientWidth: width, scrollWidth: contentWidth, isConnected: true,
      nodeType: 1, matches: selector => selector === 'span.arithmatex', querySelector: () => null,
      closest: selector => selector === 'span.arithmatex' ? result : null,
      classList: {add: value => classes.add(value), remove: value => classes.delete(value)},
      hasAttribute: name => name in attrs, getAttribute: name => attrs[name],
      setAttribute: (name, value) => { attrs[name] = value; },
      removeAttribute: name => { delete attrs[name]; }, attrs, classes};
    formulas.push(result);
    return result;
  }
  vm.runInNewContext(source, context);
  return {events, observed, formula, flush() { while (tasks.length) tasks.shift()(); },
    resize() { resized(); }, mutate(records) { mutated(records); }};
}

let p = fixture();
const fitting = p.formula(100, 100), wide = p.formula(220, 330), hidden = p.formula(0, 330);
p.flush();
assert.equal(fitting.attrs.tabindex, undefined, 'Fitting inline math does not add a Tab stop');
assert.equal(hidden.attrs.tabindex, undefined, 'Collapsed content is not marked scrollable');
assert.equal(wide.attrs.tabindex, '0');
assert.equal(wide.attrs.role, 'group');
assert.match(wide.attrs['aria-label'], /Scroll horizontally/);
assert.equal(wide.classes.has('math-overflow'), true);
const overhang = p.formula(100, 110);
overhang.querySelector = () => ({getBoundingClientRect: () => ({width: 98})});
p.events.resize(); p.flush();
assert.equal(overhang.attrs.tabindex, undefined, 'Short SVG glyph overhang does not become a scrolling equation');
assert.equal(overhang.classes.has('math-fits'), true);

wide.clientWidth = 400; p.resize(); p.flush();
assert.deepEqual(wide.attrs, {}, 'Growing the column removes only the temporary scroll controls');
assert.equal(wide.classes.has('math-overflow'), false);
wide.clientWidth = 220; p.events.resize(); p.flush();
assert.equal(wide.attrs.tabindex, '0', 'Narrowing the column restores keyboard scrolling');
wide.attrs['aria-label'] = 'Updated by the author';
wide.clientWidth = 400; p.resize(); p.flush();
assert.equal(wide.attrs['aria-label'], 'Updated by the author', 'Later accessible names survive cleanup');

const named = p.formula(100, 300, {tabindex: '-1', role: 'region', 'aria-label': 'Original equation', title: 'Original help'});
p.events.resize(); p.flush();
assert.equal(named.attrs.tabindex, '-1');
assert.equal(named.attrs['aria-label'], 'Original equation');
named.clientWidth = 400; p.resize(); p.flush();
assert.deepEqual(named.attrs, {tabindex: '-1', role: 'region', 'aria-label': 'Original equation', title: 'Original help'});

const added = p.formula(180, 500);
p.mutate([{target: {}, addedNodes: [added]}]); p.flush();
assert.equal(added.attrs.tabindex, '0', 'New search or notation results gain scrolling');
fitting.scrollWidth = 250;
p.mutate([{target: fitting, addedNodes: []}]); p.flush();
assert.equal(fitting.attrs.tabindex, '0', 'Delayed MathJax output is measured after insertion');
added.isConnected = false; p.events.resize(); p.flush();
assert.equal(p.observed.has(added), false, 'Removed results stop being observed');
assert.deepEqual(added.attrs, {});
fitting.scrollWidth = 101; p.resize(); p.flush();
assert.equal(fitting.attrs.tabindex, undefined, 'One-pixel rounding does not create a scroll stop');

p = fixture(false);
const fallback = p.formula(150, 400); p.flush();
assert.equal(fallback.attrs.tabindex, '0', 'Initial layout and resize work without observer APIs');
fallback.clientWidth = 450; p.events.resize(); p.flush();
assert.equal(fallback.attrs.tabindex, undefined);
console.log('PASS: inline formula scrolling, resized text, delayed math, live results and accessible-name preservation');
