import {readSaved,writeSaved,updateSaveButtons} from './sequence-atlas-saved.mjs';
import {fraction,exact} from './sequence-atlas-core.mjs';
import {setupStudy} from './sequence-atlas-study.js';
const root=document.querySelector('[data-entry-id]');
if(root){
  const $=id=>document.getElementById('sa-'+id),id=root.dataset.entryId,status=$('entry-status');
  root.querySelector('.sa-record-search').hidden=false;
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)};
  let saved=new Set(readSaved(storage).ids),selectedValue='';
  async function copyText(text,message){
    try{await navigator.clipboard.writeText(text);$('entry-copy-fallback').hidden=true;status.textContent=message;}
    catch{$('entry-copy-fallback').hidden=false;const field=$('entry-copy-text');field.value=text;field.focus();field.select();status.textContent='Copy the text from the selected field.';}
  }
  updateSaveButtons(root,saved);
  root.querySelector('[data-save-sequence]').addEventListener('click',()=>{const active=saved.has(id);if(active)saved.delete(id);else saved.add(id);const stored=writeSaved(storage,[...saved]);updateSaveButtons(root,saved);status.textContent=(active?'Removed from saved entries.':'Entry saved.')+(stored?'':' Saved for this page only; browser storage is unavailable.');});
  for(const button of root.querySelectorAll('[data-copy-entry]')){button.hidden=false;button.addEventListener('click',()=>copyText(document.getElementById(button.dataset.copyEntry).textContent,button.dataset.copyEntry==='sa-entry-program'?'Python program copied.':'Formula copied.'));}
  $('entry-copy').hidden=false;$('entry-copy').addEventListener('click',()=>copyText([...root.querySelectorAll('#data tbody tr')].slice(0,12).map(row=>row.querySelector('td').textContent).join(', '),'First 12 terms copied.'));
  $('entry-link').hidden=false;$('entry-link').addEventListener('click',()=>copyText(location.href,'Entry link copied.'));
  const terms=[...root.querySelectorAll('#data tbody tr')].map(row=>row.querySelector('td').textContent),factor=Number(root.dataset.indexFactor);
  setupStudy(root,terms);
  function inspect(n,{announce=true}={}){
    if(!Number.isInteger(n)||n<0||n>=terms.length){$('term-error').hidden=false;$('term-error').textContent='Choose a whole index from 0 to 63.';$('term-index').setAttribute('aria-invalid','true');$('term-index').setAttribute('aria-describedby','sa-term-help sa-term-error');return false;}
    $('term-error').hidden=true;$('term-index').removeAttribute('aria-invalid');$('term-index').setAttribute('aria-describedby','sa-term-help');$('term-index').value=n;
    selectedValue=terms[n];$('term-label').textContent='a('+n+')';$('term-value').textContent=selectedValue;$('term-data-link').href='#n-'+n;
    let basis=root.dataset.indexLabel+' = '+factor*n+'. ';
    if(root.dataset.indexKind==='factorial'){let denominator=1n;for(let k=2;k<=factor*n;k++)denominator*=BigInt(k);basis+='Ordinary coefficient = '+exact(fraction(BigInt(selectedValue),denominator))+'. The stored integer includes the factorial weight.';}
    else if(root.dataset.indexKind==='euler')basis+='This value is E_('+factor*n+'), with its sign retained.';
    else basis+='The stored value has no factorial scaling.';
    $('term-basis').textContent=basis;
    root.querySelectorAll('#data tbody tr').forEach((row,i)=>{row.classList.toggle('sa-selected-term',i===n);if(i===n)row.setAttribute('aria-current','true');else row.removeAttribute('aria-current');});
    if(announce)$('term-status').textContent='Term '+n+' selected. '+(selectedValue.length>60?'The exact value has '+selectedValue.replace('-','').length+' digits.':'a('+n+') = '+selectedValue+'.')+' Its index mapping and exact value are shown below.';
    return true;
  }
  $('term-inspector').hidden=false;
  $('term-form').noValidate=true;$('term-form').addEventListener('submit',event=>{event.preventDefault();const text=$('term-index').value;inspect(text.trim()===''?NaN:Number(text));});
  $('term-copy').addEventListener('click',()=>copyText(selectedValue,'Selected value copied.'));
  const fromHash=()=>{const match=/^#n-(\d+)$/.exec(location.hash);if(match)inspect(Number(match[1]),{announce:false});};
  inspect(2,{announce:false});fromHash();addEventListener('hashchange',fromHash);
  const links=[...root.querySelectorAll('.sa-entry-outline a')];
  if('IntersectionObserver' in window){const observer=new IntersectionObserver(items=>{const visible=items.filter(item=>item.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(!visible.length)return;const current='#'+visible[0].target.id;links.forEach(link=>{if(link.getAttribute('href')===current){link.setAttribute('aria-current','location');const menu=link.parentElement;if(menu.scrollWidth>menu.clientWidth){const item=link.getBoundingClientRect(),bounds=menu.getBoundingClientRect();if(item.left<bounds.left+8)menu.scrollLeft+=item.left-bounds.left-8;else if(item.right>bounds.right-8)menu.scrollLeft+=item.right-bounds.right+8;}}else link.removeAttribute('aria-current');});},{rootMargin:'-8% 0px -65% 0px'});links.forEach(link=>{const target=document.getElementById(link.hash.slice(1));if(target)observer.observe(target);});}
  async function typeset(){
    const math=root.querySelector('.sa-typeset');
    try{
      if(document.readyState==='loading')await new Promise(resolve=>document.addEventListener('DOMContentLoaded',resolve,{once:true}));
      if(!window.MathJax?.startup?.promise)return;
      await window.MathJax.startup.promise;if(!math.querySelector('mjx-container'))await window.MathJax.typesetPromise([math]);
      if(math.querySelector('mjx-container')&&!math.querySelector('[data-mml-node="merror"]')){math.hidden=false;const plain=root.querySelector('.sa-plain-formula');if(!plain.contains(document.activeElement))plain.open=false;root.dataset.mathReady='true';}
    }catch{root.dataset.mathReady='fallback';}
    finally{if(/^#n-\d+$/.test(location.hash))requestAnimationFrame(()=>document.getElementById(location.hash.slice(1))?.scrollIntoView({block:'center'}));}
  }
  typeset();
  addEventListener('storage',()=>{saved=new Set(readSaved(storage).ids);updateSaveButtons(root,saved);});
  root.dataset.entryReady='true';
}
