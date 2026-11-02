/* Progressive file/declaration filtering. Original source and links stay native. */
(()=>{
  'use strict';
  const normalize=value=>value.normalize('NFKC').toLocaleLowerCase();
  const outline=document.querySelector('[data-lean-outline]');
  if(outline){
    if(window.matchMedia?.('(min-width: 68rem)').matches)outline.open=true;
    const form=outline.querySelector('.lean-outline-filter'),input=form.querySelector('input');
    const status=outline.querySelector('.lean-declaration-count');
    const entries=[...outline.querySelectorAll('[data-lean-declaration]')].map(node=>({node,text:normalize(node.dataset.leanDeclaration)}));
    function filter(){
      const terms=normalize(input.value).trim().split(/\s+/).filter(Boolean);
      let count=0;
      for(const entry of entries){entry.node.hidden=!terms.every(term=>entry.text.includes(term));if(!entry.node.hidden)count++;}
      status.textContent=count+' of '+entries.length+' declarations'+(count===0?' — clear the search to show all.':'');
    }
    form.hidden=false;
    input.addEventListener('input',filter);
    form.addEventListener('submit',event=>{event.preventDefault();filter();});
    form.addEventListener('reset',()=>{input.value='';filter();});
    window.addEventListener('pageshow',filter);
    filter();
  }
  const form=document.querySelector('.lean-filter');
  if(!form)return;
  const input=form.querySelector('input'),items=[...document.querySelectorAll('[data-lean-search]')];
  const status=document.querySelector('.lean-count');
  const rows=items.map(node=>({node,text:normalize(node.dataset.leanSearch)}));
  function filter(){
    const terms=normalize(input.value).trim().split(/\s+/).filter(Boolean);
    let count=0;
    for(const row of rows){row.node.hidden=!terms.every(term=>row.text.includes(term));if(!row.node.hidden)count++;}
    status.textContent=count+' of '+rows.length+' files'+(count===0?' — try another file path or declaration name.':'');
    const url=new URL(location.href);
    if(input.value.trim())url.searchParams.set('q',input.value.trim());else url.searchParams.delete('q');
    try{history.replaceState(null,'',url);}catch{}
  }
  function restore(){input.value=new URL(location.href).searchParams.get('q')||'';filter();}
  form.hidden=false;
  input.addEventListener('input',filter);
  form.addEventListener('submit',event=>{event.preventDefault();filter();});
  form.addEventListener('reset',()=>{input.value='';filter();});
  window.addEventListener('popstate',restore);
  window.addEventListener('pageshow',restore);
  restore();
})();
