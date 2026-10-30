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
  function workIds(value, data) {
    if (typeof value !== "string") return [];
    const path = value.split(/[?#]/u)[0];
    const params = new URLSearchParams(value.split("#")[0].split("?")[1] || "");
    const explicit = path === "search.html" ? params.get("work") : path === "claims.html" ? params.get("paper") || value.split("#")[1] : "";
    const known = new Set(data.works.map(work => work.id));
    if (known.has(explicit)) return [explicit];
    const exact = data.entries.filter(row => row.url === value);
    const rows = exact.length ? exact : data.entries.filter(row => row.url.split(/[?#]/u)[0] === path);
    return [...new Set(rows.flatMap(row => row.works))].filter(id => known.has(id));
  }
  function pairURL(base, state) {
    const url = new URL("side-by-side.html", base);
    for (const side of ["left", "right"]) if (state[side]) url.searchParams.set(side, state[side]);
    if (state.view !== "both") url.searchParams.set("view", state.view);
    if (state.width !== 50) url.searchParams.set("width", String(state.width));
    return url.href;
  }
  function workPair(leftId, rightId, base, data) {
    const selected = [leftId, rightId].map(id => data.works.find(work => work.id === id));
    if (selected.some(work => !work)) return null;
    const targets = selected.map(work => canonical(work.left, base, data.pages));
    return targets.every(Boolean) ? {left:targets[0], right:targets[1]} : null;
  }
  function parsePair(href, base, data, narrow) {
    const params = new URL(href).searchParams;
    const first = canonical(params.get("left") || "", base, data.pages);
    const associated = workIds(first, data);
    const work = data.works.find(row => row.id === params.get("work")) ||
      data.works.find(row => associated.includes(row.id)) || data.works[0];
    const left = canonical(params.get("left") || work.left, base, data.pages);
    const right = canonical(params.get("right") || work.right, base, data.pages);
    const requested = params.get("view");
    const width = Number(params.get("width") || 50);
    return {left: left || work.left, right: right || work.right,
      view: ["both","left","right"].includes(requested) ? requested : narrow ? "left" : "both",
      width: [35,40,45,50,55,60,65].includes(width) ? width : 50,
      invalid: Boolean((params.has("left") && !left) || (params.has("right") && !right))};
  }
  const api = {canonical, words, filter, pairURL, parsePair, linkedPair, workIds, workPair};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.KomorebiSideReader = api;
})(globalThis);
