const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../website/assets/reader.js'), 'utf8');

function page(hash = '#L50', withSidebar = false, delayedLayout = false) {
  const events = {};
  const listeners = {};
  const tasks = [];
  const body = {};
  const elements = {};
  const document = {
    body, documentElement: {}, activeElement: body,
    querySelector(selector) { return elements[selector] || null; }, querySelectorAll() { return []; },
    getElementById(id) { return targets[id] || null; },
    addEventListener() {}
  };
  const disclosure = {open: false, parentElement: null, matches: selector => selector === 'details'};
  function target(id, parentElement = null) {
    const attrs = {};
    return {id, parentElement, textContent: 'Passage', scrolls: 0, isConnected: true,
      matches() { return false; },
      hasAttribute: key => key in attrs, setAttribute: (key, value) => { attrs[key] = value; },
      getAttribute: key => attrs[key],
      focus() { document.activeElement = this; }, scrollIntoView() { this.scrolls++; }};
  }
  const targets = {L50: target('L50', disclosure), L51: target('L51'), 'résumé': target('résumé')};
  const location = new URL('https://example.test/read/paper-iv/atlas/v03.html' + hash);
  let pushes = 0;
  const history = {pushState(a, b, value) { pushes++; location.hash = value; }};
  const window = {addEventListener(name, callback) {
    (listeners[name] ||= []).push(callback);
    events[name] = (...args) => listeners[name].forEach(listener => listener(...args));
  }};
  let finishMath, failMath, finishFonts;
  if (delayedLayout) {
    window.MathJax = {startup: {promise: new Promise((resolve, reject) => { finishMath = resolve; failMath = reject; })}};
    document.fonts = {ready: new Promise(resolve => { finishFonts = resolve; })};
  }
  let sidebar, resizeCallback;
  if (withSidebar) {
    const heights = {summary:44, returns:44}, styles = {}, links = [];
    const summary = {getBoundingClientRect:()=>({height:heights.summary})};
    const returns = {getBoundingClientRect:()=>({height:heights.returns})};
    const current = {textContent:''};
    const article = {contains:target=>Object.values(targets).includes(target),style:{
      setProperty:(key,value)=>{styles[key]=value;},removeProperty:key=>{delete styles[key];}}};
    for (const [id,top] of [['L50',-10],['L51',170]]) {
      const attrs = {};
      links.push({hash:'#'+id,textContent:id,attrs,setAttribute:(key,value)=>{attrs[key]=value;},removeAttribute:key=>{delete attrs[key];}});
      targets[id].matches = selector=>selector==='h2,h3,h4,h5,h6';
      targets[id].getBoundingClientRect=()=>({top});
    }
    const contents = {open:false,querySelector:selector=>selector==='summary'?summary:current,
      querySelectorAll:()=>links,addEventListener(){}};
    const wide = {matches:false,addEventListener(name,callback){sidebar.change=callback;}};
    window.matchMedia=()=>wide;
    elements['#chapter-text']=article;
    elements['.chapter-sidebar']={querySelector:selector=>selector==='.reading-outline'?contents:returns};
    sidebar={styles,links,contents,wide,
      resize(summaryHeight,returnHeight){heights.summary=summaryHeight;heights.returns=returnHeight;resizeCallback();}};
  }
  vm.runInNewContext(source, {document, location, history, window, setTimeout: callback => tasks.push(callback),
    requestAnimationFrame:callback=>tasks.push(callback),ResizeObserver:class {constructor(callback){resizeCallback=callback;}observe(){}}});
  return {document, targets, disclosure, location, events, pushes: () => pushes,
    sidebar, finishMath, failMath, finishFonts,
    flush() { while (tasks.length) tasks.shift()(); },
    async settle() { await new Promise(setImmediate); this.flush(); }};
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

p=page('',true);p.flush();
assert.equal(p.sidebar.styles['--reading-clearance'],'100px','Mobile passage spacing clears both sticky control rows');
assert.equal(p.sidebar.links[0].attrs['aria-current'],'location');
p.sidebar.resize(72,88);p.flush();
assert.equal(p.sidebar.styles['--reading-clearance'],'172px','Wrapped or resized controls update passage spacing');
assert.equal(p.sidebar.links[1].attrs['aria-current'],'location','The current section follows the same visible boundary');
p.sidebar.wide.matches=true;p.sidebar.change();p.flush();
assert.equal(p.sidebar.styles['--reading-clearance'],undefined,'Desktop reading does not reserve a mobile control offset');
assert.equal(p.sidebar.contents.open,true);

async function delayedNavigation() {
  let p = page('#L50', false, true);
  p.events.load(); p.flush();
  assert.equal(p.targets.L50.scrolls, 1, 'The passage is usable before math finishes');
  p.finishMath(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 1, 'Font loading also participates in the final layout');
  p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 2, 'The linked passage is realigned after math and fonts settle');
  assert.equal(p.pushes(), 0, 'Final layout correction does not add a history entry');

  for (const event of ['wheel', 'touchstart', 'pointerdown', 'keydown']) {
    p = page('#L50', false, true);
    p.events.load(); p.events[event]();
    p.finishMath(); p.finishFonts(); await p.settle();
    assert.equal(p.targets.L50.scrolls, 1, `${event} cancels the late correction`);
    assert.equal(p.document.activeElement, p.targets.L50, 'Cancellation does not move focus');

    p = page('#L50', false, true);
    p.events[event](); p.events.load();
    p.finishMath(); p.finishFonts(); await p.settle();
    assert.equal(p.targets.L50.scrolls, 0, `${event} before page load preserves the reader's position`);
  }

  p = page('#L50', false, true);
  p.events.load(); p.document.activeElement = {id: 'search'};
  p.finishMath(); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 1, 'A changed reading control keeps focus and position');

  p = page('#L50', false, true);
  p.events.load(); p.location.hash = '#L51';
  p.finishMath(); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 1, 'A changed fragment invalidates a pending correction');

  p = page('#L50', false, true);
  p.events.load(); p.targets.L50.isConnected = false;
  p.finishMath(); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 1, 'Removed passages cannot reclaim the viewport');

  p = page('#L50', false, true);
  p.events.load(); p.location.hash = '#L51'; p.events.hashchange(); p.flush();
  p.finishMath(); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 1, 'Back/Forward supersedes the earlier destination');
  assert.equal(p.targets.L51.scrolls, 2, 'The latest history destination receives the final correction');
  assert.equal(p.pushes(), 0);

  p = page('#L50', false, true);
  p.events.load(); p.events.hashchange(); p.flush();
  p.finishMath(); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 3, 'Repeated navigation to one fragment has only one final correction');

  p = page('#L50', false, true);
  p.events.load(); p.finishMath(); p.finishFonts();
  await new Promise(setImmediate);
  p.events.wheel(); p.flush();
  assert.equal(p.targets.L50.scrolls, 1, 'Reader input cancels even an already queued animation frame');

  p = page('#L50', false, true);
  p.events.load(); p.failMath(new Error('Math runtime unavailable')); p.finishFonts(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 2, 'A failed optional runtime still permits navigation');

  p = page(); p.events.load(); await p.settle();
  assert.equal(p.targets.L50.scrolls, 2, 'Plain pages without math or font promises also settle');
  console.log('PASS: direct passage focus, delayed math/fonts, interaction cancellation, Back/Forward and safe hashes');
}
delayedNavigation().catch(error => { console.error(error); process.exitCode = 1; });
