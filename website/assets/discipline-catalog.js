"use strict";
(() => {
  const form = document.querySelector("#catalog-filters");
  if (!form) return;
  const pageSize = 8;
  const controls = {
    q: document.querySelector("#catalog-query"),
    discipline: document.querySelector("#catalog-discipline"),
    stage: document.querySelector("#catalog-stage"),
    lean: document.querySelector("#catalog-lean"),
    evidence: document.querySelector("#catalog-evidence"),
    collection: document.querySelector("#catalog-group")
  };
  const items = Array.from(document.querySelectorAll(".catalog-item"));
  const sections = Array.from(document.querySelectorAll("[data-catalog-section]"));
  const count = document.querySelector("#catalog-count");
  const empty = document.querySelector("#catalog-empty");
  const pagers = Array.from(document.querySelectorAll(".catalog-pagination"));
  const disciplineLinks = Array.from(document.querySelectorAll("[data-discipline-choice]"));
  const normalize = value => value.normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase();
  const text = new Map(items.map(item => [item, normalize(item.dataset.search)]));
  let page = 1;

  function restore() {
    const params = new URLSearchParams(location.search);
    for (const [key, control] of Object.entries(controls)) {
      const candidate = params.get(key) || "";
      control.value = control.tagName === "INPUT" ||
        Array.from(control.options).some(option => option.value === candidate) ? candidate : "";
    }
    const requested = Number(params.get("page"));
    page = Number.isSafeInteger(requested) && requested > 0 ? requested : 1;
  }

  function apply({ persist = true, push = false, revealAnchor = false } = {}) {
    const words = normalize(controls.q.value).trim().split(/\s+/).filter(Boolean);
    const matches = items.filter(item => words.every(word => text.get(item).includes(word)) &&
      (!controls.discipline.value || controls.discipline.value === item.dataset.discipline) &&
      (!controls.stage.value || controls.stage.value === item.dataset.stage) &&
      (!controls.lean.value || controls.lean.value === item.dataset.lean) &&
      (!controls.evidence.value || controls.evidence.value === item.dataset.evidence) &&
      (!controls.collection.value || controls.collection.value === item.dataset.group));
    const pages = Math.max(1, Math.ceil(matches.length / pageSize));
    if (revealAnchor && !new URLSearchParams(location.search).has("page")) {
      let anchor = "";
      try { anchor = decodeURIComponent(location.hash.slice(1)); } catch (_) { /* Ignore malformed anchors. */ }
      const index = matches.findIndex(item => item.id === anchor);
      if (index >= 0) page = Math.floor(index / pageSize) + 1;
    }
    page = Math.max(1, Math.min(page, pages));
    const start = (page - 1) * pageSize;
    const visible = new Set(matches.slice(start, start + pageSize));
    for (const item of items) item.hidden = !visible.has(item);
    for (const section of sections) {
      const shown = Array.from(section.querySelectorAll(".catalog-item")).filter(item => visible.has(item)).length;
      section.hidden = shown === 0;
      section.querySelector("h2 small").textContent = shown + " shown";
    }
    count.textContent = matches.length ? "Showing " + (start + 1) + "–" + Math.min(start + pageSize, matches.length) +
      " of " + matches.length + " works" : "0 matching works";
    empty.hidden = matches.length !== 0;
    for (const pager of pagers) {
      pager.hidden = pages === 1;
      pager.querySelector(".catalog-page-status").textContent = "Page " + page + " of " + pages;
      pager.querySelector('[data-catalog-page="previous"]').disabled = page === 1;
      pager.querySelector('[data-catalog-page="next"]').disabled = page === pages;
    }
    for (const link of disciplineLinks) {
      if (link.dataset.disciplineChoice === controls.discipline.value) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    }
    if (persist) {
      const url = new URL(location.href);
      for (const [key, control] of Object.entries(controls)) {
        if (control.value) url.searchParams.set(key, control.value);
        else url.searchParams.delete(key);
      }
      if (page > 1) url.searchParams.set("page", page);
      else url.searchParams.delete("page");
      if (url.hash.startsWith("#work-")) url.hash = "";
      history[push ? "pushState" : "replaceState"](null, "", url);
    }
  }

  function filter() { page = 1; apply(); }
  for (const control of Object.values(controls)) {
    control.addEventListener(control.tagName === "INPUT" ? "input" : "change", filter);
  }
  for (const link of disciplineLinks) {
    link.addEventListener("click", event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      controls.discipline.value = link.dataset.disciplineChoice;
      filter();
    });
  }
  for (const button of document.querySelectorAll("[data-catalog-page]")) {
    button.addEventListener("click", () => {
      page += button.dataset.catalogPage === "next" ? 1 : -1;
      apply({ push: true });
      count.scrollIntoView({ block: "start", behavior: "auto" });
    });
  }
  form.addEventListener("submit", event => { event.preventDefault(); filter(); });
  form.addEventListener("reset", () => { setTimeout(filter, 0); });
  window.addEventListener("popstate", () => { restore(); apply({ persist: false }); });
  restore();
  apply({ persist: false, revealAnchor: true });
})();
