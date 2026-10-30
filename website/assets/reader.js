"use strict";

const sideReaderLink = document.querySelector("[data-side-reader-link]");
if (sideReaderLink) {
  function updateSideReaderLink() {
    const target = new URL(sideReaderLink.href, location.href);
    const base = new URL("./", target);
    const current = new URL(location.href);
    target.searchParams.set("left", current.pathname.slice(base.pathname.length) + current.search + current.hash);
    sideReaderLink.href = target.href;
  }
  updateSideReaderLink();
  sideReaderLink.addEventListener("click", updateSideReaderLink);
  window.addEventListener("hashchange", updateSideReaderLink);
}

const siteMenuToggle = document.querySelector("#site-menu-toggle");
const siteMenuPanel = document.querySelector("#site-menu-panel");
if (siteMenuToggle && siteMenuPanel) {
  function setSiteMenu(open) {
    siteMenuPanel.hidden = !open;
    siteMenuToggle.setAttribute("aria-expanded", String(open));
  }
  // Without JavaScript the grouped links remain visible and usable.
  setSiteMenu(false);
  siteMenuToggle.hidden = false;
  siteMenuToggle.addEventListener("click", () => setSiteMenu(siteMenuPanel.hidden));
  document.querySelector(".site-navigation").addEventListener("keydown", event => {
    if (event.key === "Escape" && !siteMenuPanel.hidden) {
      event.preventDefault();
      setSiteMenu(false);
      siteMenuToggle.focus();
    }
  });
}

// In-page links move keyboard focus as well as the visual reading position.
// Delegation also covers links added by search and the notation browser.
function focusReadingTarget(target, hash) {
  if (target.matches("a:not([href])") && !target.textContent.trim()) {
    const next = target.nextElementSibling || (target.parentElement.matches("p") ? target.parentElement.nextElementSibling : null);
    if (next && next.matches("h1,h2,h3,h4,h5,h6")) target = next;
  }
  for (let parent = target.parentElement; parent; parent = parent.parentElement) {
    if (parent.matches("details")) parent.open = true;
  }
  if (location.hash !== hash) history.pushState(null, "", hash);
  if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
  target.focus({preventScroll: true});
  target.scrollIntoView();
}
function linkedReadingTarget() {
  try { return document.getElementById(decodeURIComponent(location.hash.slice(1))); }
  catch { return null; }
}

// Direct passage links and browser history need the same focus movement as
// links activated within the page. Wait for load so other reading controls
// have revealed their target, and preserve focus if the reader has moved it.
window.addEventListener("load", () => {
  const target = linkedReadingTarget();
  if (target && (!document.activeElement || document.activeElement === document.body ||
      document.activeElement === document.documentElement)) focusReadingTarget(target, location.hash);
}, {once: true});
window.addEventListener("hashchange", () => {
  const hash = location.hash;
  // Claim and notation filters may reveal the destination in their own handler.
  setTimeout(() => {
    const target = location.hash === hash && linkedReadingTarget();
    if (target) focusReadingTarget(target, hash);
  }, 0);
});

document.addEventListener("click", event => {
  if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest("a[href]");
  if (!link || link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
  const url = new URL(link.href, location.href);
  if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
  let target;
  try { target = document.getElementById(decodeURIComponent(url.hash.slice(1))); } catch { return; }
  if (!target) return;
  event.preventDefault();
  focusReadingTarget(target, url.hash);
});

const readingOptions = document.querySelector(".reading-options");
const showPassageTools = document.querySelector("#show-passage-tools");
if (readingOptions && showPassageTools) {
  const passageTools = document.querySelectorAll(".readable-chapter .passage-tools");
  const preferenceKey = "komorebi.reading.showPassageTools";
  // Storage may be unavailable in private or restricted browsing.
  try { showPassageTools.checked = localStorage.getItem(preferenceKey) === "true"; } catch {}
  function applyReadingOptions() {
    for (const group of passageTools) group.hidden = !showPassageTools.checked;
  }
  showPassageTools.addEventListener("change", () => {
    applyReadingOptions();
    try { localStorage.setItem(preferenceKey, String(showPassageTools.checked)); } catch {}
  });
  applyReadingOptions();
  readingOptions.hidden = false;
}

const sourceLineForm = document.querySelector("#source-line-form");
if (sourceLineForm) {
  const lineInput = document.querySelector("#source-line-number");
  sourceLineForm.addEventListener("submit", event => {
    event.preventDefault();
    if (!sourceLineForm.reportValidity()) return;
    const target = document.getElementById("L" + lineInput.valueAsNumber);
    if (target) focusReadingTarget(target, "#" + target.id);
  });
  // The direct-line control replaces hundreds of repetitive Tab stops.
  // Without JavaScript, the original line links remain keyboard reachable.
  for (const link of document.querySelectorAll(".source-lines .line-number")) link.tabIndex = -1;
  sourceLineForm.hidden = false;
}

function normalized(value) {
  const symbols = {α:"alpha",β:"beta",γ:"gamma",ρ:"rho",ω:"omega",η:"eta",δ:"delta",ℓ:"ell"};
  value = value.replace(/[αβγρωηδℓ]/gu, symbol => " " + symbols[symbol] + " ");
  return value.normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}
function wordsFor(value) { return normalized(value).split(/\s+/).filter(Boolean); }
function highlightedText(element, value, words) {
  // Text nodes keep source snippets inert. Highlight whole matching words,
  // including accents and symbol names handled by the search normalizer.
  for (const part of value.split(/([\p{L}\p{N}\p{M}]+)/u)) {
    if (part && words.some(word => normalized(part).includes(word))) {
      const mark = document.createElement("mark");
      mark.textContent = part;
      element.append(mark);
    } else element.append(document.createTextNode(part));
  }
}
function saveParams(values, clearHash = false) {
  const url = new URL(location.href);
  for (const [key, value] of Object.entries(values)) {
    if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
  }
  if (clearHash) url.hash = "";
  history.replaceState(null, "", url);
}
function filterItems(input, selector, status, group) {
  const items = Array.from(document.querySelectorAll(selector));
  const searchable = new Map(items.map(item => [item, normalized(item.dataset.search)]));
  const params = new URLSearchParams(location.search);
  input.value = params.get("q") || "";
  if (group) group.value = params.get("collection") || "";
  const apply = () => {
    const words = wordsFor(input.value);
    let shown = 0;
    for (const item of items) {
      const match = words.every(word => searchable.get(item).includes(word)) &&
        (!group || !group.value || item.dataset.group === group.value);
      item.hidden = !match;
      shown += Number(match);
    }
    const label = input.dataset.resultLabel || "works";
    status.textContent = `${shown} of ${items.length} ${label}` + (shown ? "" : ". Try fewer words or clear the filters.");
    saveParams({q: input.value, collection: group ? group.value : ""});
  };
  input.addEventListener("input", apply);
  if (group) group.addEventListener("change", apply);
  if (input.form) {
    input.form.addEventListener("submit", event => { event.preventDefault(); apply(); });
    input.form.addEventListener("reset", () => setTimeout(apply, 0));
  }
  apply();
}

const workQuery = document.querySelector("#work-query");
if (workQuery) filterItems(workQuery, ".work", document.querySelector("#work-count"), document.querySelector("#work-group"));
const claimQuery = document.querySelector("#claim-query");
if (claimQuery) {
  const paper = document.querySelector("#claim-paper");
  const kind = document.querySelector("#claim-kind");
  const count = document.querySelector("#claim-count");
  const empty = document.querySelector("#claim-empty");
  const items = Array.from(document.querySelectorAll(".claim"));
  const sections = Array.from(document.querySelectorAll(".claim-section"));
  const texts = new Map(items.map(item => [item, normalized(item.dataset.search)]));
  const params = new URLSearchParams(location.search);
  claimQuery.value = params.get("q") || "";
  paper.value = params.get("paper") || "";
  kind.value = params.get("kind") || "";
  function apply(clearHash = false) {
    const words = wordsFor(claimQuery.value);
    let shown = 0;
    const visiblePapers = new Set();
    for (const item of items) {
      const match = (!paper.value || item.dataset.paper === paper.value) &&
        (!kind.value || item.dataset.kind === kind.value) && words.every(word => texts.get(item).includes(word));
      item.hidden = !match;
      if (match) { shown++; visiblePapers.add(item.dataset.paper); }
    }
    for (const section of sections) section.hidden = !visiblePapers.has(section.dataset.paper);
    count.textContent = `${shown} of ${items.length} records across ${visiblePapers.size} papers`;
    empty.hidden = shown > 0;
    saveParams({q: claimQuery.value, paper: paper.value, kind: kind.value}, clearHash);
  }
  function revealHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target || !(target.matches(".claim") || sections.some(s => s.querySelector("h2") === target))) return;
    paper.value = target.dataset.paper || id;
    claimQuery.value = "";
    kind.value = "";
    apply();
    requestAnimationFrame(() => { target.scrollIntoView(); });
  }
  claimQuery.addEventListener("input", () => apply(true));
  paper.addEventListener("change", () => apply(true));
  kind.addEventListener("change", () => apply(true));
  claimQuery.form.addEventListener("submit", event => { event.preventDefault(); apply(true); });
  claimQuery.form.addEventListener("reset", () => setTimeout(() => { apply(true); claimQuery.focus(); }, 0));
  for (const link of document.querySelectorAll("[data-claim-paper]")) {
    link.addEventListener("click", () => {
      paper.value = link.dataset.claimPaper;
      claimQuery.value = "";
      kind.value = "";
      apply();
    });
  }
  window.addEventListener("hashchange", revealHash);
  apply();
  revealHash();
}

const form = document.querySelector("#site-search");
if (form) {
  const input = document.querySelector("#search-query");
  const group = document.querySelector("#search-group");
  const kind = document.querySelector("#search-kind");
  const work = document.querySelector("#search-work");
  const facets = {
    discipline: document.querySelector("#search-discipline"),
    stage: document.querySelector("#search-stage"),
    lean: document.querySelector("#search-lean"),
    evidence: document.querySelector("#search-evidence")
  };
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  const more = document.querySelector("#search-more");
  let indexPromise, facetPromise, found = [], displayed = 0, generation = 0, queryWords = [];
  let mathQueue = Promise.resolve();
  function renderMore(focusNew = false) {
    const previous = displayed;
    const equations = [];
    for (const item of found.slice(displayed, displayed + 40)) {
      const li = document.createElement("li");
      const heading = document.createElement("h2");
      const link = document.createElement("a");
      link.href = item.url;
      highlightedText(link, item.title, queryWords);
      heading.append(link);
      const context = document.createElement("p");
      context.className = "status";
      context.textContent = `${item.group} · ${item.kind}`;
      const excerpt = document.createElement("p");
      const preview = item.preview || item.text;
      const at = preview.toLocaleLowerCase().indexOf(queryWords[0] || "");
      const start = Math.max(0, at - 70);
      if (item.preview_parts) {
        for (const part of item.preview_parts) {
          if (part.type === "math") {
            const math = document.createElement("span");
            math.className = "arithmatex";
            math.textContent = "\\(" + part.text + "\\)";
            excerpt.append(math);
            equations.push(math);
          } else highlightedText(excerpt, part.text, queryWords);
        }
      } else highlightedText(excerpt, (start ? "…" : "") + preview.slice(start, start + 240) + (preview.length > start + 240 ? "…" : ""), queryWords);
      li.append(heading, context, excerpt);
      if (item.math_preview) {
        const equation = document.createElement("div");
        equation.className = "arithmatex search-equation";
        equation.tabIndex = 0;
        equation.setAttribute("role", "group");
        equation.setAttribute("aria-label", "Equation excerpt. Scroll horizontally if needed.");
        equation.textContent = "\\[" + item.math_preview + "\\]";
        li.append(equation);
        equations.push(equation);
      }
      results.append(li);
      displayed++;
    }
    status.textContent = found.length ? `${found.length} results. Showing ${displayed}.` :
      "No results. Try fewer words, clear the filters or browse the glossary.";
    more.hidden = displayed >= found.length;
    if (focusNew && results.children[previous]) results.children[previous].querySelector("a").focus();
    mathQueue = mathQueue.then(async () => {
      if (window.MathJax && window.MathJax.startup) {
        await window.MathJax.startup.promise;
        const visible = equations.filter(element => element.isConnected);
        if (visible.length) await window.MathJax.typesetPromise(visible);
      }
    }).catch(() => { /* The exact TeX excerpt remains readable if MathJax fails. */ });
  }
  async function search(event) {
    if (event) event.preventDefault();
    const request = ++generation;
    const query = input.value;
    const repository = group.value;
    const type = kind.value;
    const workId = work.value;
    const selectedFacets = Object.fromEntries(
      Object.entries(facets).map(([name, control]) => [name, control.value]));
    const hasWorkFacets = Object.values(selectedFacets).some(Boolean);
    const words = wordsFor(query);
    saveParams({q: query, repository, type, work: workId, ...selectedFacets});
    if (window.MathJax && window.MathJax.typesetClear) window.MathJax.typesetClear([results]);
    results.replaceChildren();
    more.hidden = true;
    results.removeAttribute("aria-busy");
    if (!words.length && !type && !repository && !workId && !hasWorkFacets) {
      status.textContent = "Enter a term or choose a filter."; return;
    }
    status.textContent = "Searching…";
    results.setAttribute("aria-busy", "true");
    try {
      if (!indexPromise) indexPromise = fetch(form.dataset.index).then(response => {
        if (!response.ok) throw new Error("Search index could not be loaded");
        return response.json();
      }).then(rows => rows.map(item => ({...item, normalizedTitle: normalized(item.title),
        normalizedText: normalized(item.title + " " + item.text)}))).catch(error => { indexPromise = null; throw error; });
      if (hasWorkFacets && !facetPromise) {
        facetPromise = fetch(form.dataset.facets).then(response => {
          if (!response.ok) throw new Error("Work facets could not be loaded");
          return response.json();
        }).catch(error => { facetPromise = null; throw error; });
      }
      const [index, subjectIndex] = await Promise.all([
        indexPromise, hasWorkFacets ? facetPromise : Promise.resolve(null)
      ]);
      if (request !== generation) return;
      const matchesWorkFacets = item => !hasWorkFacets || (item.work_ids || []).some(id => {
        const record = subjectIndex.works[id];
        return record && Object.entries(selectedFacets).every(([name, code]) =>
          !code || record[name === "evidence" ? "evidence" : name] === code);
      });
      found = index.filter(item => (!repository || item.group === repository) &&
        (!type || item.kind === type) && (!workId || (item.work_ids || []).includes(workId)) &&
        matchesWorkFacets(item) && words.every(word => item.normalizedText.includes(word)));
      const score = item => (normalized(query) === item.normalizedTitle ? 100 : 0) +
        words.filter(word => item.normalizedTitle.includes(word)).length * 10 +
        (item.kind === "Claims" || item.kind === "Glossary" ? 1 : 0);
      found.sort((a, b) => score(b) - score(a) || a.title.localeCompare(b.title));
      displayed = 0;
      queryWords = words;
      renderMore();
    } catch (error) {
      if (request === generation) status.textContent = "Search could not load. Use the work index or glossary, or try again.";
    } finally { if (request === generation) results.removeAttribute("aria-busy"); }
  }
  form.addEventListener("submit", search);
  group.addEventListener("change", search);
  kind.addEventListener("change", search);
  work.addEventListener("change", search);
  for (const control of Object.values(facets)) control.addEventListener("change", search);
  more.addEventListener("click", () => renderMore(true));
  form.addEventListener("reset", () => {
    ++generation;
    if (window.MathJax && window.MathJax.typesetClear) window.MathJax.typesetClear([results]);
    results.replaceChildren();
    results.removeAttribute("aria-busy");
    more.hidden = true;
    status.textContent = "Enter a term or choose a filter.";
    saveParams({q: "", repository: "", type: "", work: "",
      discipline: "", stage: "", lean: "", evidence: ""});
    setTimeout(() => input.focus(), 0);
  });
  const params = new URLSearchParams(location.search);
  input.value = params.get("q") || "";
  group.value = params.get("repository") || "";
  kind.value = params.get("type") || "";
  work.value = params.get("work") || "";
  for (const [name, control] of Object.entries(facets)) {
    control.value = params.get(name) || "";
  }
  if (input.value || group.value || kind.value || work.value ||
      Object.values(facets).some(control => control.value)) search();
}

for (const pre of document.querySelectorAll("pre")) {
  pre.tabIndex = 0;
  if (!pre.hasAttribute("aria-label")) pre.setAttribute("aria-label", "Code example. Scroll horizontally if needed.");
}
