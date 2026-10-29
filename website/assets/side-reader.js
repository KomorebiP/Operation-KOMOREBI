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
  const workFor = url => data.entries.find(row => row.url === url)?.works[0] ||
    data.entries.find(row => row.url.split("#")[0] === url.split("#")[0])?.works[0] || "";
  const titleFor = url => data.entries.find(row => row.url === url)?.title || data.pages[url.split(/[?#]/u)[0]] || "Document";

  function save(push = false) {
    const url = api.pairURL(base, state);
    if (location.href !== url) history[push ? "pushState" : "replaceState"](null, "", url);
    $("side-share-fallback").hidden = true;
  }
  function layout() {
    root.dataset.view = state.view;
    root.style.setProperty("--left-width", state.width + "%");
    $("side-width").value = state.width;
    $("side-width-value").value = state.width + "%";
    for (const button of root.querySelectorAll("[data-side-view]")) button.setAttribute("aria-pressed", String(button.dataset.sideView === state.view));
    for (const side of sides) $(side + "-pane").hidden = state.view !== "both" && state.view !== side;
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
    const standalone = $(side + "-standalone");
    standalone.href = new URL(value, base).href;
    standalone.hidden = false;
    if (!pending[side] && loaded[side] === value) return;
    if (!pending[side] && loaded[side] && loaded[side].split("#")[0] === value.split("#")[0]) {
      loaded[side] = value;
      frame.contentWindow.history.replaceState(null, "", new URL(value, base).href);
      positionPane(side, Boolean(focusAfterLoad[side]));
      focusAfterLoad[side] = false;
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
    if (!main || main.dataset.sidePrepared) return;
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
      if (!api.canonical(link.href, base, data.pages)) {
        link.target = "_blank";
        link.rel = "noopener";
        link.setAttribute("aria-label", link.textContent.trim() + " (opens in a new tab)");
      }
    }
    doc.addEventListener("click", event => {
      if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest("a[href]");
      if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
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
    // Source line forms and existing reading controls can change the hash directly.
    const updateAddress = () => {
      const current = api.canonical(frame.contentWindow.location.href, base, data.pages);
      if (!current || current === state[side]) return;
      state[side] = current;
      loaded[side] = current;
      $(side + "-standalone").href = new URL(current, base).href;
      save();
    };
    frame.contentWindow.addEventListener("hashchange", updateAddress);
    doc.addEventListener("submit", () => setTimeout(updateAddress, 0));
    if (focusAfterLoad[side]) {
      focusAfterLoad[side] = false;
      focusPane(side);
    } else positionPane(side);
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
    if (matches.some(row => row.url === previous)) select.value = previous;
    else if (matches.length) select.selectedIndex = 0;
    $(side + "-count").textContent = matches.length + " documents and passages" + (matches.length ? "." : ". Try fewer words or clear the filters.");
    $(side + "-form").querySelector("button[type=submit]").disabled = !matches.length;
  }
  for (const side of sides) {
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
    $(side + "-read").addEventListener("click", () => focusPane(side));
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
    for (const side of sides) load(side);
  });
  root.hidden = false;
  document.body.classList.add("side-reader-page");
  layout(); save();
  for (const side of sides) load(side);
  status.textContent = initialInvalid ? "An unavailable address was replaced with a reading starting point. Choose a document to continue." : "Choose a document in either pane, or follow its reading links.";
})();
