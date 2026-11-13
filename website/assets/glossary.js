"use strict";

// Match text and compatibility spellings such as subscript digits and ligatures.
function glossaryWords(value) {
  return value.normalize("NFKC").toLocaleLowerCase("en").replace(/[-\u2010-\u2015\u2212]/g, " ").replace(/\s+/g, " ").trim();
}

const glossary = document.querySelector("#glossary-lookup");
if (glossary) {
  const form = document.querySelector("#glossary-form");
  const query = document.querySelector("#glossary-query");
  const subject = document.querySelector("#glossary-subject");
  const status = document.querySelector("#glossary-status");
  const matches = document.querySelector("#glossary-matches");
  const title = document.querySelector("#glossary-results-title");
  const list = document.querySelector("#glossary-results");
  const entries = Array.from(list.children, node => ({node,
    term: glossaryWords(node.dataset.term), text: glossaryWords(node.dataset.search),
    aliases: (node.dataset.aliases || '').split('\n').filter(Boolean).map(glossaryWords),
    subject: node.dataset.subject}));
  let announcement;

  function lookup(announce = true) {
    clearTimeout(announcement);
    const text = glossaryWords(query.value.trim());
    const words = text.split(/\s+/).filter(Boolean);
    const active = !!(text || subject.value);
    const ranked = entries.map(entry => ({...entry,
      visible: active && (!subject.value || entry.subject === subject.value) && words.every(word => entry.text.includes(word)),
      rank: entry.term === text ? 0 : entry.aliases.includes(text) ? 1 : entry.term.startsWith(text) ? 2 : 3}));
    ranked.sort((a, b) => a.rank - b.rank); // Preserve alphabetical order within each rank.
    let count = 0;
    for (const entry of ranked) {
      entry.node.hidden = !entry.visible;
      if (entry.visible) { count++; list.append(entry.node); }
    }
    matches.hidden = count === 0;
    const message = !active ? "Search all " + entries.length + " terms, or browse below." : count
      ? count + (count === 1 ? " matching term." : " matching terms.")
      : "No matching terms. Try fewer words or choose All subjects.";
    if (announce) announcement = setTimeout(() => { status.textContent = message; }, 180);
    else status.textContent = message;
    const url = new URL(location.href);
    for (const [key, value] of [["q", query.value.trim()], ["subject", subject.value]]) {
      if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
    }
    history.replaceState(null, "", url);
    return count;
  }

  function restoreLookup() {
    const params = new URL(location.href).searchParams;
    query.value = params.get("q") || "";
    const selected = params.get("subject") || "";
    subject.value = Array.from(subject.options).some(option => option.value === selected) ? selected : "";
    lookup(false);
  }
  window.addEventListener("popstate", restoreLookup);
  query.addEventListener("input", () => lookup());
  subject.addEventListener("change", () => lookup(false));
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (lookup(false)) { title.focus({preventScroll: true}); title.scrollIntoView(); }
  });
  form.addEventListener("reset", event => {
    event.preventDefault();
    query.value = subject.value = "";
    lookup(false);
    query.focus();
  });
  // The complete reference and every original anchor remain available below.
  form.hidden = status.hidden = false;
  restoreLookup();
}

// The section reader reuses the complete reference nodes in both views.
// Without this enhancement every subject and term remains ordinary HTML.
const glossaryBrowser = document.querySelector("#glossary-browser");
if (glossaryBrowser) {
  const controls = document.querySelector("#glossary-controls");
  const overview = document.querySelector("#glossary-overview");
  const panels = document.querySelector("#glossary-panels");
  const readingControls = document.querySelector("#glossary-reading-controls");
  const sectionPicker = document.querySelector("#glossary-section");
  const termPicker = document.querySelector("#glossary-term");
  const position = document.querySelector("#glossary-position");
  const search = document.querySelector("#glossary-search");
  const modeButtons = ["long", "slides"].map(mode => document.querySelector("#glossary-view-" + mode));
  const steps = Array.from(glossaryBrowser.querySelectorAll(".glossary-step-controls"));
  const groups = Array.from(panels.querySelectorAll("[data-glossary-panel]"), panel => ({
    node: panel, id: panel.dataset.glossaryPanel, title: panel.dataset.title,
    terms: Array.from(panel.querySelectorAll("[data-glossary-term]"))
  }));
  let mode = "long", selected = -1, current = 0, pickerSection = "";

  function savedMode() {
    try { return localStorage.getItem("glossary-view") === "slides" ? "slides" : "long"; }
    catch { return "long"; }
  }
  function rememberMode() {
    try { localStorage.setItem("glossary-view", mode); } catch { /* Reading works without storage. */ }
  }
  function hashTarget(hash) {
    try { return document.getElementById(decodeURIComponent(hash.replace(/^#/, ""))); }
    catch { return null; }
  }
  function locate(target) {
    const panel = target?.closest("[data-glossary-panel]");
    const group = groups.findIndex(group => group.node === panel);
    const term = target?.closest("[data-glossary-term]");
    return {group, term: group >= 0 ? Math.max(0, groups[group].terms.indexOf(term)) : 0};
  }
  function render() {
    const group = groups[selected];
    overview.hidden = panels.hidden = false;
    overview.hidden = !!group;
    panels.hidden = !group;
    readingControls.hidden = !group;
    sectionPicker.value = group?.id || "";
    glossaryBrowser.dataset.view = mode;
    modeButtons.forEach((button, i) => button.setAttribute("aria-pressed", String(mode === ["long", "slides"][i])));
    groups.forEach((item, i) => {
      item.node.hidden = i !== selected;
      item.terms.forEach((term, index) => { term.hidden = mode === "slides" && index !== current; });
    });
    if (group) {
      if (pickerSection !== group.id) {
        termPicker.replaceChildren(...group.terms.map(term => {
          const option = document.createElement("option");
          option.value = term.dataset.glossaryTerm;
          option.textContent = term.dataset.title;
          return option;
        }));
        pickerSection = group.id;
      }
      termPicker.value = group.terms[current].dataset.glossaryTerm;
      position.textContent = mode === "slides"
        ? group.title + " · Term " + (current + 1) + " of " + group.terms.length
        : group.title + " · " + group.terms.length + " terms · Long view";
    } else position.textContent = "";
    steps.forEach(nav => {
      nav.hidden = !group;
      const previous = nav.querySelector("[data-glossary-previous]");
      const next = nav.querySelector("[data-glossary-next]");
      previous.disabled = selected === 0 && (mode === "long" || current === 0);
      next.disabled = selected === groups.length - 1 && (mode === "long" || current === group?.terms.length - 1);
      previous.textContent = mode === "slides" && current > 0 ? "← Previous term" : "← Previous section";
      next.textContent = mode === "slides" && current < (group?.terms.length || 0) - 1 ? "Next term →" : "Next section →";
    });
  }
  function reveal(hash) {
    const target = hashTarget(hash);
    const found = locate(target);
    selected = found.group;
    current = found.term;
    if (found.group >= 0) search.open = false;
    for (let parent = target; parent; parent = parent.parentElement) {
      if (parent.tagName === "DETAILS") parent.open = true;
    }
    render();
    return target;
  }
  function restore() {
    const url = new URL(location.href);
    const params = url.searchParams;
    mode = ["long", "slides"].includes(params.get("view")) ? params.get("view") : savedMode();
    if (params.get("view") !== mode) {
      params.set("view", mode);
      history.replaceState(null, "", url);
    }
    if (location.hash) reveal(location.hash);
    else {
      selected = groups.findIndex(group => group.id === params.get("section"));
      current = 0;
      render();
    }
    if (params.get("q") || params.get("subject")) search.open = true;
  }
  function go(groupIndex, termIndex, focus = true, sectionHeading = false) {
    selected = groupIndex;
    current = termIndex;
    const group = groups[selected];
    const id = sectionHeading ? group.id : group.terms[current].dataset.glossaryTerm;
    const url = new URL(location.href);
    url.searchParams.set("view", mode);
    url.searchParams.set("section", group.id);
    url.hash = id;
    history.pushState(null, "", url);
    search.open = false;
    render();
    if (focus) {
      const heading = sectionHeading ? group.node.querySelector("h2") : group.terms[current].querySelector("h3");
      heading.setAttribute("tabindex", "-1");
      heading.focus({preventScroll: true});
      heading.scrollIntoView({block: "start"});
    }
  }
  function step(direction) {
    if (selected < 0) return;
    const count = groups[selected].terms.length;
    if (mode === "slides" && current + direction >= 0 && current + direction < count) go(selected, current + direction);
    else if (selected + direction >= 0 && selected + direction < groups.length) {
      const next = selected + direction;
      go(next, mode === "slides" && direction < 0 ? groups[next].terms.length - 1 : 0, true, mode === "long");
    }
  }
  modeButtons.forEach((button, index) => button.addEventListener("click", () => {
    const nextMode = ["long", "slides"][index];
    if (nextMode === mode) return;
    if (selected >= 0 && nextMode === "slides") {
      const visible = groups[selected].terms.findIndex(term => {
        const rect = term.getBoundingClientRect();
        return rect.bottom > 0 && rect.top < window.innerHeight;
      });
      if (visible >= 0) current = visible;
    }
    mode = nextMode;
    rememberMode();
    if (selected >= 0) go(selected, current, false);
    else {
      const url = new URL(location.href);
      url.searchParams.set("view", mode);
      history.pushState(null, "", url);
      render();
    }
  }));
  sectionPicker.addEventListener("change", () => {
    const next = groups.findIndex(group => group.id === sectionPicker.value);
    if (next >= 0) go(next, 0, true, true);
    else {
      const url = new URL(location.href);
      url.searchParams.delete("section");
      url.hash = "glossary-sections";
      history.pushState(null, "", url);
      reveal(url.hash);
      document.querySelector("#glossary-sections").focus();
    }
  });
  termPicker.addEventListener("change", () => {
    const next = groups[selected]?.terms.findIndex(term => term.dataset.glossaryTerm === termPicker.value);
    if (next >= 0) go(selected, next);
  });
  steps.forEach(nav => {
    nav.querySelector("[data-glossary-previous]").addEventListener("click", () => step(-1));
    nav.querySelector("[data-glossary-next]").addEventListener("click", () => step(1));
  });
  panels.addEventListener("keydown", event => {
    if (mode !== "slides" || event.altKey || event.ctrlKey || event.metaKey ||
        event.target.closest("a,button,input,select,textarea,summary,[contenteditable]")) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      step(event.key === "ArrowLeft" ? -1 : 1);
    }
  });
  // Reveal before reader.js moves focus: its link handler also uses pushState,
  // which does not emit hashchange. Preserve modified-click browser behavior.
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest("a[href]");
    if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && url.pathname === location.pathname && url.search === location.search && url.hash) reveal(url.hash);
  }, {capture: true});
  window.addEventListener("hashchange", restore);
  window.addEventListener("popstate", restore);
  restore();
  controls.hidden = false;
  glossaryBrowser.classList.add("glossary-ready");
}
