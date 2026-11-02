/* Progressive file/declaration filtering. Original source and links stay native. */
(()=>{
  'use strict';
  const form=document.querySelector('.lean-filter');
  if(!form)return;
  const input=form.querySelector('input'),items=[...document.querySelectorAll('[data-lean-search]')];
  const status=document.querySelector('.lean-count');
  const normalize=value=>value.normalize('NFKC').toLocaleLowerCase();
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
