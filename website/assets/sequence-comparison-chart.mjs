/* Presentation-only comparison labels. Exact values and arithmetic live elsewhere. */
export const COMPARISON_CHART_DEFAULTS=Object.freeze({
  title:'',xTitle:'',yTitle:'',legend:'show',legendPosition:'top',ticks:'magnitude',seriesLabels:[]
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
  const allowed={legend:['show','hide'],legendPosition:['top','bottom'],ticks:['magnitude','log']};
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
  return options.title||(state.view==='mod'?'Sequence residues modulo '+state.modulus:'Sequence comparison');
}
export function comparisonXAxisTitle(state,options){
  return options.xTitle||(state.alignment==='indices'?'Recorded local index':'Window position');
}
export function comparisonYAxisTitle(state,options){
  return options.yTitle||(state.view==='mod'?'Residue (mod '+state.modulus+')':
    state.scale==='signed-log'?(options.ticks==='magnitude'?'Approx. value · signed log spacing':'sgn(v) log₁₀(1+|v|)'):'Value · linear scale');
}
const signedLogText=value=>Number(value.toFixed(2)).toString();
const magnitudeFormat=new Intl.NumberFormat('en-US',{notation:'compact',maximumSignificantDigits:2});
/* Tick positions stay signed-logarithmic; the default labels invert the transform.
   These are approximate axis magnitudes, never claims about stored integer values. */
export function comparisonYAxisTick(value,{view='values',scale='signed-log',ticks='magnitude'}={}){
  if(!Number.isFinite(value))return 'undefined';
  if(view==='mod')return String(Math.round(value));
  if(scale==='signed-log'){
    if(ticks==='log')return signedLogText(value);
    if(Math.abs(value)<1e-9)return '0';
    const sign=value<0?'−':'';
    const exponent=Math.abs(value);
    if(exponent>15)return '≈'+sign+'10^'+Number(exponent.toFixed(1)).toString();
    const magnitude=Math.expm1(exponent*Math.LN10);
    return '≈'+sign+(magnitude<.01?Number(magnitude.toPrecision(2)).toString():magnitudeFormat.format(magnitude));
  }
  if(Math.abs(value)<1e-9)return '0';
  if(Math.abs(value)>=1e5)return '≈'+(value<0?'−':'')+magnitudeFormat.format(Math.abs(value));
  return Number(value.toPrecision(3)).toString();
}
export function comparisonScaleExplanation(state,options){
  if(state.view==='mod')return 'Vertical ticks are exact residues modulo '+state.modulus+'. Values and index positions in the table remain exact.';
  if(state.scale==='signed-log'&&options.ticks==='magnitude')
    return 'Vertical tick labels approximate the original values. Their spacing is signed logarithmic: sgn(v) × log₁₀(1+|v|). The exact integers appear in point details, the table, and CSV.';
  if(state.scale==='signed-log')
    return 'Vertical tick labels are signed-logarithmic coordinates, not sequence values. A coordinate t represents approximately sgn(t) × (10^|t|−1). Exact integers remain in the table and CSV.';
  return 'The vertical axis uses linear coordinates. Tick labels may be rounded, but point details, the table, and CSV retain exact integers.';
}
