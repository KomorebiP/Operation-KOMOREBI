import {analyzeStudy,STUDY_MODES,readStudyURL,studyURL,studyCSV,studyIndexed} from './sequence-atlas-study.mjs';

export function setupStudy(root,terms){
  const $=name=>document.getElementById('sa-study-'+name),form=$('form'),id=root.dataset.entryId;
  let model;
  const node=(tag,text)=>{const item=document.createElement(tag);item.textContent=text;return item;};
  const table=(table,caption,head,rows)=>{
    table.querySelector('caption').textContent=caption;
    const heading=node('tr','');for(const text of head){const cell=node('th',text);cell.scope='col';heading.append(cell);}table.querySelector('thead').replaceChildren(heading);
    table.querySelector('tbody').replaceChildren(...rows.map(values=>{const row=node('tr','');values.forEach((value,i)=>{const cell=node(i?'td':'th',value??'undefined');if(!i)cell.scope='row';row.append(cell);});return row;}));
  };
  function render(state,{announce=false,error=null}={}){
    model=analyzeStudy(terms,state);state=model.state;
    for(const key of ['transform','start','count','modulus']){$(key).value=state[key];$(key).removeAttribute('aria-invalid');$(key).removeAttribute('aria-describedby');}
    $('modulus-field').hidden=state.transform!=='mod';
    $('error').hidden=!error;$('error').textContent=error||'';form.removeAttribute('aria-describedby');
    $('rule').textContent=STUDY_MODES[state.transform][1]+(state.transform==='mod'?' Here m='+state.modulus+'.':'');
    $('range').textContent=`Indices ${state.start}–${state.start+state.count-1} of the 64 stored terms. Undefined values retain their index positions.`;
    const facts=model.facts,pairs=[['Defined values',`${facts.defined} of ${state.count}`],['Signs in this sample',`${facts.positive} positive · ${facts.zero} zero · ${facts.negative} negative`],
      ['Integer parity',`${facts.even} even · ${facts.odd} odd${facts.integers<facts.defined?' · '+(facts.defined-facts.integers)+' noninteger':''}`],['GCD of defined values',facts.gcd??'Requires a nonempty integer sample']];
    $('facts').replaceChildren(...pairs.map(([label,value])=>{const row=node('div','');row.append(node('dt',label),node('dd',value));return row;}));
    table($('values'),`${STUDY_MODES[state.transform][0]}, n=${state.start}–${state.start+state.count-1}`,['n','b(n)'],model.rows.map(row=>[row.n,row.value]));
    const columns=model.ladder[0].length;
    table($('differences'),`Original integers and backward differences, n=${state.start}–${state.start+columns-1}`,['Order',...Array.from({length:columns},(_,n)=>'n='+(state.start+n))],model.ladder.map((row,k)=>[k?'Difference '+k:'a(n)',...row]));
    const observation=model.observation;
    $('observation').textContent=observation?`Order ${observation.order} backward differences are constant (${observation.value}) across ${observation.count} tested indices, n=${observation.start}–${observation.end}. This is a finite observation.`:'No constant difference row of orders 1–4 with at least four defined values was found in this window. This does not rule out other patterns.';
    const plot=new URL('../sequences.html',location.href);plot.hash='explorer';
    for(const [key,value]of Object.entries({sequence:id,view:state.transform==='mod'?'mod':'standard',transform:state.transform==='mod'?'raw':state.transform,start:state.start,count:state.count,modulus:state.modulus}))plot.searchParams.set(key,String(value));$('plot').href=plot;$('plot').hidden=facts.defined===0;
    const search=model.search,discovery=model.discovery;
    for(const [name,values,key,fragment]of [['search',search,'q','find'],['discover',discovery,'discover','discover']]){
      $(name).hidden=!values.length;if(values.length){const url=new URL('../sequences.html',location.href);url.searchParams.set(key,values.join(','));url.hash=fragment;$(name).href=url;}else $(name).removeAttribute('href');
    }
    $('action-note').textContent=(search.length?`Search uses ${search.length} consecutive integers from n=${model.searchStart}. `:'Search needs consecutive integer values within its size limits. ')+(discovery.length?`Discovery uses ${discovery.length}, reindexed from zero in its input. `:'Discovery needs at least six consecutive integers of at most 300 digits each. ')+'Indexed copies and downloads retain undefined positions.';
    $('previous').disabled=state.start===0;$('next').disabled=state.start+state.count>=terms.length;
    if(announce)$('status').textContent=`${STUDY_MODES[state.transform][0]} updated: ${state.count} index positions, ${facts.defined} defined values. Exact values and sample statistics are shown below.`;
  }
  function commit(state){
    try{const checked=analyzeStudy(terms,state).state;render(checked,{announce:true});history.pushState(null,'',studyURL(location.href,checked));}
    catch(error){$('error').textContent=error.message;$('error').hidden=false;form.setAttribute('aria-describedby','sa-study-error');if(error.field){$(error.field).setAttribute('aria-invalid','true');$(error.field).setAttribute('aria-describedby','sa-study-error');}}
  }
  async function copy(text,message){
    try{await navigator.clipboard.writeText(text);$('copy-fallback').hidden=true;$('status').textContent=message;}
    catch{$('copy-fallback').hidden=false;$('copy-text').value=text;$('copy-text').focus();$('copy-text').select();$('status').textContent='Copy the text from the selected field.';}
  }
  function download(extension,text,type){
    const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=id+'-'+model.state.transform+'-n'+model.state.start+'.'+extension;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('status').textContent='Exact study '+extension.toUpperCase()+' downloaded.';
  }
  form.noValidate=true;form.hidden=false;
  form.addEventListener('submit',event=>{event.preventDefault();const next=Object.fromEntries(['transform','start','count','modulus'].map(key=>[key,$(key).value]));if(next.transform!=='mod')next.modulus=model.state.modulus;commit(next);});
  $('transform').addEventListener('change',()=>{$('modulus-field').hidden=$('transform').value!=='mod';});
  for(const [name,direction]of [['previous',-1],['next',1]])$(name).addEventListener('click',()=>commit({...model.state,start:Math.max(0,Math.min(terms.length-model.state.count,model.state.start+direction*model.state.count))}));
  root.querySelector('.sa-study-paging').hidden=false;
  for(const name of ['copy','share','csv','json'])$(name).hidden=false;
  $('copy').addEventListener('click',()=>copy(studyIndexed(model),'Indexed study values copied.'));
  $('share').addEventListener('click',()=>copy(studyURL(location.href,model.state).href,'Study link copied.'));
  $('csv').addEventListener('click',()=>download('csv',studyCSV(model),'text/csv;charset=utf-8'));
  $('json').addEventListener('click',()=>download('json',JSON.stringify({schema:1,entry:id,public_url:studyURL(location.href,model.state).href,definition:STUDY_MODES[model.state.transform][1],conventions:'Original stored index n retained. Prefix operations start at zero. Undefined positions are null. Difference ladder acts on original integers. All observations are finite.',...model},null,2)+'\n','application/json'));
  const restore=()=>{const {state,error}=readStudyURL(location.href);render(state,{error});};
  restore();addEventListener('popstate',restore);root.dataset.studyReady='true';
}
