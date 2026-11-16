// Progressive enhancement: the citation itself is readable without JavaScript.
if(typeof document!=='undefined')for(const button of document.querySelectorAll('[data-copy-citation]')){
  button.hidden=false;
  button.addEventListener('click',async()=>{const detail=button.closest('details'),text=detail.querySelector('.sr-citation').textContent,status=detail.querySelector('[role=status]');try{await navigator.clipboard.writeText(text);status.textContent='Citation copied.';}catch{const label=detail.querySelector('label'),field=label.querySelector('textarea');label.hidden=false;field.value=text;field.focus();field.select();status.textContent='Copy the selected citation.';}});
}
