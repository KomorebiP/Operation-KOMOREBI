"use strict";

function filterItems(input, selector, status, group) {
  const items = Array.from(document.querySelectorAll(selector));
  const apply = () => {
    const words = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const item of items) {
      const match = words.every(word => item.dataset.search.includes(word)) &&
        (!group || !group.value || item.dataset.group === group.value);
      item.hidden = !match;
      shown += Number(match);
    }
    status.textContent = `${shown} of ${items.length} ${selector === ".claim" ? "records" : "works"}`;
  };
  input.addEventListener("input", apply);
  if (group) group.addEventListener("change", apply);
  if (input.form) input.form.addEventListener("reset", () => setTimeout(apply, 0));
}

const workQuery = document.querySelector("#work-query");
if (workQuery) filterItems(workQuery, ".work", document.querySelector("#work-count"), document.querySelector("#work-group"));
const claimQuery = document.querySelector("#claim-query");
if (claimQuery) filterItems(claimQuery, ".claim", document.querySelector("#claim-count"));

const form = document.querySelector("#site-search");
if (form) {
  const input = document.querySelector("#search-query");
  const group = document.querySelector("#search-group");
  const status = document.querySelector("#search-status");
  const results = document.querySelector("#search-results");
  let index;
  async function search(event) {
    if (event) event.preventDefault();
    const words = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    results.replaceChildren();
    if (!words.length) { status.textContent = "Enter a search term."; return; }
    status.textContent = "Searching…";
    try {
      if (!index) {
        const response = await fetch(form.dataset.index);
        if (!response.ok) throw new Error("Search index could not be loaded");
        index = await response.json();
      }
      const found = index.filter(item => (!group.value || item.group === group.value) &&
        words.every(word => (item.title + " " + item.text).toLocaleLowerCase().includes(word)));
      found.sort((a, b) => Number(words.every(word => b.title.toLocaleLowerCase().includes(word))) -
        Number(words.every(word => a.title.toLocaleLowerCase().includes(word))));
      for (const item of found.slice(0, 40)) {
        const li = document.createElement("li");
        const heading = document.createElement("h2");
        const link = document.createElement("a");
        link.href = item.url;
        link.textContent = item.title;
        heading.append(link);
        const context = document.createElement("p");
        context.className = "status";
        context.textContent = item.group;
        const excerpt = document.createElement("p");
        const at = item.text.toLocaleLowerCase().indexOf(words[0]);
        const start = Math.max(0, at - 70);
        excerpt.textContent = (start ? "…" : "") + item.text.slice(start, start + 240) + "…";
        li.append(heading, context, excerpt);
        results.append(li);
      }
      status.textContent = found.length ? `${found.length} matching pages. Showing ${Math.min(40, found.length)}.` :
        "No matching pages. Try a shorter term, the glossary or another repository filter.";
      const url = new URL(location.href);
      url.searchParams.set("q", input.value);
      if (group.value) url.searchParams.set("repository", group.value); else url.searchParams.delete("repository");
      history.replaceState(null, "", url);
    } catch (error) {
      status.textContent = "Search could not load. Use the work index or glossary, or try again.";
    }
  }
  form.addEventListener("submit", search);
  const params = new URLSearchParams(location.search);
  input.value = params.get("q") || "";
  group.value = params.get("repository") || "";
  if (input.value) search();
}

for (const pre of document.querySelectorAll("pre")) {
  pre.tabIndex = 0;
  pre.setAttribute("aria-label", "Code example. Scroll horizontally if needed.");
}
