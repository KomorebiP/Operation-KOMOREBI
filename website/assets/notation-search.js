/* Matching and grouping shared by the browser and the search regression tests. */
(() => {
  'use strict';
  const normalize = value => value.normalize('NFC').toLocaleLowerCase();
  const kinds = ['notation-table','definition-passage','introduction-passage','use'];
  function rank(entry, context, query, exact) {
    const q=query.trim();
    if (!q) return 9;
    if (entry.tex===q) return 0;
    if (exact) return -1;
    const names=entry.names || [entry.tex];
    if (names.includes(q)) return 1;
    const variants=name=>name.startsWith(q+'_') || name.startsWith(q+'^') || name.startsWith(q+"'");
    if ([entry.tex,...names].some(variants)) return 2;
    // Explicit TeX and non-Latin symbols preserve case. They do not match
    // incidental letters inside words in the surrounding prose.
    if (q.includes('\\') || /[^\x00-\x7f]/.test(q)) return -1;
    const lower=normalize(q);
    if (names.some(name=>normalize(name)===lower)) return 3;
    if (q.length<=2) return -1;
    const symbolText=normalize(entry.tex+' '+entry.aliases);
    const words=lower.split(/\s+/).filter(Boolean);
    if (words.every(word=>symbolText.includes(word))) return 4;
    const excerpt=normalize(context.excerpt+' '+(context.table?.label || '')+' '+(context.table?.meaning || ''));
    return words.every(word=>(symbolText+' '+excerpt).includes(word)) ? 6 : -1;
  }
  function search(data, options) {
    const grouped=new Map();
    let count=0;
    for (const entry of data.entries) {
      if (options.work && options.work!==entry.work || options.kind && options.kind!==entry.kind) continue;
      const context=data.contexts[entry.context];
      const score=rank(entry,context,options.query,options.exact);
      if (score<0) continue;
      count++;
      // Never combine meanings from different works, even if the wording agrees.
      const key=entry.work+':'+entry.context;
      if (!grouped.has(key)) grouped.set(key,{context,work:entry.work,entries:[],score});
      const group=grouped.get(key);
      group.score=Math.min(group.score,score);
      group.entries.push({...entry,score});
    }
    const compare=(a,b)=>a.score-b.score || kinds.indexOf(a.kind)-kinds.indexOf(b.kind) || a.tex.localeCompare(b.tex);
    const groups=Array.from(grouped.values());
    for (const group of groups) group.entries.sort(compare);
    groups.sort((a,b)=>compare(a.entries[0],b.entries[0]) || a.work.localeCompare(b.work));
    return {groups,count};
  }
  const api={normalize,rank,search};
  if (typeof module!=='undefined' && module.exports) module.exports=api;
  if (typeof window!=='undefined') window.KomorebiNotationSearch=api;
})();
