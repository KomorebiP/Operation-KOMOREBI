import {COMPARISON_CHART_DEFAULTS,validateComparisonChart,comparisonScaleExplanation,chartTextStyle} from './sequence-comparison-chart.mjs';
import {plotTheme,contrastRatio} from './sequence-plot-options.mjs';

const fields={title:'chart-title',xTitle:'chart-x',yTitle:'chart-y',legend:'chart-legend',
  legendPosition:'chart-legend-position',legendStyle:'chart-legend-style',ticks:'chart-ticks',
  titleDisplay:'chart-title-display',xTitleDisplay:'chart-x-display',yTitleDisplay:'chart-y-display',
  titleSize:'chart-title-size',xTitleSize:'chart-x-size',yTitleSize:'chart-y-size',titleAlign:'chart-title-align',
  titleColor:'chart-title-color',titleFont:'chart-title-font',titleWeight:'chart-title-weight',titleStyle:'chart-title-style',
  xTitleColor:'chart-x-color',xTitleFont:'chart-x-font',xTitleWeight:'chart-x-weight',xTitleStyle:'chart-x-style',
  yTitleColor:'chart-y-color',yTitleFont:'chart-y-font',yTitleWeight:'chart-y-weight',yTitleStyle:'chart-y-style'};
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

/** The same compact title controls serve comparison, explorer and record plots. */
export function mountChartTextFields({host,prefix,state,onChange,onPatch,textIds={},getAppearance=()=>({theme:'white'})}){
  host.classList.add('sp-chart-text-grid');
  const inputs={},fontControls={};
  let current=state;
  function addSelect(parent,key,name,caption,values){
    const label=make('label',caption),select=make('select');select.id=prefix+'-chart-'+key;
    select.setAttribute('aria-label',name+' '+caption.toLowerCase());label.htmlFor=select.id;
    for(const [value,text]of values){const option=make('option',text);option.value=value;select.append(option);}
    label.append(select);parent.append(label);return select;
  }
  for(const [key,name,max]of [['title','Chart title',90],['xTitle','Horizontal axis title',64],['yTitle','Vertical axis title',64]]){
    const group=make('fieldset'),legend=make('legend',name),label=make('label','Text'),input=make('input');
    group.className='sp-chart-text-field';group.append(legend);input.type='text';input.maxLength=max;
    input.id=textIds[key]||prefix+'-chart-'+key;input.placeholder='Automatic';
    input.setAttribute('aria-label',name);label.htmlFor=input.id;label.append(input);group.append(label);inputs[key]=input;
    const row=make('div');row.className='sp-chart-text-settings';group.append(row);
    const selects=[
      [key+'Display','Visibility',[['show','Show'],['hide','Hide']]],
      [key+'Size','Text size',[['auto','Automatic'],...(key==='title'?['14','18','22','26']:['12','14','16','18']).map(value=>[value,value+' px'])]],
      ...(key==='title'?[['titleAlign','Alignment',[['left','Left'],['center','Center'],['right','Right']]]]:[])
    ];
    for(const [setting,caption,values]of selects){
      inputs[setting]=addSelect(row,setting,name,caption,values);
    }
    const details=make('details'),summary=make('summary','Font and color'),fontGrid=make('div');
    details.id=prefix+'-chart-'+key+'FontDetails';details.className='sp-chart-font-details';
    summary.setAttribute('aria-label',name+' font and color');details.append(summary,fontGrid);group.append(details);
    fontGrid.className='sp-chart-font-grid';
    inputs[key+'Font']=addSelect(fontGrid,key+'Font',name,'Font',[
      ['sans','Sans serif'],['serif','Serif'],['mono','Monospace']]);
    inputs[key+'Weight']=addSelect(fontGrid,key+'Weight',name,'Weight',[
      ['auto','Automatic'],['normal','Regular'],['bold','Bold']]);
    const italicLabel=make('label'),italic=make('input');italic.type='checkbox';
    italic.id=prefix+'-chart-'+key+'Style';italic.setAttribute('aria-label',name+' italic');
    italicLabel.className='sp-chart-italic';italicLabel.htmlFor=italic.id;italicLabel.append(italic,make('span','Italic'));fontGrid.append(italicLabel);
    const colorMode=addSelect(fontGrid,key+'ColorMode',name,'Color',[
      ['auto','Automatic'],['custom','Custom']]);
    const colorRow=make('div'),pickerLabel=make('label','Picker'),picker=make('input'),hexLabel=make('label','Hex color'),hex=make('input');
    colorRow.className='sp-chart-color-row';picker.type='color';picker.id=prefix+'-chart-'+key+'ColorPicker';
    picker.setAttribute('aria-label',name+' color picker');pickerLabel.htmlFor=picker.id;pickerLabel.append(picker);
    hex.type='text';hex.id=prefix+'-chart-'+key+'Color';hex.maxLength=7;hex.spellcheck=false;
    hex.autocomplete='off';hex.setAttribute('autocapitalize','off');hex.setAttribute('aria-label',name+' hex color');
    hexLabel.htmlFor=hex.id;hexLabel.append(hex);colorRow.append(pickerLabel,hexLabel);fontGrid.append(colorRow);
    const previewCaption=make('p','Preview'),preview=make('p'),hint=make('p'),error=make('p'),reset=make('button','Reset font and color');
    previewCaption.className='sp-chart-font-caption';preview.id=prefix+'-chart-'+key+'ColorPreview';preview.className='sp-chart-font-preview';
    preview.setAttribute('aria-label',name+' style preview');
    hint.id=prefix+'-chart-'+key+'ColorHint';hint.className='sp-chart-color-hint';
    error.id=prefix+'-chart-'+key+'ColorError';error.className='sp-chart-color-error';error.setAttribute('aria-live','polite');
    hex.setAttribute('aria-describedby',error.id+' '+hint.id);picker.setAttribute('aria-describedby',hint.id);
    reset.id=prefix+'-chart-'+key+'ResetFont';reset.type='button';reset.setAttribute('aria-label','Reset '+name.toLowerCase()+' font and color');
    details.append(previewCaption,preview,hint,error,reset);
    fontControls[key]={name,italic,colorMode,picker,hex,previewCaption,preview,hint,error,reset,lastColor:''};
    const clearError=()=>{hex.removeAttribute('aria-invalid');hex.setCustomValidity('');error.textContent='';};
    function setColor(value){
      if(!/^#[\da-f]{6}$/i.test(value)){
        const message='Enter a six-digit hex color, such as #173f32.';
        hex.setAttribute('aria-invalid','true');hex.setCustomValidity(message);error.textContent=message;return;
      }
      clearError();hex.value=value.toLowerCase();onChange(key+'Color',hex.value);
    }
    hex.addEventListener('input',clearError);
    hex.addEventListener('change',()=>setColor(hex.value.trim()));
    hex.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();setColor(hex.value.trim());}});
    picker.addEventListener('change',()=>setColor(picker.value));
    colorMode.addEventListener('change',()=>{
      clearError();onChange(key+'Color',colorMode.value==='auto'?'auto':fontControls[key].lastColor||plotTheme(getAppearance()).foreground);
    });
    italic.addEventListener('change',()=>onChange(key+'Style',italic.checked?'italic':'normal'));
    reset.addEventListener('click',()=>{
      clearError();fontControls[key].lastColor='';
      const patch=Object.fromEntries(['Font','Weight','Style','Color'].map(suffix=>[key+suffix,COMPARISON_CHART_DEFAULTS[key+suffix]]));
      if(onPatch)onPatch(patch);else for(const [setting,value]of Object.entries(patch))onChange(setting,value);
    });
    host.append(group);
  }
  for(const [key,input]of Object.entries(inputs))input.addEventListener('change',()=>onChange(key,input.value));
  function refresh(state){
    const previous=current;
    current=state;
    for(const [key,input]of Object.entries(inputs))input.value=state[key];
    for(const key of ['title','xTitle','yTitle']){
      const hidden=state[key+'Display']==='hide';
      inputs[key].disabled=inputs[key+'Size'].disabled=inputs[key+'Font'].disabled=inputs[key+'Weight'].disabled=hidden;
      const controls=fontControls[key];controls.italic.checked=state[key+'Style']==='italic';
      controls.italic.disabled=controls.colorMode.disabled=hidden;
      if(state[key+'Color']==='auto'||previous[key+'Color']!==state[key+'Color']){
        controls.hex.removeAttribute('aria-invalid');controls.hex.setCustomValidity('');controls.error.textContent='';
      }
    }
    inputs.titleAlign.disabled=state.titleDisplay==='hide';
    refreshTheme();
  }
  function refreshTheme(){
    const theme=plotTheme(getAppearance());
    for(const key of ['title','xTitle','yTitle']){
      const controls=fontControls[key],style=chartTextStyle(current,key),automatic=style.color==='auto';
      const color=automatic?theme.foreground:style.color,hidden=current[key+'Display']==='hide';
      controls.colorMode.value=automatic?'auto':'custom';
      if(!automatic)controls.lastColor=color;
      controls.picker.value=color;
      if(controls.hex.getAttribute('aria-invalid')!=='true'&&document.activeElement!==controls.hex)controls.hex.value=color;
      controls.picker.disabled=controls.hex.disabled=hidden||automatic;
      controls.preview.textContent=current[key]||controls.name;
      controls.preview.style.fontFamily=style.fontFamily;controls.preview.style.fontWeight=style.weight;
      controls.preview.style.fontStyle=style.style;controls.preview.style.color=color;controls.preview.style.backgroundColor=theme.background;
      controls.previewCaption.textContent=hidden?'Preview (title hidden)':'Preview';
      const ratio=contrastRatio(color,theme.background),lowContrast=!automatic&&ratio<4.5;
      controls.hint.dataset.lowContrast=String(lowContrast);
      controls.hint.textContent=automatic?'Automatic color follows the plot background.':
        'Contrast '+ratio.toFixed(1)+':1 against the plot background.'+(lowContrast?' This color may be difficult to read. Try another color or choose Automatic.':'');
    }
  }
  function resetDrafts(){
    for(const controls of Object.values(fontControls)){
      controls.hex.removeAttribute('aria-invalid');controls.hex.setCustomValidity('');controls.error.textContent='';controls.lastColor='';
    }
    refreshTheme();
  }
  refresh(state);
  return {refresh,refreshTheme,resetDrafts};
}

export function mountSinglePlotLabels({anchor,plot,prefix,getSources,onChange,defaults={},getAppearance}){
  const restored=readSinglePlotLabels(location.href,defaults);
  let state=restored.state,sourceKey='',lastSourceIds='';
  const panel=make('details'),summary=make('summary','Chart titles, legends and axis labels');
  panel.className='sp-chart-labels';panel.id=prefix+'-chart-labels';panel.append(summary);
  const intro=make('p','Set each title’s text, visibility and size. Open Font and color for typeface, bold, italic and custom colors. Long labels wrap automatically. Image exports and shared plot links keep your settings.');
  intro.className='sp-chart-note';panel.append(intro);
  const textHost=make('div');panel.append(textHost);
  const textFields=mountChartTextFields({host:textHost,prefix,state,onChange:update,onPatch:updatePatch,getAppearance});
  const grid=make('div');grid.className='sp-chart-grid';panel.append(grid);
  const choices=[
    ['ticks','Vertical scale labels',[['magnitude','Approximate original values'],['scientific','Scientific notation'],['log','Logarithmic coordinates']]],
    ['legend','Legend',[['show','Show'],['hide','Hide']]],
    ['legendPosition','Legend position',[['top','Above plot'],['bottom','Below plot']]],
    ['legendStyle','Legend format',[['compact','Names only'],['full','IDs and names'],['id','IDs only']]]
  ];
  const inputs={};
  function update(key,value){
    updatePatch({[key]:value});
  }
  function updatePatch(patch){
    try{
      state=validateComparisonChart({...state,...patch});
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
    status.textContent='Default chart labels restored.';sourceKey='';showFields();textFields.resetDrafts();onChange();
  });
  function showFields(){
    textFields.refresh(state);
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
    else scaleNote.textContent=comparisonScaleExplanation({view:'values',scale},state);
  }
  showFields();
  return {get state(){return {...state,seriesLabels:[...state.seriesLabels]};},
    link:href=>singlePlotLabelLink(href,state),context,refresh:showFields,refreshTheme:textFields.refreshTheme,resetDrafts:textFields.resetDrafts,
    get panel(){return panel;}};
}
