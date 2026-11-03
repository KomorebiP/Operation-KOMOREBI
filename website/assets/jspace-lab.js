/* The saved instrument remains a byte-for-byte asset. This shell selects its
   existing guided cases; all inference, grading and exports stay in that app. */
(() => {
  'use strict';
  const root = document.getElementById('j-lab');
  if (!root) return;
  const frame = document.getElementById('jl-frame');
  const workspace = document.getElementById('jl-workspace');
  const launch = document.getElementById('jl-launch');
  const status = document.getElementById('jl-status');
  const note = document.getElementById('jl-guide-note');
  const guides = {
    edit: {tab: 'causal', note: 'Choose a donor value, move the intervention strength, and compare the two agents. Then audit the remembered facts. The whole-donor branch is a reference for the requested change.'},
    relay: {tab: 'relay', demo: 'mDemo', note: 'The guided settings are loaded. Select “Trace the connection”, then inspect successive checkpoints. Compare the one-agent edit, restored first packet, packet-only replay and whole-donor reference. Try reversing the writer.'},
    persistence: {tab: 'challenge', demo: 'tDemo', note: 'The guided swap and factual-reload case is loaded. Select “Run three-way comparison”, then inspect each checkpoint. An edit can match the target initially and fail during later computation or recall.'}
  };
  let pending = 'edit', loaded = false, ready = false, timer, generation = 0;
  function chooseGuide() {
    const app = frame.contentWindow, guide = guides[pending];
    app.JCausalLab.resetDemo();
    app.document.querySelector('[data-tab="'+guide.tab+'"]').click();
    if (guide.demo) app.document.getElementById(guide.demo).click();
    note.textContent = guide.note;
    status.textContent = 'Lab ready. Saved models run locally in this browser.';
    launch.textContent = 'Return to the current lab →';
  }
  function fail() {
    clearTimeout(timer);
    ready = false;
    loaded = false;
    generation++;
    launch.textContent = 'Retry loading the lab →';
    status.textContent = 'The embedded lab could not finish loading. Retry, or use “Open in a full tab” above.';
    // Keep a partially loaded app available for inspection and direct recovery.
  }
  function awaitReady(ticket, remaining) {
    if (ticket !== generation) return;
    try {
      const app = frame.contentWindow;
      if (app.JCausalLab && app.JRelayLab && app.JChallengeLab) {
        ready = true;
        chooseGuide();
        return;
      }
    } catch (_) { fail(); return; }
    if (!remaining) { fail(); return; }
    timer = setTimeout(() => awaitReady(ticket, remaining - 1), 100);
  }
  function open(guide, focus) {
    if (guide) pending = guide;
    workspace.hidden = false;
    if (guide) note.textContent = guides[pending].note;
    if (ready && guide) chooseGuide();
    else if (!loaded) {
      loaded = true;
      frame.hidden = false;
      status.textContent = 'Loading the self-contained lab · 4.4 MB, including saved weights…';
      const ticket = ++generation;
      frame.onload = () => { clearTimeout(timer); awaitReady(ticket, 300); };
      frame.onerror = () => { if (ticket === generation) fail(); };
      timer = setTimeout(() => { if (ticket === generation) fail(); }, 45000);
      frame.src = frame.dataset.src;
    }
    if (focus) document.getElementById('jl-workspace-title').focus();
  }
  launch.disabled = false;
  launch.addEventListener('click', () => open(null, true));
  for (const button of root.querySelectorAll('[data-jl-guide]')) {
    button.disabled = false;
    button.addEventListener('click', () => open(button.dataset.jlGuide, true));
  }
  const hash = window.location.hash.slice(1);
  if (Object.hasOwn(guides, hash)) open(hash, false);
})();
