/* A presentation adapter for the verified 1.4 instrument. Move existing DOM
   controls without replacing event handlers, model outputs, checks or exports. */
(() => {
  'use strict';
  window.JSpaceWorkbench = {mount(frame, callbacks) {
    const doc = frame.contentDocument;
    const byId = id => doc.getElementById(id);
    const query = selector => doc.querySelector(selector);
    const listeners = [];
    function listen(node, event, fn) {
      node.addEventListener(event, fn);
      listeners.push(() => node.removeEventListener(event, fn));
    }
    function fold(elements, label, inline = false) {
      const nodes = Array.isArray(elements) ? elements : [elements];
      const details = doc.createElement('details');
      details.className = 'jl-fold' + (inline ? ' jl-fold-inline' : '');
      const summary = doc.createElement('summary');
      summary.textContent = label;
      nodes[0].before(details);
      details.append(summary);
      if (inline) {
        const body = doc.createElement('div');
        body.className = 'jl-fold-body';
        body.append(...nodes);
        details.append(body);
      } else details.append(...nodes);
      return details;
    }
    function heading(selector, text) { query(selector).textContent = text; }

    const startingPanels = [...doc.querySelectorAll('.causal-grid > .stack:first-child > .panel')];
    fold(startingPanels[0], 'Starting facts and model');
    fold(startingPanels[2], 'Readout and later operations');
    heading('.causal-edit h2', '1  Choose the edit');
    fold(query('.causal-edit > .fieldgrid'), 'Intervention and writing agent', true);
    byId('cApply').textContent = 'Apply full strength';
    byId('cUndo').textContent = 'Remove edit';
    const memory = byId('cMemory').closest('.panel');
    query('.causal-agentgrid').after(memory);
    fold(byId('cConsumers').closest('.panel'), 'Other ways to read the same state');
    fold(byId('rDosePanel'), 'Scan edit strengths');
    fold(byId('rControlsPanel'), 'Compare control interventions');
    fold(byId('cExport').closest('.panel'), 'Coordinates and trial export');
    fold(byId('rLivePanel'), 'Continue the edited state step by step');

    const relayControls = [...doc.querySelectorAll('.relay-layout > .stack:first-child > .panel')];
    heading('.relay-layout > .stack:first-child h2', '1  Set up the trace');
    fold([byId('mKind').parentElement, byId('mProgramBox'), byId('mCountBox')], 'Program and communication settings', true);
    fold(relayControls[1], 'Readout and trace export');
    fold(relayControls[2], 'Test both directions on more histories');
    fold(byId('mPackets').closest('.panel'), 'Inspect the eight message values');
    heading('#mResults > .panel:first-child h2', '2  Compare the recipient’s answers');
    byId('mRun').textContent = 'Run message trace';
    const checkpoint = query('label[for="mCheckpoint"]');
    const checkpointNodes = [];
    for (let node = checkpoint; node; node = node.nextSibling) checkpointNodes.push(node);
    fold(checkpointNodes, 'Checkpoint outputs and reference checks', true);

    const challengePanels = [...doc.querySelectorAll('#challenge > .panel')];
    heading('#challenge > .panel:first-of-type h3', '1  Set up the test');
    heading('#tResultsPanel h3', '2  Compare what survives');
    byId('tRun').textContent = 'Run persistence test';
    fold(byId('tWire').parentElement, 'Retrieval message options', true);
    fold(challengePanels[2], 'Try the same settings on more histories');

    for (const button of doc.querySelectorAll('[data-tab]')) {
      listen(button, 'click', () => callbacks.onTabChange(button.dataset.tab));
    }
    function notifyBusy() {
      const busy = !byId('mCancel').disabled || !byId('tCancel').disabled;
      byId('mEditor').disabled = busy;
      callbacks.onBusyChange(busy);
    }
    const busyObserver = new MutationObserver(notifyBusy);
    for (const id of ['mCancel', 'tCancel']) {
      busyObserver.observe(byId(id), {attributes: true, attributeFilter: ['disabled']});
    }

    // Measure content rather than the iframe viewport, so it can shrink again
    // after collapsing a section or switching experiments. One page scrolls.
    const wrap = query('main.wrap');
    let resizeObserver, destroyed = false;
    function resize() {
      if (destroyed) return;
      const height = Math.max(240, Math.ceil(wrap.getBoundingClientRect().height) + 2);
      if (Math.abs(frame.getBoundingClientRect().height - height) > 2) frame.style.height = height + 'px';
    }
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(wrap);
    }
    listen(frame.contentWindow, 'resize', resize);
    listen(doc, 'toggle', resize);
    const style = doc.createElement('link');
    style.rel = 'stylesheet';
    style.href = new URL(frame.dataset.style, document.baseURI).href;
    style.onload = () => { if (!destroyed) { resize(); callbacks.onReady(); } };
    style.onerror = () => { if (!destroyed) callbacks.onError(); };
    doc.head.append(style);
    notifyBusy();
    return {resize, destroy() {
      destroyed = true;
      resizeObserver?.disconnect();
      busyObserver.disconnect();
      for (const remove of listeners) remove();
    }};
  }};
})();
