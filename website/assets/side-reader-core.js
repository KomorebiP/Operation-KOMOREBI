"use strict";
(function (root) {
  function canonical(value, base, pages) {
    if (typeof value !== "string" || value.length > 4096 || /[\\\x00-\x1f]/u.test(value)) return null;
    try {
      const url = new URL(value, base);
      const site = new URL(base);
      if (url.origin !== site.origin || url.username || url.password || !url.pathname.startsWith(site.pathname)) return null;
      const path = decodeURIComponent(url.pathname.slice(site.pathname.length));
      if (!Object.hasOwn(pages, path)) return null;
      url.searchParams.delete("reading-pane");
      return path + url.search + url.hash;
    } catch { return null; }
  }
  function words(value) {
    return value.normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, " ").trim().split(/\s+/u).filter(Boolean);
  }
  function linkedPair(value, base, pages) {
    try {
      const url = new URL(value, base);
      const expected = new URL("side-by-side.html", base);
      if (url.origin !== expected.origin || url.pathname !== expected.pathname || url.username || url.password) return null;
      if (url.searchParams.getAll("left").length !== 1 || url.searchParams.getAll("right").length !== 1) return null;
      const left = canonical(url.searchParams.get("left"), base, pages);
      const right = canonical(url.searchParams.get("right"), base, pages);
      return left && right ? {left, right} : null;
    } catch { return null; }
  }
  function filter(entries, query, work, kind) {
    const wanted = words(query);
    return entries.filter(row => (!work || row.works.includes(work)) && (!kind || row.kind === kind) &&
      wanted.every(word => words(row.title + " " + row.text).join(" ").includes(word)));
  }
  function pairURL(base, state) {
    const url = new URL("side-by-side.html", base);
    for (const side of ["left", "right"]) if (state[side]) url.searchParams.set(side, state[side]);
    if (state.view !== "both") url.searchParams.set("view", state.view);
    if (state.width !== 50) url.searchParams.set("width", String(state.width));
    return url.href;
  }
  function parsePair(href, base, data, narrow) {
    const params = new URL(href).searchParams;
    const first = canonical(params.get("left") || "", base, data.pages);
    const associated = data.entries.find(row => row.url === first) ||
      data.entries.find(row => first && row.url.split("#")[0] === first.split("#")[0]);
    const work = data.works.find(row => row.id === params.get("work")) ||
      data.works.find(row => associated?.works.includes(row.id)) || data.works[0];
    const left = canonical(params.get("left") || work.left, base, data.pages);
    const right = canonical(params.get("right") || work.right, base, data.pages);
    const requested = params.get("view");
    const width = Number(params.get("width") || 50);
    return {left: left || work.left, right: right || work.right,
      view: ["both","left","right"].includes(requested) ? requested : narrow ? "left" : "both",
      width: [35,40,45,50,55,60,65].includes(width) ? width : 50,
      invalid: Boolean((params.has("left") && !left) || (params.has("right") && !right))};
  }
  const api = {canonical, words, filter, pairURL, parsePair, linkedPair};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.KomorebiSideReader = api;
})(globalThis);
