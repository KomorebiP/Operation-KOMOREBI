"use strict";
{
  const form = document.querySelector("#visual-guide-filter");
  if (form) {
    const input = form.querySelector("input"), cards = [...document.querySelectorAll(".visual-guide-card")];
    const status = document.querySelector("#visual-guide-count"), empty = document.querySelector("#visual-guide-empty");
    const normalize = value => value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase().trim();
    const searchable = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
    function apply(write = true) {
      const query = normalize(input.value), number = query.replace(/^paper\s*/, "");
      const exact = cards.some(card => number === card.dataset.number || number === card.dataset.roman);
      const words = query.split(/\s+/).filter(Boolean);
      let shown = 0;
      for (const card of cards) {
        const match = exact ? number === card.dataset.number || number === card.dataset.roman : words.every(word => searchable.get(card).includes(word));
        card.hidden = !match; shown += Number(match);
      }
      status.textContent = query ? `${shown} of ${cards.length} guides` : `${cards.length} guides`;
      empty.hidden = shown !== 0;
      form.querySelector("button").disabled = !input.value;
      if (write) {
        const url = new URL(location.href);
        if (input.value.trim()) url.searchParams.set("q", input.value.trim()); else url.searchParams.delete("q");
        history.replaceState(null, "", url);
      }
    }
    function clear() { input.value = ""; apply(); }
    input.value = new URLSearchParams(location.search).get("q") || "";
    input.addEventListener("input", () => apply());
    input.addEventListener("keydown", event => { if (event.key === "Escape") { event.preventDefault(); clear(); } });
    form.addEventListener("submit", event => { event.preventDefault(); apply(); });
    form.addEventListener("reset", event => { event.preventDefault(); clear(); input.focus(); });
    document.querySelectorAll(".visual-guide-jump a").forEach(link => link.addEventListener("click", clear));
    function revealHash() {
      const target = cards.find(card => "#" + card.id === location.hash);
      if (target?.hidden) clear();
    }
    form.hidden = false; apply(false); revealHash();
    window.addEventListener("hashchange", revealHash);
    window.addEventListener("popstate", () => { input.value = new URLSearchParams(location.search).get("q") || ""; apply(false); revealHash(); });
  }
}
