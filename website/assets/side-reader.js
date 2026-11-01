"use strict";
(async function () {
  const root = document.querySelector("#side-reader");
  if (!root) return;
  const status = document.querySelector("#side-status");
  const api = globalThis.KomorebiSideReader;
  const base = new URL("./", location.href).href;
  const $ = id => document.getElementById(id);
  let data;
  try {
    const response = await fetch(root.dataset.index);
    if (!response.ok) throw new Error("Catalogue unavailable");
    data = await response.json();
    if (data.schema !== 1 || !data.works.length || !data.entries.length || !data.pages) throw new Error("Invalid catalogue");
  } catch {
    status.textContent = "The document list could not load. Reload to try again, or use the paper and accessibility links below.";
    return;
  }
  const sides = ["left", "right"];
  const other = side => side === "left" ? "right" : "left";
  let state = api.parsePair(location.href, base, data, matchMedia("(max-width: 800px)").matches);
  const initialInvalid = state.invalid;
  const loaded = {};
  const pending = {};
  const timers = {};
  const focusAfterLoad = {};
  const positions = {};
  let sessions;
  const workFor = url => api.workIds(url, data)[0] || "";
  const titleFor = url => data.entries.find(row => row.url === url)?.title || data.pages[url.split(/[?#]/u)[0]] || "Document";

  function relatedMaterial() {
    for (const side of sides) {
      const destination = other(side);
      const ids = api.workIds(state[side], data);
      const select = $(side + "-related-work");
      const previous = select.value;
      const shared = api.workIds(state[destination], data).find(id => ids.includes(id));
      const chosen = ids.includes(previous) ? previous : shared || ids[0];
      select.replaceChildren();
      for (const id of ids) select.add(new Option(data.works.find(work => work.id === id).title, id));
      if (chosen) select.value = chosen;
      const work = data.works.find(row => row.id === chosen);
      const links = $(side + "-related-links");
      links.replaceChildren();
      for (const route of work?.routes || []) {
        const target = api.canonical(route.url, base, data.pages);
        if (!target) continue;
        const link = document.createElement("a");
        const view = state.view === "both" ? "both" : destination;
        link.href = api.pairURL(base, {...state, [destination]:target, view});
        link.dataset.relatedTarget = target;
        link.textContent = route.label;
        link.setAttribute("aria-label", route.label + " in the " + destination + " pane");
        links.append(link);
      }
      $(side + "-related").hidden = !links.childElementCount;
      $(side + "-related-choice").hidden = ids.length < 2;
      $(side + "-related-title").hidden = ids.length > 1;
      $(side + "-related-title").textContent = work?.title || "";
      $(side + "-related-description").textContent = "Open in the " + destination + " pane and keep this document here.";
    }
  }
  function save(push = false) {
    const url = api.pairURL(base, state);
    if (location.href !== url) history[push ? "pushState" : "replaceState"](null, "", url);
    $("side-share-fallback").hidden = true;
    relatedMaterial();
    sessions?.changed();
  }
  function layout() {
    sessions?.captureVisible();
    root.dataset.view = state.view;
    root.style.setProperty("--left-width", state.width + "%");
    $("side-width").value = state.width;
    $("side-width-value").value = state.width + "%";
    for (const button of root.querySelectorAll("[data-side-view]")) button.setAttribute("aria-pressed", String(button.dataset.sideView === state.view));
    for (const side of sides) {
      const pane = $(side + "-pane");
      const frame = $(side + "-frame");
      const hidden = state.view !== "both" && state.view !== side;
      if (!pane.hidden && hidden && loaded[side] && !pending[side]) {
        try { positions[side] = {url:loaded[side], x:frame.contentWindow.scrollX, y:frame.contentWindow.scrollY}; } catch {}
      }
      const revealing = pane.hidden && !hidden;
      pane.hidden = hidden;
      if (revealing) requestAnimationFrame(() => {
        if (pane.hidden || pending[side] || loaded[side] !== state[side]) return;
        const position = positions[side];
        if (position?.url === state[side]) frame.contentWindow.scrollTo(position.x, position.y);
        else positionPane(side);
        sessions?.restore(side);
      });
    }
  }
  function positionPane(side, focus = false) {
    const frame = $(side + "-frame");
    try {
      const doc = frame.contentDocument;
      let target;
      try { target = doc.getElementById(decodeURIComponent(new URL(state[side], base).hash.slice(1))); } catch {}
      target ||= doc.querySelector("#main");
      if (target) {
        for (let parent = target.parentElement; parent; parent = parent.parentElement) if (parent.matches("details")) parent.open = true;
        if (focus) {
          if (!target.hasAttribute("tabindex")) target.tabIndex = -1;
          target.focus({preventScroll:true});
          frame.scrollIntoView({block:"nearest"});
        }
        frame.contentWindow.scrollTo({top:target.getBoundingClientRect().top + frame.contentWindow.scrollY});
      } else if (focus) frame.focus();
    } catch { if (focus) frame.focus(); }
  }
  const focusPane = side => positionPane(side, true);
  function readingPreferences(value) {
    document.body.classList.toggle("side-reading-focus", value.focus);
    $("side-focus").setAttribute("aria-pressed", String(value.focus));
    $("side-focus").textContent = value.focus ? "Show site navigation" : "Focus on reading";
    for (const side of sides) $(side + "-send").checked = value.send[side];
  }
  function restoreSession(value) {
    state = {left:value.left, right:value.right, view:value.view, width:value.width, invalid:false};
    readingPreferences(value);
    $("side-work-picker").open = false;
    for (const side of sides) focusAfterLoad[side] = state.view === side || state.view === "both" && side === "left";
    layout(); save(true);
    for (const side of sides) {
      $(side + "-work").value = workFor(state[side]);
      $(side + "-query").value = "";
      $(side + "-kind").value = "";
      refresh(side); load(side);
    }
    status.textContent = "Restoring your saved reading session.";
  }
  function openPair(pair, message) {
    state.left = pair.left;
    state.right = pair.right;
    state.view = matchMedia("(max-width: 800px)").matches ? "left" : "both";
    focusAfterLoad.left = true;
    focusAfterLoad.right = false;
    layout(); save(true);
    for (const side of sides) {
      $(side + "-work").value = workFor(state[side]);
      $(side + "-query").value = "";
      $(side + "-kind").value = "";
      refresh(side); load(side);
    }
    status.textContent = message;
  }
  function navigate(side, value, push = true, reveal = true) {
    const url = api.canonical(value, base, data.pages);
    if (!url) {
      status.textContent = "That address is not in the reading catalogue. Choose a listed document.";
      return;
    }
    state[side] = url;
    if (reveal && state.view !== "both" && state.view !== side) state.view = side;
    layout();
    save(push);
    load(side);
  }
  function load(side) {
    const value = state[side];
    const frame = $(side + "-frame");
    $(side + "-current").textContent = titleFor(value);
    frame.title = (side === "left" ? "Left" : "Right") + " reading pane: " + titleFor(value);
    const standalone = $(side + "-standalone");
    standalone.href = new URL(value, base).href;
    standalone.hidden = false;
    if (!pending[side] && loaded[side] === value) {
      if (focusAfterLoad[side]) focusPane(side);
      focusAfterLoad[side] = false;
      sessions?.restore(side);
      return;
    }
    if (!pending[side] && loaded[side] && loaded[side].split("#")[0] === value.split("#")[0]) {
      loaded[side] = value;
      frame.contentWindow.history.replaceState(null, "", new URL(value, base).href);
      positionPane(side, Boolean(focusAfterLoad[side]));
      focusAfterLoad[side] = false;
      sessions?.restore(side);
      return;
    }
    $(side + "-read").disabled = true;
    $(side + "-status").textContent = "Loading document…";
    clearTimeout(timers[side]);
    timers[side] = setTimeout(() => {
      if (loaded[side] !== value && state[side] === value) $(side + "-status").textContent = "This document is taking longer to load. Use Open on its own to read it in a separate tab.";
    }, 20000);
    frame.hidden = false;
    pending[side] = value;
    // replace avoids adding a second, iframe-only entry to browser history.
    const destination = new URL(value, base);
    destination.hash = "";
    frame.contentWindow.location.replace(destination.href);
  }
  function decorate(side) {
    const frame = $(side + "-frame");
    let doc, url;
    try {
      doc = frame.contentDocument;
      url = api.canonical(frame.contentWindow.location.href, base, data.pages);
    } catch { return; }
    if (!doc || !url || url.split("#")[0] !== state[side].split("#")[0]) return;
    url = state[side];
    frame.contentWindow.history.replaceState(null, "", new URL(url, base).href);
    clearTimeout(timers[side]);
    pending[side] = null;
    loaded[side] = url;
    frame.title = (side === "left" ? "Left" : "Right") + " reading pane: " + titleFor(url);
    $(side + "-read").disabled = false;
    $(side + "-status").textContent = "Document ready.";
    doc.documentElement.classList.add("in-side-reader");
    const main = doc.querySelector("#main");
    if (!main || main.dataset.sidePrepared) {sessions?.watch(side); return;}
    main.dataset.sidePrepared = "true";
    for (const position of ["prepend", "append"]) {
      const button = doc.createElement("button");
      button.type = "button";
      button.className = "side-return";
      button.textContent = "Return to " + side + " pane controls";
      button.addEventListener("click", () => $(side + "-read").focus());
      main[position](button);
    }
    for (const nav of doc.querySelectorAll(".document-routes")) {
      const details = doc.createElement("details");
      details.className = "side-document-routes";
      const summary = doc.createElement("summary");
      summary.textContent = "Paper, proofs, Lean, code and examples";
      details.append(summary);
      nav.before(details);
      details.append(nav);
    }
    for (const link of doc.querySelectorAll("a[href]")) {
      if (link.hasAttribute("download")) continue;
      if (!api.canonical(link.href, base, data.pages) && !api.linkedPair(link.href, base, data.pages)) {
        link.target = "_blank";
        link.rel = "noopener";
        link.setAttribute("aria-label", link.textContent.trim() + " (opens in a new tab)");
      }
    }
    doc.addEventListener("click", event => {
      if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest("a[href]");
      if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
      const pair = api.linkedPair(link.href, base, data.pages);
      if (pair) {
        event.preventDefault();
        event.stopPropagation();
        openPair(pair, "The statement and its recorded companion are open. Use either pane’s reading controls to continue.");
        return;
      }
      const target = api.canonical(link.href, base, data.pages);
      if (!target) return;
      event.preventDefault();
      event.stopPropagation();
      const destination = $(side + "-send").checked ? other(side) : side;
      focusAfterLoad[destination] = true;
      navigate(destination, target);
      if (destination !== side) status.textContent = "Opened in the " + destination + " pane. Your " + side + " document stays in place.";
      else if (loaded[side] === target) focusPane(side);
    }, true);
    doc.addEventListener("submit", event => {
      if (event.target.id !== "source-line-form") return;
      const line = doc.querySelector("#source-line-number");
      if (!line || !event.target.reportValidity() || !doc.getElementById("L" + line.valueAsNumber)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      navigate(side, state[side].split("#")[0] + "#L" + line.valueAsNumber);
      focusPane(side);
    }, true);
    // Reading controls and filters can change the document address directly.
    const updateAddress = () => {
      const current = api.canonical(frame.contentWindow.location.href, base, data.pages);
      if (!current || current === state[side]) return;
      state[side] = current;
      loaded[side] = current;
      $(side + "-standalone").href = new URL(current, base).href;
      save();
    };
    frame.contentWindow.addEventListener("hashchange", updateAddress);
    for (const event of ["submit", "input", "change", "reset"]) doc.addEventListener(event, () => setTimeout(updateAddress, 0));
    if (focusAfterLoad[side]) {
      focusAfterLoad[side] = false;
      focusPane(side);
    } else positionPane(side);
    sessions?.watch(side);
  }
  function refresh(side) {
    const matches = api.filter(data.entries, $(side + "-query").value, $(side + "-work").value, $(side + "-kind").value);
    const select = $(side + "-document");
    const previous = select.value;
    const fragment = document.createDocumentFragment();
    for (const row of matches) {
      const option = document.createElement("option");
      option.value = row.url;
      option.textContent = row.kind + ": " + row.title;
      fragment.append(option);
    }
    select.replaceChildren(fragment);
    if (matches.some(row => row.url === state[side])) select.value = state[side];
    else if (matches.some(row => row.url === previous)) select.value = previous;
    else if (matches.length) select.selectedIndex = 0;
    $(side + "-count").textContent = matches.length + " documents and passages" + (matches.length ? "." : ". Try fewer words or clear the filters.");
    $(side + "-form").querySelector("button[type=submit]").disabled = !matches.length;
  }
  for (const work of data.works) {
    $("side-left-work").add(new Option(work.title, work.id));
    $("side-right-work").add(new Option(work.title, work.id));
  }
  $("side-left-work").value = workFor(state.left) || data.works[0].id;
  const rightWork = workFor(state.right);
  const nextWork = (data.works.findIndex(work => work.id === $("side-left-work").value) + 1) % data.works.length;
  $("side-right-work").value = rightWork && rightWork !== $("side-left-work").value ? rightWork : data.works[nextWork].id;
  $("side-work-picker").open = !new URL(location.href).searchParams.has("right");
  $("side-works-form").addEventListener("submit", event => {
    event.preventDefault();
    const pair = api.workPair($("side-left-work").value, $("side-right-work").value, base, data);
    if (!pair) {
      status.textContent = "Choose two available works to read together.";
      return;
    }
    $("side-work-picker").open = false;
    openPair(pair, "Your chosen works are open. Each pane has its own chapters and related material.");
  });
  for (const side of sides) {
    $(side + "-related-work").addEventListener("change", relatedMaterial);
    $(side + "-related-links").addEventListener("click", event => {
      if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest("a[data-related-target]");
      if (!link) return;
      event.preventDefault();
      const destination = other(side);
      focusAfterLoad[destination] = true;
      navigate(destination, link.dataset.relatedTarget);
      $(destination + "-work").value = $(side + "-related-work").value;
      $(destination + "-query").value = "";
      $(destination + "-kind").value = "";
      refresh(destination);
      status.textContent = "Opened " + link.textContent + " in the " + destination + " pane. Your " + side + " document stays in place.";
    });
    for (const work of data.works) $(side + "-work").add(new Option(work.title, work.id));
    for (const kind of [...new Set(data.entries.map(row => row.kind))].sort()) $(side + "-kind").add(new Option(kind, kind));
    $(side + "-work").value = workFor(state[side]);
    for (const name of ["query", "work", "kind"]) $(side + "-" + name).addEventListener(name === "query" ? "input" : "change", () => refresh(side));
    $(side + "-form").addEventListener("reset", () => setTimeout(() => refresh(side), 0));
    $(side + "-form").addEventListener("submit", event => {
      event.preventDefault();
      if (!$(side + "-document").value) return;
      navigate(side, $(side + "-document").value);
      $(side + "-picker").open = false;
      $(side + "-picker").querySelector("summary").focus();
    });
    $(side + "-frame").addEventListener("load", () => decorate(side));
    $(side + "-read").addEventListener("click", () => {if (!sessions?.focusCurrent(side)) focusPane(side);});
    $(side + "-send").addEventListener("change", () => sessions?.changed());
    refresh(side);
    $(side + "-picker").open = false;
  }
  for (const button of root.querySelectorAll("[data-side-view]")) button.addEventListener("click", () => {
    state.view = button.dataset.sideView;
    layout(); save();
  });
  $("side-width").addEventListener("input", () => {state.width = Number($("side-width").value); layout(); save();});
  $("side-focus").addEventListener("click", () => {
    const focused = document.body.classList.toggle("side-reading-focus");
    $("side-focus").setAttribute("aria-pressed", String(focused));
    $("side-focus").textContent = focused ? "Show site navigation" : "Focus on reading";
    $("side-focus").focus();
    sessions?.changed();
  });
  $("side-swap").addEventListener("click", () => {
    [state.left, state.right] = [state.right, state.left];
    save(true);
    for (const side of sides) {$(side + "-work").value = workFor(state[side]); refresh(side); load(side);}
    status.textContent = "The documents have swapped sides.";
  });
  $("side-share").addEventListener("click", async () => {
    const url = api.pairURL(base, state);
    try {
      await navigator.clipboard.writeText(url);
      status.textContent = "Link copied. It opens this pair and its HTML passage anchors.";
    } catch {
      $("side-share-fallback").hidden = false;
      $("side-share-url").value = url;
      $("side-share-url").focus(); $("side-share-url").select();
      status.textContent = "Copy the selected link with your browser’s copy command.";
    }
  });
  window.addEventListener("popstate", () => {
    state = api.parsePair(location.href, base, data, matchMedia("(max-width: 800px)").matches);
    layout();
    relatedMaterial();
    for (const side of sides) load(side);
  });
  sessions = globalThis.KomorebiReaderSessions.create({base, data, titleFor,
    getFrame:side => $(side + "-frame"), isCurrent:side => !pending[side] && loaded[side] === state[side],
    getState:() => ({...state, focus:document.body.classList.contains("side-reading-focus"),
      send:{left:$("left-send").checked, right:$("right-send").checked}}), restoreSession});
  const resumed = sessions.initial();
  if (resumed) {
    state = {left:resumed.left, right:resumed.right, view:resumed.view, width:resumed.width, invalid:false};
    readingPreferences(resumed);
    $("side-work-picker").open = false;
    for (const side of sides) {$(side + "-work").value = workFor(state[side]); refresh(side);}
  }
  root.hidden = false;
  document.body.classList.add("side-reader-page");
  layout(); save();
  for (const side of sides) load(side);
  status.textContent = resumed ? "Resumed your last reading session. Your saved positions will appear as the documents load." :
    initialInvalid ? "An unavailable address was replaced with a reading starting point. Choose a document to continue." : "Choose a document in either pane, or follow its reading links.";
})();
