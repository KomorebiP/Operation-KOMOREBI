'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

// Exercise the actual math functions without initializing the DOM.
const source = fs.readFileSync(path.join(__dirname, '../website/assets/smith-chart.js'), 'utf8');
const marker = 'const fmt=';
const cut = source.indexOf(marker);
assert.ok(cut >= 0 && source.indexOf(marker, cut + 1) < 0, 'math prefix is unambiguous');
const sandbox = {};
vm.runInNewContext(source.slice(0, cut) +
  '\nglobalThis.probe={smithQuantile,smithCdf};})();', sandbox, {timeout: 5000});
const {smithQuantile, smithCdf} = sandbox.probe;

test('quantiles remain distinct immediately around the half-turn', () => {
  for (const rho of [.70, .84, .94, .97]) {
    const masses = [.5 - 1e-13, .5, .5 + 1e-13];
    const angles = masses.map(mass => smithQuantile(rho, mass));
    assert.ok(angles[0] < angles[1] && angles[1] < angles[2], `rho=${rho}`);
    for (let i = 0; i < masses.length; i++) {
      assert.ok(Math.abs(smithCdf(rho, angles[i]) - masses[i]) < 5e-14, `rho=${rho}, mass=${masses[i]}`);
    }
  }
});

test('quantile grid stays monotone and inverts the CDF', () => {
  for (const rho of [.70, .84, .94, .97]) for (const count of [32, 64, 96, 128]) {
    let previous = -1;
    for (let j = 0; j <= count; j++) {
      const mass = j / count;
      const angle = smithQuantile(rho, mass);
      assert.ok(angle > previous, `rho=${rho}, count=${count}, index=${j}`);
      assert.ok(Math.abs(smithCdf(rho, angle) - mass) < 2e-12, `rho=${rho}, count=${count}, index=${j}`);
      previous = angle;
    }
  }
});

test('representable points near the half-turn do not move backwards', () => {
  for (const rho of [.70, .84, .94, .97]) {
    let previous = -1;
    for (let k = -64; k <= 64; k++) {
      const mass = .5 + k * Number.EPSILON / 2;
      const angle = smithQuantile(rho, mass);
      assert.ok(angle >= previous, `rho=${rho}, k=${k}`);
      assert.ok(Math.abs(smithCdf(rho, angle) - mass) < 5e-14, `rho=${rho}, k=${k}`);
      previous = angle;
    }
  }
});

test('packet note distinguishes the boundary from a near-boundary interior load', () => {
  const renderCut = source.indexOf('function render(){');
  assert.ok(renderCut > cut, 'packet-rendering prefix is present');
  const elements = new Map();
  const sandboxRender = {document: {getElementById(id) {
    if (!elements.has(id)) elements.set(id, {textContent: ''});
    return elements.get(id);
  }}};
  vm.runInNewContext(source.slice(0, renderCut) +
    '\nglobalThis.probe={states,renderExactPackets};})();', sandboxRender, {timeout: 5000});
  const {states, renderExactPackets} = sandboxRender.probe;
  states.special = null; states.r = 1e-10; states.x = 0; states.z0 = 50;
  renderExactPackets();
  assert.match(elements.get('exact-disk-note').textContent, /inside the disk but within/);
  states.special = 'open';
  renderExactPackets();
  assert.match(elements.get('exact-disk-note').textContent, /\|Γ\| = 1 lies outside/);
  states.special = null; states.r = 25; states.x = 25;
  renderExactPackets();
  assert.match(elements.get('exact-disk-note').textContent, /angular mean-square/);
});
