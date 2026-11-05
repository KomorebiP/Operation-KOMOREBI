"use strict";

// Normalize names and formula spellings while retaining the catalog's own terms.
function operatorCatalogWords(value) {
  const symbols = {α: "alpha", β: "beta", γ: "gamma", δ: "delta", η: "eta",
    θ: "theta", π: "pi", ρ: "rho", φ: "phi", ω: "omega", ℓ: "ell"};
  return value.toLocaleLowerCase("en").replace(/[αβγδηθπρφωℓ]/g, character => " " + symbols[character] + " ")
    .normalize("NFKD").replace(/\p{M}/gu, "").replace(/[^\p{L}\p{N}]+/gu, " ").trim();
}

const operatorCatalog = document.querySelector("#operator-catalog-lookup");
if (operatorCatalog) {
  const form = document.querySelector("#operator-catalog-form");
  const query = document.querySelector("#operator-catalog-query");
  const family = document.querySelector("#operator-catalog-family");
  const checks = document.querySelector("#operator-catalog-checks");
  const status = document.querySelector("#operator-catalog-status");
  const matches = document.querySelector("#operator-catalog-matches");
  const title = document.querySelector("#operator-catalog-results-title");
  const list = document.querySelector("#operator-catalog-results");
  const entries = Array.from(list.children, node => ({node,
    id: node.dataset.operatorId,
    name: operatorCatalogWords(node.dataset.name),
    text: operatorCatalogWords(node.dataset.search),
    family: node.dataset.family, checked: Number(node.dataset.checks) > 0}));
  let announcement;

  function fragmentEntry() {
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)).toLocaleLowerCase("en"); }
    catch { return undefined; }
    return entries.find(entry => fragment === entry.node.id || fragment === entry.id.toLocaleLowerCase("en"));
  }

  function lookup({announce = true, clearEntryHash = false} = {}) {
    clearTimeout(announcement);
    const text = operatorCatalogWords(query.value);
    const words = text.split(/\s+/).filter(Boolean);
    const idMatch = text.match(/^op\s*0*(\d{1,3})$/);
    const requestedId = idMatch ? "OP-" + idMatch[1].padStart(3, "0") : "";
    const active = !!(text || family.value || checks.value);
    const ranked = entries.map(entry => ({...entry,
      visible: active && (!family.value || entry.family === family.value) &&
        (!checks.value || entry.checked === (checks.value === "linked")) &&
        (requestedId ? entry.id === requestedId : words.every(word => entry.text.includes(word))),
      rank: entry.id === requestedId || entry.name === text ? 0 : entry.name.startsWith(text) ? 1 :
        words.every(word => entry.name.includes(word)) ? 2 : 3}));
    ranked.sort((a, b) => a.rank - b.rank); // Keep the original alphabetical order within each rank.
    let count = 0;
    for (const entry of ranked) {
      entry.node.hidden = !entry.visible;
      if (entry.visible) { count++; list.append(entry.node); }
    }
    matches.hidden = count === 0;
    const message = !active ? "Search all " + entries.length + " entries, or browse the families below." : count
      ? count + (count === 1 ? " matching entry" : " matching entries") + " out of " + entries.length + "."
      : "No matching entries. Try fewer words, choose All families, or clear filters.";
    if (announce) announcement = setTimeout(() => { status.textContent = message; }, 180);
    else status.textContent = message;
    const url = new URL(location.href);
    for (const [key, value] of [["q", query.value.trim()], ["family", family.value], ["checks", checks.value]]) {
      if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
    }
    // A new lookup replaces a result fragment, but keeps unrelated section anchors.
    if (clearEntryHash && fragmentEntry()) url.hash = "";
    if (url.href !== location.href) history.replaceState(null, "", url);
    return count;
  }

  function validOption(select, value) {
    return Array.from(select.options).some(option => option.value === value) ? value : "";
  }

  function restoreLookup() {
    const params = new URL(location.href).searchParams;
    query.value = params.get("q") || "";
    family.value = validOption(family, (params.get("family") || "").toUpperCase());
    checks.value = validOption(checks, params.get("checks") || "");
    const target = fragmentEntry();
    if (target) {
      query.value = target.id;
      family.value = checks.value = "";
    }
    lookup({announce: false});
    // A shared entry fragment must be visible even when its old filters disagree.
    // Opening or restoring the page never moves keyboard focus.
    if (target) target.node.scrollIntoView({block: "start"});
  }

  query.addEventListener("input", () => lookup({clearEntryHash: true}));
  family.addEventListener("change", () => lookup({announce: false, clearEntryHash: true}));
  checks.addEventListener("change", () => lookup({announce: false, clearEntryHash: true}));
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (lookup({announce: false})) {
      title.focus({preventScroll: true});
      title.scrollIntoView({block: "start"});
    }
  });
  form.addEventListener("reset", event => {
    event.preventDefault();
    query.value = family.value = checks.value = "";
    lookup({announce: false, clearEntryHash: true});
    query.focus();
  });
  window.addEventListener("popstate", restoreLookup);
  window.addEventListener("hashchange", restoreLookup);
  // The family table and complete alphabetical index remain usable without JS.
  form.hidden = status.hidden = false;
  restoreLookup();
}
