/* Authenticated, chapter-sized HTML loading; passage tools initialize afterward. */
(() => {
  'use strict';
  const spec=document.getElementById('mnr-payload');if(!spec)return;
  const record=JSON.parse(spec.textContent),article=document.getElementById('chapter-text'),status=document.getElementById('mnr-loading'),retry=document.getElementById('mnr-retry');
  const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  const start=async()=>{
    retry.hidden=true;status.hidden=false;status.firstElementChild.textContent='Loading chapter…';article.setAttribute('aria-busy','true');
    try{
      let url=new URL(record.url),figures=new URL(record.figure_root);
      const pin=/^\/KomorebiP\/Operation-KOMOREBI\/[a-f0-9]{40}\/publication\/mnr-html-reading\/2026-11-04\//;
      if(url.origin!=='https://raw.githubusercontent.com'||!pin.test(url.pathname)||figures.origin!==url.origin||!pin.test(figures.pathname))throw Error('Invalid chapter location');
      // The local preview serves the same retained publication bytes.
      if(['localhost','127.0.0.1'].includes(location.hostname)){url=new URL('../../'+record.path,location.href);figures=new URL('../../publication/mnr-html-reading/2026-11-04/figures/',location.href);}
      const response=await fetch(url,{cache:'force-cache'});if(!response.ok)throw Error('Chapter download failed');
      const bytes=await response.arrayBuffer();if(bytes.byteLength>524288||await digest(bytes)!==record.part_sha256)throw Error('Chapter part failed integrity verification');
      const {offset,bytes:size,html_bytes:expected}=record;
      if(!Number.isSafeInteger(offset)||!Number.isSafeInteger(size)||offset<0||size<1||offset+size>bytes.byteLength||expected>1048576)throw Error('Invalid chapter boundaries');
      const stream=new Blob([bytes.slice(offset,offset+size)]).stream().pipeThrough(new DecompressionStream('gzip'));
      const raw=await new Response(stream).arrayBuffer();if(raw.byteLength!==expected||await digest(raw)!==record.html_sha256)throw Error('Chapter HTML failed integrity verification');
      const template=document.createElement('template');template.innerHTML=new TextDecoder('utf-8',{fatal:true}).decode(raw);
      if(template.content.querySelector('script,iframe,object,embed'))throw Error('Unexpected active chapter content');
      for(const node of template.content.querySelectorAll('*'))for(const a of node.attributes)if(/^on/i.test(a.name)||/javascript:/i.test(a.value))throw Error('Unexpected active chapter attribute');
      for(const img of template.content.querySelectorAll('img')){const src=img.getAttribute('src');if(src.startsWith('mnr-figure/'))img.src=new URL(src.slice(11),figures).href;}
      if(window.MathJax?.startup?.promise)await MathJax.startup.promise;
      window.MathJax?.typesetClear?.([article]);article.replaceChildren(template.content);article.removeAttribute('aria-busy');
      if(window.MathJax?.typesetPromise)await MathJax.typesetPromise([article]);
      for(const original of document.querySelectorAll('script[type="application/x-mnr-deferred"]'))await new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=original.dataset.src;script.onload=resolve;script.onerror=reject;original.replaceWith(script);});
      status.hidden=true;document.dispatchEvent(new CustomEvent('mnr-chapter-ready'));
      if(location.hash){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));target?.scrollIntoView();}
    }catch(error){article.removeAttribute('aria-busy');status.firstElementChild.textContent='The chapter could not load. Retry, or use the PDF and source links below.';retry.hidden=false;console.error(error);}
  };
  retry.addEventListener('click',start);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
