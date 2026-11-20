import './sequence-reading-theme.mjs';
import {enhanceMath,clearMath} from './math-display.mjs';
import {searchEntries} from './sequence-atlas-search.mjs';
import {SEARCH_KEYS,RECORD_FILTERS,FAMILY_FILTERS,emptySearch,normalizeSearch,librarySearch,librarySearchCSV} from './sequence-library-search.mjs';
import {createInspectionLink,readInspectionLink} from './sequence-inspection-links.mjs';

import {referenceQuery} from './sequence-oeis-core.mjs';
import {createReferenceClient} from './sequence-oeis-client.mjs';

import {workbenchLink,localSource,referenceSource,customSource,familySource,WORKBENCH_DEFAULTS} from './sequence-workbench-core.mjs';



import {STORAGE_KEY,readSaved,writeSaved,updateSaveButtons} from './sequence-atlas-saved.mjs';
import {familySearchEntries} from './sequence-library-membership.mjs';

const root=document.querySelector('[data-library]'),$=id=>document.getElementById('sl-'+id),make=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
/** Deep links reveal optional panels without discarding static source content. */
function revealLibraryTarget(){
  if(!location.hash||!root)return;
  let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
  const target=document.getElementById(id);
  if(!target||!root.contains(target))return;
  for(let ancestor=target.parentElement;ancestor&&ancestor!==root;ancestor=ancestor.parentElement){
    if(ancestor.tagName==='DETAILS')ancestor.open=true;
  }
  if(target.matches('.sl-optional-section'))target.querySelector(':scope > details.sl-topic-disclosure')?.setAttribute('open','');
  if(['generalized','research-graph','identify','modular-dynamics','research-notebooks'].includes(target.id)){
    target.querySelector('details')?.setAttribute('open','');
  }
}
if(root){
  addEventListener('hashchange',revealLibraryTarget);
  revealLibraryTarget();
}

/** Render stored integer strings without numeric conversion or invented source-degree maps. */
function inlineExactValues(entry,initialPosition=0,openFromLink=false,selectedFormula=()=>0,variantCount=1){
  const values=entry.terms;
  if(!Array.isArray(values)||!values.length)return null;
  const panel=make('details'),summary=make('summary',`Inspect exact values (${values.length})`);
  panel.className='sl-term-inspector';panel.append(summary);
  const symbol=entry.index_symbol||'n',offset=Number.isSafeInteger(entry.offset)?entry.offset:0;
  const triangle=entry.triangle;
  const hasCoordinates=Array.isArray(triangle?.row_offsets)&&Array.isArray(triangle?.row_lengths);
  const rationals=Array.isArray(entry.rational_terms)&&entry.rational_terms.length===values.length;
  const degrees=entry.source_degrees;
  const hasDegrees=Array.isArray(degrees)&&degrees.length===values.length&&degrees.every(Number.isSafeInteger);
  const size=8;
  let first=Math.max(0,Math.min(values.length-1,Math.floor(initialPosition/size)*size)),mounted=false,shareGeneration=0;
  let shareStatus,fallbackLabel,fallbackInput;
  function invalidateShare(){
    shareGeneration++;
    if(!mounted)return;
    fallbackLabel.hidden=true;fallbackInput.value='';shareStatus.textContent='';
  }
  function init(){
    if(mounted)return;
    mounted=true;
    const container=make('div'),controls=make('form'),previous=make('button','Previous 8'),next=make('button','Next 8'),exportWindow=make('button','Export window CSV'),copyLink=make('button','Copy inspection link');
    const jumpLabel=make('label',`Go to stored ${symbol}`),jump=make('input'),go=make('button','Go');
    container.className='sl-term-inspector-body';controls.className='sl-term-controls';
    previous.type=next.type=exportWindow.type=copyLink.type='button';go.type='submit';
    copyLink.className='sl-term-share-button';
    exportWindow.className='sl-term-export';
    jump.type='number';jump.min=String(offset);jump.max=String(offset+values.length-1);jump.step='1';jump.required=true;
    jump.inputMode='numeric';jumpLabel.append(jump);
    controls.append(previous,next,jumpLabel,go,exportWindow,copyLink);
    const status=make('p'),frame=make('div'),table=make('table'),head=make('thead'),header=make('tr'),body=make('tbody');
    status.className='sl-term-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    frame.className='sl-term-scroll';frame.tabIndex=0;frame.setAttribute('role','region');
    frame.setAttribute('aria-label',`Exact indexed values for ${entry.id}`);
    const columns=[symbol,...(hasCoordinates?['Row n','Column k']:[]),...(hasDegrees?['Source degree']:[]),'Exact stored value',...(rationals?['Original rational value']:[])];
    const csvColumns=['record_id','stored_index',...(hasCoordinates?['row_n','column_k']:[]),...(hasDegrees?['source_degree']:[]),'exact_stored_value',...(rationals?['original_rational_value']:[])];
    for(const col of columns){const th=make('th',col);th.scope='col';header.append(th);}
    head.append(header);table.append(head,body);frame.append(table);
    const detail=make('p',hasCoordinates?
      'The first column is the flat stored index. Row and column coordinates are shown separately.':
      'Indices are the stored sequence indices, which may differ from source Taylor degrees.');
    if(hasDegrees)detail.textContent+=' Source degrees follow each record’s recorded index map.';
    detail.className='sl-term-index-note';
    shareStatus=make('p');fallbackLabel=make('label','Select and copy this inspection link');fallbackInput=make('input');
    shareStatus.className='sl-inspection-link-status';shareStatus.setAttribute('role','status');shareStatus.setAttribute('aria-live','polite');
    fallbackLabel.className='sl-inspection-link-fallback';fallbackLabel.hidden=true;
    fallbackInput.type='url';fallbackInput.readOnly=true;
    fallbackLabel.append(fallbackInput);
    container.append(controls,status,frame,detail,shareStatus,fallbackLabel);panel.append(container);
    let currentRows=[];
    function renderWindow(){
      invalidateShare();
      const end=Math.min(values.length,first+size);
      status.textContent=`Stored ${symbol}=${offset+first}–${offset+end-1} · ${end-first} of ${values.length} exact values`;
      jump.value=String(offset+first);
      previous.disabled=first===0;next.disabled=end>=values.length;
      body.replaceChildren();currentRows=[];
      for(let i=first;i<end;i++){
        const index=offset+i,row=make('tr'),cells=[String(index)];
        if(hasCoordinates){
          let n=-1;
          for(let j=0;j<triangle.row_offsets.length;j++){
            if(index>=triangle.row_offsets[j]&&index<triangle.row_offsets[j]+triangle.row_lengths[j]){n=j;break;}
          }
          cells.push(n<0?'Not recorded':String(n),n<0?'Not recorded':String(index-triangle.row_offsets[n]));
        }
        if(hasDegrees)cells.push(String(degrees[i]));
        cells.push(String(values[i]));
        if(rationals)cells.push(String(entry.rational_terms[i]));
        currentRows.push(cells);
        for(let j=0;j<cells.length;j++){
          const cell=make(j===0?'th':'td',cells[j]);
          if(j===0)cell.scope='row';
          row.append(cell);
        }
        body.append(row);
      }
    }
    copyLink.addEventListener('click',async()=>{
      invalidateShare();
      const url=createInspectionLink(location.href,entry,selectedFormula(),offset+first,variantCount),generation=shareGeneration;
      const current=()=>generation===shareGeneration&&panel.isConnected&&!panel.closest('details:not([open])');
      try {
        if(!navigator.clipboard?.writeText)throw Error('Clipboard unavailable');
        await navigator.clipboard.writeText(url);
        if(!current())return;
        fallbackLabel.hidden=true;
        shareStatus.textContent='Inspection link copied. The recipient will see this formula and index window.';
      }catch{
        if(!current())return;
        fallbackLabel.hidden=false;fallbackInput.value=url;
        shareStatus.textContent='Clipboard unavailable. Select and copy the link below.';
        fallbackInput.focus();fallbackInput.select();
      }
    });
    exportWindow.addEventListener('click',()=>{
      const encodeCell=value=>'"'+String(value).replaceAll('"','""')+'"';
      const data=[csvColumns,...currentRows.map(row=>[entry.id,...row])];
      const csv=data.map(row=>row.map(encodeCell).join(',')).join('\r\n')+'\r\n';
      const id=String(entry.id).replace(/[^A-Za-z0-9_.-]/g,'_');
      const end=Math.min(values.length,first+size);
      save(csv,'text/csv;charset=utf-8',`sequence-${id}-${offset+first}-${offset+end-1}.csv`);
    });
    function pageWindow(step,button){
      const hadFocus=document.activeElement===button;
      first=Math.max(0,Math.min(values.length-1,first+step*size));renderWindow();
      if(hadFocus&&button.disabled)frame.focus({preventScroll:true});
    }
    previous.addEventListener('click',()=>pageWindow(-1,previous));
    next.addEventListener('click',()=>pageWindow(1,next));
    controls.addEventListener('submit',event=>{
      event.preventDefault();
      const index=jump.value.trim()===''?NaN:Number(jump.value);
      if(!Number.isSafeInteger(index)||index<offset||index>=offset+values.length){
        jump.setCustomValidity(`Enter a stored index from ${offset} to ${offset+values.length-1}.`);
        jump.reportValidity();return;
      }
      jump.setCustomValidity('');
      first=Math.floor((index-offset)/size)*size;renderWindow();
    });
    jump.addEventListener('input',()=>jump.setCustomValidity(''));
    renderWindow();
  }
  panel.addEventListener('toggle',()=>{if(panel.open)init();});
  if(openFromLink){panel.open=true;init();}
  return {panel,invalidateShare};
}

function definitionPreview(formula,label,expanded,recordedVariants=[],entry=null,initialPosition=0){
  const definingExpression=formula.textContent;
  const detail=make('details'),summary=make('summary'),name=make('span','Defining formula'),excerpt=make('span',definingExpression.replace(/\s+/g,' ').trim());
  name.className='sl-definition-label';excerpt.className='sl-definition-excerpt';
  excerpt.setAttribute('aria-hidden','true');
  summary.setAttribute('aria-label','Defining formula for '+label);
  summary.append(name,excerpt);
  detail.className='sl-result-definition';detail.open=expanded;
  detail.append(summary,formula);

  // Keep the original defining expression even when a source catalogue lists only alternatives.
  const variants=Array.isArray(recordedVariants)?recordedVariants.filter(v=>v&&typeof v.expression==='string'&&v.expression.length):[];
  if(variants.length&&!variants.some(v=>v.expression===definingExpression)){
    variants.unshift({title:'Defining formula',kind:'definition',expression:definingExpression});
  }
  let selected=Math.max(0,variants.findIndex(v=>v.expression===definingExpression)),mounted=false;
  const shared=entry&&results.length===1?readInspectionLink(location.href,entry,variants.length):null;
  if(shared){
    selected=shared.variantIndex;
    formula.textContent=variants[selected].expression;
    detail.open=true;
  }
  function mountVariants(){
    if(mounted||!variants.length)return;
    mounted=true;
    const toolbar=make('div'),note=make('p'),source=make('p'),sourceLink=make('a','Definition and derivation source'),kind=make('span');
    toolbar.className='sl-variant-toolbar';kind.className='sl-variant-kind';
    note.className='sl-variant-note';source.className='sl-variant-source';
    sourceLink.rel='noopener noreferrer';source.append(sourceLink);
    let selector,inspection;
    if(variants.length>1){
      const field=make('label'),caption=make('span','Formula representation');
      field.className='sl-variant-field';selector=make('select');selector.className='sl-variant-select';
      for(const [index,variant] of variants.entries()){
        const option=make('option',`${index+1}. ${variant.title||'Formula'} · ${variant.kind||'representation'}`);
        option.value=String(index);selector.append(option);
      }
      field.append(caption,selector);toolbar.append(field);
      selector.value=String(selected);
      selector.addEventListener('change',()=>{
        const index=Number(selector.value);
        if(!Number.isInteger(index)||index<0||index>=variants.length)return;
        selected=index;
        inspection?.invalidateShare();
        // Mutate the original source node so the shared MathJax controller can
        // replace its existing typeset pair without leaving stale formulas.
        formula.textContent=variants[index].expression;
        updateInformation();
        enhanceMath(detail);
      });
    }
    toolbar.append(kind);
    detail.insertBefore(toolbar,formula);
    const layout=make('div');layout.className='sl-formula-inspection-layout';
    detail.insertBefore(layout,formula);layout.append(formula);
    if(entry){
      inspection=inlineExactValues(entry,shared?.startPosition??initialPosition,Boolean(shared),()=>selected,variants.length);
      if(inspection){
        const inspector=inspection.panel;
        layout.append(inspector);
        inspector.addEventListener('toggle',()=>{layout.dataset.exactOpen=String(inspector.open);});
      }
    }
    detail.append(note,source);
    const raw=make('details'),rawSummary=make('summary','View original formula text'),pre=make('pre'),copy=make('button','Copy exact formula'),copyStatus=make('span');
    raw.className='sl-formula-raw';pre.className='sl-formula-source-text';pre.tabIndex=0;
    pre.setAttribute('role','region');pre.setAttribute('aria-label','Original exact formula text');
    copy.type='button';copyStatus.className='sl-source-copy-status';
    copyStatus.setAttribute('role','status');copyStatus.setAttribute('aria-live','polite');
    raw.append(rawSummary,pre,copy,copyStatus);detail.append(raw);
    let formulaCopyGeneration=0;
    copy.addEventListener('click',async()=>{
      const content=variants[selected].expression,generation=++formulaCopyGeneration;
      const current=()=>generation===formulaCopyGeneration&&raw.isConnected&&!raw.closest('details:not([open])');
      copyStatus.textContent='';
      try{
        if(!navigator.clipboard?.writeText)throw Error('Clipboard unavailable');
        await navigator.clipboard.writeText(content);
        if(!current())return;
        copyStatus.textContent='Exact formula copied.';
      }catch{
        if(!current())return;
        copyStatus.textContent='Clipboard unavailable. Select and copy the source text above.';
        raw.open=true;pre.focus();
      }
    });
    function updateInformation(){
      formulaCopyGeneration++;
      const item=variants[selected];
      kind.textContent=`${item.kind||'Representation'} · ${selected+1} of ${variants.length}`;
      const currentLabel=item.expression===definingExpression?'Defining formula':'Alternative formula';
      name.textContent=currentLabel;summary.setAttribute('aria-label',currentLabel+' for '+label);
      excerpt.textContent=item.expression.replace(/\s+/g,' ').trim();
      pre.textContent=item.expression;copyStatus.textContent='';
      note.textContent=typeof item.note==='string'?item.note:'';
      note.hidden=!note.textContent;
      source.hidden=true;
      if(typeof item.source==='string'&&item.source.trim()){
        try{
          const url=new URL(item.source,location.href);
          if(['https:','http:'].includes(url.protocol)){
            sourceLink.href=url.href;source.hidden=false;
          }
        }catch{/* Preserve the exact formula without an unsupported source URL. */}
      }
    }
    updateInformation();
  }
  detail.addEventListener('toggle',()=>{if(detail.open){mountVariants();enhanceMath(detail);}});
  if(detail.open)mountVariants();
  return detail;
}

function legacyDestination(){
  const onSearch=root?.dataset.page==='search',onResearch=root?.dataset.page==='research';
  if(!onSearch&&!onResearch)return null;
  let hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch{}
  const routes={
    transfers:'sequence-transfers.html',comparison:'sequence-compare.html',
    oeis:'sequence-oeis.html','research-families':'sequence-research.html',
    generalized:'sequence-research.html','research-graph':'sequence-connections.html',
    identify:'sequence-identify.html','modular-dynamics':'sequence-modular.html',
    'research-notebooks':'sequence-workspace.html','family-explorer':'sequence-research.html',
    'tr-matrices':'sequence-transfers.html','tr-convolution-witness':'sequence-transfers.html',
    'tr-compose':'sequence-transfers.html'
  };
  const params=new URL(location.href).searchParams;
  const combinedFamily=hash==='family-explorer'&&['q','scope','mode','paper','collection'].some(key=>params.has(key));
  const researchHashTarget={'research-graph':'sequence-connections.html',identify:'sequence-identify.html','modular-dynamics':'sequence-modular.html','research-notebooks':'sequence-workspace.html'};
  const target=onResearch?(researchHashTarget[hash]||(params.has('graph')?'sequence-connections.html':params.has('identify')?'sequence-identify.html':params.has('modular')?'sequence-modular.html':null)):
    combinedFamily?'sequence-workspace.html':
    (routes[hash]||(params.has('wb')?'sequence-compare.html':params.has('tr-source')?'sequence-transfers.html':params.has('graph')?'sequence-connections.html':params.has('identify')?'sequence-identify.html':params.has('modular')?'sequence-modular.html':params.has('notebook')?'sequence-workspace.html':null));
  if(!target)return null;
  const url=new URL(target,location.href);
  const defaultHash={
    'sequence-compare.html':'#comparison','sequence-transfers.html':'#transfers',
    'sequence-oeis.html':'#oeis','sequence-connections.html':'#research-graph',
    'sequence-identify.html':'#identify','sequence-modular.html':'#modular-dynamics',
    'sequence-workspace.html':'#research-notebooks','sequence-research.html':'#research-families'
  };
  url.search=location.search;url.hash=location.hash||defaultHash[target]||'#research-families';
  return url.href;
}
const legacyRoute=legacyDestination();
if(legacyRoute)location.replace(legacyRoute);
function comparisonHandoff(entries,snapshot){
  const link=sources=>{
    const target=new URL('sequence-compare.html',location.href);
    location.href=workbenchLink(target.href,sources,WORKBENCH_DEFAULTS);
  };
  return {
    addLocal(entry){link([localSource(entry,location.href)]);return true;},
    addReference(hit){link([referenceSource(hit,snapshot)]);return true;},
    addCustom(terms,title='Identification input',offset=0){link([customSource({terms,title,offset})]);return true;},
    addFamily(engine,params){link([familySource(engine,params,location.href)]);return true;}
  };
}
const collectionLabels={atlas:'Curated sequences',recovered:'Research archive',formulas:'Formula families'};
const keys=SEARCH_KEYS;
let results=[],page=0,applied={},workbench,transfers,toggleSaved,saved=new Set(),searchShareGeneration=0;
const RESULT_LAYOUT_KEY='komorebi.sequence-library-result-layout.v1';
function setResultLayout(layout,remember=false){
  const normalized=layout==='cards'?'cards':'compact',buttons=root.querySelectorAll('#sl-result-layout [data-layout]');
  $('results').dataset.layout=normalized;
  for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.layout===normalized));
  if(remember){try{localStorage.setItem(RESULT_LAYOUT_KEY,normalized);}catch{/* The choice still applies to this page. */}}
}

function save(content,type,name){const url=URL.createObjectURL(new Blob([content],{type})),link=make('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function share(){const url=new URL(location.href);url.search='';for(const [key,value]of Object.entries(applied))if(value&&value!=='any'&&value!=='relevance')url.searchParams.set(key,value);if(page)url.searchParams.set('page',String(page+1));url.hash='library-search';return url.href;}
function invalidateSearchShare(){
  searchShareGeneration++;
  $('link-wrap').hidden=true;$('link').value='';$('action-status').textContent='';
}
function render(){
  invalidateSearchShare();
  clearMath($('results'));$('results').replaceChildren();page=Math.max(0,Math.min(page,Math.ceil(results.length/24)-1));
  const expandFormulas=results.length<=3;
  for(const hit of results.slice(page*24,(page+1)*24)){
    const entry=hit.entry;
    if(entry.collection==='generalized'){
      const li=make('li'),heading=make('h3'),link=make('a',entry.title),formula=make('p',entry.formula),actions=make('div');
      li.dataset.resultId=entry.id;li.className='sl-family-result';link.href=entry.url;heading.append(link);formula.className='sar-formula';actions.className='sp-actions';
      const identifier=make('p',entry.id),mode=make('span',entry.mode),domain=make('p'),sourceNote=make('p',entry.paper_title);
      identifier.className='sar-kicker';mode.className='sl-result-badge';sourceNote.className='sl-family-source';domain.append(make('strong','Parameters: '),document.createTextNode(entry.domain));
      const explore=make('a',entry.engine?'Explore parameters':entry.examples?.length?'Read construction and examples':'Read definition and source');explore.href=entry.url+(entry.engine?'#family-explorer':'#definition');
      const source=make('a','Defining source');source.href=entry.source;actions.append(explore,source);
      if(entry.record_ids.length){const members=make('a','Search '+entry.record_ids.length+' integer record'+(entry.record_ids.length===1?'':'s'));members.href='sequence-library.html?q='+encodeURIComponent('family:'+entry.id)+'#library-search';actions.append(members);}
      const overview=make('div');overview.className='sl-result-main';overview.append(identifier,heading,mode,sourceNote,domain,make('p',entry.note));
      li.append(overview,definitionPreview(formula,entry.title,expandFormulas),actions);$('results').append(li);continue;
    }
    const li=make('li'),label=make('p',entry.id+' / '+(collectionLabels[entry.collection]||'Sequence library'));label.className='sar-kicker';const heading=make('h3'),link=make('a',entry.title),overview=make('div');overview.className='sl-result-main';link.href=entry.url;heading.append(link);overview.append(label,heading,make('p',entry.kind+' · '+entry.formulas.length+' representation'+(entry.formulas.length===1?'':'s')+' · first index '+entry.offset));li.append(overview);
    li.dataset.resultId=entry.id;if(entry.triangle){const tableNote=make('p',`${entry.triangle.row_lengths.length} complete rows · row/column inspection · ${entry.terms.length} exact coefficients`);tableNote.className='sl-match-reason';overview.append(tableNote);}
    const expression=make('p',entry.formula);expression.className='sar-formula';li.append(definitionPreview(expression,entry.title,expandFormulas,entry.formulas,entry,hit.termMatch?.start||0));
    const start=hit.termMatch?Math.max(0,hit.termMatch.start-(hit.termMatch.length<8?1:0)):0,count=Math.min(Math.max(6,hit.termMatch?.length||0),8),values=entry.terms.slice(start,start+count),symbol=entry.index_symbol||'n';
    const excerpt=make('div'),caption=make('p',`${symbol} = ${entry.offset+start}–${entry.offset+start+values.length-1} · exact stored terms`),terms=make('div');excerpt.className='sl-term-preview';caption.className='sl-term-caption';terms.className='sl-term-values';terms.tabIndex=0;terms.setAttribute('role','region');terms.setAttribute('aria-label',`Exact term preview for ${entry.id}`);
    values.forEach((value,i)=>{if(i)terms.append(document.createTextNode(', '));const relative=start+i-(hit.termMatch?.start??-1),matched=hit.termMatch&&relative>=0&&relative<hit.termMatch.length&&hit.termMatch.pattern[relative]!==null;const item=make(matched?'mark':'span',value);item.title=`${symbol}=${entry.offset+start+i}`;terms.append(item);});excerpt.append(caption,terms);li.append(excerpt);
    if(hit.termMatch){const reason=make('p',hit.reason);reason.className='sl-match-reason';overview.append(reason);}
    const review=make('p',entry.status);review.className='sl-result-status';overview.append(review);
    if(entry.tags.includes('hypergeometric')){const badge=make('span','Hypergeometric representation');badge.className='sl-result-badge';overview.append(badge);}
    const links=make('div'),plot=make('a','Plot and inspect'),formulas=make('a','Read formulas'),bookmark=make('button'),compare=make('button','Add to comparison');links.className='sp-actions';plot.href=entry.url+(entry.collection==='atlas'?'#analysis':'#plot');formulas.href=entry.url+(entry.collection==='recovered'?'#definition':'#formulas');bookmark.type=compare.type='button';bookmark.dataset.saveSequence=entry.id;bookmark.addEventListener('click',()=>toggleSaved(entry.id));compare.setAttribute('aria-label','Add '+entry.id+' to comparison');compare.addEventListener('click',()=>{if(workbench)workbench.addLocal(entry);else comparisonHandoff([],null).addLocal(entry);});links.append(plot,bookmark,compare);
    if(entry.calculator_url){
      const calculate=make('a','Calculate exact');
      calculate.href=entry.calculator_url;
      calculate.setAttribute('aria-label','Recalculate exact integer values for '+entry.id);
      links.append(calculate);
    }
    li.append(links);
    const more=make('details'),moreSummary=make('summary',entry.match_count?`More actions · ${entry.match_count.toLocaleString()} OEIS match${entry.match_count===1?'':'es'}`:'More actions'),secondary=make('div');
    more.className='sl-result-more';more.open=results.length<=3;secondary.className='sp-actions';secondary.append(formulas);
    if(entry.closed_form_collection){
      const proof=make('a','Research definitions and proofs');
      proof.href='sequence-closed-forms.html#closed-theorems';
      secondary.append(proof);
    }
    more.append(moreSummary,secondary);li.append(more);
    if(!entry.triangle&&entry.id!=='KOM084'){const transfer=make('button','Build a transfer');transfer.type='button';transfer.addEventListener('click',()=>{if(transfers)transfers.source(entry);else{const url=new URL('sequence-transfers.html',location.href);url.searchParams.set('tr-source',entry.id);url.hash='transfers';location.href=url.href;}});secondary.append(transfer);}
    const comparisons=make('details'),summary=make('summary',entry.oeis_checked===false?'OEIS bulk comparison pending':`OEIS comparisons (${entry.match_count.toLocaleString()} ${entry.match_count===1?'match':'matches'})`);comparisons.className='sl-matches';comparisons.append(summary);
    if(entry.oeis_checked===false){
      if(entry.source_claimed_oeis&&entry.oeis){
        const sourceNote=make('p','The source identifies this sequence as ');
        const identified=make('a',entry.oeis);identified.href='https://oeis.org/'+entry.oeis;
        sourceNote.append(identified,document.createTextNode('. This identification has not been rechecked against the pinned bulk snapshot.'));
        comparisons.append(sourceNote);
      }
      comparisons.append(make('p','This record has not been compared with the retained OEIS snapshot. Neither a match nor an exclusion is claimed.'));
    }else if(entry.matches.length){const list=make('ol');for(const hit of entry.matches.slice(0,3)){const item=make('li'),reference=make('a',hit.id+' · '+hit.name);reference.href='https://oeis.org/'+hit.id;item.append(reference,make('p',`${hit.matched_terms} matching terms, beginning at local index ${entry.offset}. OEIS export position: ${hit.position}.`));list.append(item);}comparisons.append(list,make('p',`Showing ${Math.min(3,entry.matches.length)} of ${entry.match_count.toLocaleString()} recorded matches. Up to 50 matches are retained.`));}else comparisons.append(make('p','No contiguous match of eight terms was recorded. That does not establish novelty.'));
    if(entry.oeis_checked===true&&entry.oeis_prefix_note)comparisons.append(make('p',entry.oeis_prefix_note));
    const credit=make('p','Finite matches do not prove that infinite sequences are identical. Export positions are not mathematical offsets. Reference data: '),oeis=make('a','The Online Encyclopedia of Integer Sequences'),license=make('a','CC BY-SA 4.0');oeis.href='https://oeis.org/';license.href='https://creativecommons.org/licenses/by-sa/4.0/';credit.append(oeis,document.createTextNode(' · '),license);comparisons.append(credit);more.append(comparisons);$('results').append(li);
  }
  for(const definition of $('results').querySelectorAll('.sl-result-definition[open]'))enhanceMath(definition);
  const active=$('active-filters');active.replaceChildren();
  const names={collection:'Collection',kind:'Family',representation:'Formula type',status:'Review status',hits:'OEIS comparisons',saved:'Saved entries',match:'Term matching',mode:'Construction type',paper:'Source'};
  for(const key of Object.keys(names))if(applied[key]&&!(key==='match'&&applied[key]==='any')){const field=$(key),text=Array.from(field.options).find(option=>option.value===applied[key])?.textContent||applied[key],button=make('button',`${names[key]}: ${text} ×`);button.type='button';button.className='sl-filter-chip';button.setAttribute('aria-label',`Clear ${names[key].toLowerCase()} filter`);button.addEventListener('click',()=>{field.value=key==='match'?'any':'';field.dispatchEvent(new Event('change'));$('count').focus({preventScroll:true});});active.append(button);}
  root.querySelectorAll('[data-scope]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.scope===(applied.scope||'records'))));
  const familyScope=applied.scope==='families';
  $('search').querySelector('.sl-collections').hidden=familyScope;
  for(const key of RECORD_FILTERS){$(key).disabled=familyScope;$(key).closest('label').hidden=familyScope;}
  for(const key of FAMILY_FILTERS){$(key).disabled=!familyScope;$(key).closest('label').hidden=!familyScope;}
  for(const key of ['saved-status','research','triangles','generalized','help'])$(key).hidden=familyScope;
  $('family-help').hidden=$('family-summary').hidden=!familyScope;
  $('query-label').textContent=familyScope?'Name, construction, family ID, or source':'Name, formula, identifier, or exact terms';
  $('query').placeholder=familyScope?'Try Hankel, theta, or paper:SF-VI':'Try hypergeometric, j:1 r:2, or 1, 1, 69';
  $('query').setAttribute('aria-describedby',(familyScope?'sl-family-help':'sl-help')+' sl-error');
  $('empty').hidden=results.length!==0;
  $('export').disabled=results.length===0;
  root.querySelectorAll('[data-collection]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.collection===applied.collection)));
  updateSaveButtons($('results'),saved);$('results').start=page*24+1;$('count').textContent=`${results.length.toLocaleString()} matching ${familyScope?'famil'+(results.length===1?'y':'ies'):'record'+(results.length===1?'':'s')}. ${results.length?`Showing ${page*24+1}–${Math.min(results.length,(page+1)*24)}.`:applied.saved?'Save records from any collection to view them here.':familyScope?'Try a different construction or source, or remove a filter.':'Try fewer words or another formula type.'}`;$('page').textContent=`Page ${page+1} of ${Math.max(1,Math.ceil(results.length/24))}`;$('previous').disabled=page===0;$('next').disabled=(page+1)*24>=results.length;$('pages').hidden=results.length<=24;
}
function setupSearch(entries,families,sources=[]){
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)},allowed=new Set(entries.map(e=>e.id)),loaded=readSaved(storage,allowed);saved=new Set(loaded.ids);
  const label=make('label','Saved entries'),select=make('select');select.id='sl-saved';label.htmlFor=select.id;for(const [value,text]of [['','All entries'],['only','Saved in this browser']]){const option=make('option',text);option.value=value;select.append(option);}label.append(select);$('search').querySelector('.sar-controls').append(label);
  const modes=[...new Set(families.map(f=>f.mode))],papers=new Map(sources.map(source=>[source.id,source.title]));
  for(const family of families)for(const id of family.paper_refs)if(id===family.paper||!papers.has(id))papers.set(id,id===family.paper?family.paper_title:id);
  for(const [key,title,choices]of [['mode','Construction type',[['','All construction types'],...modes.map(mode=>[mode,mode])]],['paper','Source',[['','All sources'],...Array.from(papers).sort(([a],[b])=>a.localeCompare(b))]]]){
    const fieldLabel=make('label',title),field=make('select');field.id='sl-'+key;fieldLabel.htmlFor=field.id;
    for(const [value,text]of choices){const option=make('option',text);option.value=value;field.append(option);}
    fieldLabel.append(field);$('search').querySelector('.sar-controls').append(fieldLabel);
  }
  const modeCounts=modes.map(mode=>{const count=families.filter(f=>f.mode===mode).length,label=mode.toLowerCase();return `${count} ${count===1?label:label.endsWith('family')?label.slice(0,-1)+'ies':label+'s'}`;});
  $('family-summary').textContent=`${families.length} indexed constructions: ${modeCounts.join(' · ')}. Select a construction to read its definition, examples, and sources.`;
  const note=make('p',loaded.available?'Save up to 500 records from any collection in this browser.':'Saved entries could not be loaded from this browser. You can still save records for this session.');note.id='sl-saved-status';note.setAttribute('role','status');$('search').append(note);
  const params=new URL(location.href).searchParams;for(const key of keys){const control=$(key==='q'?'query':key);if(params.has(key))control.value=params.get(key);}page=Math.max(0,(Number(params.get('page'))||1)-1);
  let hasSuccessfulSearch=false;
  const resultState=make('p');resultState.id='sl-result-state';resultState.className='sl-result-state';
  resultState.hidden=true;resultState.setAttribute('role','status');resultState.setAttribute('aria-live','polite');resultState.setAttribute('aria-atomic','true');
  $('count').after(resultState);
  function run(update=false,focusError=false){
    const state=normalizeSearch(Object.fromEntries(keys.map(key=>[key,$(key==='q'?'query':key).value])));
    let nextResults;
    try{nextResults=librarySearch(entries,families,state,saved);}
    catch(error){
      invalidateSearchShare();
      if(!hasSuccessfulSearch)applied=emptySearch(state.scope);
      for(const key of keys.filter(key=>key!=='q'))$(key).value=applied[key];
      if(!hasSuccessfulSearch){
        results=[];page=0;render();
        $('count').textContent='Search not applied.';$('empty').hidden=true;
      }
      $('error').textContent=error.message;$('error').hidden=false;
      $('query').setAttribute('aria-invalid','true');$('query').setAttribute('aria-errormessage','sl-error');
      resultState.textContent=hasSuccessfulSearch?'Showing the previous successful search. Correct the highlighted query and search again.':'No search results yet. Correct the highlighted query and search again.';
      resultState.hidden=false;$('share').disabled=!hasSuccessfulSearch;
      if(focusError)$('query').focus();
      return false;
    }
    for(const key of keys)$(key==='q'?'query':key).value=state[key];
    results=nextResults;applied=state;hasSuccessfulSearch=true;if(update)page=0;
    render();$('error').hidden=true;$('query').removeAttribute('aria-invalid');$('query').removeAttribute('aria-errormessage');
    resultState.hidden=true;resultState.textContent='';$('share').disabled=false;
    if(update)history.replaceState(null,'',share());
    return true;
  }
  function reset(scope=$('scope').value){const state=emptySearch(scope);for(const key of keys)$(key==='q'?'query':key).value=state[key];}
  function refreshSavedResults(){
    if(hasSuccessfulSearch&&applied.saved){
      const hadResultFocus=$('results').contains(document.activeElement);
      results=librarySearch(entries,families,applied,saved);render();
      if(hadResultFocus)$('count').focus({preventScroll:true});
    }else updateSaveButtons($('results'),saved);
  }
  toggleSaved=id=>{const next=new Set(saved);if(next.has(id))next.delete(id);else if(next.size>=500){note.textContent='You have 500 saved records. Remove one before saving another.';return;}else next.add(id);saved=next;const stored=writeSaved(storage,[...saved],allowed);note.textContent=(saved.has(id)?id+' saved.':id+' removed from saved entries.')+(stored?'':' Browser storage is unavailable. This change lasts only for this session.');refreshSavedResults();};
  $('count').tabIndex=-1;for(const key of keys.filter(key=>key!=='q'))$(key).addEventListener('change',()=>run(true));
  for(const button of root.querySelectorAll('[data-scope]'))button.addEventListener('click',()=>{$('scope').value=button.dataset.scope;run(true);});
  $('generalized').addEventListener('click',()=>{reset('families');run(true);$('count').focus({preventScroll:true});$('count').scrollIntoView({block:'start'});});
  for(const button of root.querySelectorAll('[data-collection]'))button.addEventListener('click',()=>{$('collection').value=button.dataset.collection;run(true);});
  window.addEventListener('storage',event=>{if(event.key===STORAGE_KEY||event.key===null){saved=new Set(readSaved(storage,allowed).ids);refreshSavedResults();}});
  const layoutControls=$('result-layout');
  if(layoutControls){
    let selected='compact';try{selected=localStorage.getItem(RESULT_LAYOUT_KEY)==='cards'?'cards':'compact';}catch{}
    setResultLayout(selected);
    for(const button of layoutControls.querySelectorAll('[data-layout]'))button.addEventListener('click',()=>{
      setResultLayout(button.dataset.layout,true);
    });
    layoutControls.hidden=false;
  }
  $('query').addEventListener('input',invalidateSearchShare);
  $('search').hidden=false;$('search').addEventListener('submit',event=>{event.preventDefault();run(true,true);});
  function clear(){reset();run(true);$('query').focus();}
  $('clear').addEventListener('click',clear);$('reset').addEventListener('click',clear);
  $('triangles').hidden=false;$('triangles').addEventListener('click',()=>{reset('records');$('query').value='tag:triangle';run(true);$('count').focus();$('count').scrollIntoView({block:'start'});});
  $('research').hidden=false;$('research').addEventListener('click',()=>{reset('records');$('query').value='tag:research-derived';run(true);$('count').focus();$('count').scrollIntoView({block:'start'});});
  for(const [key,step]of [['previous',-1],['next',1]])$(key).addEventListener('click',()=>{page+=step;render();history.replaceState(null,'',share());$('count').focus({preventScroll:true});$('count').scrollIntoView({block:'nearest'});});
  $('share').addEventListener('click',async()=>{
    if(!hasSuccessfulSearch)return;
    const url=share(),generation=++searchShareGeneration;
    try{
      if(!navigator.clipboard?.writeText)throw Error('Clipboard unavailable');
      await navigator.clipboard.writeText(url);
      if(generation!==searchShareGeneration)return;
      $('link-wrap').hidden=true;$('link').value='';$('action-status').textContent='Search link copied.';
    }catch{
      if(generation!==searchShareGeneration)return;
      $('link-wrap').hidden=false;$('link').value=url;
      $('action-status').textContent='Clipboard unavailable. Select and copy the search link.';
      $('link').focus();$('link').select();
    }
  });
  $('export').addEventListener('click',()=>save(librarySearchCSV(results,applied.scope,location.href),'text/csv;charset=utf-8',applied.scope==='families'?'family-definitions.csv':'sequence-search-results.csv'));
  run();
  function validate(value){if(!value||typeof value.q!=='string'||!['records','families'].includes(value.scope||'records'))throw Error('Choose valid saved search settings.');searchEntries(value.scope==='families'?families:entries,value.q);for(const key of keys.filter(k=>k!=='q'))if(value[key]!==undefined&&!Array.from($(key).options).some(o=>o.value===value[key]))throw Error('A saved search filter is unavailable: '+key);if(value.page!==undefined&&(!Number.isSafeInteger(value.page)||value.page<0||value.page>10000))throw Error('The saved search page is invalid.');return value;}
  return {snapshot:()=>({...applied,page}),validate,restore(value){validate(value);for(const key of keys)$(key==='q'?'query':key).value=value[key]??(key==='scope'?'records':key==='sort'?'relevance':key==='match'?'any':'');page=value.page||0;run();}};
}
function setupTriangleNavigation(){
  const table=root.querySelector('#triangle table');if(!table)return;
  const rows=[...table.tBodies[0].rows].map(row=>[...row.querySelectorAll('td a')]);
  const all=rows.flat();let active=all[0];
  for(const [n,row]of rows.entries())for(const [k,link]of row.entries()){
    const exact=link.textContent,digits=exact.replace('-',''),spoken=digits.length>60?`${exact.startsWith('-')?'negative ':''}${digits.length} digits, beginning with ${digits.slice(0,12)}, ending with ${digits.slice(-8)}`:exact;
    link.tabIndex=link===active?0:-1;link.setAttribute('aria-label',`Row ${n}, column ${k}; coefficient ${spoken}`);
    link.addEventListener('focus',()=>{if(active)active.tabIndex=-1;active=link;link.tabIndex=0;});
    link.addEventListener('keydown',event=>{
      let r=n,c=k;if(event.key==='ArrowDown')r=Math.min(rows.length-1,n+1);else if(event.key==='ArrowUp')r=Math.max(0,n-1);else if(event.key==='ArrowRight')c=Math.min(row.length-1,k+1);else if(event.key==='ArrowLeft')c=Math.max(0,k-1);else if(event.key==='Home'){r=event.ctrlKey?0:n;c=0;}else if(event.key==='End'){r=event.ctrlKey?rows.length-1:n;c=rows[r].length-1;}else return;
      event.preventDefault();rows[r][Math.min(c,rows[r].length-1)].focus();
    });
  }
  root.querySelector('.sl-triangle-help').hidden=false;table.dataset.keyboardReady='true';
}
function setupReference(client){
  if(!globalThis.Worker){$('oeis-status').textContent='Interactive OEIS search is unavailable in this browser. You can still download the reference data and browse entry comparisons.';return;}
  $('oeis-form').hidden=false;
  const busy=value=>{$('oeis-search').disabled=value;$('oeis-cancel').disabled=!value;};
  $('oeis-form').addEventListener('submit',async event=>{
    event.preventDefault();try{referenceQuery($('oeis-query').value);}catch(error){$('oeis-status').textContent=error.message;return;}
    busy(true);$('oeis-status').textContent='Loading OEIS reference data and searching in this browser…';root.dataset.referenceReady='false';
    try{
      const data=await client.search($('oeis-query').value,message=>{$('oeis-status').textContent=message;});
      $('oeis-results').replaceChildren();for(const hit of data.results){
        const li=make('li'),link=make('a',hit.id+' · '+(hit.name||'Name not recorded'));link.href='https://oeis.org/'+hit.id;
        li.append(link,make('p',hit.position===null?'Terms from the exported excerpt; its mathematical offset is not included.':`Pattern at excerpt position ${hit.position}; ${hit.matched_terms} pattern positions (${hit.known_terms} known integers); ${hit.positions} matching position(s) in this excerpt.`));
        const values=make('p',(hit.values||[]).join(', '));values.className='sar-formula';li.append(values);
        if(hit.values?.length){const compare=make('button','Add excerpt to comparison');compare.type='button';compare.setAttribute('aria-label','Compare '+hit.id+' excerpt');compare.addEventListener('click',()=>{if(workbench)workbench.addReference(hit);else comparisonHandoff([],root.dataset.oeisSnapshot||'').addReference(hit);});li.append(compare);}
        $('oeis-results').append(li);
      }
      $('oeis-status').textContent=`Matching OEIS records: ${data.total.toLocaleString()}. Showing ${data.results.length}. Results use reference terms and names only. ${data.query_type==='terms'?'Finite matching does not prove sequence identity.':''}`;root.dataset.referenceReady='true';
    }catch(error){$('oeis-status').textContent=error.message;}finally{busy(false);}
  });
  $('oeis-cancel').addEventListener('click',()=>client.cancel());
}
if(!legacyRoute)try{
  if(root.dataset.entry){const [{setupArchivePlot},{mountTriangleExplorer}]=await Promise.all([import('./sequence-archive-plot.mjs'),import('./sequence-triangle.mjs')]);const response=await fetch(new URL(root.dataset.entry,location.href));if(!response.ok)throw Error('The exact record could not be loaded.');const entry=await response.json();setupArchivePlot(entry);setupTriangleNavigation();mountTriangleExplorer(entry,root.querySelector('#triangle'));}
  else if(root.dataset.page==='oeis'){
    const response=await fetch(new URL('./sequence-oeis-meta.json',import.meta.url));
    if(!response.ok)throw Error('The local OEIS reference metadata could not be loaded.');
    const metadata=await response.json();
    if(!/^[0-9a-f]{64}$/.test(metadata.stripped_sha256||''))throw Error('The OEIS reference identifier is invalid.');
    root.dataset.oeisSnapshot=metadata.stripped_sha256;
    setupReference(createReferenceClient());
  }
  else if($('search')||root.querySelector('#family-explorer-controls')||root.querySelector('#sr-transfer-tool')||root.querySelector('#comparison')||root.querySelector('#sl-oeis-form')||root.querySelector('#research-families')||['connections','identify','modular'].includes(root.dataset.page)){
    const responses=await Promise.all([fetch(new URL('./sequence-library-data.json',import.meta.url)),fetch(new URL('./sequence-generalized-data.json',import.meta.url))]);
    if(responses.some(r=>!r.ok))throw Error('The local sequence and family catalogue could not be loaded.');
    const [data,generalized]=await Promise.all(responses.map(r=>r.json()));
    const entries=familySearchEntries(data.entries,generalized.families),client=createReferenceClient();
    const snapshot=data.snapshot.stripped_sha256,handoff=comparisonHandoff(entries,snapshot);
    root.dataset.oeisSnapshot=snapshot;
    if(root.querySelector('#comparison:not(.sl-legacy-gateway)')){const {mountWorkbench}=await import('./sequence-workbench.mjs');workbench=mountWorkbench({root,entries,snapshot,referenceClient:client});}
    if(root.querySelector('#sr-transfer-tool')){const {mountTransfers}=await import('./sequence-transfers.mjs');transfers=mountTransfers(entries,document.getElementById('sr-transfer-tool'));}
    let search;
    if($('search'))search=setupSearch(entries,generalized.families,generalized.sources);
    if($('oeis-form'))setupReference(client);
    if(root.querySelector('#family-explorer-controls')||['research','workspace','connections','identify','modular'].includes(root.dataset.page)){
      const {mountStudio}=await import('./sequence-research-studio.mjs');mountStudio({root,entries,data:generalized,referenceClient:client,workbench:workbench||handoff,transfers,search});
    }
  }
  // The central Search desk and focused Closed Forms page share one
  // calculator. The mathematical core loads only when the disclosure opens.
  const disclosure=root.querySelector('#closed-calculator-panel');
  const target=root.querySelector('#closed-calculator-root');
  if(disclosure&&target){
    let loaded=false;
    async function loadCalculator(){
      if(loaded||!disclosure.open)return;
      loaded=true;
      try{
        const {mountClosedFormsCalculator}=await import('./sequence-closed-forms-ui.mjs');
        mountClosedFormsCalculator(target,{href:location.href});
      }catch(error){
        loaded=false;
        const note=make('p','The exact calculator could not start: '+error.message+
          '. Source definitions and static exact tables remain available.');
        note.setAttribute('role','status');target.replaceChildren(note);
      }
    }
    disclosure.addEventListener('toggle',()=>{void loadCalculator();});
    if(new URL(location.href).searchParams.has('cf-version')){
      disclosure.open=true;
      await loadCalculator();
    }
  }
  root.dataset.libraryReady='true';
}catch(error){const note=make('p',error.message+' Static definitions and the complete index remain available.');note.setAttribute('role','status');root.prepend(note);}
