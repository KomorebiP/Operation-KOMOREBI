/* On-demand notation lookup, scoped to the work being read. */
(() => {
  'use strict';
  const dialog=document.querySelector('#chapter-notation');
  const opener=document.querySelector('.chapter-notation-open');
  if (!dialog || !opener || typeof dialog.showModal!=='function' || !window.KomorebiNotationSearch) return;
  const fallback=document.querySelector('.chapter-notation-fallback');
  const input=dialog.querySelector('#chapter-notation-query');
  const form=dialog.querySelector('form');
  const status=dialog.querySelector('.chapter-notation-status');
  const results=dialog.querySelector('.chapter-notation-results');
  const work=dialog.dataset.work;
  const base=new URL('../../',new URL(dialog.dataset.source,location.href));
  let dataPromise,generation=0,timer,mathQueue=Promise.resolve(),returnFocus=true;
  function node(tag,text,cls) {
    const element=document.createElement(tag);
    if (text!==undefined) element.textContent=text;
    if (cls) element.className=cls;
    return element;
  }
  function targetURL(target) {
    const url=new URL(target,base);
    if (url.origin!==base.origin || !url.pathname.startsWith(base.pathname)) throw new Error('Invalid notation destination');
    return url.href;
  }
  function formula(parent,tex) {
    if (!tex) return;
    const math=node('span','\\('+tex+'\\)','arithmatex');
    parent.append(math);
    mathQueue=mathQueue.then(async()=>{
      const mj=window.MathJax;
      if (!mj?.startup?.promise) return;
      await mj.startup.promise;
      if (math.isConnected) await mj.typesetPromise?.([math]);
    }).catch(()=>{}); // Exact TeX remains available if typesetting fails.
  }
  async function data() {
    if (!dataPromise) dataPromise=fetch(dialog.dataset.source).then(response=>{
      if (!response.ok) throw new Error('Notation unavailable');
      return response.json();
    }).then(index=>{
      if (index.version!==2 || index.works.length!==1 || index.works[0].id!==work ||
          index.contexts.some(context=>context.work!==work) ||
          index.entries.some(entry=>entry.work!==work || index.contexts[entry.context]?.work!==work)) throw new Error('Wrong notation work');
      return index;
    }).catch(error=>{ dataPromise=null;throw error; });
    return dataPromise;
  }
  async function search() {
    clearTimeout(timer);
    const current=++generation;
    const query=input.value.trim();
    window.MathJax?.typesetClear?.([results]);results.replaceChildren();
    results.setAttribute('aria-busy','true');status.textContent='Looking up notation…';
    try {
      const index=await data();
      if (current!==generation || !dialog.open) return;
      const found=window.KomorebiNotationSearch.search(index,{query,work,kind:'',exact:false});
      const exactLabel=group=>group.context.table?.label?.trim().toLocaleLowerCase()===query.toLocaleLowerCase();
      const groups=found.groups.sort((a,b)=>a.score-b.score || Number(exactLabel(b))-Number(exactLabel(a))).slice(0,6);
      const labels={'notation-table':'Notation table','definition-passage':'Definition passage','introduction-passage':'Introduction passage','use':'In context'};
      for (const group of groups) {
        const entry=group.entries[0],context=group.context;
        const row=node('li'),heading=node('h3',context.table?.label || labels[entry.kind]);
        row.append(heading);
        const symbols=node('p',undefined,'chapter-notation-symbols');
        const display=context.table?.display || (!context.table ? entry.display : null);
        if (display) formula(symbols,display);
        else symbols.append(node('code',context.table?.tex || entry.tex));
        row.append(symbols,node('p',context.table?.meaning || context.excerpt));
        const links=node('p',undefined,'chapter-notation-links');
        const passage=node('a','Read passage');passage.href=targetURL(context.reading_url || context.source_url);
        passage.title=context.source_label;
        const full=node('a','Full notation entry');full.href=targetURL(entry.url);
        links.append(passage,node('span',' · '),full);row.append(links);results.append(row);
      }
      status.textContent=groups.length ? (query ? 'Showing '+groups.length+' of '+found.groups.length+' matching passages.' : 'Browse this work’s notation, or search above.') : 'No matching passages. Try a symbol name or open the full notation index below.';
    } catch (error) {
      if (current===generation && dialog.open) status.textContent='Notation could not load. Search again to retry, or open the full notation index below.';
    } finally { if (current===generation) results.removeAttribute('aria-busy'); }
  }
  opener.addEventListener('click',()=>{
    returnFocus=true;
    const selection=window.getSelection?.();
    const article=document.querySelector('#chapter-text');
    const selected=selection && article?.contains(selection.anchorNode) ? selection.toString().trim() : '';
    if (selected && selected.length<=80) input.value=selected;
    dialog.showModal();input.focus();search();
  });
  form.addEventListener('submit',event=>{event.preventDefault();search();});
  input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(search,200);});
  dialog.querySelector('.chapter-notation-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('keydown',event=>{if (event.key==='Escape') {event.preventDefault();dialog.close();}});
  dialog.addEventListener('close',()=>{++generation;clearTimeout(timer);results.removeAttribute('aria-busy');if (returnFocus) opener.focus();});
  dialog.addEventListener('click',event=>{
    if (!event.button && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && event.target.closest('a[href]')) {returnFocus=false;dialog.close();}
    const bounds=dialog.getBoundingClientRect();
    if (event.target===dialog && (event.clientX<bounds.left || event.clientX>bounds.right || event.clientY<bounds.top || event.clientY>bounds.bottom)) dialog.close();
  });
  opener.hidden=false;
  if (fallback) fallback.hidden=true;
})();
