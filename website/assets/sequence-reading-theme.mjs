import './sequence-research-ui.mjs';
export const PAGE_THEME_KEY='komorebi.sequence-reading-theme.v1';
export const PAGE_SCHEME_KEY='komorebi.sequence-reading-scheme.v1';
export function readPageTheme(storage){try{const value=storage.getItem(PAGE_THEME_KEY);return ['light','dark','system'].includes(value)?value:'light';}catch{return 'light';}}
export function readPageScheme(storage){try{const value=storage.getItem(PAGE_SCHEME_KEY);return ['green','mono'].includes(value)?value:'green';}catch{return 'green';}}
export function effectiveDark(theme,systemDark=false){return theme==='dark'||theme==='system'&&systemDark;}
if(typeof document!=='undefined'){
  const root=document.querySelector('.sl-library,.sequence-atlas,.sar');
  if(root&&!document.getElementById('sq-page-theme')){
    const binomialReading=root.dataset.page==='central-binomial';
    const colorSchemeName=binomialReading?'Ink & blue':'Site green';
    const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)},system=matchMedia('(prefers-color-scheme:dark)');
    let theme=readPageTheme(storage),scheme=readPageScheme(storage);
    const apply=()=>{document.documentElement.dataset.sequenceTheme=theme;document.documentElement.dataset.sequenceScheme=scheme;};apply();
    const bar=document.createElement('div');bar.className='sequence-reading-controls';
    const group=document.createElement('div');group.className='sequence-scheme-toggles';group.setAttribute('role','group');group.setAttribute('aria-label','Color scheme');
    const buttons=new Map();for(const [value,text]of [['green',colorSchemeName],['mono','Black & white']]){const button=document.createElement('button');button.type='button';button.id='sq-scheme-'+value;button.textContent=text;button.setAttribute('aria-pressed',String(value===scheme));buttons.set(value,button);group.append(button);}
    const label=document.createElement('label');label.htmlFor='sq-page-theme';label.append(document.createTextNode('Display'));
    const select=document.createElement('select');select.id='sq-page-theme';
    for(const [value,text]of [['light','Light'],['dark','Dark'],['system','Match system']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}select.value=theme;label.append(select);
    const status=document.createElement('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');bar.append(group,label,status);root.prepend(bar);
    const announce=(schemeChanged=false)=>window.dispatchEvent(new CustomEvent('sequence-page-theme',{detail:{dark:effectiveDark(theme,system.matches),scheme,schemeChanged}}));
    const refresh=()=>{apply();select.value=theme;for(const [value,button]of buttons)button.setAttribute('aria-pressed',String(value===scheme));};
    for(const [value,button]of buttons)button.addEventListener('click',()=>{scheme=value;refresh();try{storage.setItem(PAGE_SCHEME_KEY,scheme);status.textContent=(scheme==='mono'?'Black & white':colorSchemeName)+(binomialReading?' selected. Display preference remembered in this browser.':' remembered. Plots match this scheme; other palettes are optional.');}catch{status.textContent='Scheme applied for this page. Browser storage is unavailable.';}announce(true);});
    select.addEventListener('change',()=>{theme=select.value;apply();try{storage.setItem(PAGE_THEME_KEY,theme);status.textContent='Display mode remembered in this browser.';}catch{status.textContent='Display changed for this page. Browser storage is unavailable.';}announce();});
    system.addEventListener('change',()=>{if(theme==='system')announce();});
    addEventListener('storage',event=>{if([PAGE_THEME_KEY,PAGE_SCHEME_KEY,null].includes(event.key)){const previous=scheme;theme=readPageTheme(storage);scheme=readPageScheme(storage);refresh();announce(previous!==scheme);}});
  }
}
