"use strict";
(() => {
  const form = document.querySelector("#catalog-filters");
  if (!form) return;
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
  const text = new Map(items.map(item => [item, item.dataset.search.normalize("NFKD")
    .replace(/\p{M}/gu, "").toLocaleLowerCase()]));
  const params = new URLSearchParams(location.search);
  for (const [key, control] of Object.entries(controls)) {
    const candidate = params.get(key) || "";
    control.value = Array.from(control.options || []).some(option => option.value === candidate) ||
      control.tagName === "INPUT" ? candidate : "";
  }
  function apply(persist = true) {
    const words = controls.q.value.normalize("NFKD").replace(/\p{M}/gu, "")
      .toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0, activeFields = 0;
    for (const item of items) {
      const matches = words.every(word => text.get(item).includes(word)) &&
        (!controls.discipline.value || controls.discipline.value === item.dataset.discipline) &&
        (!controls.stage.value || controls.stage.value === item.dataset.stage) &&
        (!controls.lean.value || controls.lean.value === item.dataset.lean) &&
        (!controls.evidence.value || controls.evidence.value === item.dataset.evidence) &&
        (!controls.collection.value || controls.collection.value === item.dataset.group);
      item.hidden = !matches;
      if (matches) shown++;
    }
    for (const section of sections) {
      const hasVisible = Array.from(section.querySelectorAll(".catalog-item")).some(item => !item.hidden);
      section.hidden = !hasVisible;
      activeFields += Number(hasVisible);
    }
    count.textContent = shown + " of " + items.length + " primary works in " +
      activeFields + (activeFields === 1 ? " discipline" : " disciplines");
    empty.hidden = shown !== 0;
    if (persist) {
      const url = new URL(location.href);
      for (const [key, control] of Object.entries(controls)) {
        if (control.value) url.searchParams.set(key, control.value);
        else url.searchParams.delete(key);
      }
      history.replaceState(null, "", url);
    }
  }
  for (const control of Object.values(controls)) {
    control.addEventListener(control.tagName === "INPUT" ? "input" : "change", () => apply());
  }
  form.addEventListener("submit", event => { event.preventDefault(); apply(); });
  form.addEventListener("reset", () => { setTimeout(() => apply(), 0); });
  apply(false);
})();
