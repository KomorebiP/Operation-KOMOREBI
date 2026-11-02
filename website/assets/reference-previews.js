/* Explicit, on-demand previews; the original reference links remain ordinary links. */
(() => {
  'use strict';
  const script=document.querySelector('script[data-reference-source]');
  const links=Array.from(document.querySelectorAll('a[data-reference-preview]'));
  if (!script || !links.length) return;
  const dialog=document.createElement('dialog');
  if (typeof dialog.showModal!=='function') return;
  const work=script.dataset.referenceWork;
  const source=new URL(script.dataset.referenceSource,location.href);
  const base=new URL('../../',source);
  const tags=new Set('p em strong code pre div span section ul ol li dl dt dd table thead tbody tfoot tr th td caption blockquote h3 h4 h5 h6 a br sub sup figcaption'.split(' '));
  const classes=new Set(['arithmatex','equation-number','table-scroll','source-formal-note']);
  function node(tag,text,cls) {
    const result=document.createElement(tag);
    if (text!==undefined) result.textContent=text;
    if (cls) result.className=cls;
    return result;
  }
  function urlFor(value,external=false) {
    const url=new URL(value,base);
    if (!['http:','https:'].includes(url.protocol)) throw Error('Invalid reference URL');
    if (url.origin===base.origin && !url.pathname.startsWith(base.pathname)) throw Error('Reference outside reader');
    if (!external && (url.origin!==base.origin || !url.pathname.startsWith(base.pathname+'read/'+work+'/') || url.search || !url.hash)) throw Error('Wrong reference work');
    return url;
  }
  function keyFor(link) {
    const url=urlFor(link.href);
    return decodeURIComponent(url.pathname.slice(base.pathname.length))+decodeURIComponent(url.hash)+'|'+link.dataset.referencePreview;
  }
  function part(value,depth=0) {
    if (typeof value==='string') return document.createTextNode(value);
    if (!value || depth>30 || !tags.has(value.tag) || !Array.isArray(value.children)) throw Error('Invalid reference content');
    const result=node(value.tag);
    if (value.classes) result.className=value.classes.split(' ').filter(name=>classes.has(name)).join(' ');
    for (const name of ['colspan','rowspan']) if (/^\d{1,3}$/.test(value[name] || '')) result.setAttribute(name,value[name]);
    if (['row','col','rowgroup','colgroup'].includes(value.scope)) result.setAttribute('scope',value.scope);
    if (value.tag==='a') result.href=urlFor(value.url,true).href;
    for (const child of value.children) result.append(part(child,depth+1));
    if (result.classList.contains('table-scroll') || (value.tag==='div' && result.classList.contains('arithmatex'))) {
      result.tabIndex=0;result.setAttribute('role','group');
      result.setAttribute('aria-label',result.classList.contains('table-scroll') ? 'Table. Scroll horizontally if needed.' : 'Displayed equation. Scroll horizontally if needed.');
    }
    return result;
  }
  dialog.id='reference-preview';dialog.className='reference-preview';dialog.setAttribute('aria-labelledby','reference-preview-title');
  const header=node('div',undefined,'reference-preview-header');
  const title=node('h2','Reference preview');title.id='reference-preview-title';title.tabIndex=-1;
  const close=node('button','Close');close.type='button';header.append(title,close);
  const context=node('p',undefined,'reference-preview-context');
  const status=node('p',undefined,'reference-preview-status');status.setAttribute('role','status');
  const content=node('div',undefined,'reference-preview-content');
  const body=node('div',undefined,'reference-preview-body');body.append(context,status,content);
  const footer=node('div',undefined,'reference-preview-footer');
  const open=node('a','Open referenced passage','button');
  const retry=node('button','Retry preview');retry.type='button';retry.hidden=true;footer.append(open,retry);
  dialog.append(header,body,footer);document.body.append(dialog);
  let dataPromise,opener,reference,generation=0,returnFocus=true,mathQueue=Promise.resolve();
  function rememberReturn(destination) {
    try {
      const state=history.state && typeof history.state==='object' ? history.state : {};
      history.replaceState({...state,referencePreviewReturn:{index:links.indexOf(reference),label:reference.dataset.referencePreview,href:reference.href,destination}},'',location.href);
    } catch {} // Original navigation still works when history is restricted.
  }
  function restoreReturn() {
    try {
      const marker=history.state?.referencePreviewReturn;
      if (!marker || !Number.isInteger(marker.index)) return;
      const state={...history.state};delete state.referencePreviewReturn;history.replaceState(state,'',location.href);
      const link=links[marker.index],button=link?.nextElementSibling;
      if (!link || link.href!==marker.href || link.dataset.referencePreview!==marker.label || !button?.classList.contains('reference-preview-open')) return;
      const destinationId=decodeURIComponent(new URL(marker.destination || location.href,location.href).hash.slice(1));
      const currentId=decodeURIComponent(location.hash.slice(1));
      setTimeout(()=>{
        const active=document.activeElement;
        const automatic=active===document.body || active===document.documentElement || active?.id==='main' ||
          (active?.tabIndex===-1 && active.id && (active.id===destinationId || active.id===currentId));
        if (button.isConnected && automatic) button.focus({preventScroll:true});
      },0);
    } catch {}
  }
  window.addEventListener('pageshow',restoreReturn);window.addEventListener('popstate',restoreReturn);
  function data() {
    if (!dataPromise) dataPromise=fetch(source.href).then(response=>{
      if (!response.ok) throw Error('Reference previews unavailable');
      return response.json();
    }).then(index=>{
      if (index.version!==1 || index.work!==work || !index.entries || typeof index.entries!=='object') throw Error('Wrong reference index');
      return index;
    }).catch(error=>{dataPromise=null;throw error;});
    return dataPromise;
  }
  async function show() {
    const current=++generation;
    window.MathJax?.typesetClear?.([content]);content.replaceChildren();context.textContent='';
    retry.hidden=true;status.textContent='Loading referenced passage…';content.setAttribute('aria-busy','true');
    open.href=urlFor(reference.href).href;
    try {
      const index=await data();
      if (current!==generation || !dialog.open) return;
      const entry=index.entries[keyFor(reference)];
      if (!entry || !Array.isArray(entry.parts) || urlFor(entry.url).href!==open.href) throw Error('Missing reference excerpt');
      const nodes=entry.parts.map(value=>part(value));
      content.replaceChildren(...nodes);context.textContent=entry.context;
      status.textContent=entry.excerpt ? 'Excerpt from the referenced passage. Open the passage for its complete content and context.' : 'From the referenced passage.';
      mathQueue=mathQueue.then(async()=>{
        const math=window.MathJax;
        if (!math?.startup?.promise) return;
        await math.startup.promise;
        if (current===generation && dialog.open) await math.typesetPromise?.([content]);
      }).catch(()=>{if (current===generation && dialog.open) status.textContent='Math is shown as exact TeX. Open the referenced passage for the full reading view.';});
    } catch {
      dataPromise=null;
      if (current===generation && dialog.open) {status.textContent='The preview could not load. Retry, or open the referenced passage.';retry.hidden=false;}
    } finally {if (current===generation) content.removeAttribute('aria-busy');}
  }
  for (const link of links) {
    try {keyFor(link);} catch {continue;}
    const button=node('button','Preview','reference-preview-open');button.type='button';
    button.setAttribute('aria-label','Preview '+(link.getAttribute('aria-label') || link.textContent.trim()));
    button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-controls',dialog.id);
    button.addEventListener('click',()=>{
      const article=document.querySelector('#chapter-text');
      content.dataset.textSize=article?.dataset.textSize || 'default';content.dataset.textFont=article?.dataset.textFont || 'default';
      opener=button;reference=link;returnFocus=true;dialog.showModal();title.focus();show();
    });
    link.after(button);
  }
  retry.addEventListener('click',show);close.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('keydown',event=>{
    if (event.key==='Escape') {event.preventDefault();dialog.close();}
    if (event.key==='Tab') {
      const controls=Array.from(dialog.querySelectorAll('button,a[href],[tabindex]')).filter(element=>!element.disabled && element.tabIndex>=0 && element.getClientRects().length);
      const first=controls[0],last=controls[controls.length-1],active=document.activeElement;
      if (first && event.shiftKey && (active===first || active===title)) {event.preventDefault();last.focus();}
      else if (last && !event.shiftKey && active===last) {event.preventDefault();first.focus();}
    }
  });
  dialog.addEventListener('close',()=>{
    ++generation;content.removeAttribute('aria-busy');
    if (returnFocus && opener?.isConnected) opener.focus({preventScroll:true});
  });
  dialog.addEventListener('click',event=>{
    const link=event.target.closest('a[href]');
    if (!event.button && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && link) {rememberReturn(link.href);returnFocus=false;dialog.close();}
    const bounds=dialog.getBoundingClientRect();
    if (event.target===dialog && (event.clientX<bounds.left || event.clientX>bounds.right || event.clientY<bounds.top || event.clientY>bounds.bottom)) dialog.close();
  });
})();
