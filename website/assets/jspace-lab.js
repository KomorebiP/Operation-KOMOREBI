/* The verified instrument owns inference, grading and exports. This controller
   selects examples and coordinates its presentation within the reader site. */
(() => {
  'use strict';
  const root = document.getElementById('j-lab');
  if (!root) return;
  const frame = document.getElementById('jl-frame');
  const launch = document.getElementById('jl-launch');
  const reset = document.getElementById('jl-reset');
  const resume = document.getElementById('jl-return');
  const start = document.getElementById('jl-start-panel');
  const status = document.getElementById('jl-status');
  const note = document.getElementById('jl-guide-note');
  const title = document.getElementById('jl-workspace-title');
  const label = document.getElementById('jl-step-label');
  const buttons = [...root.querySelectorAll('[data-jl-guide]')];
  const jumps = [...root.querySelectorAll('[data-jl-jump]')];
  const guides = {
    edit: {tab: 'causal', label: '01 / State edit', title: 'Can an edit change the answer?', start: 'Start state edit', steps: ['Choose edit', 'Compare answers', 'Check facts'], note: 'Change a small part of the agents’ internal states. Test whether the answers change while the remembered facts stay retrievable.'},
    relay: {tab: 'relay', demo: 'mDemo', label: '02 / Message trace', title: 'Does the change reach the other agent?', start: 'Start message trace', steps: ['Set up trace', 'Read the message effect', 'Check facts'], note: 'Edit one agent, then test whether its first message carries the effect to its partner. Restoration and replay help isolate that first connection.'},
    persistence: {tab: 'challenge', demo: 'tDemo', label: '03 / Persistence', title: 'Will the change last?', start: 'Start persistence test', steps: ['Choose later steps', 'Read the results', 'Inspect recall'], note: 'Continue computing after a single edit. Check when the intended answer fails and whether stored facts can still be recalled.'}
  };
  let pending = 'edit', loaded = false, ready = false, busy = false;
  let timer, watchdog, generation = 0, view, returnGuide;
  function selection(key) {
    pending = key;
    const guide = guides[key];
    title.textContent = guide.title;
    label.textContent = guide.label;
    note.textContent = guide.note;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.jlGuide === key));
    jumps.forEach((button, index) => { button.textContent = (index + 1) + ' · ' + guide.steps[index]; });
    if (!loaded) launch.textContent = guide.start + ' →';
  }
  function setBusy(value) {
    busy = value;
    for (const button of buttons) button.disabled = value;
    reset.disabled = !ready || value;
    for (const button of jumps) button.disabled = !ready;
    resume.disabled = !ready || value;
    if (ready) status.textContent = value ? 'Test running. You can inspect results; stop or cancel before switching examples.' : 'Ready · Use the steps below. Predictions run on your device.';
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
    resume.hidden = true;
    returnGuide = undefined;
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
          onEditSettings(key) {
            returnGuide = key;
            resume.hidden = false;
            resume.disabled = false;
            note.textContent = 'Adjust the target or edit amount, then use “Return to message trace with these settings”. Your settings will be kept; run the trace again to measure the new setup.';
          },
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
      resume.hidden = true;
      returnGuide = undefined;
      for (const button of jumps) button.disabled = true;
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
  resume.addEventListener('click', () => {
    if (!ready || busy || !returnGuide) return;
    const key = returnGuide;
    returnGuide = undefined;
    resume.hidden = true;
    selection(key);
    frame.contentWindow.document.querySelector('[data-tab="' + guides[key].tab + '"]').click();
    view?.useEditorSettings(key);
    view?.jump(0);
  });
  for (const button of buttons) {
    button.disabled = false;
    button.addEventListener('click', () => open(button.dataset.jlGuide, false));
  }
  jumps.forEach((button, index) => {
    button.addEventListener('click', () => { if (ready) view?.jump(index); });
  });
  const hash = window.location.hash.slice(1);
  if (Object.hasOwn(guides, hash)) open(hash, false);
})();
