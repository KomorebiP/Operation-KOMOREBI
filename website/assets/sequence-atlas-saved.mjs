export const STORAGE_KEY='komorebi.sequence-atlas.saved.v1';
const valid=id=>typeof id==='string'&&/^KSEQ-\d{6}$/.test(id);
export function readSaved(storage,allowed){
  try{const raw=storage.getItem(STORAGE_KEY);if(!raw)return{ids:[],available:true};if(raw.length>10000)throw Error('Invalid saved list');const data=JSON.parse(raw);if(!Array.isArray(data))throw Error('Invalid saved list');return{ids:[...new Set(data.filter(id=>valid(id)&&(!allowed||allowed.has(id))))].slice(0,100),available:true};}
  catch{return{ids:[],available:false};}
}
export function writeSaved(storage,ids){try{storage.setItem(STORAGE_KEY,JSON.stringify([...new Set(ids.filter(valid))].slice(0,100)));return true;}catch{return false;}}
export function updateSaveButtons(root,ids){const saved=new Set(ids);root.querySelectorAll('[data-save-sequence]').forEach(button=>{const active=saved.has(button.dataset.saveSequence);button.hidden=false;button.setAttribute('aria-pressed',String(active));button.textContent=active?'Saved':'Save entry';button.setAttribute('aria-label',(active?'Remove ':'Save ')+button.dataset.saveSequence+(active?' from saved entries':''));});}
