/* The host editor owns diagnostics. Loading its frame is never a proof result. */
(() => {
  'use strict';
  const root = document.querySelector('[data-lean-playground]');
  if (!root) return;
  const open = root.querySelector('[data-lean-open]');
  const close = root.querySelector('[data-lean-close]');
  const external = root.querySelector('[data-lean-external]');
  const slot = root.querySelector('[data-lean-slot]');
  const status = root.querySelector('[data-lean-status]');
  const original = root.querySelector('[data-lean-original]');
  const help = root.querySelector('[data-lean-help]');
  let frame = null;
  open.hidden = false;
  open.addEventListener('click', () => {
    if (frame) frame.remove();
    frame = document.createElement('iframe');
    frame.title = 'Lean editor: Paper XII local idempotents proof';
    frame.referrerPolicy = 'no-referrer';
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-downloads allow-popups');
    frame.src = external.href;
    slot.replaceChildren(frame);
    slot.hidden = false;
    close.hidden = false;
    help.hidden = false;
    original.open = false;
    open.textContent = 'Restore original proof';
    status.textContent = 'Editor opened. Lean checks automatically; see its All Messages panel for results and connection errors.';
  });
  close.addEventListener('click', () => {
    if (frame) frame.remove();
    frame = null;
    slot.replaceChildren();
    slot.hidden = true;
    close.hidden = true;
    help.hidden = true;
    original.open = true;
    open.textContent = 'Load Lean editor';
    status.textContent = 'Editor closed. Load it again to restore the original proof.';
    open.focus();
  });
})();
