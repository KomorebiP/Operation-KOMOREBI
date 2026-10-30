"use strict";

// Match text and compatibility spellings such as subscript digits and ligatures.
function glossaryWords(value) {
  return value.normalize("NFKC").toLocaleLowerCase("en").replace(/[-\u2010-\u2015\u2212]/g, " ").replace(/\s+/g, " ");
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
    subject: node.dataset.subject}));
  let announcement;

  function lookup(announce = true) {
    clearTimeout(announcement);
    const text = glossaryWords(query.value.trim());
    const words = text.split(/\s+/).filter(Boolean);
    const active = !!(text || subject.value);
    const ranked = entries.map(entry => ({...entry,
      visible: active && (!subject.value || entry.subject === subject.value) && words.every(word => entry.text.includes(word)),
      rank: entry.term === text ? 0 : entry.term.startsWith(text) ? 1 : 2}));
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
