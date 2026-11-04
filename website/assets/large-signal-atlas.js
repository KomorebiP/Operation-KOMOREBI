/* Exact, bounded teaching example. The original source remains the proof. */
(function () {
  'use strict';
  const MAX_T = 8;
  function gcd(a, b) { a = a < 0n ? -a : a; while (b) [a, b] = [b, a % b]; return a; }
  function q(n, d = 1n) {
    n = BigInt(n); d = BigInt(d);
    if (!d) throw new RangeError('Zero denominator');
    if (d < 0n) { n = -n; d = -d; }
    const g = gcd(n, d);
    return Object.freeze({n:n / g, d:d / g});
  }
  function add(a, b) { return q(a.n * b.d + b.n * a.d, a.d * b.d); }
  function mul(a, b) { return q(a.n * b.n, a.d * b.d); }
  function text(a) { return a.d === 1n ? String(a.n) : a.n + '/' + a.d; }
  function number(a) { return Number(a.n) / Number(a.d); }
  function step(state) {
    if (!Array.isArray(state) || state.length !== 2) throw new TypeError('Two coordinates required');
    const [x, w] = state;
    return [add(mul(q(1, 2), x), w), add(mul(q(1, 4), x), mul(q(1, 3), w))];
  }
  function trace(initial, lastStep) {
    if (!Number.isInteger(lastStep) || lastStep < 0 || lastStep > 12) throw new RangeError('Bounded trace required');
    const rows = [initial];
    for (let t = 0; t < lastStep; t++) rows.push(step(rows[rows.length - 1]));
    return rows;
  }
  function forecast(previous, current) { return add(mul(q(1, 12), previous), mul(q(5, 6), current)); }
  function compare(h, t) {
    if (!Number.isInteger(h) || h < -2 || h > 2 || !Number.isInteger(t) || t < 0 || t > MAX_T) {
      throw new RangeError('Use an integer hidden coordinate from -2 to 2 and an observed step from 0 to 8');
    }
    const a = trace([q(0), q(0)], t + 1), b = trace([q(0), q(h)], t + 1);
    return {h, t, states:[a[t], b[t]], outputs:[a[t][0], b[t][0]], next:[a[t + 1][0], b[t + 1][0]],
      histories:t ? [[a[t - 1][0], a[t][0]], [b[t - 1][0], b[t][0]]] : null,
      delayed:t ? [forecast(a[t - 1][0], a[t][0]), forecast(b[t - 1][0], b[t][0])] : null,
      observed:a.slice(0, t + 1).map((row, i) => [row[0], b[i][0]])};
  }
  function normalize(value) { return value.normalize('NFKD').toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim(); }
  function matches(query, value) {
    const haystack=normalize(value), tokens=new Set(haystack.split(/\s+/));
    return normalize(query).split(/\s+/).filter(Boolean).every(word => /^p\d+$/.test(word) ? tokens.has(word) : haystack.includes(word));
  }
  const api = Object.freeze({MAX_T, q, add, mul, text, number, step, trace, forecast, compare, matches});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;

  function node(tag, value, attributes = {}) {
    const element = document.createElement(tag);
    if (value !== undefined) element.textContent = value;
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    return element;
  }
  function svg(tag, attributes = {}, value) {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    if (value !== undefined) element.textContent = value;
    return element;
  }
  function plot(root, values) {
    const group = root.querySelector('[data-lsm-plot]');
    const numbers = values.flat().map(number), low = Math.min(-0.1, ...numbers), high = Math.max(0.1, ...numbers);
    const x = i => 48 + i * 620 / MAX_T, y = v => 180 - (v - low) * 150 / (high - low);
    group.replaceChildren();
    group.append(svg('line', {x1:48, x2:674, y1:y(0), y2:y(0), class:'lsm-chart-axis'}));
    for (const t of [0, 4, 8]) {
      group.append(svg('text', {x:x(t), y:207, 'text-anchor':'middle'}, String(t)));
    }
    group.append(svg('text', {x:694, y:207}, 'step'));
    for (const [label, value] of [['0', 0], [high.toFixed(2), high], [low.toFixed(2), low]]) {
      group.append(svg('text', {x:40, y:y(value) + 4, 'text-anchor':'end'}, label));
    }
    for (let series = 0; series < 2; series++) {
      const cls = series ? 'lsm-plot-b' : 'lsm-plot-a';
      const points = values.map((row, i) => x(i) + ',' + y(number(row[series]))).join(' ');
      group.append(svg('polyline', {points, class:cls, fill:'none', 'stroke-width':2.5,
        ...(series ? {'stroke-dasharray':'6 4'} : {})}));
      values.forEach((row, i) => {
        const cx = x(i), cy = y(number(row[series]));
        group.append(series ? svg('path', {d:`M ${cx} ${cy - 5} L ${cx + 5} ${cy} L ${cx} ${cy + 5} L ${cx - 5} ${cy} Z`, class:cls}) :
          svg('circle', {cx, cy, r:3.4, class:cls}));
      });
    }
    root.querySelector('#lsm-chart-description').textContent = 'Observed steps 0 through ' + (values.length - 1) +
      '. State A: ' + values.map(r => text(r[0])).join(', ') + '. State B: ' + values.map(r => text(r[1])).join(', ') + '.';
    root.querySelector('.lsm-explorer-chart').hidden = false;
  }
  function mount(root) {
    let t = 0;
    const slider = root.querySelector('#lsm-hidden-coordinate'), next = root.querySelector('[data-lsm-next]');
    function render() {
      const h = Number(slider.value), data = compare(h, t);
      root.querySelector('[data-lsm-h]').textContent = String(h);
      slider.setAttribute('aria-valuetext', String(h));
      root.querySelector('[data-lsm-time]').textContent = 'Observed step ' + t + ' of ' + MAX_T;
      next.disabled = t === MAX_T;
      for (const [i, key] of ['a', 'b'].entries()) {
        const put = (name, value) => { root.querySelector('[data-lsm-' + key + '-' + name + ']').textContent = value; };
        put('state', '(' + data.states[i].map(text).join(', ') + ')');
        put('output', text(data.outputs[i])); put('next', text(data.next[i]));
        put('history', data.histories ? '(' + data.histories[i].map(text).join(', ') + ')' : 'Available after one observation');
        put('delay', data.delayed ? text(data.delayed[i]) + ' · agrees with the full-state calculation' : 'Available after one observation');
      }
      const rows = root.querySelector('[data-lsm-rows]'); rows.replaceChildren();
      data.observed.forEach((values, i) => {
        const row = node('tr'); if (i === t) row.setAttribute('aria-current', 'step');
        row.append(node('th', String(i), {scope:'row'}), node('td', text(values[0])), node('td', text(values[1]))); rows.append(row);
      });
      const status = !h ? 'These comparison states coincide. Choose a nonzero hidden coordinate to see the obstruction; the h = 1 pair still disproves scalar closure for this operator.' :
        t ? 'At step ' + t + ', the previous and current observations are available. The delay recurrence predicts the next output exactly for each comparison state in this fixed system.' :
        'At step 0, both current outputs are 0, but their next outputs are 0 and ' + h + '. The causal delay state is available after one observation step.';
      root.querySelector('[data-lsm-status]').textContent = status;
      plot(root, data.observed);
    }
    slider.addEventListener('input', () => { t = 0; render(); });
    next.addEventListener('click', () => { if (t < MAX_T) { t++; render(); } });
    root.querySelector('[data-lsm-reset]').addEventListener('click', () => { slider.value = '1'; t = 0; render(); });
    render(); root.querySelector('.lsm-explorer-controls').hidden = false;
  }
  for (const root of document.querySelectorAll('[data-lsm-explorer]')) mount(root);

  const query = document.querySelector('#lsm-visual-query');
  if (query) {
    const cards = [...document.querySelectorAll('.lsm-atlas-card')];
    function filter() {
      for (const card of cards) card.hidden = !matches(query.value,card.dataset.search);
      const count = cards.filter(card => !card.hidden).length;
      document.querySelector('#lsm-visual-count').textContent = count + ' of ' + cards.length + ' plates';
      document.querySelector('#lsm-visual-empty').hidden = count !== 0;
    }
    query.addEventListener('input', filter);
    query.form.addEventListener('reset', () => { query.value = ''; filter(); });
    query.form.hidden = false; filter();
  }
})();
