// Native links remain usable without JavaScript. Enhancement shows one workspace.
export function setupInterface(root,{onLeavePlot=()=>{}}={}){
  const names=['find','discover','explorer','catalogue','reference'];let current=null;
  const nav=root.querySelector('.sa-mode-nav');root.querySelector('.sa-intro').after(nav);
  const panels=new Map(names.map(id=>[id,document.getElementById(id)]));
  const topics=root.querySelector('.sa-topic-index');if(topics)panels.get('find').append(topics);
  for(const [id,panel]of panels){const heading=panel.querySelector('h2');if(!heading.id)heading.id='sa-mode-'+id+'-title';heading.tabIndex=-1;panel.setAttribute('aria-labelledby',heading.id);panel.dataset.atlasPanel=id;}
  function activate(id,{history=true,focus=false}={}){
    if(!panels.has(id))id=document.getElementById(id)?.closest('[data-atlas-panel]')?.dataset.atlasPanel||'find';
    if(current==='explorer'&&id!==current)onLeavePlot();
    for(const [name,panel]of panels)panel.hidden=name!==id;
    root.querySelectorAll('[data-atlas-mode]').forEach(link=>{if(link.dataset.atlasMode===id)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
    current=id;root.dataset.activePanel=id;
    if(history&&location.hash!=='#'+id){const url=new URL(location.href);url.hash=id;window.history.pushState(null,'',url);}
    if(focus)panels.get(id).querySelector('h2').focus({preventScroll:true});
  }
  root.addEventListener('click',event=>{const link=event.target.closest('a[href^="#"]');if(!link||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey)return;const id=link.getAttribute('href').slice(1);if(panels.has(id))activate(id,{history:false,focus:true});});
  const restore=()=>activate(location.hash.slice(1)||'find',{history:false});addEventListener('hashchange',restore);addEventListener('popstate',restore);
  root.classList.add('sa-enhanced');
  return activate;
}
