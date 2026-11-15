export const PAGE_THEME_KEY='komorebi.sequence-reading-theme.v1';
export function readPageTheme(storage){try{const value=storage.getItem(PAGE_THEME_KEY);return ['light','dark','system'].includes(value)?value:'light';}catch{return 'light';}}
export function effectiveDark(theme,systemDark=false){return theme==='dark'||theme==='system'&&systemDark;}
if(typeof document!=='undefined'){
  const root=document.querySelector('.sl-library,.sequence-atlas,.sar');
  if(root&&!document.getElementById('sq-page-theme')){
    const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)},system=matchMedia('(prefers-color-scheme:dark)');
    let theme=readPageTheme(storage);document.documentElement.dataset.sequenceTheme=theme;
    const bar=document.createElement('div');bar.className='sequence-reading-controls';
    const label=document.createElement('label');label.htmlFor='sq-page-theme';label.append(document.createTextNode('Page appearance'));
    const select=document.createElement('select');select.id='sq-page-theme';
    for(const [value,text]of [['light','High contrast light'],['dark','High contrast dark'],['system','Match system']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}select.value=theme;label.append(select);
    const status=document.createElement('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');bar.append(label,status);root.prepend(bar);
    const announce=()=>window.dispatchEvent(new CustomEvent('sequence-page-theme',{detail:{dark:effectiveDark(theme,system.matches)}}));
    select.addEventListener('change',()=>{theme=select.value;document.documentElement.dataset.sequenceTheme=theme;try{storage.setItem(PAGE_THEME_KEY,theme);status.textContent='Page appearance remembered in this browser.';}catch{status.textContent='Appearance changed for this page. Browser storage is unavailable.';}announce();});
    system.addEventListener('change',()=>{if(theme==='system')announce();});
    addEventListener('storage',event=>{if(event.key===PAGE_THEME_KEY||event.key===null){theme=readPageTheme(storage);select.value=theme;document.documentElement.dataset.sequenceTheme=theme;announce();}});
  }
}
