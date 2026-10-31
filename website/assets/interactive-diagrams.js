import {reconstruct, refine, recover, haarAnalyze, haar} from './interactive-diagrams-core.mjs';

const byId = id => document.getElementById(id);
const text = (id, value) => { byId(id).textContent = value; };
const number = id => Number(byId(id).value);
const vectorText = values => '(' + values.join(', ') + ')';
const sliders = [...document.querySelectorAll('.math-lab input[type="range"]')];
function sliderValues() {
  for (const input of sliders) text(input.id + '-value', input.value);
}
const NS = 'http://www.w3.org/2000/svg';
function svgNode(tag, attrs = {}, value) {
  const node = document.createElementNS(NS, tag);
  for (const [key, val] of Object.entries(attrs)) node.setAttribute(key, String(val));
  if (value !== undefined) node.textContent = value;
  return node;
}
function picture(id, width, height, description) {
  const container = byId(id);
  container.setAttribute('aria-label', description);
  const svg = svgNode('svg', {viewBox: `0 0 ${width} ${height}`, 'aria-hidden': 'true', focusable: 'false'});
  container.replaceChildren(svg);
  return svg;
}
function label(svg, x, y, value, className = '', anchor = 'middle') {
  svg.append(svgNode('text', {x, y, class: className, 'text-anchor': anchor}, value));
}
function verdict(id, message, loss) {
  const node = byId(id);
  node.textContent = message;
  node.dataset.loss = String(loss);
}

function drawPackets(matrix, vector, keep, result) {
  const svg = picture('packet-diagram', 620, 310,
    `Input ${vectorText(vector)}. Direct output ${vectorText(result.direct)}. Output from kept blocks ${vectorText(result.rebuilt)}. Residual ${vectorText(result.residual)}.`);
  label(svg, 75, 28, 'INPUT', 'diagram-heading');
  label(svg, 535, 28, 'KEPT OUTPUT', 'diagram-heading');
  label(svg, 305, 28, 'FOUR TRANSFER BLOCKS', 'diagram-heading');
  const ys = [100, 242];
  keep.forEach((kept, i) => {
    const row = Math.floor(i / 2), column = i % 2;
    const start = ys[column], end = ys[row];
    const path = svgNode('path', {d: `M 122 ${start} C 245 ${start}, 365 ${end}, 488 ${end}`,
      class: kept ? 'packet-wire' : 'packet-wire omitted'});
    svg.append(path);
  });
  // Offset the crossing labels so both contributions remain readable.
  const positions = [[305, 94], [380, 143], [230, 205], [305, 236]];
  result.contributions.forEach((value, i) => {
    const [x, y] = positions[i];
    const group = svgNode('g', {class: keep[i] ? 'packet-contribution' : 'packet-contribution omitted'});
    group.append(svgNode('rect', {x: x-54, y: y-20, width: 108, height: 32, rx: 5}));
    group.append(svgNode('text', {x, y, 'text-anchor': 'middle', class: 'contribution-full'}, `${matrix[i]} × ${vector[i % 2]} = ${value}`));
    group.append(svgNode('text', {x, y, 'text-anchor': 'middle', class: 'contribution-short'}, value));
    svg.append(group);
  });
  for (let i = 0; i < 2; i++) {
    svg.append(svgNode('circle', {cx: 75, cy: ys[i], r: 40, class: 'packet-node'}));
    svg.append(svgNode('circle', {cx: 535, cy: ys[i], r: 40, class: 'packet-node output-node'}));
    label(svg, 75, ys[i]+8, vector[i], 'diagram-number');
    label(svg, 535, ys[i]+8, result.rebuilt[i], 'diagram-number');
    label(svg, 75, ys[i]+57, `x${i === 0 ? '₁' : '₂'}`, 'diagram-coordinate');
    label(svg, 535, ys[i]+57, `y${i === 0 ? '₁' : '₂'}`, 'diagram-coordinate');
  }
}

function updatePackets() {
  const inputs = Array.from({length: 4}, (_, i) => byId('matrix-' + i));
  const invalid = inputs.filter(input => input.value.trim() === '' || !input.checkValidity() || !Number.isInteger(Number(input.value)));
  for (const input of inputs) {
    input.setAttribute('aria-invalid', String(invalid.includes(input)));
    input.setAttribute('aria-describedby', 'matrix-error');
  }
  byId('matrix-error').hidden = invalid.length === 0;
  if (invalid.length) {
    text('matrix-error', 'Use whole numbers from −9 to 9. The diagram keeps the last valid calculation until all four entries are valid.');
    return;
  }
  const matrix = inputs.map(input => Number(input.value));
  const vector = [number('vector-0'), number('vector-1')];
  const keep = Array.from({length: 4}, (_, i) => byId('block-' + i).checked);
  const result = reconstruct(matrix, vector, keep);
  result.contributions.forEach((value, i) => text('block-' + i + '-value', (keep[i] ? '' : 'omitted · ') + value));
  text('packet-direct', vectorText(result.direct));
  text('packet-rebuilt', vectorText(result.rebuilt));
  text('packet-residual', vectorText(result.residual));
  const omitted = keep.filter(value => !value).length;
  const loss = result.residual.some(value => value !== 0);
  verdict('packet-status', omitted === 0 ? 'All four blocks retained. The operation is reconstructed.' :
    loss ? `${omitted} block${omitted === 1 ? '' : 's'} omitted. The residual shows the missing output.` :
      `${omitted} block${omitted === 1 ? '' : 's'} omitted. Outputs agree for this input; that alone does not establish equality of the operators.`, loss);
  drawPackets(matrix, vector, keep, result);
}

function drawSignal(signal, result) {
  const svg = picture('signal-diagram', 640, 330,
    `Original ${vectorText(signal)}. Rebuilt ${vectorText(result.rebuilt)}. Residual ${vectorText(result.residual)}. Squared residual norm ${result.energy}.`);
  const series = [signal, result.rebuilt, result.residual];
  const names = ['Original', 'Rebuilt', 'Residual'];
  series.forEach((values, row) => {
    const baseline = 64 + row * 105;
    label(svg, 8, baseline-38, names[row], 'signal-row-label', 'start');
    svg.append(svgNode('line', {x1: 95, x2: 628, y1: baseline, y2: baseline, class: 'signal-baseline'}));
    values.forEach((value, index) => {
      const x = 118 + index * 68;
      const length = Math.abs(value) * 4;
      svg.append(svgNode('rect', {x: x-16, y: value > 0 ? baseline-length : baseline,
        width: 32, height: Math.max(length, 1), rx: 2, class: `signal-bar series-${row}`}));
      label(svg, x, value >= 0 ? baseline-length-7 : baseline+length+14, value, 'signal-value');
      if (row === 2) label(svg, x, 322, index, 'signal-address');
    });
  });
  label(svg, 8, 322, 'Address', 'signal-address', 'start');
}

function makePacketControls(count) {
  const host = byId('signal-packets');
  host.querySelectorAll('label').forEach(node => node.remove());
  for (let r = 0; r < count; r++) {
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'checkbox'; input.id = 'signal-keep-' + r; input.checked = true;
    input.setAttribute('aria-label', 'Keep signal packet ' + r);
    const title = document.createElement('span');
    title.className = 'signal-packet-title'; title.textContent = 'Packet ' + r;
    const values = document.createElement('span');
    values.id = 'signal-packet-values-' + r; values.className = 'signal-packet-values';
    label.append(input, title, values); host.append(label);
  }
  text('signal-drop', 'Discard packet ' + Math.min(2, count-1));
}
function updateSignal() {
  const signal = Array.from({length: 8}, (_, i) => number('sample-' + i));
  const count = number('signal-count');
  const keep = Array.from({length: count}, (_, i) => byId('signal-keep-' + i).checked);
  const result = refine(signal, count, keep);
  result.packets.forEach((packet, r) => {
    text('signal-packet-values-' + r, packet.map(entry => entry.value).join(', '));
    byId('signal-packet-values-' + r).parentElement.dataset.omitted = String(!keep[r]);
    byId('signal-keep-' + r).setAttribute('aria-description', 'Addresses ' + packet.map(entry => entry.index).join(', '));
  });
  const retained = result.packets.reduce((sum, packet, i) => sum + (keep[i] ? packet.length : 0), 0);
  text('signal-retained', retained + ' / 8');
  text('signal-energy', result.energy);
  verdict('signal-status', keep.every(Boolean) ? 'All packets retained. Every sample is recovered.' :
    result.energy === 0 ? 'Packets omitted, but their values are zero. This signal is still recovered exactly.' :
      `Discarded samples leave a squared residual norm of ${result.energy}. Restore their packets to recover the signal.`, result.energy !== 0);
  const rows = signal.map((value, index) => {
    const tr = document.createElement('tr');
    [index, value, result.rebuilt[index], result.residual[index]].forEach((entry, j) => {
      const cell = document.createElement(j === 0 ? 'th' : 'td');
      if (j === 0) cell.scope = 'row';
      cell.textContent = entry; tr.append(cell);
    });
    return tr;
  });
  byId('signal-table').replaceChildren(...rows);
  drawSignal(signal, result);
}

function drawRecovery(summary, result) {
  const svg = picture('recovery-diagram', 420, 352,
    `Line x one plus x two equals ${summary}. Input u ${vectorText(result.u)} and input v ${vectorText(result.v)} have answers ${result.answers.join(' and ')}.`);
  const px = x => 210 + x * 14, py = y => 170 - y * 14;
  for (let i = -10; i <= 10; i += 2) {
    svg.append(svgNode('line', {x1: px(i), x2: px(i), y1: py(10), y2: py(-10), class: 'recovery-grid'}));
    svg.append(svgNode('line', {x1: px(-10), x2: px(10), y1: py(i), y2: py(i), class: 'recovery-grid'}));
    if (i !== 0) label(svg, px(i), py(0)+17, i, 'axis-tick');
  }
  svg.append(svgNode('line', {x1: px(-10), x2: px(10), y1: py(0), y2: py(0), class: 'recovery-axis'}));
  svg.append(svgNode('line', {x1: px(0), x2: px(0), y1: py(10), y2: py(-10), class: 'recovery-axis'}));
  label(svg, px(10)+18, py(0)+5, 'x₁', 'diagram-coordinate');
  label(svg, px(0)+15, py(10)-10, 'x₂', 'diagram-coordinate');
  const left = Math.max(-10, summary-10), right = Math.min(10, summary+10);
  svg.append(svgNode('line', {x1: px(left), y1: py(summary-left), x2: px(right), y2: py(summary-right), class: 'recovery-fibre'}));
  [result.u, result.v].forEach((point, i) => {
    const x = px(point[0]), y = py(point[1]);
    svg.append(svgNode('circle', {cx: x, cy: y, r: 7, class: i ? 'recovery-point point-v' : 'recovery-point point-u'}));
    const lx = x + (i ? -25 : 25), ly = y + (i ? -21 : 29);
    svg.append(svgNode('rect', {x: lx-14, y: ly-17, width: 28, height: 24, rx: 4, class: 'point-label-bg'}));
    label(svg, lx, ly, i ? 'v' : 'u', 'point-label');
  });
  label(svg, 210, 340, `Same summary everywhere on the line: s = ${summary}`, 'diagram-heading');
}
function updateRecovery() {
  const summary = number('summary');
  const coefficients = [number('coefficient-a'), number('coefficient-b')];
  const [a, b] = coefficients;
  const result = recover(summary, number('position'), coefficients);
  text('recovery-u', vectorText(result.u)); text('recovery-v', vectorText(result.v));
  text('recovery-u-answer', 'F(u) = ' + result.answers[0]); text('recovery-v-answer', 'F(v) = ' + result.answers[1]);
  text('recovery-summary', summary);
  verdict('recovery-status', result.compatible ? 'Recoverable from the sum. Every input with this summary gives the same answer.' :
    'Same summary, different answers. This question cannot be answered from the sum alone.', !result.compatible);
  text('recovery-rule', result.compatible ? `The rule G(s) = ${a} × s works for every real input. Here G(${summary}) = ${result.recovered}.` :
    `F(x) = ${a}x₁ + (${b})x₂. The summary erases (1, −1), while F(u) − F(v) = a − b = ${result.difference}.`);
  drawRecovery(summary, result);
}

const haarShapes = {
  step: [2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4],
  ramp: Array.from({length:16}, (_, i) => i-8),
  alternating: Array.from({length:16}, (_, i) => i % 2 ? -8 : 8),
  pulse: Array.from({length:16}, (_, i) => i === 10 ? 16 : 0),
  triangle: [-8,-6,-4,-2,0,2,4,6,8,6,4,2,0,-2,-4,-6],
};
const haarState = {keep: Array(16).fill(true), mode: 'all'};
function readHaarSignal() {
  const inputs = Array.from({length:16}, (_, i) => byId('haar-sample-' + i));
  const invalid = inputs.filter(input => input.value.trim() === '' || !input.checkValidity() || !Number.isInteger(Number(input.value)));
  for (const input of inputs) {
    input.setAttribute('aria-invalid', String(invalid.includes(input)));
    input.setAttribute('aria-describedby', 'haar-error');
  }
  byId('haar-error').hidden = invalid.length === 0;
  if (invalid.length) {
    text('haar-error', 'Use whole numbers from −16 to 16. The graphs keep the last valid calculation until all samples are valid.');
    return null;
  }
  return inputs.map(input => Number(input.value));
}
function haarSelection(mode, coefficients) {
  return coefficients.map((coefficient, index) => index === 0 || mode === 'all' ||
    (mode === 'coarse' && coefficient.level >= 3) ||
    (mode === 'no-fine' && coefficient.level >= 2) ||
    (mode === 'threshold' && Math.abs(coefficient.value) >= number('haar-cutoff')));
}
function makeHaarControls(coefficients) {
  if (byId('haar-levels').children.length) return;
  for (let level = 4; level >= 1; level--) {
    const row = document.createElement('div'); row.className = 'haar-level-row';
    const title = document.createElement('p'); title.id = 'haar-level-title-' + level;
    title.textContent = `Level ${level} · ${2**level}-sample blocks`;
    const grid = document.createElement('div'); grid.className = 'haar-coefficient-grid';
    grid.dataset.count = String(16 / 2**level);
    grid.setAttribute('role', 'group'); grid.setAttribute('aria-labelledby', title.id);
    coefficients.forEach((coefficient, index) => {
      if (coefficient.kind !== 'detail' || coefficient.level !== level) return;
      const label = document.createElement('label'); label.htmlFor = 'haar-keep-' + index;
      const input = document.createElement('input'); input.type = 'checkbox';
      input.id = 'haar-keep-' + index; input.dataset.index = index;
      input.setAttribute('aria-label', `Keep level ${level} detail ${coefficient.index}, addresses ${coefficient.start} to ${coefficient.end}`);
      const name = document.createElement('span'); name.className = 'haar-coefficient-name';
      name.textContent = `d${level},${coefficient.index}`;
      const value = document.createElement('output'); value.id = 'haar-coefficient-' + index;
      value.setAttribute('aria-live', 'off');
      const support = document.createElement('span'); support.className = 'haar-support';
      support.textContent = `${coefficient.start}–${coefficient.end}`;
      label.append(input, name, value, support); grid.append(label);
    });
    row.append(title, grid); byId('haar-levels').append(row);
  }
}
function drawHaar(signal, result) {
  const svg = picture('haar-diagram', 720, 370,
    `16-sample Haar reconstruction using ${result.retained} coefficients. Squared error ${result.residualEnergy}. Exact sample values and intermediate levels are in the table below.`);
  const x = i => 58 + i * 42;
  function plot(values, top, bottom, limit, className) {
    const y = value => (top+bottom)/2 - value*(bottom-top)/(2*limit);
    svg.append(svgNode('polyline', {points: values.map((v,i) => `${x(i)},${y(v)}`).join(' '), class: 'haar-trace ' + className}));
    values.forEach((value, i) => svg.append(svgNode('circle', {cx:x(i), cy:y(value), r:className === 'haar-rebuilt-trace' ? 4.5 : 2.6,
      class:'haar-dot ' + className})));
  }
  function axes(top, bottom, limit, title) {
    label(svg, 58, top-12, title, 'haar-chart-title', 'start');
    for (const [value, y] of [[limit,top],[0,(top+bottom)/2],[-limit,bottom]]) {
      svg.append(svgNode('line', {x1:58,x2:x(15),y1:y,y2:y,class:value === 0 ? 'signal-baseline' : 'haar-chart-grid'}));
      label(svg, 45, y+4, value, 'haar-axis-label', 'end');
    }
  }
  const topLimit = Math.max(4, Math.ceil(Math.max(...signal.map(Math.abs), ...result.rebuilt.map(Math.abs))/4)*4);
  const residualLimit = Math.max(4, Math.ceil(Math.max(...result.residual.map(Math.abs))/4)*4);
  axes(35, 190, topLimit, 'Original and reconstruction');
  plot(result.rebuilt, 35, 190, topLimit, 'haar-rebuilt-trace');
  plot(signal, 35, 190, topLimit, 'haar-original-trace');
  axes(245, 332, residualLimit, 'Residual · original − reconstruction');
  plot(result.residual, 245, 332, residualLimit, 'haar-residual-trace');
  for (const i of [0,4,8,12,15]) label(svg,x(i),355,i,'haar-axis-label');
  label(svg, 8, 355, 'Address', 'haar-axis-label', 'start');
}
function dataRow(values, rowHeading = true) {
  const row = document.createElement('tr');
  values.forEach((value, index) => {
    const cell = document.createElement(index === 0 && rowHeading ? 'th' : 'td');
    if (index === 0 && rowHeading) cell.scope = 'row';
    cell.textContent = value; row.append(cell);
  });
  return row;
}
function updateHaar() {
  const signal = readHaarSignal();
  if (!signal) return;
  const analysis = haarAnalyze(signal);
  if (haarState.mode !== 'custom') haarState.keep = haarSelection(haarState.mode, analysis.coefficients);
  const result = haar(signal, haarState.keep);
  makeHaarControls(result.coefficients);
  text('haar-mean', result.coefficients[0].value);
  result.coefficients.forEach((coefficient, index) => {
    if (index === 0) return;
    const input = byId('haar-keep-' + index);
    input.checked = haarState.keep[index];
    input.parentElement.dataset.omitted = String(!haarState.keep[index]);
    text('haar-coefficient-' + index, coefficient.value);
  });
  text('haar-retained', `${result.retained} / 16`);
  text('haar-error-energy', result.residualEnergy);
  text('haar-original-energy', result.energy);
  text('haar-rebuilt-energy', result.rebuiltEnergy);
  text('haar-residual-energy', result.residualEnergy);
  const modes = {all:'all coefficients',coarse:'mean and the two coarsest detail levels',
    'no-fine':'all but the finest detail level',mean:'global mean only',
    threshold:`details with magnitude at least ${number('haar-cutoff')}`,custom:'manually chosen details'};
  text('haar-selection-note', 'Selection: ' + modes[haarState.mode] + '.');
  document.querySelectorAll('[data-haar-selection]').forEach(button =>
    button.setAttribute('aria-pressed', String(button.dataset.haarSelection === haarState.mode)));
  verdict('haar-status', result.residualEnergy === 0 ?
    `${result.retained} of 16 coefficients retained. Every sample is recovered exactly.` :
    `${result.retained} of 16 coefficients retained. Omitted details contribute exactly ${result.residualEnergy} units of squared reconstruction error.`, result.residualEnergy !== 0);
  byId('haar-analysis-table').replaceChildren(...result.levels.map(level =>
    dataRow([level.level, level.averages.join(', '), level.details.join(', ')])));
  byId('haar-sample-table').replaceChildren(...signal.map((value, index) =>
    dataRow([index,value,result.rebuilt[index],result.residual[index]])));
  drawHaar(signal, result);
}

function reset(name) {
  if (name === 'packets') {
    [1, 2, 3, 4].forEach((v, i) => { byId('matrix-' + i).value = v; byId('block-' + i).checked = true; });
    byId('vector-0').value = 2; byId('vector-1').value = 3;
    updatePackets();
  } else if (name === 'refinement') {
    byId('signal-preset').value = 'ramp'; byId('signal-count').value = '4';
    Array.from({length: 8}, (_, i) => { byId('sample-' + i).value = i+1; });
    makePacketControls(4); updateSignal();
  } else if (name === 'recovery') {
    byId('recovery-question').value = 'first';
    byId('summary').value = 1; byId('position').value = 1;
    byId('coefficient-a').value = 1; byId('coefficient-b').value = 0;
    updateRecovery();
  } else if (name === 'haar') {
    byId('haar-preset').value = 'step'; byId('haar-cutoff').value = 0;
    haarShapes.step.forEach((value, i) => { byId('haar-sample-' + i).value = value; });
    haarState.mode = 'all'; updateHaar();
  }
  sliderValues();
}

const tabs = [...document.querySelectorAll('.lab-tabs a')];
const names = ['packets', 'refinement', 'recovery', 'haar'];
function selectTab(name, updateUrl = false) {
  if (!names.includes(name)) name = 'packets';
  tabs.forEach(tab => {
    const selected = tab.hash === '#' + name;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    byId(tab.hash.slice(1)).hidden = !selected;
  });
  if (updateUrl && location.hash !== '#' + name) history.pushState(null, '', '#' + name);
}
document.querySelector('.lab-tabs').setAttribute('role', 'tablist');
tabs.forEach((tab, i) => {
  tab.setAttribute('role', 'tab'); tab.setAttribute('aria-controls', names[i]);
  const panel = byId(names[i]);
  panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', tab.id);
  panel.tabIndex = 0;
  tab.addEventListener('click', event => { event.preventDefault(); selectTab(names[i], true); });
  tab.addEventListener('keydown', event => {
    let index;
    if (event.key === 'ArrowRight') index = (i+1) % tabs.length;
    if (event.key === 'ArrowLeft') index = (i+tabs.length-1) % tabs.length;
    if (event.key === 'Home') index = 0;
    if (event.key === 'End') index = tabs.length-1;
    if (index === undefined) return;
    event.preventDefault(); selectTab(names[index], true); tabs[index].focus();
  });
});
function restoreTab() {
  const name = location.hash.slice(1);
  if (!name || names.includes(name)) selectTab(name);
}
window.addEventListener('popstate', restoreTab);
window.addEventListener('hashchange', restoreTab);
byId('packet-controls').addEventListener('input', () => { sliderValues(); updatePackets(); });
byId('packet-remove').addEventListener('click', () => { byId('block-3').checked = false; updatePackets(); });
byId('signal-controls').addEventListener('input', event => {
  if (event.target.id.startsWith('sample-')) { byId('signal-preset').value = 'custom'; sliderValues(); updateSignal(); }
});
byId('signal-preset').addEventListener('change', () => {
  const shapes = {ramp: [1,2,3,4,5,6,7,8], alternating: [6,-6,6,-6,6,-6,6,-6], pulse: [0,0,0,8,0,0,0,0]};
  const shape = shapes[byId('signal-preset').value];
  if (!shape) return;
  shape.forEach((value, i) => { byId('sample-' + i).value = value; });
  sliderValues(); updateSignal();
});
byId('signal-count').addEventListener('change', () => { makePacketControls(number('signal-count')); updateSignal(); });
byId('signal-packets').addEventListener('change', updateSignal);
byId('signal-drop').addEventListener('click', () => {
  byId('signal-keep-' + Math.min(2, number('signal-count')-1)).checked = false; updateSignal();
});
byId('recovery-question').addEventListener('change', () => {
  const choices = {first: [1,0], sum: [2,2], difference: [1,-1]};
  const choice = choices[byId('recovery-question').value];
  if (!choice) return;
  byId('coefficient-a').value = choice[0]; byId('coefficient-b').value = choice[1];
  sliderValues(); updateRecovery();
});
byId('recovery-controls').addEventListener('input', event => {
  if (event.target.type !== 'range') return;
  if (event.target.id.startsWith('coefficient-')) byId('recovery-question').value = 'custom';
  sliderValues(); updateRecovery();
});
byId('haar-controls').addEventListener('input', event => {
  if (event.target.id.startsWith('haar-sample-')) byId('haar-preset').value = 'custom';
  else if (event.target.id === 'haar-cutoff') haarState.mode = 'threshold';
  else return;
  sliderValues(); updateHaar();
});
byId('haar-cutoff').setAttribute('aria-describedby', 'haar-cutoff-help');
byId('haar-preset').addEventListener('change', () => {
  const shape = haarShapes[byId('haar-preset').value];
  if (!shape) return;
  shape.forEach((value, i) => { byId('haar-sample-' + i).value = value; });
  updateHaar();
});
document.querySelectorAll('[data-haar-selection]').forEach(button => {
  button.addEventListener('click', () => { haarState.mode = button.dataset.haarSelection; updateHaar(); });
});
byId('haar-coefficients').addEventListener('change', event => {
  const index = Number(event.target.dataset.index);
  if (!Number.isInteger(index) || index < 1 || index > 15) return;
  haarState.keep[index] = event.target.checked; haarState.mode = 'custom'; updateHaar();
});
document.querySelectorAll('[data-reset]').forEach(button => {
  button.addEventListener('click', () => reset(button.dataset.reset));
});
names.forEach(reset);
document.querySelectorAll('.math-lab fieldset, .math-lab [data-reset]').forEach(node => { node.disabled = false; });
selectTab(location.hash.slice(1));
byId('math-lab').dataset.ready = 'true';
