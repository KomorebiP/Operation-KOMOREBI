import {WORKBENCH_DEFAULTS,validateWorkbench,localSource,referenceSource,familySource,customSource,descriptor,workbenchRows,agreements,readWorkbenchLink,workbenchLink,comparisonCSV} from './sequence-workbench-core.mjs';
import {mountPlotOptions,plotColors,plotHeight,showIndexLabel,mergePlotLabels,finishPlotTheme,exportPlot,validateAppearance} from './sequence-plot-options.mjs';
import {COMPARISON_CHART_DEFAULTS,validateComparisonChart,comparisonChartTitle,comparisonXAxisTitle,comparisonYAxisTitle,comparisonYAxisTick,comparisonScaleExplanation,comparisonLegendLabel,wrapLegendLabel} from './sequence-comparison-chart.mjs';

const node=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
const svg=(tag,attrs={},text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value]of Object.entries(attrs))el.setAttribute(key,value);if(text!==undefined)el.textContent=text;return el;};
const short=(value,max=60)=>value.length>max?value.slice(0,max-1)+'…':value;
export function mountWorkbench({root,entries,snapshot,referenceClient}){
  const section=root.querySelector('#comparison')||node('section');section.id='comparison';section.className='sw-workbench';
  section.innerHTML=`<p class="sar-kicker">Comparison workbench</p><h2 id="sw-heading" tabindex="-1">Compare sequences</h2>
    <p>Add up to four records from the search results or OEIS finder. Compare exact terms, differences, partial sums, and residues. Each line has its own mark and pattern as well as a color.</p>
    <p id="sw-status" role="status" aria-live="polite"></p><ol id="sw-sources" class="sw-sources"></ol>
    <div class="sp-actions"><button type="button" id="sw-example">Try Fibonacci + Lucas</button><button type="button" id="sw-clear">Clear comparison</button><button type="button" id="sw-share-top">Copy comparison link</button></div>
    <form id="sw-add-form" class="sw-add-form"><label for="sw-record">Add a sequence by name or record ID<input id="sw-record" autocomplete="off" list="sw-record-choices" placeholder="Fibonacci or KSEQ-000025"></label><datalist id="sw-record-choices"></datalist><button type="submit">Add record</button><p id="sw-add-error" role="alert" hidden></p></form>
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
     <details id="sw-provenance"><summary>Source identity and comparison receipts</summary>
       <p id="sw-receipt-status"></p><ol id="sw-receipt-list"></ol>
       <p>SHA-256 receipts identify indexed integer data, not mathematical proofs or historical priority. Generated families are reconstructed from their parameters. OEIS references retain snapshot checks and require an explicit load.</p>
     </details>
    <div id="sw-appearance"></div>
    <details id="sw-chart-labels" class="sw-chart-labels"><summary>Customize chart title, legend and axes</summary>
      <div class="sw-chart-label-grid">
        <label for="sw-title-text">Chart title<input type="text" id="sw-title-text" maxlength="90" placeholder="Sequence comparison"></label>
        <label for="sw-x-title">Horizontal axis title<input type="text" id="sw-x-title" maxlength="64" placeholder="Window position"></label>
        <label for="sw-y-title">Vertical axis title<input type="text" id="sw-y-title" maxlength="64" placeholder="Auto: value scale"></label>
        <label for="sw-tick-mode">Value-axis tick labels<select id="sw-tick-mode"><option value="magnitude">Approximate original values</option><option value="scientific">Scientific notation</option><option value="log">Logarithmic coordinates</option></select></label>
        <label for="sw-legend">Legend<select id="sw-legend"><option value="show">Show legend</option><option value="hide">Hide legend</option></select></label>
        <label for="sw-legend-position">Legend placement<select id="sw-legend-position"><option value="top">Above plot</option><option value="bottom">Below plot</option></select></label>
        <label for="sw-legend-style">Legend text<select id="sw-legend-style"><option value="compact">Names only</option><option value="full">Record IDs and names</option><option value="id">Record IDs only</option></select></label>
      </div>
      <div id="sw-series-labels" class="sw-series-labels"></div>
      <p>Leave any title blank to use a suitable default. Legend names correspond to the selected series in order. These labels change only the picture, not the integer data.</p>
      <button type="button" id="sw-reset-chart-labels">Restore chart labels</button>
      <p id="sw-chart-label-status" role="status" aria-live="polite"></p>
    </details>
    <p id="sw-summary"></p><div id="sw-chart" class="sw-chart"></div>
    <p id="sw-scale-note" class="sw-scale-note" role="note"></p>
    <p id="sw-inspector" class="sw-inspector" role="status">Focus a plotted point to inspect its exact integer. Use the left and right arrows to move along a series, the up and down arrows to switch series, and Home or End to reach an endpoint.</p>
    <div id="sw-agreements"></div><div class="sp-actions"><button type="button" id="sw-share">Copy comparison link</button><button type="button" id="sw-csv">Export exact CSV</button><button type="button" id="sw-svg">Export SVG</button><button type="button" id="sw-png">Export PNG</button></div>
    <label id="sw-link-wrap" for="sw-link" hidden>Copy this comparison link<input id="sw-link" readonly></label>
    <details id="sw-data"><summary>Exact comparison table</summary><div class="sar-scroll" role="region" aria-label="Exact comparison values" tabindex="0"><table><caption>Stored indices and displayed exact integers</caption><thead><tr><th scope="col">Series</th><th scope="col">Index convention</th><th scope="col">Index / position</th><th scope="col">Window position</th><th scope="col">Original integer</th><th scope="col">Displayed integer</th></tr></thead><tbody></tbody></table></div></details>`;
  // Keep the comparison task beside search and transfers, ahead of optional research tools.
  if(!root.querySelector('#comparison')){
    const previous=root.querySelector('#transfers')||root.querySelector('#oeis');
    if(previous)previous.after(section);else root.append(section);
  }
  const $=id=>section.querySelector('#sw-'+id);let sources=[],state={...WORKBENCH_DEFAULTS},result=null,activeKey=null,restoredSchema=null,chartLabels=validateComparisonChart();
  const matches=entries.map(entry=>({entry,key:(entry.id+' '+entry.title).toLowerCase()}));
  function suggest(){
    const term=$('record').value.toLowerCase().trim();
    $('record-choices').replaceChildren();
    for(const {entry} of matches.filter(item=>!term||item.key.includes(term)).slice(0,16)){
      const option=node('option');option.value=entry.id;option.label=entry.title;$('record-choices').append(option);
    }
  }
  $('record').addEventListener('input',suggest);suggest();
  $('add-form').addEventListener('submit',event=>{
    event.preventDefault();const text=$('record').value.trim();
    const entry=entries.find(item=>item.id.toLowerCase()===text.toLowerCase()||item.title.toLowerCase()===text.toLowerCase());
    if(!entry){$('add-error').hidden=false;$('add-error').textContent='Choose a sequence from the suggested names or record IDs.';return;}
    $('add-error').hidden=true;if(add(localSource(entry,location.href))){$('record').value='';suggest();}
  });

  const say=text=>{$('status').textContent=text;},fail=error=>{$('error').textContent=error.message;$('error').hidden=false;};
  try{const linked=readWorkbenchLink(location.href,entries,snapshot);if(linked){sources=linked.sources;state=linked.state;restoredSchema=linked.schema;chartLabels=linked.chartLabels;}}catch(error){fail(error);}
  const fields=Object.keys(WORKBENCH_DEFAULTS);for(const key of fields)$(key).value=state[key];
  const appearance=mountPlotOptions({host:$('appearance'),prefix:'sw',onChange:()=>draw()});
  const labelFields={title:$('title-text'),xTitle:$('x-title'),yTitle:$('y-title'),ticks:$('tick-mode'),legend:$('legend'),legendPosition:$('legend-position'),legendStyle:$('legend-style')};
  function showChartLabels(){
    for(const [key,input] of Object.entries(labelFields))input.value=chartLabels[key];
    $('legend-position').disabled=$('legend-style').disabled=chartLabels.legend==='hide';
    $('tick-mode').disabled=state.view==='mod'||state.scale!=='signed-log';
    const controls=$('series-labels');controls.replaceChildren();
    if(sources.length&&chartLabels.legend==='show'){
      controls.append(node('p','Legend labels (optional)'));
      for(const [index,source] of sources.entries()){
        const label=node('label'),caption=node('span',(index+1)+'. '+source.id),input=node('input');
        input.type='text';input.maxLength=60;input.value=chartLabels.seriesLabels[index]||'';
        input.placeholder=source.title;input.setAttribute('aria-label','Legend label for '+source.id);
        input.addEventListener('change',()=>{
          try{
            const seriesLabels=Array.from({length:sources.length},(_,i)=>chartLabels.seriesLabels[i]||'');
            seriesLabels[index]=input.value;
            chartLabels=validateComparisonChart({...chartLabels,seriesLabels});
            $('chart-label-status').textContent='Legend label updated.';
            draw();
          }catch(error){$('chart-label-status').textContent=error.message;}
        });
        label.append(caption,input);controls.append(label);
      }
    }
  }
  for(const [key,input] of Object.entries(labelFields))input.addEventListener('change',()=>{
    try{
      chartLabels=validateComparisonChart({...chartLabels,[key]:input.value});
      $('chart-label-status').textContent='Chart labels updated.';
      showChartLabels();draw();
    }catch(error){$('chart-label-status').textContent=error.message;}
  });
  $('reset-chart-labels').addEventListener('click',()=>{
    chartLabels=validateComparisonChart(COMPARISON_CHART_DEFAULTS);
    $('chart-label-status').textContent='Default chart labels restored.';
    showChartLabels();draw();
  });
  function draw(){
    $('chart').replaceChildren();$('agreements').replaceChildren();$('data').querySelector('tbody').replaceChildren();
    const pending=sources.some(s=>s.pending),ready=sources.length&&!pending;
    for(const key of ['csv','svg','png','share','share-top'])$(key).disabled=!ready;
    $('scale-note').textContent=comparisonScaleExplanation(state,chartLabels);
    if(!ready){result=null;$('summary').textContent=pending?'Load or remove the pending reference excerpts to draw this comparison.':'Choose Add to comparison on any local result, or try the example.';$('inspector').textContent='Exact point values will appear here.';return;}
    try{result=workbenchRows(sources,state);}catch(error){fail(error);return;}
    const colors=plotColors(appearance.state),theme=appearance.state,chart=$('chart');
    const width=Math.max(280,chart.clientWidth),height=plotHeight(width,theme),mobile=width<560;
    const showLegend=chartLabels.legend==='show',bottomLegend=showLegend&&chartLabels.legendPosition==='bottom',hasOEIS=sources.some(s=>s.type==='oeis');
    const left=mobile?84:92,right=18,legendWidth=Math.max(12,Math.floor((width-left-right-12)/7));
    const legendLines=showLegend?result.series.map(({source},i)=>{
      const label=(i+1)+'. '+comparisonLegendLabel(source,i,chartLabels);
      return wrapLegendLabel(label,legendWidth,mobile&&sources.length>=3?1:2);
    }):[];
    const totalLegendLines=legendLines.reduce((sum,lines)=>sum+lines.length,0),legendSpace=totalLegendLines*16;
    const top=showLegend&&!bottomLegend?45+legendSpace+12:56;
    const bottom=height-(hasOEIS?106:69)-(bottomLegend?legendSpace+10:0),plotWidth=width-left-right;
    const all=result.series.flatMap(s=>s.rows),points=all.filter(r=>r.y!==null&&Number.isFinite(r.y));
    for(const {source,rows}of result.series)for(const row of rows){const tr=node('tr');for(const value of [source.id,source.indexKind,row.index,row.position,row.raw,row.value??'undefined'])tr.append(node('td',String(value)));$('data').querySelector('tbody').append(tr);}
    const checks=agreements(result);if(checks.length){$('agreements').append(node('h3',state.view==='mod'?`Finite residue agreements · mod ${state.modulus}`:'Finite exact agreements'),node('p','Compared with the first selected series at overlapping displayed positions. Finite agreement does not prove that the infinite sequences are identical.'));const list=node('ul');for(const check of checks){const source=sources.find(s=>s.key===check.source);list.append(node('li',`${source.id}: ${check.equal} of ${check.compared} displayed integers agree.`+(check.firstMismatch?` First difference at ${state.alignment==='positions'?'window position':'local index'} ${check.firstMismatch.x}.`:'')));}$('agreements').append(list);}
    if(!points.length){$('svg').disabled=$('png').disabled=true;$('summary').textContent='No plottable points in this window. Reduce the skip, choose another transformation, or use the signed logarithm for very large integers. Exact stored values remain in the table and CSV.';return;}
    let xmin=Math.min(...points.map(r=>r.x)),xmax=Math.max(...points.map(r=>r.x)),ymin=Math.min(...points.map(r=>r.y)),ymax=Math.max(...points.map(r=>r.y));
    if(state.view==='mod'){ymin=0;ymax=state.modulus-1;}else if(theme.baseline==='zero'){ymin=Math.min(ymin,0);ymax=Math.max(ymax,0);}if(xmin===xmax){xmin-=.5;xmax+=.5;}if(ymin===ymax){ymin=Math.min(0,ymin);ymax=Math.max(0,ymax);if(ymin===ymax){ymin=-1;ymax=1;}}
    const normalizer=Math.max(1,Math.abs(ymin),Math.abs(ymax)),lo=ymin/normalizer,hi=ymax/normalizer;
    const x=value=>left+(value-xmin)/(xmax-xmin)*plotWidth,y=value=>bottom-(value/normalizer-lo)/(hi-lo)*(bottom-top),picture=svg('svg',{viewBox:`0 0 ${width} ${height}`,role:'group','aria-labelledby':'sw-chart-title sw-chart-desc'});
    const chartTitle=comparisonChartTitle(state,chartLabels,result.series.map(({source})=>source)),xTitle=comparisonXAxisTitle(state,chartLabels),yTitle=comparisonYAxisTitle(state,chartLabels);
    picture.append(svg('title',{id:'sw-chart-title'},chartTitle),svg('desc',{id:'sw-chart-desc'},comparisonScaleExplanation(state,chartLabels)+' Focus a point to inspect exact integer values. A complete indexed HTML table follows the chart.'),svg('rect',{width,height,fill:'#fafaf5'}));
    const heading=svg('text',{x:width/2,y:23,'text-anchor':'middle','font-size':mobile?13:15,'font-weight':650,'data-chart-title':'true','aria-label':chartTitle},short(chartTitle,Math.max(12,Math.floor((width-38)/8))));
    picture.append(heading);
    if(showLegend)result.series.forEach(({source},i)=>{
      const raw=comparisonLegendLabel(source,i,chartLabels);
      const prior=legendLines.slice(0,i).reduce((sum,lines)=>sum+lines.length,0),ly=(bottomLegend?bottom+67:45)+prior*16;
      const display=svg('text',{x:left,y:ly,'font-size':mobile?11:12,'data-legend-label':String(i),'aria-label':source.id+' · '+raw});
      legendLines[i].forEach((text,j)=>display.append(svg('tspan',{x:left,dy:j?16:0},text)));
      picture.append(display);
      picture.append(svg('line',{x1:left-24,x2:left-5,y1:ly-4,y2:ly-4,stroke:colors[i],'stroke-width':theme.width,'stroke-dasharray':['','7 4','2 4','9 3 2 3'][i]}));
    });
    const yticks=state.view==='mod'?[...new Set(Array.from({length:Math.min(state.modulus,5)},(_,i)=>Math.round(i*(state.modulus-1)/(Math.min(state.modulus,5)-1))))]:Array.from({length:5},(_,i)=>(lo+(hi-lo)*i/4)*normalizer);
    for(const tick of yticks){if(theme.grid==='on')picture.append(svg('line',{x1:left,x2:width-right,y1:y(tick),y2:y(tick),stroke:'#d9dfd4','data-plot-grid':'true'}));picture.append(svg('text',{x:left-9,y:y(tick)+4,'text-anchor':'end','font-size':11,'data-y-tick':''},comparisonYAxisTick(tick,{view:state.view,scale:state.scale,ticks:chartLabels.ticks})));}
    const xticks=[...new Set(Array.from({length:mobile?3:5},(_,i)=>Math.round(xmin+(xmax-xmin)*i/(mobile?2:4))))].filter(v=>v>=xmin&&v<=xmax);
    for(const tick of xticks)picture.append(svg('text',{x:x(tick),y:bottom+20,'text-anchor':'middle','font-size':11},String(tick)));
    picture.append(svg('line',{x1:left,x2:width-right,y1:bottom,y2:bottom,stroke:'#87988b','data-plot-axis':'true'}));
    const xLabel=svg('text',{x:left+plotWidth/2,y:bottom+42,'font-size':mobile?11:12,'text-anchor':'middle','data-x-axis-title':'true','aria-label':xTitle},short(xTitle,Math.max(12,Math.floor(plotWidth/7))));
    picture.append(xLabel);
    const yLabel=svg('text',{x:16,y:(top+bottom)/2,'font-size':mobile?10:12,'text-anchor':'middle',transform:'rotate(-90 16 '+((top+bottom)/2)+')','data-y-axis-title':'true','aria-label':yTitle},short(yTitle,Math.max(10,Math.floor((bottom-top)/(mobile?5:6)))));
    picture.append(yLabel);
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
    const first=focusables.flat().find(item=>item.key===activeKey)||focusables.flat()[0];first?.mark.setAttribute('tabindex','0');$('inspector').textContent='Focus a plotted point to inspect its exact integer. Use the left and right arrows to move along a series, the up and down arrows to switch series, and Home or End to reach an endpoint.';
    if(sources.some(s=>s.type==='oeis')){picture.append(svg('text',{x:left,y:height-30,'font-size':mobile?9:11},'OEIS terms © OEIS Foundation Inc. · CC BY-SA 4.0'),svg('text',{x:left,y:height-14,'font-size':mobile?9:11},'oeis.org · export positions; mathematical offsets unknown'));}
    finishPlotTheme(picture,theme);chart.append(picture);appearance.context(state.view==='mod');
    $('summary').textContent=`${points.length} points plotted from ${sources.length} stored prefixes. ${all.length-points.length} points are undefined or outside the selected numeric scale. `+(state.view==='values'?'Only the plotted coordinates are approximate. The table, point details, comparisons, and CSV retain exact integers.':'Residues are computed with exact integers before plotting.');
  }
  function refreshReceipts(){
    const list=$('receipt-list');list.replaceChildren();
    const unpinned=sources.some(source=>source.type==='local'&&!source.receipt);
    $('receipt-status').textContent=restoredSchema===1
      ?'Legacy comparison link. Its local record IDs were not bound to the original exact data, so their stored terms might have changed.'
      :restoredSchema===2
      ?'The SHA-256 receipts in this shared comparison match the current local catalogue. The comparison retains its original view settings.'
      :unpinned
      ?'Some local entries have no exact-data receipt. Links containing those entries use the earlier, unpinned format.'
      :'New comparison links pin the full indexed integer data of local records. See the receipts below.';
    for(const source of sources){
      const item=node('li'),name=node('strong',source.id+' · '),details=node('span');
      if(source.type==='local'&&source.receipt){
        details.textContent='Local record · '+source.terms.length+' stored integers · SHA-256: ';
        details.append(node('code',source.receipt));
      }else if(source.type==='local')details.textContent='Local record without a stored exact-data receipt.';
      else if(source.type==='oeis'){
        const hash=source.snapshot||source.descriptor?.snapshot||'not available';
        details.textContent='OEIS excerpt · retained snapshot: ';
        details.append(node('code',hash));
      }else if(source.type==='family')details.textContent='Generated family · reconstructed from explicit parameters (no source-code digest).';
      else details.textContent='Pasted exact integers embedded directly in the comparison link.';
      item.append(name,details);list.append(item);
    }
  }
  function refresh(){
    $('sources').replaceChildren();for(const [i,source]of sources.entries()){const li=node('li'),heading=node('strong',`${i+1}. ${source.title}`),info=node('p',source.pending?'Pending reference excerpt.':`${source.indexKind}: ${source.offset}–${source.offset+source.terms.length-1} · ${source.terms.length} stored integers.`),remove=node('button','Remove '+source.id);remove.type='button';remove.addEventListener('click',()=>{const previous=sources.findIndex(s=>s.key===source.key);
    const labels=Array.from({length:sources.length},(_,i)=>chartLabels.seriesLabels[i]||'');
    labels.splice(previous,1);chartLabels=validateComparisonChart({...chartLabels,seriesLabels:labels});
    restoredSchema=null;sources=sources.filter(s=>s.key!==source.key);refresh();$('heading').focus({preventScroll:true});});li.append(heading,info);if(!source.pending&&source.url){const link=node('a',source.type==='oeis'?'Open OEIS entry':source.type==='family'?'Open family parameters and formulas':'Read definitions and formulas');link.href=source.url;li.append(link);}li.append(remove);$('sources').append(li);}
    const hasReference=sources.some(s=>s.type==='oeis');$('alignment').querySelector('[value="indices"]').disabled=hasReference;if(hasReference&&state.alignment==='indices'){state.alignment='positions';$('alignment').value='positions';}
    $('restore').hidden=!sources.some(s=>s.pending);$('clear').disabled=!sources.length;refreshReceipts();showChartLabels();draw();
  }
  function add(source){if(sources.some(s=>s.key===source.key)){say(source.id+' is already selected.');return false;}if(sources.length===4){say('The comparison already has four series. Remove one before adding another.');$('heading').focus();$('heading').scrollIntoView({block:'start'});return false;}restoredSchema=null;sources.push(source);refresh();say(source.id+' added.');$('heading').focus({preventScroll:true});$('heading').scrollIntoView({block:'start'});return true;}
  $('form').addEventListener('submit',event=>{event.preventDefault();try{const next=validateWorkbench(Object.fromEntries(fields.map(key=>[key,$(key).value])));workbenchRows(sources.filter(s=>!s.pending),next);state=next;$('error').hidden=true;showChartLabels();draw();}catch(error){fail(error);}});
  $('clear').addEventListener('click',()=>{restoredSchema=null;sources=[];chartLabels=validateComparisonChart({...chartLabels,seriesLabels:[]});refresh();say('Comparison cleared.');});
  $('example').addEventListener('click',()=>{restoredSchema=null;sources=['fibonacci','lucas'].map(kind=>localSource(entries.find(e=>e.kind===kind),location.href));chartLabels=validateComparisonChart({...chartLabels,seriesLabels:[]});state={...WORKBENCH_DEFAULTS};for(const key of fields)$(key).value=state[key];refresh();say('Fibonacci and Lucas added.');});
  $('load').addEventListener('click',async()=>{const pending=sources.filter(s=>s.pending);$('load').disabled=true;$('cancel').disabled=false;try{const response=await referenceClient.records(pending.map(s=>s.descriptor),say);for(const [i,source]of pending.entries()){const index=sources.findIndex(s=>s.key===source.key);if(index!==-1)sources[index]=referenceSource(response.results[i],snapshot);}refresh();say('Shared OEIS excerpts are ready to compare.');}catch(error){say(error.message);}finally{$('load').disabled=false;$('cancel').disabled=true;}});
  $('cancel').addEventListener('click',()=>referenceClient.cancel());
    const copyComparison=async()=>{let link;try{link=appearance.link(workbenchLink(location.href,sources,state,chartLabels));}catch(error){fail(error);return;}try{await navigator.clipboard.writeText(link);say('Comparison link copied. Exact local data receipts are checked when available. OEIS excerpts require explicit restoration.');}catch{$('link-wrap').hidden=false;$('link').value=link;$('link').focus();$('link').select();}};
  $('share').addEventListener('click',copyComparison);
  $('share-top').addEventListener('click',copyComparison);
  $('csv').addEventListener('click',()=>{if(!result)return;const url=URL.createObjectURL(new Blob([comparisonCSV(result)],{type:'text/csv;charset=utf-8'})),link=node('a');link.href=url;link.download='sequence-comparison.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  for(const format of ['svg','png'])$(format).addEventListener('click',async()=>{try{await exportPlot($('chart').querySelector('svg'),format,'sequence-comparison');say(format.toUpperCase()+' exported.');}catch(error){say(error.message);}});
  let timer;if(typeof ResizeObserver==='function'){const observer=new ResizeObserver(()=>{clearTimeout(timer);timer=setTimeout(draw,100);});observer.observe($('chart'));}refresh();
  function validate(data){if(!data||data.schema!==1)throw Error('Unsupported comparison workspace.');const url=new URL(location.href);url.search='';url.searchParams.set('wb',JSON.stringify(data));const parsed=readWorkbenchLink(url.href,entries,snapshot);if(data.appearance)validateAppearance(data.appearance);if(data.chartLabels)validateComparisonChart(data.chartLabels);return parsed;}
  return {addLocal:entry=>add(localSource(entry,location.href)),addReference:hit=>add(referenceSource(hit,snapshot)),addFamily:(engine,params)=>add(familySource(engine,params,location.href)),addCustom:(terms,title='Identification input',offset=0)=>add(customSource({terms,title,offset})),snapshot:()=>({schema:1,state:{...state},sources:sources.map(source=>source.pending?source.descriptor:descriptor(source)),appearance:appearance.state,chartLabels:{...chartLabels,seriesLabels:[...chartLabels.seriesLabels]}}),validate,restore(data){const next=validate(data);sources=next.sources;state=next.state;chartLabels=validateComparisonChart(data.chartLabels||next.chartLabels);for(const key of fields)$(key).value=state[key];if(data.appearance)appearance.set(data.appearance);refresh();say('Comparison restored. Reference excerpts load only when explicitly requested.');}};
}
