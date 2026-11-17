// Pure catalogue membership index. No research workbench is loaded by a search page.
export function familySearchEntries(entries,families){
  const memberships=new Map();
  for(const family of families)for(const id of family.record_ids){
    if(!memberships.has(id))memberships.set(id,[]);
    memberships.get(id).push(family);
  }
  return entries.map(entry=>{
    const groups=memberships.get(entry.id)||[];
    const copy={...entry,
      generalized_family_ids:groups.map(g=>g.id),
      family_names:groups.map(g=>g.title),
      paper_refs:[...new Set(groups.flatMap(g=>g.paper_refs))],
      paper_titles:groups.map(g=>g.paper_title)};
    if(entry.id==='KSEQ-000025')copy.recurrence_order=2;
    if(/^KOM01[3-6]$/.test(entry.id))copy.recurrence_order=Number(entry.id.slice(3))-10;
    return copy;
  });
}
