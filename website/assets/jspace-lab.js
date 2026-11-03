/* The verified instrument owns inference, grading and exports. This controller
   selects examples and coordinates its presentation within the reader site. */
(() => {
  'use strict';
  const root = document.getElementById('j-lab');
  if (!root) return;
  const frame = document.getElementById('jl-frame');
  const launch = document.getElementById('jl-launch');
  const reset = document.getElementById('jl-reset');
  const start = document.getElementById('jl-start-panel');
  const status = document.getElementById('jl-status');
  const note = document.getElementById('jl-guide-note');
  const title = document.getElementById('jl-workspace-title');
  const label = document.getElementById('jl-step-label');
  const buttons = [...root.querySelectorAll('[data-jl-guide]')];
  const guides = {
    edit: {tab: 'causal', label: '01 / State edit', title: 'Can an edit change the answer?', start: 'Start state edit', note: 'Choose a target pair and adjust the edit strength. Compare the two agents’ answers, then audit their remembered facts.'},
    relay: {tab: 'relay', demo: 'mDemo', label: '02 / Message trace', title: 'Does the change reach the other agent?', start: 'Start message trace', note: 'Choose which agent to edit, then select “Run message trace”. Compare the recipient’s answer with the original, restored-message and replayed-message branches.'},
    persistence: {tab: 'challenge', demo: 'tDemo', label: '03 / Persistence', title: 'Will the change last?', start: 'Start persistence test', note: 'Choose what happens after the edit, then select “Run persistence test”. Compare the original, edited and donor states, including the facts each agent can still recall.'}
  };
  let pending = 'edit', loaded = false, ready = false, busy = false;
  let timer, watchdog, generation = 0, view;
  function selection(key) {
    pending = key;
    const guide = guides[key];
    title.textContent = guide.title;
    label.textContent = guide.label;
    note.textContent = guide.note;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.jlGuide === key));
    if (!loaded) launch.textContent = guide.start + ' →';
  }
  function setBusy(value) {
    busy = value;
    for (const button of buttons) button.disabled = value;
    reset.disabled = !ready || value;
    if (ready) status.textContent = value ? 'Experiment running. Stop or cancel it before changing experiments.' : 'Ready · Saved models run locally in this browser.';
  }
  function chooseGuide() {
    const app = frame.contentWindow, guide = guides[pending];
    if (guide.demo) app.document.getElementById(guide.demo).click();
    else app.JCausalLab.resetDemo();
    app.document.querySelector('[data-tab="' + guide.tab + '"]').click();
    view?.resize();
    setBusy(false);
  }
  function fail() {
    clearTimeout(timer);
    clearTimeout(watchdog);
    view?.destroy();
    view = undefined;
    ready = false;
    loaded = false;
    generation++;
    frame.hidden = true;
    start.hidden = false;
    reset.hidden = true;
    launch.disabled = false;
    launch.textContent = 'Retry loading the lab →';
    setBusy(false);
    status.textContent = 'The lab could not finish loading. Retry, or open the full research lab above.';
  }
  function awaitReady(ticket, remaining) {
    if (ticket !== generation) return;
    try {
      const app = frame.contentWindow;
      if (app.JCausalLab && app.JRelayLab && app.JChallengeLab) {
        view = window.JSpaceWorkbench.mount(frame, {
          onTabChange(tab) {
            const key = Object.keys(guides).find(key => guides[key].tab === tab);
            if (key) selection(key);
          },
          onBusyChange: setBusy,
          onReady() {
            if (ticket !== generation) return;
            clearTimeout(watchdog);
            ready = true;
            frame.hidden = false;
            start.hidden = true;
            reset.hidden = false;
            chooseGuide();
          },
          onError() { if (ticket === generation) fail(); }
        });
        return;
      }
    } catch (_) { fail(); return; }
    if (!remaining) { fail(); return; }
    timer = setTimeout(() => awaitReady(ticket, remaining - 1), 100);
  }
  function open(guide, focus, fresh = false) {
    if (busy) return;
    const changed = guide && guide !== pending;
    if (guide) selection(guide);
    if (ready && (changed || fresh)) {
      // A new example gets a fresh instrument document. The original demo
      // buttons change inputs but retain old trace tables and batch results.
      // Reloading avoids presenting those measurements as a new run.
      view?.destroy();
      view = undefined;
      ready = false;
      loaded = false;
      frame.hidden = true;
      start.hidden = false;
      reset.hidden = true;
      reset.disabled = true;
    }
    if (!loaded) {
      loaded = true;
      launch.disabled = true;
      launch.textContent = 'Loading the lab…';
      status.textContent = 'Loading saved models · 4.4 MB…';
      const ticket = ++generation;
      frame.onload = () => {
        if (ticket !== generation) return;
        clearTimeout(timer);
        awaitReady(ticket, 300);
      };
      frame.onerror = () => { if (ticket === generation) fail(); };
      watchdog = setTimeout(() => { if (ticket === generation) fail(); }, 45000);
      frame.src = frame.dataset.src;
    }
    if (focus) title.focus();
  }
  launch.disabled = false;
  launch.addEventListener('click', () => open(null, true));
  reset.addEventListener('click', () => open(pending, true, true));
  for (const button of buttons) {
    button.disabled = false;
    button.addEventListener('click', () => open(button.dataset.jlGuide, false));
  }
  const hash = window.location.hash.slice(1);
  if (Object.hasOwn(guides, hash)) open(hash, false);
})();
