import {WORKBENCH_DEFAULTS,validateWorkbench,localSource,referenceSource,workbenchRows,agreements,readWorkbenchLink,workbenchLink,comparisonCSV} from './sequence-workbench-core.mjs';
import {mountPlotOptions,plotColors,plotHeight,showIndexLabel,mergePlotLabels,finishPlotTheme,exportPlot} from './sequence-plot-options.mjs';

const node=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
const svg=(tag,attrs={},text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value]of Object.entries(attrs))el.setAttribute(key,value);if(text!==undefined)el.textContent=text;return el;};
const short=(value,max=60)=>value.length>max?value.slice(0,max-1)+'…':value;
export function mountWorkbench({root,entries,snapshot,referenceClient}){
  const section=root.querySelector('#comparison')||node('section');section.id='comparison';section.className='sw-workbench';
  section.innerHTML=`<p class="sar-kicker">Comparison workbench</p><h2 id="sw-heading" tabindex="-1">Compare sequences</h2>
    <p>Add up to four records from the search results or OEIS finder. Compare exact terms, differences, partial sums, and residues. Each line has its own mark and pattern as well as a color.</p>
    <p id="sw-status" role="status" aria-live="polite"></p><ol id="sw-sources" class="sw-sources"></ol>
    <div class="sp-actions"><button type="button" id="sw-example">Try Fibonacci + Lucas</button><button type="button" id="sw-clear">Clear comparison</button></div>
    <div id="sw-restore" hidden><p>Shared OEIS excerpts require the reference data, about 39.8 MiB on first use. Nothing downloads until you choose to load it. Mathematical offsets are absent from these exports.</p><div class="sp-actions"><button type="button" id="sw-load">Load OEIS excerpts</button><button type="button" id="sw-cancel" disabled>Cancel loading</button></div></div>
    <form id="sw-form"><div class="sar-controls">
    <label for="sw-view">View<select id="sw-view"><option value="values">Integer values</option><option value="mod">Residues modulo m</option></select></label>
    <label for="sw-transform">Transformation<select id="sw-transform"><option value="raw">Original terms</option><option value="difference">First differences</option><option value="sum">Partial sums</option></select></label>
    <label for="sw-scale">Value scale<select id="sw-scale"><option value="signed-log">Signed logarithm</option><option value="linear">Linear</option></select></label>
    <label for="sw-alignment">Align by<select id="sw-alignment"><option value="positions">Window position · start together</option><option value="indices">Recorded local index</option></select></label>
    <label for="sw-skip">Skip stored terms<input id="sw-skip" type="number" min="0" max="1000000" step="1" value="0" required></label>
    <label for="sw-count">Terms per series<input id="sw-count" type="number" min="1" max="1000" step="1" value="32" required></label>
    <label for="sw-modulus">Modulus m<input id="sw-modulus" type="number" min="2" max="1000000" step="1" value="7" required></label>
    <label for="sw-marks">Marks<select id="sw-marks"><option value="line">Points and lines</option><option value="points">Points only</option></select></label>
    </div><button type="submit">Update comparison</button><p id="sw-error" role="alert" hidden></p></form>
    <p id="sw-conventions">Windows count from each stored prefix, without extrapolation. Partial sums include all earlier stored terms; differences use the preceding stored term. Position alignment pairs window positions and does not assert equal mathematical indices.</p>
    <div id="sw-appearance"></div><p id="sw-summary"></p><div id="sw-chart" class="sw-chart"></div>
    <p id="sw-inspector" class="sw-inspector" role="status">Focus a plotted point to inspect its exact integer. Left/right moves along a series; up/down switches series; Home/End moves to an endpoint.</p>
    <div id="sw-agreements"></div><div class="sp-actions"><button type="button" id="sw-share">Copy comparison link</button><button type="button" id="sw-csv">Export exact CSV</button><button type="button" id="sw-svg">Export SVG</button><button type="button" id="sw-png">Export PNG</button></div>
    <label id="sw-link-wrap" for="sw-link" hidden>Copy this comparison link<input id="sw-link" readonly></label>
    <details id="sw-data"><summary>Exact comparison table</summary><div class="sar-scroll" role="region" aria-label="Exact comparison values" tabindex="0"><table><caption>Stored indices and displayed exact integers</caption><thead><tr><th scope="col">Series</th><th scope="col">Index convention</th><th scope="col">Index / position</th><th scope="col">Window position</th><th scope="col">Original integer</th><th scope="col">Displayed integer</th></tr></thead><tbody></tbody></table></div></details>`;
  root.querySelector('#oeis').before(section);
  const $=id=>section.querySelector('#sw-'+id);let sources=[],state={...WORKBENCH_DEFAULTS},result=null,activeKey=null;
  const say=text=>{$('status').textContent=text;},fail=error=>{$('error').textContent=error.message;$('error').hidden=false;};
  try{const linked=readWorkbenchLink(location.href,entries,snapshot);if(linked){sources=linked.sources;state=linked.state;}}catch(error){fail(error);}
  const fields=Object.keys(WORKBENCH_DEFAULTS);for(const key of fields)$(key).value=state[key];
  const appearance=mountPlotOptions({host:$('appearance'),prefix:'sw',onChange:()=>draw()});
  function draw(){
    $('chart').replaceChildren();$('agreements').replaceChildren();$('data').querySelector('tbody').replaceChildren();
    const pending=sources.some(s=>s.pending),ready=sources.length&&!pending;
    for(const key of ['csv','svg','png','share'])$(key).disabled=!ready;
    if(!ready){result=null;$('summary').textContent=pending?'Load or remove the pending reference excerpts to draw this comparison.':'Choose Add to comparison on any local result, or try the example.';$('inspector').textContent='Exact point values will appear here.';return;}
    try{result=workbenchRows(sources,state);}catch(error){fail(error);return;}
    const colors=plotColors(appearance.state),theme=appearance.state,chart=$('chart'),width=Math.max(280,chart.clientWidth),height=plotHeight(width,theme),mobile=width<560,left=mobile?49:68,right=18,top=62+sources.length*14,bottom=height-(sources.some(s=>s.type==='oeis')?94:65),plotWidth=width-left-right;
    const all=result.series.flatMap(s=>s.rows),points=all.filter(r=>r.y!==null&&Number.isFinite(r.y));
    for(const {source,rows}of result.series)for(const row of rows){const tr=node('tr');for(const value of [source.id,source.indexKind,row.index,row.position,row.raw,row.value??'undefined'])tr.append(node('td',String(value)));$('data').querySelector('tbody').append(tr);}
    const checks=agreements(result);if(checks.length){$('agreements').append(node('h3',state.view==='mod'?`Finite residue agreements · mod ${state.modulus}`:'Finite exact agreements'),node('p','Compared with the first selected series over overlapping displayed positions. These finite comparisons do not prove infinite sequence identity.'));const list=node('ul');for(const check of checks){const source=sources.find(s=>s.key===check.source);list.append(node('li',`${source.id}: ${check.equal} of ${check.compared} displayed integers agree.`+(check.firstMismatch?` First difference at ${state.alignment==='positions'?'window position':'local index'} ${check.firstMismatch.x}.`:'')));}$('agreements').append(list);}
    if(!points.length){$('svg').disabled=$('png').disabled=true;$('summary').textContent='No plottable points in this window. Reduce the skip, choose another transformation, or use the signed logarithm for very large integers. Exact stored values remain in the table and CSV.';return;}
    let xmin=Math.min(...points.map(r=>r.x)),xmax=Math.max(...points.map(r=>r.x)),ymin=Math.min(...points.map(r=>r.y)),ymax=Math.max(...points.map(r=>r.y));
    if(state.view==='mod'){ymin=0;ymax=state.modulus-1;}else if(theme.baseline==='zero'){ymin=Math.min(ymin,0);ymax=Math.max(ymax,0);}if(xmin===xmax){xmin-=.5;xmax+=.5;}if(ymin===ymax){ymin=Math.min(0,ymin);ymax=Math.max(0,ymax);if(ymin===ymax){ymin=-1;ymax=1;}}
    const normalizer=Math.max(1,Math.abs(ymin),Math.abs(ymax)),lo=ymin/normalizer,hi=ymax/normalizer;
    const x=value=>left+(value-xmin)/(xmax-xmin)*plotWidth,y=value=>bottom-(value/normalizer-lo)/(hi-lo)*(bottom-top),picture=svg('svg',{viewBox:`0 0 ${width} ${height}`,role:'group','aria-labelledby':'sw-chart-title sw-chart-desc'});
    picture.append(svg('title',{id:'sw-chart-title'},state.view==='mod'?`Sequence residues modulo ${state.modulus}`:'Exact sequence comparison'),svg('desc',{id:'sw-chart-desc'},'Finite stored terms. Focus a point for its exact value. Arrow keys navigate. A full HTML table follows the chart.'),svg('rect',{width,height,fill:'#fafaf5'}));
    picture.append(svg('text',{x:left,y:23,'font-size':mobile?12:15,'font-weight':600},state.view==='mod'?`Residues mod ${state.modulus} · ${state.transform}`:`${state.transform} · ${state.scale==='signed-log'?'sgn(v) log10(1+|v|)':'linear scale'}`));
    result.series.forEach(({source},i)=>{const text=svg('text',{x:left,y:45+i*14,'font-size':11},short(`${i+1}. ${source.id} · ${source.title}`,Math.floor((width-left-right)/7)));text.append(svg('title',{},source.title));picture.append(text);picture.append(svg('line',{x1:left-24,x2:left-5,y1:41+i*14,y2:41+i*14,stroke:colors[i],'stroke-width':theme.width,'stroke-dasharray':['','7 4','2 4','9 3 2 3'][i]}));});
    const yticks=state.view==='mod'?[...new Set(Array.from({length:Math.min(state.modulus,5)},(_,i)=>Math.round(i*(state.modulus-1)/(Math.min(state.modulus,5)-1))))]:Array.from({length:5},(_,i)=>(lo+(hi-lo)*i/4)*normalizer);
    for(const tick of yticks){if(theme.grid==='on')picture.append(svg('line',{x1:left,x2:width-right,y1:y(tick),y2:y(tick),stroke:'#d9dfd4','data-plot-grid':'true'}));picture.append(svg('text',{x:left-8,y:y(tick)+4,'text-anchor':'end','font-size':11,'data-y-tick':''},state.view==='mod'?String(tick):Number(tick.toPrecision(3)).toString()));}
    const xticks=[...new Set(Array.from({length:mobile?3:5},(_,i)=>Math.round(xmin+(xmax-xmin)*i/(mobile?2:4))))].filter(v=>v>=xmin&&v<=xmax);
    for(const tick of xticks)picture.append(svg('text',{x:x(tick),y:bottom+20,'text-anchor':'middle','font-size':11},String(tick)));
    picture.append(svg('line',{x1:left,x2:width-right,y1:bottom,y2:bottom,stroke:'#87988b','data-plot-axis':'true'}),svg('text',{x:left,y:bottom+42,'font-size':11},state.alignment==='indices'?'Recorded local index':'Window position (each stored prefix + skip)'));
    const focusables=[],labels=[],patterns=['','7 4','2 4','9 3 2 3'];
    const inspected=(source,row)=>`${source.id} · ${source.indexKind} ${row.index} · window position ${row.position} · original ${row.raw} · ${state.view==='mod'?'residue':'displayed'} ${row.value}`;
    for(const [si,{source,rows}]of result.series.entries()){
      let path='',pen=false;for(const row of rows){if(row.y===null||!Number.isFinite(row.y)){pen=false;continue;}path+=(pen?' L':' M')+x(row.x)+' '+y(row.y);pen=true;}
      if(state.marks==='line')picture.append(svg('path',{d:path,fill:'none',stroke:colors[si],'stroke-width':theme.width,'stroke-dasharray':patterns[si],opacity:theme.opacity}));
      const group=[];focusables.push(group);
      for(const [ri,row]of rows.entries()){
        if(row.y===null||!Number.isFinite(row.y))continue;
        const cx=x(row.x),cy=y(row.y),r=Number(theme.point),attrs={fill:colors[si],stroke:colors[si],'stroke-width':1,role:'button',tabindex:'-1','aria-label':inspected(source,row),'data-point':'','data-series':si,'data-position':row.position};let mark;
        if(si===0)mark=svg('circle',{...attrs,cx,cy,r});else if(si===1)mark=svg('rect',{...attrs,x:cx-r,y:cy-r,width:2*r,height:2*r});else if(si===2)mark=svg('path',{...attrs,d:`M${cx} ${cy-r-1}L${cx+r+1} ${cy+r}L${cx-r-1} ${cy+r}Z`});else mark=svg('path',{...attrs,d:`M${cx} ${cy-r-1}L${cx+r+1} ${cy}L${cx} ${cy+r+1}L${cx-r-1} ${cy}Z`});
        const key=source.key+':'+row.storedPosition;mark.append(svg('title',{},inspected(source,row)));group.push({mark,row,key});
        const inspect=()=>{for(const item of focusables.flat())item.mark.setAttribute('tabindex',item.mark===mark?'0':'-1');activeKey=key;$('inspector').textContent=inspected(source,row);};
        mark.addEventListener('focus',inspect);mark.addEventListener('click',()=>{mark.focus();inspect();});
        mark.addEventListener('keydown',event=>{const index=group.findIndex(item=>item.mark===mark);let next;if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key))next=group[event.key==='Home'?0:event.key==='End'?group.length-1:Math.max(0,Math.min(group.length-1,index+(event.key==='ArrowLeft'?-1:1)))];else if(['ArrowUp','ArrowDown'].includes(event.key)){let target=si;for(let step=0;step<focusables.length;step++){target=(target+(event.key==='ArrowUp'?-1:1)+focusables.length)%focusables.length;const items=focusables[target];if(items.length){next=items.reduce((best,item)=>Math.abs(item.row.position-row.position)<Math.abs(best.row.position-row.position)?item:best,items[0]);break;}}}else if(['Enter',' '].includes(event.key))inspect();else return;event.preventDefault();next?.mark.focus();});
        picture.append(mark);if(showIndexLabel(ri,rows.length,theme,width))labels.push({x:cx,y:cy-10,text:String(row.index)});
      }
    }
    for(const label of mergePlotLabels(labels)){const text=svg('text',{x:label.x,y:Math.max(top-5,label.y),'text-anchor':'middle','font-size':10},label.text);text.append(svg('title',{},label.full));picture.append(text);}
    const first=focusables.flat().find(item=>item.key===activeKey)||focusables.flat()[0];first?.mark.setAttribute('tabindex','0');$('inspector').textContent='Focus a plotted point to inspect its exact integer. Left/right moves along a series; up/down switches series; Home/End moves to an endpoint.';
    if(sources.some(s=>s.type==='oeis')){picture.append(svg('text',{x:left,y:height-30,'font-size':mobile?9:11},'OEIS terms © OEIS Foundation Inc. · CC BY-SA 4.0'),svg('text',{x:left,y:height-14,'font-size':mobile?9:11},'oeis.org · export positions; mathematical offsets unknown'));}
    finishPlotTheme(picture,theme);chart.append(picture);appearance.context(state.view==='mod');
    $('summary').textContent=`${points.length} plotted points from ${sources.length} stored prefixes. ${all.length-points.length} undefined or outside the selected numeric scale. `+(state.view==='values'?'Only plotting coordinates are approximate; the table, inspection, comparisons and CSV retain exact integers.':'Residues are computed with exact integers before plotting.');
  }
  function refresh(){
    $('sources').replaceChildren();for(const [i,source]of sources.entries()){const li=node('li'),heading=node('strong',`${i+1}. ${source.title}`),info=node('p',source.pending?'Pending reference excerpt.':`${source.indexKind}: ${source.offset}–${source.offset+source.terms.length-1} · ${source.terms.length} stored integers.`),remove=node('button','Remove '+source.id);remove.type='button';remove.addEventListener('click',()=>{sources=sources.filter(s=>s.key!==source.key);refresh();$('heading').focus({preventScroll:true});});li.append(heading,info);if(!source.pending){const link=node('a',source.type==='oeis'?'Open OEIS entry':'Read definitions and formulas');link.href=source.url;li.append(link);}li.append(remove);$('sources').append(li);}
    const hasReference=sources.some(s=>s.type==='oeis');$('alignment').querySelector('[value="indices"]').disabled=hasReference;if(hasReference&&state.alignment==='indices'){state.alignment='positions';$('alignment').value='positions';}
    $('restore').hidden=!sources.some(s=>s.pending);$('clear').disabled=!sources.length;draw();
  }
  function add(source){if(sources.some(s=>s.key===source.key)){say(source.id+' is already selected.');return false;}if(sources.length===4){say('The comparison already has four series. Remove one before adding another.');$('heading').focus();$('heading').scrollIntoView({block:'start'});return false;}sources.push(source);refresh();say(source.id+' added.');$('heading').focus({preventScroll:true});$('heading').scrollIntoView({block:'start'});return true;}
  $('form').addEventListener('submit',event=>{event.preventDefault();try{const next=validateWorkbench(Object.fromEntries(fields.map(key=>[key,$(key).value])));workbenchRows(sources.filter(s=>!s.pending),next);state=next;$('error').hidden=true;draw();}catch(error){fail(error);}});
  $('clear').addEventListener('click',()=>{sources=[];refresh();say('Comparison cleared.');});
  $('example').addEventListener('click',()=>{sources=['fibonacci','lucas'].map(kind=>localSource(entries.find(e=>e.kind===kind),location.href));state={...WORKBENCH_DEFAULTS};for(const key of fields)$(key).value=state[key];refresh();say('Fibonacci and Lucas added.');});
  $('load').addEventListener('click',async()=>{const pending=sources.filter(s=>s.pending);$('load').disabled=true;$('cancel').disabled=false;try{const response=await referenceClient.records(pending.map(s=>s.descriptor),say);for(const [i,source]of pending.entries()){const index=sources.findIndex(s=>s.key===source.key);if(index!==-1)sources[index]=referenceSource(response.results[i],snapshot);}refresh();say('Shared OEIS excerpts are ready to compare.');}catch(error){say(error.message);}finally{$('load').disabled=false;$('cancel').disabled=true;}});
  $('cancel').addEventListener('click',()=>referenceClient.cancel());
  $('share').addEventListener('click',async()=>{const link=appearance.link(workbenchLink(location.href,sources,state));try{await navigator.clipboard.writeText(link);say('Comparison link copied. OEIS excerpts load only when the recipient chooses to restore them.');}catch{$('link-wrap').hidden=false;$('link').value=link;$('link').focus();$('link').select();}});
  $('csv').addEventListener('click',()=>{if(!result)return;const url=URL.createObjectURL(new Blob([comparisonCSV(result)],{type:'text/csv;charset=utf-8'})),link=node('a');link.href=url;link.download='sequence-comparison.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  for(const format of ['svg','png'])$(format).addEventListener('click',async()=>{try{await exportPlot($('chart').querySelector('svg'),format,'sequence-comparison');say(format.toUpperCase()+' exported.');}catch(error){say(error.message);}});
  let timer;if(typeof ResizeObserver==='function'){const observer=new ResizeObserver(()=>{clearTimeout(timer);timer=setTimeout(draw,100);});observer.observe($('chart'));}refresh();
  return {addLocal:entry=>add(localSource(entry,location.href)),addReference:hit=>add(referenceSource(hit,snapshot))};
}
