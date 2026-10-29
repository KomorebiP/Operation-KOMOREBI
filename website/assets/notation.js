/* Source-linked notation. All result text is inserted as text, never HTML. */
(() => {
  'use strict';
  const labels = {'notation-table':'Notation table','definition-passage':'Definition passage','introduction-passage':'Introduction passage',use:'Use in source'};
  const ranks = Object.keys(labels);
  const query = document.getElementById('notation-query');
  if (!query) return;
  const status = document.getElementById('notation-status');
  const more = document.getElementById('notation-more');
  const kind = document.getElementById('notation-kind');
  const params = new URLSearchParams(location.search);
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const node = (tag, text, cls) => {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  };
  async function getJSON(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Could not load the notation data');
    return response.json();
  }
  let mathQueue = Promise.resolve();
  function typeset(elements) {
    mathQueue = mathQueue.then(async () => {
      const mj = window.MathJax;
      if (!mj?.startup?.promise) return;
      await mj.startup.promise;
      if (mj.typesetPromise) await mj.typesetPromise(elements);
    }).catch(() => {}); // Exact TeX remains visible if math display is unavailable.
  }
  function formula(parent, tex) {
    if (!tex) return;
    const display = node('span', '\\('+tex+'\\)', 'arithmatex');
    parent.append(display); typeset([display]);
  }
  query.value = params.get('q') || '';
  if (params.has('kind')) kind.value = params.get('kind');
  const globalForm = document.getElementById('notation-search');
  if (globalForm) {
    const work = document.getElementById('notation-work');
    const exact = document.getElementById('notation-exact');
    const results = document.getElementById('notation-results');
    work.value = params.get('work') || '';
    exact.checked = params.get('exact') === '1';
    let dataPromise, data, matches = [], shown = 0, generation = 0;
    function page() {
      const slice = matches.slice(shown, shown+30);
      const first = results.children.length;
      for (const entry of slice) {
        const li=node('li'), heading=node('h2'), link=node('a');
        link.href=entry.url; link.append(node('code',entry.tex)); heading.append(link);
        li.append(heading);
        const math=node('p',undefined,'notation-result-math'); formula(math,entry.display); li.append(math);
        li.append(node('p',data.works.find(w=>w.id===entry.work)?.title || entry.work,'eyebrow'));
        li.append(node('p',labels[entry.kind]+' · '+entry.count+' source passages'));
        li.append(node('p',entry.excerpt,'notation-excerpt'));
        results.append(li);
      }
      shown += slice.length;
      more.hidden = shown >= matches.length;
      status.textContent = matches.length ? `${shown} of ${matches.length} matching entries. Meanings stay local to each work.` : 'No matching entries. Try a base symbol, its TeX spelling, or a different work. PDF and image notation may need the source document.';
      return results.children[first]?.querySelector('a');
    }
    async function search(updateURL=true) {
      const current=++generation;
      const q=query.value.trim();
      results.replaceChildren(); more.hidden=true;
      if (updateURL) {
        const next=new URLSearchParams();
        if(q)next.set('q',q);if(work.value)next.set('work',work.value);
        if(kind.value)next.set('kind',kind.value);if(exact.checked)next.set('exact','1');
        history.replaceState(null,'',location.pathname+(next.size?'?'+next:'')+location.hash);
      }
      if (!q && !work.value && !kind.value) { status.textContent='Choose a work or enter a symbol to search.'; return; }
      status.textContent='Loading the notation index…';
      try {
        dataPromise ||= getJSON(globalForm.dataset.index).catch(error=>{dataPromise=null;throw error;});
        data=await dataPromise;
        if(current!==generation)return;
        const words=normalize(q).split(/\s+/).filter(Boolean);
        matches=data.entries.filter(entry=> (!work.value || work.value===entry.work) && (!kind.value || kind.value===entry.kind) &&
          (exact.checked ? !q || entry.tex===q : words.every(word=>normalize(entry.tex+' '+entry.aliases+' '+entry.excerpt).includes(word))));
        matches.sort((a,b)=> Number(b.tex===q)-Number(a.tex===q) || ranks.indexOf(a.kind)-ranks.indexOf(b.kind) || a.tex.localeCompare(b.tex) || a.work.localeCompare(b.work));
        shown=0;page();
      } catch(error) {
        if(current===generation)status.textContent='The search data could not be loaded. Use the work indexes below, or submit the search to retry.';
      }
    }
    globalForm.addEventListener('submit',event=>{event.preventDefault();search();});
    for(const field of [work,kind,exact])field.addEventListener('change',()=>search());
    globalForm.addEventListener('reset',()=>{setTimeout(()=>search(),0);});
    more.addEventListener('click',()=>page()?.focus());
    if(query.value || work.value || kind.value)search(false);
    return;
  }
  const localForm=document.querySelector('[data-notation-work]');
  if(!localForm)return;
  const entries=Array.from(document.querySelectorAll('.notation-entry'));
  let matches=entries, shown=0, sourcePromise;
  function page() {
    const slice=matches.slice(shown,shown+60);
    for(const entry of slice)entry.hidden=false;
    shown+=slice.length;more.hidden=shown>=matches.length;
    status.textContent=`${shown} of ${matches.length} matching entries. Open an entry for its source passage.`;
    return slice[0]?.querySelector('summary');
  }
  function filter() {
    const words=normalize(query.value.trim()).split(/\s+/).filter(Boolean);
    matches=entries.filter(entry=>(!kind.value || entry.dataset.kind===kind.value) && words.every(word=>normalize(entry.dataset.search).includes(word)));
    for(const entry of entries)entry.hidden=true;
    shown=0;page();
  }
  localForm.addEventListener('submit',event=>{event.preventDefault();filter();});
  localForm.addEventListener('reset',()=>setTimeout(filter,0));
  kind.addEventListener('change',filter);
  more.addEventListener('click',()=>page()?.focus());
  function openHash() {
    const entry=document.getElementById(location.hash.slice(1));
    if(!entry?.classList.contains('notation-entry'))return;
    entry.hidden=false;entry.open=true;
    requestAnimationFrame(()=>entry.scrollIntoView({block:'start'}));
  }
  for(const entry of entries) {
    entry.addEventListener('toggle',()=>{
      if(!entry.open)return;
      const display=entry.querySelector('[data-math]');
      if(display && !display.hasChildNodes())formula(display,display.dataset.math);
    });
    const button=entry.querySelector('.notation-occurrences');button.hidden=false;
    button.addEventListener('click',async()=>{
      button.disabled=true;button.textContent='Loading source passages…';
      try {
        sourcePromise ||= getJSON(localForm.dataset.source).catch(error=>{sourcePromise=null;throw error;});
        const data=await sourcePromise;
        const record=data.entries.find(item=>item.id===button.dataset.symbol);
        const list=node('ol');list.className='notation-location-list';
        const target=entry.querySelector('.notation-all');target.replaceChildren(list);
        const next=node('button','Show more passages');next.type='button';target.append(next);
        let cursor=0;
        function append() {
          const first=list.children.length;
          for(const number of record.occurrences.slice(cursor,cursor+100)) {
            const passage=data.passages[number],source=data.sources[passage.source];
            const li=node('li'),link=node('a',source.repository_path.split('/').at(-1)+', line '+passage.line);
            link.href='../'+(source.source_url || source.url)+'#L'+passage.line;
            li.append(link,node('span',' · '+labels[passage.kind]));list.append(li);
          }
          cursor=Math.min(cursor+100,record.occurrences.length);next.hidden=cursor===record.occurrences.length;
          return list.children[first]?.querySelector('a');
        }
        append();next.addEventListener('click',()=>append()?.focus());
        button.textContent=record.occurrences.length+' source passages listed below';
        list.querySelector('a')?.focus();
      } catch(error) {button.disabled=false;button.textContent='Could not load passages. Try again';}
    });
  }
  for(const button of document.querySelectorAll('.notation-copy'))button.addEventListener('click',async()=>{
    try {await navigator.clipboard.writeText(button.dataset.copy);status.textContent='TeX copied: '+button.dataset.copy;}
    catch(error){status.textContent='Copy is unavailable. Select the exact TeX spelling in the entry.';}
  });
  filter();openHash();window.addEventListener('hashchange',openHash);
})();
