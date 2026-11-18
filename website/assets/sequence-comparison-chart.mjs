/* Presentation-only comparison labels. Exact values and arithmetic live elsewhere. */
export const COMPARISON_CHART_DEFAULTS=Object.freeze({
  title:'',xTitle:'',yTitle:'',legend:'show',legendPosition:'top',legendStyle:'compact',ticks:'magnitude',seriesLabels:[],
  titleDisplay:'show',xTitleDisplay:'show',yTitleDisplay:'show',
  titleSize:'auto',xTitleSize:'auto',yTitleSize:'auto',titleAlign:'center',
  titleColor:'auto',xTitleColor:'auto',yTitleColor:'auto',
  titleFont:'sans',xTitleFont:'sans',yTitleFont:'sans',
  titleWeight:'auto',xTitleWeight:'auto',yTitleWeight:'auto',
  titleStyle:'normal',xTitleStyle:'normal',yTitleStyle:'normal'
});
export const CHART_TEXT_FONTS=Object.freeze({
  sans:'system-ui, sans-serif',
  serif:'Georgia, "Times New Roman", serif',
  mono:'ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace'
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
  const allowed={legend:['show','hide'],legendPosition:['top','bottom'],legendStyle:['compact','full','id'],ticks:['magnitude','scientific','log'],
    titleDisplay:['show','hide'],xTitleDisplay:['show','hide'],yTitleDisplay:['show','hide'],
    titleSize:['auto','14','18','22','26'],xTitleSize:['auto','12','14','16','18'],yTitleSize:['auto','12','14','16','18'],titleAlign:['left','center','right']};
  for(const key of Object.keys(MAX_TEXT)){
    allowed[key+'Font']=Object.keys(CHART_TEXT_FONTS);
    allowed[key+'Weight']=['auto','normal','bold'];
    allowed[key+'Style']=['normal','italic'];
    const color=options[key+'Color'];
    if(Object.hasOwn(options,key+'Color')){
      if(typeof color!=='string'||color!=='auto'&&!/^#[\da-f]{6}$/i.test(color))throw Error('Choose automatic color or a six-digit hex color for '+key+'.');
      out[key+'Color']=color.toLowerCase();
    }
  }
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

/** Portable font stacks are shared by the controls, measured layout and exports. */
export function chartTextStyle(options={},key='title'){
  if(!Object.hasOwn(MAX_TEXT,key))throw Error('Choose a chart title or axis title.');
  const settings=validateComparisonChart(options),weight=settings[key+'Weight'];
  return {fontFamily:CHART_TEXT_FONTS[settings[key+'Font']],
    weight:weight==='bold'?700:weight==='normal'?400:key==='title'?650:400,
    style:settings[key+'Style'],color:settings[key+'Color']};
}
export function comparisonChartTitle(state,options,sources=[]){
  if(options.title)return options.title;
  const transform=state.transform==='difference'?'First differences':state.transform==='sum'?'Partial sums':'Original terms';
  const shortName=source=>{
    const full=String(source?.title||source?.id||'Sequence').trim().replace(/\s+(?:numbers?|sequence)$/i,'');
    return full.length>29?full.slice(0,28).trimEnd()+'…':full;
  };
  const comparison=sources.length===1?shortName(sources[0]):
    sources.length===2?shortName(sources[0])+' vs '+shortName(sources[1]):
    sources.length>2?sources.length+' sequences':'sequence comparison';
  const view=state.view==='mod'?'Residues mod '+state.modulus+' · ':'';
  return view+transform+' · '+comparison;
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
    let order=Math.floor(value),mantissa=Number((10**(value-order)).toPrecision(2));
    if(mantissa===10){mantissa=1;order++;}
    if(ticks==='scientific')return '≈'+mantissa+'×10^'+order;
    // Very small fractions should not render as a long string of zeros.
    if(value< -3)return '≈'+mantissa+'×10^'+order;
    return value>15?'≈10^'+Number(value.toFixed(1)):magnitudeFormat.format(10**value);
  }
  if(scale==='signed-log'){
    if(ticks==='log')return signedLogText(value);
    if(Math.abs(value)<1e-9)return '0';
    const sign=value<0?'−':'';
    const exponent=Math.abs(value);
    // Coefficients regularly exceed 10^15. Scientific mode must still use
    // a mantissa and exponent instead of silently falling back to 10^n.
    if(exponent>15&&ticks==='scientific'){
      let order=Math.floor(exponent),mantissa=Number((10**(exponent-order)).toPrecision(2));
      if(mantissa===10){mantissa=1;order++;}
      return '≈'+sign+mantissa+'×10^'+order;
    }
    if(exponent>15)return '≈'+sign+'10^'+Number(exponent.toFixed(1)).toString();
    const magnitude=Math.expm1(exponent*Math.LN10);
    if(ticks==='scientific'){
      const order=Number.isFinite(magnitude)&&magnitude>0?Math.floor(Math.log10(magnitude)):Math.floor(exponent);
      const mantissa=Number.isFinite(magnitude)&&magnitude>0?magnitude/10**order:10**(exponent-order);
      return '≈'+sign+Number(mantissa.toPrecision(2))+'×10^'+order;
    }
    return '≈'+sign+(Number.isFinite(magnitude)?magnitude<.01?Number(magnitude.toPrecision(2)).toString():magnitudeFormat.format(magnitude):'10^'+Number(exponent.toFixed(1)));
  }
  if(Math.abs(value)<1e-9)return '0';
  if(Math.abs(value)>=1e15){
    const [mantissa,exponent]=Math.abs(value).toExponential(1).split('e');
    return '≈'+(value<0?'−':'')+Number(mantissa)+'×10^'+Number(exponent);
  }
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
export function wrapLegendLabel(label,maxChars=24,maxLines=2,width){
  if(Number.isFinite(width)){
    const lines=wrapChartText(label,Math.max(12,width),12);
    if(lines.length<=maxLines)return lines;
    const visible=lines.slice(0,maxLines),characters=Array.from(visible[maxLines-1]);
    while(characters.length&&textWidth(characters.join('')+'…',12)>width)characters.pop();
    visible[maxLines-1]=characters.join('').trimEnd()+'…';
    return visible;
  }
  const words=String(label).split(/\s+/).filter(Boolean),out=[];
  for(const word of words){
    const last=out.length-1;
    if(last>=0&&out[last].length+word.length+1<=maxChars)out[last]+=' '+word;
    else if(out.length<maxLines)out.push(word.length>maxChars?word.slice(0,maxChars-1)+'…':word);
    else{out[out.length-1]=out[out.length-1].slice(0,maxChars-1).replace(/…$/,'')+'…';break;}
  }
  return out.length?out:[''];
}

// Measure the same font that the standalone SVG uses. The deterministic fallback
// also lets non-browser consumers compute a conservative layout.
let measureContext;
function textWidth(text,size,{weight=400,fontFamily=CHART_TEXT_FONTS.sans,style='normal'}={}){
  if(measureContext===undefined){
    measureContext=typeof document==='undefined'?null:document.createElement('canvas').getContext('2d');
  }
  if(!measureContext)return Array.from(text).length*size*.72+(style==='italic'?size*.2:0);
  measureContext.font=style+' '+weight+' '+size+'px '+fontFamily;
  const measured=measureContext.measureText(text);
  // Italic glyphs can extend beyond their advance width on either side.
  return measured.width+Math.max(0,measured.actualBoundingBoxLeft||0)+
    Math.max(0,(measured.actualBoundingBoxRight||0)-measured.width);
}
function wrapChartText(text,width,size,typography={}){
  const lines=[];
  // Wrapped tspans keep a trailing space so their text remains copyable. Reserve
  // that advance as well as the visible glyph width before deciding line breaks.
  width=Math.max(size,width-textWidth(' ',size,typography));
  let line='';
  for(const word of String(text).trim().split(/\s+/).filter(Boolean)){
    const joined=line?line+' '+word:word;
    if(textWidth(joined,size,typography)<=width){line=joined;continue;}
    if(line){lines.push(line);line='';}
    for(const character of Array.from(word)){
      if(line&&textWidth(line+character,size,typography)>width){lines.push(line);line='';}
      line+=character;
    }
  }
  if(line)lines.push(line);
  return lines;
}

/** Reserve real space for chart text, legends and ticks before placing points. */
export function layoutChartText({width,height,left=90,right=20,title='',xTitle='',yTitle='',options={},legendHeight=0,legendPosition='top',footerHeight=0,tickLabels=[]}){
  const settings=validateComparisonChart(options),mobile=width<560;
  const size=(key,automatic)=>settings[key]==='auto'?automatic:Number(settings[key]);
  const titleSize=size('titleSize',mobile?14:16),xSize=size('xTitleSize',12),ySize=size('yTitleSize',12);
  const titleType=chartTextStyle(settings,'title'),xType=chartTextStyle(settings,'xTitle'),yType=chartTextStyle(settings,'yTitle');
  const titleLines=settings.titleDisplay==='hide'?[]:wrapChartText(title,width-32,titleSize,titleType);
  const titleLineHeight=Math.ceil(titleSize*1.3),yLineHeight=Math.ceil(ySize*1.3);
  // Two rotated lines leave room for numeric ticks on narrow screens. A long
  // vertical title grows the chart height instead of consuming the plot width.
  let ySpan=Math.max(160,Math.min(260,height*.5));
  let yLines=settings.yTitleDisplay==='hide'?[]:wrapChartText(yTitle,ySpan,ySize,yType);
  while(yLines.length>2){ySpan+=16;yLines=wrapChartText(yTitle,ySpan,ySize,yType);}
  const tickWidth=Math.max(0,...tickLabels.map(label=>Math.ceil(textWidth(label,12))));
  const titleBand=yLines.length?8+yLines.length*yLineHeight+10:8;
  left=Math.max(left,titleBand+tickWidth+9);
  const plotWidth=width-left-right,xLines=settings.xTitleDisplay==='hide'?[]:wrapChartText(xTitle,plotWidth,xSize,xType);
  const xLineHeight=Math.ceil(xSize*1.3),headingBottom=titleLines.length?12+titleLines.length*titleLineHeight+8:12;
  const bottomLegend=legendHeight>0&&legendPosition==='bottom';
  const top=headingBottom+(legendHeight&&!bottomLegend?legendHeight+12:12);
  const xBlock=xLines.length?xLines.length*xLineHeight+8:0;
  const bottomSpace=32+xBlock+(bottomLegend?legendHeight+12:0)+footerHeight+12;
  const minimumPlotHeight=Math.max(180,...yLines.map(line=>Math.ceil(textWidth(line,ySize,yType))+16));
  height=Math.max(height,Math.ceil(top+bottomSpace+minimumPlotHeight));
  const bottom=height-bottomSpace,centerY=(top+bottom)/2,yBlock=yLines.length*yLineHeight;
  const titleX=settings.titleAlign==='left'?16:settings.titleAlign==='right'?width-16:width/2;
  const plan=(text,lines,fontSize,lineHeight,x,y,typography,anchor='middle')=>({text,lines,fontSize,lineHeight,x,y,anchor,...typography});
  return {width,height,left,right,top,bottom,plotWidth,plotHeight:bottom-top,
    legendY:bottomLegend?bottom+32+xBlock+12:headingBottom+12,
    title:plan(title,titleLines,titleSize,titleLineHeight,titleX,12+titleSize,titleType,{left:'start',center:'middle',right:'end'}[settings.titleAlign]),
    xTitle:plan(xTitle,xLines,xSize,xLineHeight,left+plotWidth/2,bottom+32+xSize,xType),
    yTitle:{...plan(yTitle,yLines,ySize,yLineHeight,8+yBlock/2,centerY-(yLines.length-1)*yLineHeight/2+ySize*.35,yType),
      rotation:{x:8+yBlock/2,y:centerY}}
  };
}

/** Full visible text and exportable inline typography, independent of page CSS. */
export function appendChartText(picture,layout){
  const svg=(name,attributes,text)=>{
    const element=document.createElementNS('http://www.w3.org/2000/svg',name);
    for(const [key,value]of Object.entries(attributes))element.setAttribute(key,value);
    if(text!==undefined)element.textContent=text;
    return element;
  };
  picture.append(svg('rect',{x:layout.left,y:layout.top,width:layout.plotWidth,height:layout.plotHeight,
    fill:'none','pointer-events':'none','aria-hidden':'true','data-plot-area':''}));
  for(const [key,attribute]of [['title','data-chart-title'],['xTitle','data-x-axis-title'],['yTitle','data-y-axis-title']]){
    const plan=layout[key];if(!plan.lines.length)continue;
    const text=svg('text',{x:plan.x,y:plan.y,'text-anchor':plan.anchor,'font-size':plan.fontSize,
      'font-family':plan.fontFamily,'font-weight':plan.weight,'font-style':plan.style,
      'data-chart-text-color':plan.color,[attribute]:'true','aria-label':plan.text});
    text.style.fontFamily=plan.fontFamily;text.style.fontSize=plan.fontSize+'px';text.style.fontWeight=plan.weight;text.style.fontStyle=plan.style;
    if(plan.color!=='auto')text.style.fill=plan.color;
    if(plan.rotation)text.setAttribute('transform',`rotate(-90 ${plan.rotation.x} ${plan.rotation.y})`);
    plan.lines.forEach((line,i)=>text.append(svg('tspan',{x:plan.x,dy:i?plan.lineHeight:0},line+(i<plan.lines.length-1?' ':''))));
    picture.append(text);
  }
}
