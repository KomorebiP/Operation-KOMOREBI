/* Pure statement matching, shared by the reader and its regression tests. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.KomorebiStatementSearch = api;
})(typeof window === 'undefined' ? this : window, function() {
  'use strict';
  const greek = {α:'alpha',β:'beta',γ:'gamma',δ:'delta',ε:'epsilon',ϵ:'epsilon',ζ:'zeta',η:'eta',θ:'theta',
    κ:'kappa',λ:'lambda',μ:'mu',ν:'nu',ξ:'xi',π:'pi',ρ:'rho',σ:'sigma',τ:'tau',υ:'upsilon',φ:'phi',ϕ:'phi',χ:'chi',ψ:'psi',ω:'omega',ℓ:'ell'};
  const greekNames = new Set(Object.values(greek));
  function normalize(value) {
    return String(value || '').normalize('NFKD').replace(/\p{M}/gu,'').toLocaleLowerCase()
      .replace(/[αβγδεϵζηθκλμνξπρστυφϕχψωℓ]/gu,letter=>' '+greek[letter]+' ')
      .replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  }
  function printedNumber(value) {
    const number = String(value).trim().replace(/\s*\.\s*/g,'.').replace(/\.$/,'');
    return /^(?:(?:[ivxlcdm]+|[a-z])\.)*[a-z]?\d+(?:\.\d+)*[a-z]?$/i.test(number) ? number.toLocaleLowerCase() : null;
  }
  const aliases = {thm:'theorem',lem:'lemma',prop:'proposition',cor:'corollary',def:'definition',conj:'conjecture'};
  function search(entries, query, proofOnly = false) {
    query = String(query || '').trim();
    const names = new Map();
    function register(name,kind) {
      if (!names.has(name)) names.set(name,new Set());
      names.get(name).add(kind);
    }
    for (const kind of ['theorem','lemma','proposition','corollary','definition','conjecture','example','remark',
      'construction','warning','boundary','problem']) register(kind,kind);
    for (const entry of entries) register(String(entry.name || entry.kind).toLocaleLowerCase(),entry.kind);
    for (const [alias,kind] of Object.entries(aliases)) register(alias,kind);
    let number = printedNumber(query), kind = null;
    if (!number) {
      const lower = query.toLocaleLowerCase();
      for (const [name,type] of Array.from(names).sort((a,b)=>b[0].length-a[0].length)) {
        if (!lower.startsWith(name)) continue;
        const candidate = printedNumber(query.slice(name.length).replace(/^\.\s*/,''));
        if (candidate) {number = candidate;kind = type;break;}
      }
    }
    const words = normalize(query).split(/\s+/).filter(Boolean);
    const requestedKind = names.get(query.toLocaleLowerCase());
    return entries.filter(entry => {
      if (proofOnly && !entry.hasProof) return false;
      if (number) return printedNumber(entry.number) === number && (!kind || kind.has(entry.kind));
      if (requestedKind) return requestedKind.has(entry.kind);
      if (query.includes(':') && !/\s/.test(query)) return String(entry.labels || '').split(/\s+/).some(label=>normalize(label) === normalize(query));
      const tokens = normalize([entry.text,entry.name,entry.number,entry.labels].join(' ')).split(/\s+/);
      return words.every(word=>tokens.some(token=>word.length<=2 || greekNames.has(word)
        ? token === word : token.startsWith(aliases[word] || word)));
    });
  }
  function readFilters(search) {
    const params = new URLSearchParams(search);
    return {query:params.get('q') || '',proofOnly:params.get('proof') === '1'};
  }
  function filterUrl(href, query, proofOnly) {
    const url = new URL(href);
    query = String(query || '').trim();
    if (query) url.searchParams.set('q',query);else url.searchParams.delete('q');
    if (proofOnly) url.searchParams.set('proof','1');else url.searchParams.delete('proof');
    return url.href;
  }
  return {normalize,search,readFilters,filterUrl};
});
