import {COMPARISON_CHART_DEFAULTS,validateComparisonChart,comparisonScaleExplanation} from './sequence-comparison-chart.mjs';

const fields={title:'chart-title',xTitle:'chart-x',yTitle:'chart-y',legend:'chart-legend',
  legendPosition:'chart-legend-position',legendStyle:'chart-legend-style',ticks:'chart-ticks'};
const allParams=[...Object.values(fields),'chart-series-1','chart-series-2','chart-series-3','chart-series-4'];

/** Bounded, view-only URL state. Invalid links retain the default plot and a visible explanation. */
export function readSinglePlotLabels(href,defaults={}){
  const fallback=validateComparisonChart({...COMPARISON_CHART_DEFAULTS,...defaults});
  try{
    const params=new URL(href).searchParams;
    if(!allParams.some(key=>params.has(key)))return {state:fallback,note:''};
    for(const key of allParams)if(params.getAll(key).length>1)throw Error('Repeated chart setting');
    const selected={...fallback};
    for(const [key,param]of Object.entries(fields))if(params.has(param))selected[key]=params.get(param);
    selected.seriesLabels=[];
    for(let i=0;i<4;i++)if(params.has('chart-series-'+(i+1)))selected.seriesLabels[i]=params.get('chart-series-'+(i+1));
    return {state:validateComparisonChart(selected),note:''};
  }catch{return {state:fallback,note:'Invalid chart label settings in the link. Showing default labels.'};}
}
export function singlePlotLabelLink(href,state){
  state=validateComparisonChart(state);
  const url=new URL(href);
  for(const key of allParams)url.searchParams.delete(key);
  // Persist all chart settings: archive and atlas pages have different default
  // legend visibility, so omitting a global-default value can lose the view.
  for(const [key,param]of Object.entries(fields))url.searchParams.set(param,state[key]);
  for(let i=0;i<state.seriesLabels.length;i++)if(state.seriesLabels[i])url.searchParams.set('chart-series-'+(i+1),state.seriesLabels[i]);
  return url.href;
}
const make=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
export function mountSinglePlotLabels({anchor,plot,prefix,getSources,onChange,defaults={}}){
  const restored=readSinglePlotLabels(location.href,defaults);
  let state=restored.state,sourceKey='',lastSourceIds='';
  const panel=make('details'),summary=make('summary','Chart titles, legends and axis labels');
  panel.className='sp-chart-labels';panel.id=prefix+'-chart-labels';panel.append(summary);
  const intro=make('p','Use the default labels or customize them for exports and shared plot links. Exact values and mathematical indexing are unchanged.');
  intro.className='sp-chart-note';panel.append(intro);
  const grid=make('div');grid.className='sp-chart-grid';panel.append(grid);
  const choices=[
    ['title','Chart title','text',90],
    ['xTitle','Horizontal axis title','text',64],
    ['yTitle','Vertical axis title','text',64],
    ['ticks','Vertical scale labels',[['magnitude','Approximate original values'],['scientific','Scientific notation'],['log','Logarithmic coordinates']]],
    ['legend','Legend',[['show','Show'],['hide','Hide']]],
    ['legendPosition','Legend position',[['top','Above plot'],['bottom','Below plot']]],
    ['legendStyle','Legend format',[['compact','Names only'],['full','IDs and names'],['id','IDs only']]]
  ];
  const inputs={};
  function update(key,value){
    try{
      state=validateComparisonChart({...state,[key]:value});
      status.textContent='Chart text updated.';
      showFields();onChange();
    }catch(error){status.textContent=error.message;}
  }
  for(const [key,title,type,max] of choices){
    const label=make('label',title),input=make(type==='text'?'input':'select');
    input.id=prefix+'-chart-'+key;label.htmlFor=input.id;
    if(type==='text'){input.type='text';input.maxLength=max;input.placeholder='Automatic';}
    else for(const [id,name]of type){const option=make('option',name);option.value=id;input.append(option);}
    inputs[key]=input;input.value=state[key];label.append(input);grid.append(label);
    input.addEventListener('change',()=>update(key,input.value));
  }
  const series=make('div');series.className='sp-chart-series';panel.append(series);
  const reset=make('button','Restore default chart labels');reset.type='button';
  panel.append(reset);
  const status=make('p',restored.note);status.className='sp-chart-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');panel.append(status);
  reset.addEventListener('click',()=>{
    state=validateComparisonChart({...COMPARISON_CHART_DEFAULTS,...defaults});
    status.textContent='Default chart labels restored.';sourceKey='';showFields();onChange();
  });
  function showFields(){
    for(const [key,input]of Object.entries(inputs))input.value=state[key];
    inputs.legendPosition.disabled=inputs.legendStyle.disabled=state.legend==='hide';
    const sources=getSources(),ids=sources.map(x=>x.id||x.title).join('\u001f'),key=ids+'|'+state.legend;
    if(lastSourceIds&&ids!==lastSourceIds)state=validateComparisonChart({...state,seriesLabels:[]});
    lastSourceIds=ids;
    if(sourceKey===key)return;sourceKey=key;
    series.replaceChildren();
    if(state.legend==='hide'||!sources.length)return;
    series.append(make('p','Optional names for the legend'));
    for(const [i,source]of sources.slice(0,4).entries()){
      const label=make('label'),input=make('input');input.type='text';input.maxLength=60;
      input.value=state.seriesLabels[i]||'';input.placeholder=source.title||source.id;
      label.append(make('span',(i+1)+'. '+(source.id||'Series')),input);
      input.addEventListener('change',()=>{
        const labels=Array.from({length:sources.length},(_,j)=>state.seriesLabels[j]||'');
        labels[i]=input.value;
        try{state=validateComparisonChart({...state,seriesLabels:labels});status.textContent='Legend name updated.';onChange();}
        catch(error){status.textContent=error.message;}
      });
      series.append(label);
    }
  }
  anchor.after(panel);
  const scaleNote=make('p');scaleNote.className='sp-scale-explanation';plot.after(scaleNote);
  function context(view,scale,modulus=7){
    inputs.ticks.disabled=view==='mod'||view==='grid'||view==='frequency'||view==='mod-pairs'||scale==='linear';
    if(view==='mod'||view==='grid'||view==='mod-pairs')
      scaleNote.textContent='Axes show exact integer residues. The full recorded values remain in the point inspector, table and CSV.';
    else if(view==='frequency')
      scaleNote.textContent='Bars show exact counts of residues in the selected finite window.';
    else if(scale==='log')scaleNote.textContent='Positive-value log₁₀ spacing. Tick magnitudes are approximate; the exact numbers remain in the table and CSV.';
    else scaleNote.textContent=comparisonScaleExplanation({view:'values',scale},state);
  }
  showFields();
  return {get state(){return {...state,seriesLabels:[...state.seriesLabels]};},
    link:href=>singlePlotLabelLink(href,state),context,refresh:showFields,
    get panel(){return panel;}};
}
