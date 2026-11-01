/* Source-linked notation. All result text is inserted as text, never HTML. */
(() => {
  'use strict';
  const labels = {'notation-table':'Notation table','definition-passage':'Definition passage','introduction-passage':'Introduction passage',use:'Use in source'};
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
      const connected=elements.filter(element=>element.isConnected);
      if (mj.typesetPromise && connected.length) await mj.typesetPromise(connected);
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
    const optionsPanel=document.getElementById('notation-options');
    if(kind.value || exact.checked)optionsPanel.open=true;
    let dataPromise, data, matches = [], entryCount=0, shown = 0, generation = 0, queryTimer;
    function updateOptions() {
      const count=Number(Boolean(kind.value))+Number(exact.checked);
      optionsPanel.querySelector('summary').textContent='More options'+(count?' · '+count+' active':'');
    }
    updateOptions();
    function page() {
      const slice = matches.slice(shown, shown+12);
      const first = results.children.length;
      for (const group of slice) {
        const entry=group.entries[0], context=group.context;
        const table=group.score>=6 ? context.table : null;
        const definitionTitle=group.score>=6 ? context.title : null;
        const title=table?.label || definitionTitle;
        const symbol=table?.display || (!table ? entry.display : null);
        const li=node('li'), heading=node('h2'), link=node('a');
        link.href=table ? context.source_url : definitionTitle ? (context.reading_url || context.source_url) : entry.url;
        if(title)link.textContent=title;
        else if(symbol)formula(link,symbol);
        else link.append(node('code',table?.tex || entry.tex));
        heading.append(link);li.append(heading);
        const workRecord=data.works.find(w=>w.id===entry.work);
        const meta=node('p',undefined,'notation-result-meta');
        const workLink=node('a',workRecord?.short_title || entry.work);
        workLink.href='collection/works/'+entry.work+'.html';workLink.title=workRecord?.title || entry.work;
        meta.append(workLink,node('span',' · '+labels[entry.kind]+(!definitionTitle && context.title ? ' · From “'+context.title+'”' : '')));li.append(meta);
        if(title && table) {
          const math=node('p',undefined,'notation-result-math');
          if(symbol)formula(math,symbol);else math.append(node('code',table.tex));
          li.append(math);
        }
        const excerpt=table?.meaning || context.excerpt;
        const end=excerpt.length>280 ? Math.max(excerpt.lastIndexOf(' ',280),200) : excerpt.length;
        li.append(node('p',excerpt.slice(0,end)+(end<excerpt.length?'…':''),'notation-excerpt'));
        const actions=node('p',undefined,'notation-result-actions');
        const sourceLink=node('a','Read source');sourceLink.href=context.source_url;
        sourceLink.title=context.source_label;actions.append(sourceLink);
        const entryLink=node('a','Open entry');entryLink.href=entry.url;
        if(group.entries.length===1)actions.append(node('span',' · '),entryLink);
        li.append(actions);
        const spellings=node('details',undefined,'notation-spellings');
        spellings.append(node('summary',group.entries.length===1 ? 'TeX spelling and source locations' : group.entries.length+' matching entries in this passage'));
        const list=node('ul');
        for(const match of group.entries) {
          const row=node('li'),a=node('a');a.href=match.url;a.append(node('code',match.tex));
          row.append(a,node('span',' · '+match.count+' source '+(match.count===1?'passage':'passages')));list.append(row);
        }
        spellings.append(list);li.append(spellings);
        results.append(li);
      }
      shown += slice.length;
      more.hidden = shown >= matches.length;
      status.textContent = matches.length ? `${shown} of ${matches.length} source ${matches.length===1?'passage':'passages'} · ${entryCount} matching ${entryCount===1?'entry':'entries'}` : 'No matches. Try a base symbol, another work, or turn off exact matching. PDF and image notation may need the source document.';
      return results.children[first]?.querySelector('a');
    }
    async function search(updateURL=true) {
      clearTimeout(queryTimer);updateOptions();
      const current=++generation;
      const q=query.value.trim();
      window.MathJax?.typesetClear?.([results]);results.replaceChildren(); more.hidden=true;
      if (updateURL) {
        const next=new URLSearchParams();
        if(q)next.set('q',q);if(work.value)next.set('work',work.value);
        if(kind.value)next.set('kind',kind.value);if(exact.checked)next.set('exact','1');
        history.replaceState(null,'',location.pathname+(next.size?'?'+next:'')+location.hash);
      }
      if (!q && !work.value && !kind.value) { status.textContent='Enter a symbol or choose a work.'; return; }
      status.textContent='Loading the notation index…';
      try {
        dataPromise ||= getJSON(globalForm.dataset.index).catch(error=>{dataPromise=null;throw error;});
        data=await dataPromise;
        if(current!==generation)return;
        const found=window.KomorebiNotationSearch.search(data,{query:q,work:work.value,kind:kind.value,exact:exact.checked});
        matches=found.groups;entryCount=found.count;
        shown=0;page();
      } catch(error) {
        if(current===generation)status.textContent='The search data could not be loaded. Use the work indexes below, or submit the search to retry.';
      }
    }
    globalForm.addEventListener('submit',event=>{event.preventDefault();search();});
    query.addEventListener('input',()=>{clearTimeout(queryTimer);queryTimer=setTimeout(()=>search(),300);});
    for(const field of [work,kind,exact])field.addEventListener('change',()=>search());
    globalForm.addEventListener('reset',()=>{setTimeout(()=>{optionsPanel.open=false;search();query.focus();},0);});
    for(const button of document.querySelectorAll('[data-query]'))button.addEventListener('click',()=>{
      query.value=button.dataset.query;exact.checked=false;search();query.focus();
    });
    window.addEventListener('hashchange',()=>{
      const target=document.getElementById(location.hash.slice(1));
      if(target?.matches('.notation-browse'))target.open=true;
    });
    const target=document.getElementById(location.hash.slice(1));
    if(target?.matches('.notation-browse'))target.open=true;
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
