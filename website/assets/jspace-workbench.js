/* A presentation adapter for the verified 1.4 instrument. Move existing DOM
   controls without replacing event handlers, model outputs, checks or exports. */
(() => {
  'use strict';
  window.JSpaceWorkbench = {mount(frame, callbacks) {
    const doc = frame.contentDocument;
    const byId = id => doc.getElementById(id);
    const query = selector => doc.querySelector(selector);
    const listeners = [];
    const copyObservers = [];
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
    function element(tag, className, text) {
      const node = doc.createElement(tag);
      node.className = className;
      if (text) node.textContent = text;
      return node;
    }
    function noteAfter(node, text, id) {
      const note = element('p', 'jl-help-text', text);
      if (id) {
        note.id = id;
        const previous = node.getAttribute('aria-describedby');
        node.setAttribute('aria-describedby', [previous, id].filter(Boolean).join(' '));
      }
      node.after(note);
      return note;
    }
    function intro(panel, text) {
      const anchor = panel.querySelector('.panelhead') || panel.querySelector('h2, h3');
      anchor.after(element('p', 'jl-instruction', text));
    }
    function readingKey(anchor, title, entries) {
      const details = element('details', 'jl-reading-key');
      details.append(element('summary', '', title));
      const list = element('dl', '');
      for (const [term, meaning] of entries) {
        const row = element('div', '');
        row.append(element('dt', '', term), element('dd', '', meaning));
        list.append(row);
      }
      details.append(list);
      anchor.after(details);
      return details;
    }
    function label(id, text) { query('label[for="' + id + '"]').textContent = text; }
    function options(id, labels) {
      for (const option of byId(id).options) if (labels[option.value]) option.textContent = labels[option.value];
    }
    function explainLabels(id, replacements) {
      const root = byId(id);
      function update() {
        const walker = doc.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode;
          let value = node.nodeValue;
          for (const [original, plain] of replacements) value = value.replaceAll(original, plain);
          if (value !== node.nodeValue) node.nodeValue = value;
        }
      }
      update();
      // The saved renderer replaces these containers' children. Only human
      // labels are translated; numeric values and the trace objects stay intact.
      const observer = new MutationObserver(update);
      observer.observe(root, {childList: true});
      copyObservers.push(observer);
    }

    const startingPanels = [...doc.querySelectorAll('.causal-grid > .stack:first-child > .panel')];
    fold(startingPanels[0], 'Starting facts and model');
    fold(startingPanels[2], 'Readout and later operations');
    heading('.causal-edit h2', '1  Choose the edit');
    intro(query('.causal-edit'), 'Choose the working pair you want, then vary how much of the candidate state is replaced. The networks compute their own answers.');
    query('.causal-edit > label').textContent = 'Target working pair [left, right]';
    byId('cTargets').setAttribute('aria-label', 'Choose the target working pair');
    noteAfter(byId('cTargets'), 'The target is a request. Compare it with the model’s actual answer in step 2.', 'jl-target-help');
    fold(byId('cDonorInfo'), 'How the target reference was prepared', true);
    fold(query('.causal-edit > .fieldgrid'), 'Intervention and writing agent', true);
    label('cAlpha', 'Edit amount α');
    noteAfter(byId('cAlpha'), 'For the default J edit, 0 leaves the state unchanged and 1 applies the full target projection. Values above 1 push past that projection; they are not confidence scores.', 'jl-amount-help');
    byId('cApply').textContent = 'Set amount to 1';
    byId('cUndo').textContent = 'Remove edit';
    label('cAgent', 'Which agents receive the edit?');
    label('cQuery', 'Which answer should the model give?');
    label('cSuffix', 'Working steps after the edit');
    const answers = query('.causal-results');
    const answerIntro = element('header', 'jl-result-intro');
    answerIntro.append(element('h2', '', '2  Compare the answers'), element('p', 'jl-instruction', 'The dark strip shows expected reference values. The agent cards show actual predictions before and after the edit. Check for a change toward the requested target. If both reference answers are the same, that question cannot distinguish the two states.'));
    answers.prepend(answerIntro);
    explainLabels('cOutcome', [
      ['donor counterfactual', 'requested target answer'],
      ['for this consumer', 'for the selected question'],
      ['Choose a different donor value or move the strength slider.', 'Choose a different target pair or change the edit amount.']
    ]);
    const memory = byId('cMemory').closest('.panel');
    memory.querySelector('h2').textContent = '3  Check remembered facts';
    byId('cMemory').textContent = 'Test all 8 facts';
    memory.querySelector('.smalltext').textContent = 'Four separate recall attempts cover the eight original facts. Each attempt starts from a copy of the same snapshot.';
    noteAfter(byId('cMemoryResults'), '8/8 means every fact was recalled correctly in this audit. A lower score shows a recall problem; it does not prove the information was erased.');
    query('.causal-agentgrid').after(memory);
    fold(byId('cConsumers').closest('.panel'), 'Other ways to read the same state');
    fold(byId('rDosePanel'), 'Scan edit strengths');
    fold(byId('rControlsPanel'), 'Compare control interventions');
    fold(byId('cExport').closest('.panel'), 'Coordinates and trial export');
    fold(byId('rLivePanel'), 'Continue the edited state step by step');

    const relayControls = [...doc.querySelectorAll('.relay-layout > .stack:first-child > .panel')];
    const editorNotice = element('p', 'jl-editor-notice', 'Using the editor’s settings. Run message trace to measure this setup. Any earlier results below retain their recorded settings.');
    editorNotice.hidden = true;
    byId('relay').prepend(editorNotice);
    listen(byId('mEditor'), 'click', () => callbacks.onEditSettings('relay'));
    let recordedTrace;
    const traceObserver = new MutationObserver(() => {
      // A bank run or a rejected run can leave the displayed trace intact.
      // Clear the notice only after the renderer presents a different trace.
      if (frame.contentWindow.JRelayLab.getTrace() !== recordedTrace) editorNotice.hidden = true;
    });
    traceObserver.observe(byId('mMeta'), {childList: true});
    copyObservers.push(traceObserver);
    heading('.relay-layout > .stack:first-child h2', '1  Set up the trace');
    intro(relayControls[0], 'Edit one agent and watch its partner. The restored-message and replayed-message runs test the role of the first message.');
    label('mWriter', 'Which agent gets the edit?');
    options('mWriter', {'0': 'Edit Agent 1 → observe Agent 2', '1': 'Edit Agent 2 → observe Agent 1'});
    label('mKind', 'Communication mode');
    options('mKind', {work: 'Working steps with normal messages', exchange: 'Messages only · diagnostic schedule'});
    label('mProgram', 'Working program · I, L, R, S');
    noteAfter(byId('mProgram'), 'I keeps the pair. L flips the left value. R flips the right value. S swaps the two values.', 'jl-program-help');
    label('mQuery', 'Which answer should we inspect?');
    byId('mEditor').textContent = 'Change target or edit settings';
    byId('mEditor').classList.add('widebutton');
    const currentEdit = fold(byId('mContext'), 'Current model and edit settings', true);
    byId('mWriter').parentElement.after(byId('mEditor'), currentEdit);
    noteAfter(byId('mEditor'), 'Edit this same example, then return here with your target and amount.');
    fold([byId('mKind').parentElement, byId('mProgramBox'), byId('mCountBox')], 'Program and communication settings', true);
    fold(relayControls[1], 'Readout and trace export');
    fold(relayControls[2], 'Test both directions on more histories');
    fold(byId('mPackets').closest('.panel'), 'Inspect the eight message values');
    heading('#mResults > .panel:first-child h2', '2  Compare the recipient’s answers');
    intro(query('#mResults > .panel:first-child'), 'First compare the edited run with the unedited original and the whole-target reference. Then inspect restoration and replay to test the first message’s role.');
    const messageKey = readingKey(byId('mChart'), 'What do the five comparison branches mean?', [
      ['Original', 'No hidden-state edit. This is the starting comparison.'],
      ['Edited', 'Edit only the selected writer, then let the agents communicate.'],
      ['Restored', 'Keep the writer edit, but send the original first message instead.'],
      ['Replay', 'Keep the original states, but send the edited first message instead.'],
      ['Donor reference', 'Replace both states with the whole target execution. This checks competence; it is a broader change than the candidate edit.']
    ]);
    explainLabels('mSummary', [
      ['First recipient donor answer', 'After the first message'],
      ['Latest recipient donor answer', 'At the latest checkpoint'],
      ['Reached donor', 'Target reached'],
      ['Not reached', 'Target not reached'],
      ['First original-packet restoration', 'Restoring the first message'],
      ['First edited-packet replay', 'Replaying the first edited message'],
      ['donor answer', 'target answer']
    ]);
    noteAfter(messageKey, 'The chart shows model scores for the target answer, not calibrated confidence. Only the first message is restored or replayed; later messages run freely. Read checkpoint outputs to check the actual answers.');
    const relayFacts = byId('mFacts').closest('.panel');
    relayFacts.querySelector('h2').textContent = '3  Check remembered facts';
    intro(relayFacts, 'Compare recall in every branch. Reaching the target answer and preserving the original facts are separate tests.');
    byId('mRun').textContent = 'Run message trace';
    const checkpoint = query('label[for="mCheckpoint"]');
    const checkpointNodes = [];
    for (let node = checkpoint; node; node = node.nextSibling) checkpointNodes.push(node);
    fold(checkpointNodes, 'Checkpoint outputs and reference checks', true);

    const challengePanels = [...doc.querySelectorAll('#challenge > .panel')];
    heading('#challenge > .panel:first-of-type h3', '1  Set up the test');
    intro(challengePanels[0], 'The edit is applied once. The original, edited and whole-target runs then perform the same later work. Factual recall can be tested afterward.');
    fold(byId('tContext'), 'Current model and edit settings', true);
    label('tFamily', 'What should happen after the edit?');
    options('tFamily', {swap: 'Swap the left and right values once', commute: 'Flip both values, then flip them back', conjugate: 'Swap, flip left, swap back, flip right', idle: 'Keep the pair unchanged · I steps', custom: 'Write your own working program'});
    label('tLength', 'Number of later working steps');
    label('tReloads', 'Recall the stored facts afterward');
    options('tReloads', {'0': 'Skip factual recall', '1': 'Recall the starting pair once', '4': 'Recall all 8 facts in one pass', '8': 'Recall all 8 facts twice · no resets'});
    noteAfter(byId('tReloads'), 'A recall operation intentionally replaces the temporary working pair with remembered facts. The expected answer changes at that point.', 'jl-reload-help');
    heading('#tResultsPanel h3', '2  Compare what survives');
    intro(byId('tResultsPanel'), 'Read the failure boxes before judging the edit. Each agent is graded separately. A failed original or whole-target reference prevents attributing that agent’s error to the edit.');
    explainLabels('tSummary', [
      ['Edit-specific failure', 'First edit failure'],
      ['Reference failure', 'Failure in a reference run'],
      ['Edited facts at final work', 'Facts after working steps']
    ]);
    const recall = element('section', 'jl-recall-guide');
    byId('tMemoryChart').before(recall);
    recall.append(element('h3', '', '3  Inspect factual recall'), element('p', 'jl-help-text', 'The chart audits recall from independent copies at each checkpoint. If you selected factual reloads, those later rows follow a real sequence without resetting.'), byId('tMemoryChart'));
    readingKey(byId('tResultsPanel').querySelector('.panelhead'), 'Understand the result labels', [
      ['Transferred', 'For this agent, both reference answers work and the edited answer matches the intended target.'],
      ['Reverted', 'For this agent, both reference answers work but the edit gives the original answer again.'],
      ['Other error', 'For this agent, both reference answers work but the edited answer is neither the original nor the intended target.'],
      ['Reference error', 'An unedited or whole-target comparison already failed. Judge this separately from edit-specific failures.'],
      ['No contrast', 'The original and target answers are the same for this readout, so that readout cannot distinguish the two states.'],
      ['Factual reload', 'The model is now being asked for stored facts instead of the earlier temporary values.']
    ]);
    noteAfter(byId('tRows').closest('.causal-tablewrap'), 'Read a row as a checkpoint in the same run. On a small screen, scroll the table sideways to compare all three branches.');
    byId('tRun').textContent = 'Run persistence test';
    fold(byId('tWire').parentElement, 'Retrieval message options', true);
    fold(challengePanels[2], 'Try the same settings on more histories');

    const destinations = {
      causal: [query('.causal-edit'), answerIntro, memory],
      relay: [relayControls[0], query('#mResults > .panel:first-child'), relayFacts],
      challenge: [challengePanels[0], byId('tResultsPanel'), recall]
    };
    function jump(index) {
      const mode = query('[data-tab][aria-selected="true"]').dataset.tab;
      const target = destinations[mode]?.[index];
      if (!target) return;
      const title = target.querySelector('h2, h3') || target;
      title.tabIndex = -1;
      title.focus({preventScroll: true});
      resize();
      const bar = document.querySelector('.jlab-steps');
      const offset = (bar?.getBoundingClientRect().height || 0) + 24;
      window.scrollBy({top: frame.getBoundingClientRect().top + target.getBoundingClientRect().top - offset, behavior: 'auto'});
    }

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
    return {resize, jump, useEditorSettings(key) {
      if (key === 'relay') {
        recordedTrace = frame.contentWindow.JRelayLab.getTrace();
        editorNotice.hidden = false;
      }
      resize();
    }, destroy() {
      destroyed = true;
      resizeObserver?.disconnect();
      busyObserver.disconnect();
      for (const observer of copyObservers) observer.disconnect();
      for (const remove of listeners) remove();
    }};
  }};
})();
