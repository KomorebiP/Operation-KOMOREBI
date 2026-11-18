/* Presentation-only comparison labels. Exact values and arithmetic live elsewhere. */
export const COMPARISON_CHART_DEFAULTS=Object.freeze({
  title:'',xTitle:'',yTitle:'',legend:'show',legendPosition:'top',legendStyle:'compact',ticks:'magnitude',seriesLabels:[]
});

const MAX_TEXT={title:90,xTitle:64,yTitle:64};
function chartText(value,max,label){
  if(typeof value!=='string'||value.length>max||/[\u0000-\u001f\u007f]/.test(value))throw Error(label+' must be plain text of at most '+max+' characters.');
  return value.trim();
}
export function validateComparisonChart(options={}){
  if(!options||typeof options!=='object'||Array.isArray(options))throw Error('Invalid chart label settings.');
  const out={...COMPARISON_CHART_DEFAULTS,seriesLabels:[]};
  for(const [key,max] of Object.entries(MAX_TEXT))if(Object.hasOwn(options,key))out[key]=chartText(options[key],max,key);
  const allowed={legend:['show','hide'],legendPosition:['top','bottom'],legendStyle:['compact','full','id'],ticks:['magnitude','scientific','log']};
  for(const [key,values] of Object.entries(allowed))if(Object.hasOwn(options,key)){
    if(!values.includes(options[key]))throw Error('Choose a valid '+key+' setting.');
    out[key]=options[key];
  }
  if(Object.hasOwn(options,'seriesLabels')){
    if(!Array.isArray(options.seriesLabels)||options.seriesLabels.length>4)throw Error('Provide up to four legend labels.');
    out.seriesLabels=options.seriesLabels.map(value=>chartText(value,60,'Legend label'));
  }
  return out;
}
export function comparisonChartTitle(state,options){
  if(options.title)return options.title;
  const transform=state.transform==='difference'?'First differences':state.transform==='sum'?'Partial sums':'Original terms';
  return state.view==='mod'?'Sequence residues modulo '+state.modulus+' · '+transform:transform+' · sequence comparison';
}
export function comparisonXAxisTitle(state,options){
  return options.xTitle||(state.alignment==='indices'?'Recorded local index':'Window position');
}
export function comparisonYAxisTitle(state,options){
  return options.yTitle||(state.view==='mod'?'Residue (mod '+state.modulus+')':
    state.scale==='signed-log'?(options.ticks==='log'?'sgn(v) log₁₀(1+|v|)':'Approx. value · signed log spacing'):'Value · linear scale');
}
const signedLogText=value=>Number(value.toFixed(2)).toString();
const magnitudeFormat=new Intl.NumberFormat('en-US',{notation:'compact',maximumSignificantDigits:2});
/* Tick positions stay signed-logarithmic; the default labels invert the transform.
   These are approximate axis magnitudes, never claims about stored integer values. */
export function comparisonYAxisTick(value,{view='values',scale='signed-log',ticks='magnitude'}={}){
  if(!Number.isFinite(value))return 'undefined';
  if(view==='mod')return String(Math.round(value));
  if(scale==='log'){
    if(ticks==='log')return signedLogText(value);
    const order=Math.floor(value),mantissa=Number((10**(value-order)).toPrecision(2));
    if(ticks==='scientific')return '≈'+mantissa+'×10^'+order;
    return value>15?'≈10^'+Number(value.toFixed(1)):magnitudeFormat.format(10**value);
  }
  if(scale==='signed-log'){
    if(ticks==='log')return signedLogText(value);
    if(Math.abs(value)<1e-9)return '0';
    const sign=value<0?'−':'';
    const exponent=Math.abs(value);
    if(exponent>15)return '≈'+sign+'10^'+Number(exponent.toFixed(1)).toString();
    const magnitude=exponent>300?Infinity:Math.expm1(exponent*Math.LN10);
    if(ticks==='scientific'){
      const order=Number.isFinite(magnitude)&&magnitude>0?Math.floor(Math.log10(magnitude)):Math.floor(exponent);
      const mantissa=Number.isFinite(magnitude)&&magnitude>0?magnitude/10**order:10**(exponent-order);
      return '≈'+sign+Number(mantissa.toPrecision(2))+'×10^'+order;
    }
    return '≈'+sign+(Number.isFinite(magnitude)?magnitude<.01?Number(magnitude.toPrecision(2)).toString():magnitudeFormat.format(magnitude):'10^'+Number(exponent.toFixed(1)));
  }
  if(Math.abs(value)<1e-9)return '0';
  if(Math.abs(value)>=1e5)return '≈'+(value<0?'−':'')+magnitudeFormat.format(Math.abs(value));
  return Number(value.toPrecision(3)).toString();
}
export function comparisonScaleExplanation(state,options){
  if(state.view==='mod')return 'Vertical ticks are exact residues modulo '+state.modulus+'. Values and index positions in the table remain exact.';
  if(state.scale==='log'){
    if(options.ticks==='log')return 'Tick labels are log₁₀ coordinates for positive values, not the original sequence values. Exact values remain available in the table and CSV.';
    return 'Vertical ticks approximate positive original values'+(options.ticks==='scientific'?' in scientific notation':'')+'; their spacing remains logarithmic. Exact stored values remain in point inspection, tables and CSV.';
  }
  if(state.scale==='signed-log'&&options.ticks!=='log')
    return 'Vertical tick labels approximate the original values'+(options.ticks==='scientific'?' in scientific notation':'')+'. Their spacing is signed logarithmic: sgn(v) × log₁₀(1+|v|). The exact integers appear in point details, the table, and CSV.';
  if(state.scale==='signed-log')
    return 'Vertical tick labels are signed-logarithmic coordinates, not sequence values. A coordinate t represents approximately sgn(t) × (10^|t|−1). Exact integers remain in the table and CSV.';
  return 'The vertical axis uses linear coordinates. Tick labels may be rounded, but point details, the table, and CSV retain exact integers.';
}

/** A compact legend can use an author's alias without losing the source ID. */
export function comparisonLegendLabel(source,index,options={}){
  const custom=options.seriesLabels?.[index];
  if(custom)return custom;
  if(options.legendStyle==='id')return source.id||source.title||'Series';
  if(options.legendStyle==='full')return [source.id,source.title].filter(Boolean).join(' · ');
  return source.title||source.id||'Series';
}
/** Wrap long SVG labels at word boundaries, with an ellipsis if a third line remains. */
export function wrapLegendLabel(label,maxChars=24,maxLines=2){
  const words=String(label).split(/\s+/).filter(Boolean),out=[];
  for(const word of words){
    const last=out.length-1;
    if(last>=0&&out[last].length+word.length+1<=maxChars)out[last]+=' '+word;
    else if(out.length<maxLines)out.push(word.length>maxChars?word.slice(0,maxChars-1)+'…':word);
    else{out[out.length-1]=out[out.length-1].slice(0,maxChars-1).replace(/…$/,'')+'…';break;}
  }
  return out.length?out:[''];
}
