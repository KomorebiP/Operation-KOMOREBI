import {readSaved,writeSaved,updateSaveButtons} from './sequence-atlas-saved.mjs';
const root=document.querySelector('[data-entry-id]');
if(root){
  const id=root.dataset.entryId,status=document.getElementById('sa-entry-status');
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)};
  let saved=new Set(readSaved(storage).ids);
  updateSaveButtons(root,saved);
  root.querySelector('[data-save-sequence]').addEventListener('click',()=>{const active=saved.has(id);if(active)saved.delete(id);else saved.add(id);const stored=writeSaved(storage,[...saved]);updateSaveButtons(root,saved);status.textContent=(active?'Removed from saved entries.':'Entry saved.')+(stored?'':' Saved for this page only; browser storage is unavailable.');});
  const copy=document.getElementById('sa-entry-copy');copy.hidden=false;
  copy.addEventListener('click',async()=>{const terms=[...root.querySelectorAll('tbody tr')].slice(0,12).map(row=>row.querySelector('td').textContent).join(', ');try{await navigator.clipboard.writeText(terms);status.textContent='First 12 terms copied.';}catch{document.getElementById('sa-entry-copy-fallback').hidden=false;const field=document.getElementById('sa-entry-copy-text');field.value=terms;field.focus();field.select();status.textContent='Copy the terms from the field.';}});
  addEventListener('storage',()=>{saved=new Set(readSaved(storage).ids);updateSaveButtons(root,saved);});
}
