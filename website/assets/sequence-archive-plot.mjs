import {archiveWindow,archiveLink,windowCSV,moveArchiveWindow,triangleWindow,triangleLayout,trianglePolynomial,archivePreset} from './sequence-archive-core.mjs';
import {mod} from './sequence-atlas-core.mjs';
import {mountPlotOptions,plotColors,plotHeight,showIndexLabel,mergePlotLabels,exportPlot,finishPlotTheme} from './sequence-plot-options.mjs';

const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
const svg=(tag,attrs,text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,val]of Object.entries(attrs))el.setAttribute(key,String(val));if(text!==undefined)el.textContent=text;return el;};
export function setupArchivePlot(entry){
  const $=id=>document.getElementById('sar-'+id),keys=['view','scale','start','size','mod','marks','color'],params=new URL(location.href).searchParams;
  let current,appearance,selectedN=null,figure,rowSync=()=>{};
  const link=state=>appearanceControls.link(archiveLink(location.href,state,'plot'));
  const say=(target,text)=>{if(target.textContent!==text)target.textContent=text;};
  function point(row){selectedN=row.n;say($('point'),`Index ${row.n}: a(${row.n}) = ${row.raw}; plotted value ${row.value??'undefined'}${row.next===null?'':`; following residue ${row.next}`}.`);}
  function draw(result){
    const state=result.state,valid=result.rows.filter(row=>Number.isFinite(row.x)&&Number.isFinite(row.y)),colors=plotColors(appearance);
    const width=Math.max(270,Math.min(1000,$('plot').clientWidth||760)),height=plotHeight(width,appearance),right=width-22,bottom=height-55;
    const focused=$('plot').contains(document.activeElement),picture=svg('svg',{viewBox:`0 0 ${width} ${height}`,role:'group','aria-labelledby':'sar-plot-title sar-plot-desc'});
    picture.append(svg('rect',{width,height,fill:getComputedStyle($('plot')).backgroundColor}),svg('title',{id:'sar-plot-title'},entry.id+' · '+entry.title+' — '+state.view),svg('desc',{id:'sar-plot-desc'},'Discrete recorded samples. Focus points for exact values; arrow keys move between them. Lines connect samples and do not interpolate additional data.'));
    const modular=['mod','pairs'].includes(state.view),stems=state.marks==='stems'&&state.view!=='pairs',zero=appearance.baseline==='zero'||modular||stems;
    appearanceControls.context(modular||stems);$('scale').disabled=modular;
    if(valid.length){
      let minX=Math.min(...valid.map(r=>r.x)),maxX=Math.max(...valid.map(r=>r.x)),minY=Math.min(...valid.map(r=>r.y),...(zero?[0]:[])),maxY=Math.max(...valid.map(r=>r.y),...(zero?[0]:[]));
      if(modular){minY=0;maxY=state.mod-1;if(state.view==='pairs'){minX=0;maxX=state.mod-1;}}
      const expand=(a,b)=>{if(a!==b)return[a,b];const margin=Math.max(1,Math.abs(a)*.05);return[Number.isFinite(a-margin)?a-margin:a,Number.isFinite(b+margin)?b+margin:b];};
      [minX,maxX]=expand(minX,maxX);[minY,maxY]=expand(minY,maxY);
      const unit=Math.max(Math.abs(minY),Math.abs(maxY),1),lo=minY/unit,hi=maxY/unit;
      const scaleCaption=!modular&&state.scale==='signed-log'?'sgn(v) log10(1+|v|)':'',top=scaleCaption&&width<560?104:80;
      const xx=v=>65+(v-minX)/(maxX-minX)*(right-65),yy=v=>bottom-(v/unit-lo)/(hi-lo)*(bottom-top);
      picture.append(svg('path',{d:`M65 ${top-10}V${bottom}H${right}`,class:'sar-axis'}));
      const ticks=modular?(state.mod<=12?Array.from({length:state.mod},(_,k)=>k):[...new Set(Array.from({length:5},(_,k)=>Math.round(minY+(maxY-minY)*k/4)))]):Array.from({length:5},(_,k)=>(lo+(hi-lo)*k/4)*unit);
      for(const value of ticks){
        const py=yy(value);
        if(appearance.grid==='on')picture.append(svg('path',{d:`M65 ${py}H${right}`,stroke:'#d9dfd4','stroke-width':1,fill:'none','data-plot-grid':'true'}));
        picture.append(svg('text',{x:57,y:py+4,'text-anchor':'end'},value===0?'0':modular?String(value):Number(value).toPrecision(3)));
      }
      const names={raw:'Original values',difference:'First differences',sum:'Partial sums',mod:`Residues · m=${state.mod}`,pairs:`Consecutive residues · m=${state.mod}`};
      const title=entry.id+' · '+entry.title,limit=Math.max(18,Math.floor((right-65)/5.8));
      picture.append(svg('text',{x:65,y:22},title.length>limit?title.slice(0,limit-1)+'…':title),svg('text',{x:65,y:44},names[state.view]+(scaleCaption&&width>=560?' · '+scaleCaption:!modular&&!scaleCaption?' · linear':'')),svg('text',{x:65,y:bottom+22},String(minX)),svg('text',{x:right,y:bottom+22,'text-anchor':'end'},String(maxX)),svg('text',{x:(65+right)/2,y:height-10,'text-anchor':'middle'},state.view==='pairs'?`a(${entry.index_symbol}) mod m`:`Sequence index ${entry.index_symbol}`));
      if(scaleCaption&&width<560)picture.append(svg('text',{x:65,y:62},scaleCaption));
      if(state.marks==='line'){
        let d='',connected=false;
        for(const row of result.rows){if(!Number.isFinite(row.x)||!Number.isFinite(row.y)){connected=false;continue;}d+=(connected?'L':'M')+xx(row.x)+','+yy(row.y)+' ';connected=true;}
        picture.append(svg('path',{d,fill:'none',stroke:colors[0],'stroke-width':appearance.width,'data-plot-line':'true'}));
      }
      const active=Math.max(0,valid.findIndex(row=>row.n===selectedN)),indexLabels=[];
      for(const [i,row]of valid.entries()){
        const colorIndex=state.color==='value'?Number(mod(BigInt(row.value),state.mod))%colors.length:state.color==='index'?Number(mod(BigInt(row.n),state.mod))%colors.length:0,color=colors[colorIndex];
        if(stems)picture.append(svg('line',{x1:xx(row.x),x2:xx(row.x),y1:yy(0),y2:yy(row.y),stroke:color,'stroke-width':appearance.width,'data-plot-stem':'true'}));
        const dot=svg('circle',{cx:xx(row.x),cy:yy(row.y),r:appearance.point,tabindex:i===active?'0':'-1',role:'button','aria-label':`Index ${row.n}; exact value ${row.value}${row.next===null?'':`; following residue ${row.next}`}`});
        dot.style.setProperty('--sar-mark',color);dot.style.setProperty('--sar-active-radius',Math.max(7,Number(appearance.point)+2));dot.append(svg('title',{},`${entry.index_symbol}=${row.n}: ${row.value}`));
        dot.addEventListener('focus',()=>point(row));dot.addEventListener('pointerenter',()=>point(row));
        dot.addEventListener('click',()=>{for(const mark of picture.querySelectorAll('circle'))mark.setAttribute('tabindex','-1');dot.setAttribute('tabindex','0');dot.focus({preventScroll:true});point(row);});
        dot.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const dots=[...picture.querySelectorAll('circle')],at=event.key==='Home'?0:event.key==='End'?dots.length-1:Math.max(0,Math.min(dots.length-1,i+(event.key==='ArrowLeft'?-1:1)));dot.setAttribute('tabindex','-1');dots[at].setAttribute('tabindex','0');dots[at].focus({preventScroll:true});}else if(event.key==='Enter'||event.key===' '){event.preventDefault();point(row);}});
        picture.append(dot);
        if(showIndexLabel(i,valid.length,appearance,right-65))indexLabels.push({x:xx(row.x),y:Math.max(top-15,yy(row.y)-Number(appearance.point)-8),text:String(row.n)});
      }
      for(const label of mergePlotLabels(indexLabels)){const text=svg('text',{x:label.x,y:label.y,'text-anchor':'middle',class:'sp-plot-index'},label.text);text.append(svg('title',{},'Indices '+label.full));picture.append(text);}
      point(valid[active]);
    }else picture.append(svg('text',{x:25,y:100},'No defined coordinates. Try another window or scale.'));
    finishPlotTheme(picture,appearance);$('plot').replaceChildren(picture);figure=picture;
    if(focused)picture.querySelector('circle[tabindex="0"]')?.focus({preventScroll:true});
    const table=$('window-values');table.replaceChildren();for(const row of result.rows){const tr=make('tr');for(const value of [row.n,row.raw,row.value??'undefined',row.next??'—'])tr.append(make('td',value));table.append(tr);}
    say($('window'),`${result.rows.length} index positions, ${valid.length} plotted points; indices ${state.start}–${state.start+state.size-1}. Stored range ${entry.offset}–${entry.offset+entry.terms.length-1}.`);
    $('previous').disabled=state.start===entry.offset;$('next').disabled=state.start+state.size>=entry.offset+entry.terms.length;$('zoom-in').disabled=state.size===1;$('zoom-out').disabled=state.size>=Math.min(1000,entry.terms.length);
  }
  function run(update=false){
    try{const result=archiveWindow(entry,Object.fromEntries(keys.map(key=>[key,$(key).value])));current=result;rowSync(result.state);draw(result);$('plot-error').hidden=true;for(const key of keys)$(key).removeAttribute('aria-invalid');if(update)history.replaceState(null,'',link(result.state));}
    catch(error){$('plot-error').textContent=error.message+' The previous plot remains available.';$('plot-error').hidden=false;if(error.field){$(error.field).setAttribute('aria-invalid','true');if(update)$(error.field).focus();}}
  }
  function apply(state){for(const key of keys)$(key).value=state[key];run(true);}
  for(const key of keys)if(params.has(key))$(key).value=params.get(key);
  const appearanceControls=mountPlotOptions({host:$('plot-options'),prefix:'sar',onChange:style=>{appearance=style;if(current)draw(current);}});appearance=appearanceControls.state;
  for(const key of ['marks','color'])$(key).addEventListener('change',()=>{if(!current)return;current=archiveWindow(entry,{...current.state,marks:$('marks').value,color:$('color').value});draw(current);});
  $('explorer').hidden=false;$('static-note').hidden=true;
  $('plot-form').addEventListener('submit',event=>{event.preventDefault();run(true);});
  $('view-link').addEventListener('click',async()=>{if(!current)return;try{await navigator.clipboard.writeText(link(current.state));say($('window'),'Plot link copied, including its appearance.');}catch{$('plot-fallback').hidden=false;$('plot-link').value=link(current.state);$('plot-link').focus();$('plot-link').select();say($('window'),'Copy the selected plot link.');}});
  $('export').addEventListener('click',()=>{if(!current)return;const url=URL.createObjectURL(new Blob([windowCSV(current.rows,entry.index_symbol)],{type:'text/csv;charset=utf-8'})),anchor=make('a');anchor.href=url;anchor.download=entry.id+'-'+current.state.view+'.csv';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  for(const format of ['svg','png'])$(format).addEventListener('click',()=>exportPlot(figure,format,entry.id+'-'+current.state.view).catch(error=>{$('plot-error').hidden=false;$('plot-error').textContent=error.message;}));
  for(const [id,action]of [['previous','previous'],['next','next'],['zoom-in','in'],['zoom-out','out'],['all','all']])$(id).addEventListener('click',()=>{if(current)apply(moveArchiveWindow(entry,current.state,action));});
  const presetBar=$('presets');
  for(const [name,label]of [['growth','Growth view'],['residues','Residue view'],['changes','Changes']]){const button=make('button',label);button.type='button';button.dataset.archivePreset=name;button.addEventListener('click',()=>{if(current)apply({...current.state,...archivePreset(entry,name)});});presetBar.append(button);}
  if(/valuation|carries|Collatz|totient/i.test(entry.kind)){const button=make('button',/valuation|carries/i.test(entry.kind)?'Valuation / count profile':'Arithmetic profile');button.type='button';button.dataset.archivePreset='profile';button.addEventListener('click',()=>{if(current)apply({...current.state,...archivePreset(entry,'profile')});});presetBar.append(button);}
  if(entry.id==='KOM084'||entry.triangle){
    const group=make('div');group.className='sp-row-preset';const label=make('label','Polynomial row n'),select=make('select');select.id='sar-row';label.htmlFor=select.id;
    for(const row of triangleLayout(entry)){const option=make('option',String(row.row));option.value=String(row.row);select.append(option);}label.append(select);
    const polynomial=make('p');polynomial.id='sar-row-polynomial';polynomial.className='sar-formula';const note=make('p');
    const updateRow=()=>{polynomial.textContent=trianglePolynomial(entry,select.value);const row=triangleLayout(entry)[Number(select.value)];note.textContent=`Row ${row.row} contains columns k=0–${row.size-1}. Its flat indices are ${row.start}–${row.start+row.size-1}. The polynomial uses the stored coefficients in column order.`;};
    select.addEventListener('change',updateRow);
    rowSync=state=>{const row=triangleLayout(entry).find(row=>row.start===state.start&&row.size===state.size);if(row&&select.value!==String(row.row)){select.value=String(row.row);updateRow();}};
    const button=make('button','Plot selected polynomial row');button.id='sar-apply-row';button.type='button';button.addEventListener('click',()=>{if(current)apply({...current.state,...triangleWindow(entry,select.value)});});group.append(label,button,note,polynomial);presetBar.after(group);updateRow();
  }

  function inspect(){const value=$('inspect').value,n=Number(value),i=n-entry.offset;if(!value.trim()||!Number.isSafeInteger(n)||i<0||i>=entry.terms.length){$('inspect').setAttribute('aria-invalid','true');$('exact').textContent=`Choose a stored index from ${entry.offset} through ${entry.offset+entry.terms.length-1}.`;return;}$('inspect').removeAttribute('aria-invalid');$('exact').replaceChildren(make('strong',`a(${n}) = `),make('code',entry.terms[i]));}
  $('inspect').addEventListener('input',inspect);inspect();run();
  if(!current){const defaults=archiveWindow(entry).state;for(const key of keys)$(key).value=defaults[key];run();$('plot-error').hidden=false;$('plot-error').textContent='Invalid plot options in this link. Showing the first recorded window.';}
  let observedWidth=$('plot').clientWidth;new ResizeObserver(()=>{const width=$('plot').clientWidth;if(width!==observedWidth){observedWidth=width;if(current)draw(current);}}).observe($('plot'));
}
