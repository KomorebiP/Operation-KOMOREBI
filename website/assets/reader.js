"use strict";

function normalized(value) {
  return value.normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}
function wordsFor(value) { return normalized(value).split(/\s+/).filter(Boolean); }
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
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  const more = document.querySelector("#search-more");
  let indexPromise, found = [], displayed = 0, generation = 0, queryWords = [];
  function renderMore(focusNew = false) {
    const previous = displayed;
    for (const item of found.slice(displayed, displayed + 40)) {
      const li = document.createElement("li");
      const heading = document.createElement("h2");
      const link = document.createElement("a");
      link.href = item.url;
      link.textContent = item.title;
      heading.append(link);
      const context = document.createElement("p");
      context.className = "status";
      context.textContent = `${item.group} · ${item.kind}`;
      const excerpt = document.createElement("p");
      const preview = item.preview || item.text;
      const at = preview.toLocaleLowerCase().indexOf(queryWords[0] || "");
      const start = Math.max(0, at - 70);
      excerpt.textContent = (start ? "…" : "") + preview.slice(start, start + 240) + (preview.length > start + 240 ? "…" : "");
      li.append(heading, context, excerpt);
      results.append(li);
      displayed++;
    }
    status.textContent = found.length ? `${found.length} results. Showing ${displayed}.` :
      "No results. Try fewer words, clear the filters or browse the glossary.";
    more.hidden = displayed >= found.length;
    if (focusNew && results.children[previous]) results.children[previous].querySelector("a").focus();
  }
  async function search(event) {
    if (event) event.preventDefault();
    const request = ++generation;
    const query = input.value;
    const repository = group.value;
    const type = kind.value;
    const workId = work.value;
    const words = wordsFor(query);
    saveParams({q: query, repository, type, work: workId});
    results.replaceChildren();
    more.hidden = true;
    results.removeAttribute("aria-busy");
    if (!words.length && !type && !repository && !workId) { status.textContent = "Enter a term, choose a work or choose a result type."; return; }
    status.textContent = "Searching…";
    results.setAttribute("aria-busy", "true");
    try {
      if (!indexPromise) indexPromise = fetch(form.dataset.index).then(response => {
        if (!response.ok) throw new Error("Search index could not be loaded");
        return response.json();
      }).then(rows => rows.map(item => ({...item, normalizedTitle: normalized(item.title),
        normalizedText: normalized(item.title + " " + item.text)}))).catch(error => { indexPromise = null; throw error; });
      const index = await indexPromise;
      if (request !== generation) return;
      found = index.filter(item => (!repository || item.group === repository) &&
        (!type || item.kind === type) && (!workId || (item.work_ids || []).includes(workId)) && words.every(word => item.normalizedText.includes(word)));
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
  more.addEventListener("click", () => renderMore(true));
  form.addEventListener("reset", () => {
    ++generation;
    results.replaceChildren();
    results.removeAttribute("aria-busy");
    more.hidden = true;
    status.textContent = "Enter a term, choose a work or choose a result type.";
    saveParams({q: "", repository: "", type: "", work: ""});
    setTimeout(() => input.focus(), 0);
  });
  const params = new URLSearchParams(location.search);
  input.value = params.get("q") || "";
  group.value = params.get("repository") || "";
  kind.value = params.get("type") || "";
  work.value = params.get("work") || "";
  if (input.value || group.value || kind.value || work.value) search();
}

for (const pre of document.querySelectorAll("pre")) {
  pre.tabIndex = 0;
  if (!pre.hasAttribute("aria-label")) pre.setAttribute("aria-label", "Code example. Scroll horizontally if needed.");
}
