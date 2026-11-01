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
// Match drawing units to CSS pixels, including when a hidden tab becomes visible.
function diagramWidth(id) {
  return Math.max(220, Math.floor(byId(id).getBoundingClientRect().width));
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
  const width = diagramWidth('packet-diagram');
  const compact = width < 440;
  const svg = picture('packet-diagram', width, compact ? 330 : 310,
    `Input ${vectorText(vector)}. Direct output ${vectorText(result.direct)}. Output from kept blocks ${vectorText(result.rebuilt)}. Residual ${vectorText(result.residual)}.`);
  if (compact) {
    label(svg, 8, 22, 'INPUT → TRANSFER → CONTRIBUTION', 'diagram-heading', 'start');
    result.contributions.forEach((value, i) => {
      const y = 65 + i * 66;
      const row = Math.floor(i / 2), column = i % 2;
      const group = svgNode('g', {class: keep[i] ? 'packet-contribution' : 'packet-contribution omitted'});
      group.append(svgNode('rect', {x: 1, y: y-25, width: width-2, height: 54, rx: 5}));
      group.append(svgNode('text', {x: 12, y: y-3}, `T${row+1}${column+1} · x${column+1} → y${row+1}`));
      group.append(svgNode('text', {x: 12, y: y+17, class: 'compact-block-state'}, keep[i] ? 'Kept' : 'Omitted'));
      group.append(svgNode('text', {x: width-12, y: y+17, 'text-anchor': 'end'}, `${matrix[i]} × (${vector[column]}) = ${value}`));
      svg.append(group);
    });
    return;
  }
  const left = 48, right = width-48, middle = width/2;
  label(svg, left, 28, 'INPUT', 'diagram-heading');
  label(svg, right, 28, 'KEPT OUTPUT', 'diagram-heading');
  label(svg, middle, 28, 'TRANSFER BLOCKS', 'diagram-heading');
  const ys = [100, 242];
  keep.forEach((kept, i) => {
    const row = Math.floor(i / 2), column = i % 2;
    const start = ys[column], end = ys[row];
    const path = svgNode('path', {d: `M ${left+34} ${start} C ${middle-50} ${start}, ${middle+50} ${end}, ${right-34} ${end}`,
      class: kept ? 'packet-wire' : 'packet-wire omitted'});
    svg.append(path);
  });
  // Offset the crossing labels so both contributions remain readable.
  const positions = [[middle, 94], [middle+45, 143], [middle-45, 205], [middle, 236]];
  result.contributions.forEach((value, i) => {
    const [x, y] = positions[i];
    const group = svgNode('g', {class: keep[i] ? 'packet-contribution' : 'packet-contribution omitted'});
    group.append(svgNode('rect', {x: x-54, y: y-20, width: 108, height: 32, rx: 5}));
    group.append(svgNode('text', {x, y, 'text-anchor': 'middle', class: 'contribution-full'}, `${matrix[i]} × ${vector[i % 2]} = ${value}`));
    svg.append(group);
  });
  for (let i = 0; i < 2; i++) {
    svg.append(svgNode('circle', {cx: left, cy: ys[i], r: 32, class: 'packet-node'}));
    svg.append(svgNode('circle', {cx: right, cy: ys[i], r: 32, class: 'packet-node output-node'}));
    label(svg, left, ys[i]+8, vector[i], 'diagram-number');
    label(svg, right, ys[i]+8, result.rebuilt[i], 'diagram-number');
    label(svg, left, ys[i]+54, `x${i === 0 ? '₁' : '₂'}`, 'diagram-coordinate');
    label(svg, right, ys[i]+54, `y${i === 0 ? '₁' : '₂'}`, 'diagram-coordinate');
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
  const width = diagramWidth('signal-diagram');
  const svg = picture('signal-diagram', width, 370,
    `Original ${vectorText(signal)}. Rebuilt ${vectorText(result.rebuilt)}. Residual ${vectorText(result.residual)}. Squared residual norm ${result.energy}.`);
  const series = [signal, result.rebuilt, result.residual];
  const names = ['Original', 'Rebuilt', 'Residual'];
  series.forEach((values, row) => {
    const baseline = 76 + row * 114;
    label(svg, 8, baseline-56, names[row], 'signal-row-label', 'start');
    svg.append(svgNode('line', {x1: 8, x2: width-8, y1: baseline, y2: baseline, class: 'signal-baseline'}));
    values.forEach((value, index) => {
      const x = 22 + index * (width-44)/7;
      const length = Math.abs(value) * 4;
      const barWidth = Math.min(32, (width-44)/7 * .65);
      svg.append(svgNode('rect', {x: x-barWidth/2, y: value > 0 ? baseline-length : baseline,
        width: barWidth, height: Math.max(length, 1), rx: 2, class: `signal-bar series-${row}`}));
      label(svg, x, value >= 0 ? baseline-length-7 : baseline+length+14, value, 'signal-value');
      if (row === 2) label(svg, x, 352, index, 'signal-address');
    });
  });
  label(svg, width/2, 368, 'Original address', 'signal-address');
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
  const width = diagramWidth('recovery-diagram');
  const size = Math.min(320, width-68), leftEdge = (width-size)/2;
  const svg = picture('recovery-diagram', width, size+80,
    `Line x one plus x two equals ${summary}. Input u ${vectorText(result.u)} and input v ${vectorText(result.v)} have answers ${result.answers.join(' and ')}.`);
  const px = x => width/2 + x * size/20, py = y => 32 + size/2 - y * size/20;
  for (let i = -10; i <= 10; i += 2) {
    svg.append(svgNode('line', {x1: px(i), x2: px(i), y1: py(10), y2: py(-10), class: 'recovery-grid'}));
    svg.append(svgNode('line', {x1: px(-10), x2: px(10), y1: py(i), y2: py(i), class: 'recovery-grid'}));
    if (i !== 0 && (width >= 360 || i % 4 === 0)) label(svg, px(i), py(0)+17, i, 'axis-tick');
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
  label(svg, leftEdge+size/2, size+67, `Same summary on the line: s = ${summary}`, 'diagram-heading');
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
let haarView = null;
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
  coefficients.forEach((coefficient, index) => {
    const option = document.createElement('option'); option.value = index;
    option.textContent = coefficient.kind === 'average' ? 'Global mean' : `d${coefficient.level},${coefficient.index} · addresses ${coefficient.start}–${coefficient.end}`;
    byId('haar-inspect').append(option);
  });
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
  const width = diagramWidth('haar-diagram');
  const svg = picture('haar-diagram', width, 388,
    `16-sample Haar reconstruction using ${result.retained} coefficients. Squared error ${result.residualEnergy}. Exact sample values and intermediate levels are in the table below.`);
  const x = i => 40 + i * (width-54)/15;
  const address = number('haar-address');
  const selected = byId('haar-inspect').value;
  const coefficient = selected === 'none' ? null : result.coefficients[Number(selected)];
  if (coefficient) {
    const step = (width-54)/15;
    const start = Math.max(34, x(coefficient.start)-step/2);
    const end = Math.min(width-8, x(coefficient.end)+step/2);
    const middle = x((coefficient.start+coefficient.end)/2);
    for (const [top, bottom] of [[35,190],[245,332]]) {
      svg.append(svgNode('rect', {x:start,y:top,width:end-start,height:bottom-top,class:'haar-support-band'}));
      if (coefficient.kind === 'detail') svg.append(svgNode('rect', {x:middle,y:top,width:end-middle,height:bottom-top,class:'haar-support-half'}));
    }
  }
  function plot(values, top, bottom, limit, className) {
    const y = value => (top+bottom)/2 - value*(bottom-top)/(2*limit);
    svg.append(svgNode('polyline', {points: values.map((v,i) => `${x(i)},${y(v)}`).join(' '), class: 'haar-trace ' + className}));
    values.forEach((value, i) => svg.append(svgNode('circle', {cx:x(i), cy:y(value), r:i === address ? 5 : className === 'haar-rebuilt-trace' ? 4 : 2,
      class:'haar-dot ' + className})));
  }
  function axes(top, bottom, limit, title) {
    label(svg, 40, top-12, title, 'haar-chart-title', 'start');
    for (const [value, y] of [[limit,top],[0,(top+bottom)/2],[-limit,bottom]]) {
      svg.append(svgNode('line', {x1:40,x2:x(15),y1:y,y2:y,class:value === 0 ? 'signal-baseline' : 'haar-chart-grid'}));
      label(svg, 30, y+4, value, 'haar-axis-label', 'end');
    }
  }
  const topLimit = Math.max(4, Math.ceil(Math.max(...signal.map(Math.abs), ...result.rebuilt.map(Math.abs))/4)*4);
  const residualLimit = Math.max(4, Math.ceil(Math.max(...result.residual.map(Math.abs))/4)*4);
  axes(35, 190, topLimit, 'Original and reconstruction');
  plot(result.rebuilt, 35, 190, topLimit, 'haar-rebuilt-trace');
  plot(signal, 35, 190, topLimit, 'haar-original-trace');
  axes(245, 332, residualLimit, 'Residual · original − reconstruction');
  plot(result.residual, 245, 332, residualLimit, 'haar-residual-trace');
  svg.append(svgNode('line', {x1:x(address),x2:x(address),y1:35,y2:332,class:'haar-address-guide'}));
  for (const i of [0,4,8,12,15]) label(svg,x(i),355,i,'haar-axis-label');
  label(svg, (x(0)+x(15))/2, 379, 'Original address', 'haar-axis-label');
  // A range control provides the same inspection to keyboard and touch users.
  svg.addEventListener('pointerdown', event => {
    const bounds = svg.getBoundingClientRect();
    const pointerX = (event.clientX-bounds.left) * width/bounds.width;
    byId('haar-address').value = Math.max(0, Math.min(15, Math.round((pointerX-40) * 15/(width-54))));
    inspectHaar();
  });
}
function inspectHaar() {
  if (!haarView) return;
  const {signal, result} = haarView;
  const selected = byId('haar-inspect').value;
  byId('haar-inspect-detail').hidden = selected === 'none';
  if (selected !== 'none') {
    const index = Number(selected), c = result.coefficients[index];
    const kept = haarState.keep[index];
    const contribution = c.kind === 'average' ? `Adds ${c.value} at every address.` :
      `If kept, adds ${c.value} at addresses ${c.start}–${(c.start+c.end-1)/2} and ${-c.value || 0} at ${(c.start+c.end+1)/2}–${c.end}.`;
    text('haar-inspect-detail', `${kept ? 'Kept' : 'Omitted'} · coefficient ${c.value}. ${contribution} ${kept ? 'Retained' : 'Discarded'} energy: ${c.weight} × (${c.value})² = ${c.weight*c.value**2}.`);
  }
  const address = number('haar-address');
  text('haar-address-value', address);
  text('haar-sample-detail', `Address ${address} · original ${signal[address]} · reconstructed ${result.rebuilt[address]} · residual ${result.residual[address]}`);
  drawHaar(signal, result);
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
  haarView = {signal, result};
  inspectHaar();
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
    byId('haar-inspect').value = 'none'; byId('haar-address').value = 10;
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
  // Hidden diagrams have no measurable width until their tab is selected.
  redrawDiagram(name);
}
function redrawDiagram(name) {
  ({packets: updatePackets, refinement: updateSignal, recovery: updateRecovery, haar: updateHaar})[name]();
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
byId('haar-inspect').addEventListener('change', inspectHaar);
byId('haar-address').addEventListener('input', inspectHaar);
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
let resizeFrame;
const diagramWidths = new WeakMap();
const diagramObserver = new ResizeObserver(entries => {
  let changed = false;
  for (const entry of entries) {
    const width = Math.floor(entry.contentRect.width);
    if (width > 0 && diagramWidths.get(entry.target) !== width) changed = true;
    diagramWidths.set(entry.target, width);
  }
  if (!changed) return;
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(() => {
    const active = names.find(name => !byId(name).hidden);
    if (active) redrawDiagram(active);
  });
});
document.querySelectorAll('.lab-diagram').forEach(node => diagramObserver.observe(node));
byId('math-lab').dataset.ready = 'true';
