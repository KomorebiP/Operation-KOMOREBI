import {sequenceTransfer,transferAnchor,transferMatrix,transferCSV,transferJSON,transferLink} from './sequence-transfer-core.mjs';
import {canonicalID,normalizeText} from './sequence-atlas-search.mjs';
import {enhanceMath,clearMath} from './math-display.mjs';
import {mathLine,transferPolynomialPlain,transferPolynomialTeX,transferWitnessPlain,transferWitnessTeX,transferMatrixTeX,transferMatrixPlain} from './sequence-math.mjs';

const make=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
const save=(text,name,type='text/csv;charset=utf-8')=>{const url=URL.createObjectURL(new Blob([text],{type})),link=make('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};

export function mountTransfers(entries,host){
  if(!host)return null;
  const eligible=entries.filter(entry=>!entry.triangle&&entry.id!=='KOM084'&&entry.index_symbol!=='j'),lookup=new Map(eligible.map(entry=>[normalizeText(entry.id),entry]));
  const names=eligible.map(entry=>({entry,text:normalizeText(entry.id+' '+entry.title+' '+entry.kind)}));
  const form=make('form'),grid=make('div'),fields={},lists={};form.noValidate=true;form.id='tr-form';grid.className='sar-controls';
  for(const [key,title] of [['source','Source sequence'],['target','Target sequence']]){
    const label=make('label',title),input=make('input'),list=make('datalist');input.id='tr-'+key;input.setAttribute('list','tr-'+key+'-choices');input.maxLength=200;input.autocomplete='off';input.placeholder='Name or record ID';label.htmlFor=input.id;list.id='tr-'+key+'-choices';label.append(input,list);grid.append(label);fields[key]=input;lists[key]=list;
    input.addEventListener('input',()=>{suggest(key);updateWindowHelp();});
  }
  const countLabel=make('label','Coefficients after each nonzero anchor'),count=make('input');count.id='tr-count';count.type='number';count.min='1';count.max='48';count.value='12';count.step='1';countLabel.htmlFor=count.id;countLabel.append(count);grid.append(countLabel);fields.count=count;
  const hint=make('p');hint.id='tr-window-help';hint.className='sr-transfer-hint';hint.setAttribute('role','status');hint.setAttribute('aria-live','polite');
  count.setAttribute('aria-describedby','tr-window-help');
  const actions=make('div');actions.className='sp-actions';const run=make('button','Build exact transfer'),reverse=make('button','Reverse source and target');run.type='submit';reverse.type='button';actions.append(run,reverse);
  const presets=make('div');presets.className='sp-preset-bar';presets.setAttribute('role','group');presets.setAttribute('aria-label','Research transfer examples');const euler=eligible.find(entry=>entry.collection==='atlas'&&entry.kind==='euler'),fib=eligible.find(entry=>entry.collection==='atlas'&&entry.kind==='fibonacci');
  const forward=make('button','Euler to Fibonacci'),back=make('button','Fibonacci to Euler'),identity=make('button','Check identity transfer');
  forward.type=back.type=identity.type='button';presets.append(forward,back,identity);
  const error=make('p');error.id='tr-error';error.setAttribute('role','alert');error.hidden=true;form.append(presets,grid,hint,actions,error);host.append(form);host.parentElement.querySelector('.sr-transfer-static')?.setAttribute('hidden','');
  const result=make('div');result.id='tr-result';result.hidden=true;const summary=make('p'),indices=make('p'),domain=make('p'),sourceLink=make('a'),targetLink=make('a'),links=make('p'),scope=make('p');
  const metrics=make('div');metrics.id='tr-certificate';metrics.className='sr-transfer-facts';
  const preview=make('div');preview.id='tr-kernel-preview';preview.className='sr-transfer-previews';
  const witness=make('details'),witnessText=make('p'),witnessMath=mathLine('b_j = sum_(i=0)^j h_i a_(j-i)',String.raw`b_j=\sum_{i=0}^j h_i a_{j-i}`);witness.id='tr-convolution-witness';witness.append(make('summary','Inspect a coefficient calculation'),witnessText,witnessMath);summary.id='tr-summary';summary.setAttribute('role','status');summary.setAttribute('aria-live','polite');indices.id='tr-indices';domain.id='tr-domain';scope.textContent='This is an exact transfer of the displayed stored prefixes over Q. The kernel is constructed from the chosen target. It does not predict unrecorded values or establish a shared homogeneous recurrence.';links.append(sourceLink,document.createTextNode(' · '),targetLink);
  const detail=make('details'),description=make('p');detail.append(make('summary','Map, inverse, and normalization'),description);description.textContent='For the selected nonzero tails A and B, define H=B/A and K=A/B as ordinary formal series modulo z^L. Convolution by H sends A to B. Convolution by K recovers A. Each matrix row uses the full preceding prefix, not just one source value. Leading zero prefixes and their displayed index shifts remain attached. Different prefix lengths require a shift between classes with prescribed leading zeros. A negative shift applies only to a stream containing the required zeros. The calculation does not substitute EGF or compressed Taylor normalizations.';detail.append(mathLine('b_j = sum_(i=0)^j h_i a_(j-i)',String.raw`b_j=\sum_{i=0}^{j}h_i a_{j-i}`),mathLine('a_j = sum_(i=0)^j k_i b_(j-i)',String.raw`a_j=\sum_{i=0}^{j}k_i b_{j-i}`));
  const matrixDetails=make('details'),matrixIntro=make('p','Each matrix acts on anchored ordinary coefficients at local tail positions 0, 1, 2, ... . Its entries are h_(i-j) or k_(i-j) on and below the diagonal, and zero above it. Original sequence index shifts are recorded separately.'),matrixRule=mathLine('L(H)_(i,j) = h_(i-j) for 0<=j<=i; 0 for j>i',String.raw`\bigl(L(H)\bigr)_{i,j}=\begin{cases}h_{i-j}&0\le j\le i\\0&j>i\end{cases}`),matrixIdentity=mathLine('L(H)*L(K) = I',String.raw`L(H)L(K)=I`);
  matrixDetails.id='tr-matrices';matrixDetails.open=true;
  matrixDetails.append(make('summary','Transfer matrix and inverse'),matrixIntro,matrixRule);
  const matrixSizeLabel=make('label','Typeset matrix size'),matrixSize=make('select');matrixSize.id='tr-matrix-size';matrixSizeLabel.htmlFor=matrixSize.id;matrixSizeLabel.append(matrixSize);
  const matrixHelp=make('p','The typeset display shows a leading square block. The exact tables below always retain the first eight rows and columns, or fewer when the window is shorter.');
  matrixHelp.id='tr-matrix-help';matrixSize.setAttribute('aria-describedby',matrixHelp.id);
  const matrices=make('div');matrices.className='sr-matrices';
  matrixDetails.append(matrixSizeLabel,matrixHelp,matrices,matrixIdentity);
  const tableWrap=make('div'),table=make('table'),thead=make('thead'),tbody=make('tbody'),caption=make('caption','Exact source, target, kernel, and round-trip coefficients');tableWrap.className='sar-scroll';tableWrap.tabIndex=0;tableWrap.setAttribute('role','region');tableWrap.setAttribute('aria-label','Exact transfer certificate');const head=make('tr');for(const label of ['Tail j','Source index','Target index','Source integer','Target integer','Kernel H','Inverse K','H times source','Recovered source','Residual']){const th=make('th',label);th.scope='col';head.append(th);}thead.append(head);table.append(caption,thead,tbody);tableWrap.append(table);
  const output=make('div'),csv=make('button','Download transfer CSV'),json=make('button','Download certificate JSON'),copy=make('button','Copy kernel coefficients'),copyInverse=make('button','Copy inverse coefficients'),share=make('button','Copy transfer link'),status=make('p'),fallbackLabel=make('label','Copy this exact text'),fallback=make('textarea');output.className='sp-actions';for(const button of [csv,json,copy,copyInverse,share])button.type='button';output.append(csv,json,copy,copyInverse,share);status.setAttribute('role','status');status.setAttribute('aria-live','polite');fallbackLabel.hidden=true;fallback.id='tr-copy-text';fallback.readOnly=true;fallback.rows=3;fallbackLabel.htmlFor=fallback.id;fallbackLabel.append(fallback);
  const research=make('details');research.id='tr-euler-research';research.append(make('summary','Euler/Fibonacci research interpretation'));const researchText=make('p'),researchSource=make('a','Read the complete transfer and transported-operation derivation');researchSource.href='collection/demonstrations/EULER_PACKETS.html#transfer-the-euler-sequence-to-fibonacci-values';research.append(researchText,researchSource);
  result.append(summary,metrics,indices,domain,links,scope,preview,witness,detail,research,output,status,fallbackLabel,tableWrap,matrixDetails);host.append(result);let current;
  function suggest(key){const value=normalizeText(fields[key].value);lists[key].replaceChildren();for(const {entry,text} of names.filter(item=>!value||item.text.includes(value)).slice(0,20)){const option=make('option');option.value=entry.id;option.label=entry.title;lists[key].append(option);}}
  function resolve(key){const text=fields[key].value.trim(),entry=lookup.get(normalizeText(canonicalID(text)))||eligible.find(entry=>normalizeText(entry.title)===normalizeText(text));if(!entry)throw Object.assign(Error('Choose a '+key+' record from the name or ID suggestions.'),{field:key});return entry;}
  function updateWindowHelp(){
    try{
      const source=resolve('source'),target=resolve('target'),a=transferAnchor(source),b=transferAnchor(target),maximum=Math.min(48,a.available,b.available);
      count.max=String(maximum);
      hint.textContent='Available window: 1 to '+maximum+' coefficients. Source anchor '+(source.index_symbol||'n')+'='+a.index+' ('+a.value+'). Target anchor '+(target.index_symbol||'n')+'='+b.index+' ('+b.value+'). The original index shift is '+(b.index-a.index)+'.';
    }catch{
      count.max='48';
      hint.textContent='Select two scalar records by name or ID. The available coefficient range and nonzero anchors will appear here.';
    }
  }
  function matrix(label,values,preview,symbol){const block=make('div'),heading=make('h3',label),display=mathLine(transferMatrixPlain(preview,symbol),transferMatrixTeX(preview,symbol),'sr-transfer-matrix-equation'),scroll=make('div'),t=make('table'),body=make('tbody'),head=make('thead'),headers=make('tr');scroll.className='sar-scroll';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label',label);const corner=make('th','Output / input');corner.scope='col';headers.append(corner);for(let j=0;j<values.length;j++){const th=make('th',String(j));th.scope='col';headers.append(th);}head.append(headers);for(const [n,valuesRow] of values.entries()){const row=make('tr'),th=make('th',String(n));th.scope='row';row.append(th);for(const value of valuesRow)row.append(make('td',value));body.append(row);}t.append(make('caption',label+' · rows and columns are local tail positions'),head,body);scroll.append(t);block.append(heading,display,scroll);return block;}
  function renderMatrices(map){
    // Preserve the exact 8-by-8 tables. Only the typeset leading block is adjustable.
    const max=Math.min(8,map.count),previous=Number(matrixSize.value)||4,size=Math.max(1,Math.min(max,previous));
    matrixSize.replaceChildren();
    for(let n=1;n<=max;n++){const option=make('option',n+' × '+n);option.value=String(n);matrixSize.append(option);}
    matrixSize.value=String(size);
    const forward=transferMatrix(map,false),inverse=transferMatrix(map,true);
    clearMath(matrices);
    matrices.replaceChildren(matrix('Transfer L(H)',forward,transferMatrix(map,false,size),'H'),matrix('Inverse L(K)',inverse,transferMatrix(map,true,size),'K'));
    matrixIdentity.textContent='L_'+size+'(H)*L_'+size+'(K) = I_'+size;
    matrixIdentity.setAttribute('data-math-latex','L_{'+size+'}(H)L_{'+size+'}(K)=I_{'+size+'}');
    enhanceMath(matrixDetails);
  }
  function render(map,a,b,update){
    current=map;result.hidden=false;fields.source.value=a.id;fields.target.value=b.id;suggest('source');suggest('target');fields.count.max=String(Math.min(48,map.sourceAnchor.available,map.targetAnchor.available));
    summary.textContent=`${map.count} coefficients verified exactly: forward transfer, inverse recovery, and kernel product.`;
    indices.textContent=`Source ${a.index_symbol||'n'}=${map.sourceAnchor.index}; target ${b.index_symbol||'n'}=${map.targetAnchor.index}. Leading stored zeros: ${map.sourceAnchor.position} and ${map.targetAnchor.position}. Window position shift: ${map.positionShift}. Original index shift: ${map.indexShift}. Tail j=0 starts at those anchors.`;
    domain.textContent=map.integerKernel&&map.integerInverse?'Both computed kernels have integer coefficients in this window.':'The coefficients are exact rationals. '+(map.integerKernel?'H has integer coefficients in this window. ':'H has rational coefficients in this window. ')+(map.integerInverse?'K has integer coefficients in this window.':'K has rational coefficients in this window.');
    const checks=[
      ['Forward certificate','H · A = B',map.rows.every(row=>row.forward===row.target)],
      ['Inverse certificate','K · B = A',map.rows.every(row=>row.recovered===row.source)],
      ['Kernel product','H · K = 1',map.rows.every((row,j)=>row.identity===(j?'0':'1'))]
    ];
    clearMath(metrics);metrics.replaceChildren();
    for(const [title,equation,passed] of checks){
      const card=make('div'),heading=make('h3',title),formula=mathLine(equation,{'H · A = B':String.raw`H(z)A(z)\equiv B(z)\pmod{z^L}`,'K · B = A':String.raw`K(z)B(z)\equiv A(z)\pmod{z^L}`,'H · K = 1':String.raw`H(z)K(z)\equiv1\pmod{z^L}`} [equation],'sr-transfer-certificate'),verdict=make('p',passed?'Verified for all '+map.count+' coefficients.':'Certificate failed.');
      card.className='sr-transfer-fact';verdict.className='sr-transfer-verdict';card.append(heading,formula,verdict);metrics.append(card);
    }
    clearMath(preview);preview.replaceChildren();
    for(const [name,key,note] of [['Forward kernel H','kernel','Convolve H with the source tail to recover the target tail.'],['Inverse kernel K','inverse','Convolve K with the target tail to recover the source tail.']]){
      const panel=make('div'),heading=make('h3',name),formula=make('code',map.rows.slice(0,8).map(row=>row[key]).join(', ')),display=mathLine(transferPolynomialPlain(map.rows,key,key==='kernel'?'H':'K'),transferPolynomialTeX(map.rows,key,key==='kernel'?'H':'K')),description=make('p',note);
      panel.className='sr-transfer-preview';formula.className='sr-transfer-values';panel.append(heading,display,formula,description);preview.append(panel);
    }
    const j=Math.min(2,map.count-1),row=map.rows[j],expression=map.rows.slice(0,j+1).map((_,i)=>'('+map.rows[i].kernel+') × ('+map.rows[j-i].source+')').join(' + ');
    witnessText.textContent='At tail position '+j+', (H · A)['+j+'] = '+expression+' = '+row.forward+'. The stored target coefficient is '+row.target+'. The residual is '+row.residual+'.';witnessMath.textContent=transferWitnessPlain(map.rows,j);witnessMath.setAttribute('data-math-latex',transferWitnessTeX(map.rows,j));
    sourceLink.href=a.url;sourceLink.textContent=a.id+' · '+a.title;targetLink.href=b.url;targetLink.textContent=b.id+' · '+b.title;tbody.replaceChildren();for(const row of map.rows){const tr=make('tr');for(const value of [row.j,row.sourceIndex,row.targetIndex,row.source,row.target,row.kernel,row.inverse,row.forward,row.recovered,row.residual])tr.append(make('td',String(value)));tbody.append(tr);}renderMatrices(map);
    research.hidden=!(a.id===euler.id&&b.id===fib.id||a.id===fib.id&&b.id===euler.id);if(!research.hidden){const values=euler.terms.map(BigInt),defects=values.slice(0,5).map((_,n)=>String(values[n+2]-values[n+1]-values[n]));researchText.textContent='The cited research uses signed even Euler values and F(n+1), including its required one-index Fibonacci shift. Its infinite formal identity is derived in the cited research. The Euler Fibonacci defects begin '+defects.join(', ')+'. The recurrence operation must be transported with the map and its boundary term. The Euler values do not satisfy the homogeneous Fibonacci recurrence.';}
    error.hidden=true;for(const field of Object.values(fields))field.removeAttribute('aria-invalid');fallbackLabel.hidden=true;status.textContent='';updateWindowHelp();host.dataset.transferReady='true';enhanceMath(result);if(update)history.replaceState(null,'',transferLink(location.href,map));
  }
  function calculate(update=false){try{const a=resolve('source'),b=resolve('target'),map=sequenceTransfer(a,b,count.value);if(!map.verified)throw Error('The exact transfer certificate failed.');render(map,a,b,update);}catch(problem){error.hidden=false;error.textContent=problem.message+(current?' The previous certificate remains available.':'');if(fields[problem.field])fields[problem.field].setAttribute('aria-invalid','true');}}
  form.addEventListener('submit',event=>{event.preventDefault();calculate(true);});matrixSize.addEventListener('change',()=>{if(current)renderMatrices(current);});
  function preset(a,b){fields.source.value=a.id;fields.target.value=b.id;fields.count.value=String(Math.min(12,48,transferAnchor(a).available,transferAnchor(b).available));updateWindowHelp();calculate(true);}
  forward.addEventListener('click',()=>preset(euler,fib));back.addEventListener('click',()=>preset(fib,euler));
  identity.addEventListener('click',()=>{try{const source=resolve('source');preset(source,source);}catch(problem){error.hidden=false;error.textContent=problem.message;}});
  reverse.addEventListener('click',()=>{[fields.source.value,fields.target.value]=[fields.target.value,fields.source.value];updateWindowHelp();calculate(true);});
  async function clipboard(text,message){try{await navigator.clipboard.writeText(text);status.textContent=message;}catch{fallback.value=text;fallbackLabel.hidden=false;fallback.focus();fallback.select();status.textContent='Copy the selected exact text.';}}
  csv.addEventListener('click',()=>{if(current)save(transferCSV(current),current.sourceId+'-to-'+current.targetId+'-transfer.csv');});
  json.addEventListener('click',()=>{if(current)save(transferJSON(current),current.sourceId+'-to-'+current.targetId+'-transfer.json','application/json;charset=utf-8');});
  copy.addEventListener('click',()=>{if(current)clipboard(current.rows.map(row=>row.kernel).join(', '),'Forward kernel coefficients copied exactly.');});
  copyInverse.addEventListener('click',()=>{if(current)clipboard(current.rows.map(row=>row.inverse).join(', '),'Inverse kernel coefficients copied exactly.');});
  share.addEventListener('click',()=>{if(current)clipboard(transferLink(location.href,current),'Transfer link copied.');});
  const params=new URL(location.href).searchParams;fields.source.value=params.get('tr-source')||euler.id;fields.target.value=params.get('tr-target')||fib.id;fields.count.value=params.get('tr-count')||'12';suggest('source');suggest('target');updateWindowHelp();calculate();
  function validate(data){const a=lookup.get(normalizeText(canonicalID(data?.source||''))),b=lookup.get(normalizeText(canonicalID(data?.target||'')));if(!a||!b)throw Error('The saved transfer needs two available scalar records.');return {a,b,map:sequenceTransfer(a,b,data.count)};}
  return {snapshot:()=>current?{source:current.sourceId,target:current.targetId,count:current.count}:{source:fields.source.value,target:fields.target.value,count:Number(count.value)},validate,restore(data){const {a,b,map}=validate(data);fields.count.value=String(map.count);render(map,a,b,false);},source(entry){if(!lookup.has(normalizeText(entry.id)))return;fields.source.value=entry.id;try{const a=transferAnchor(entry),b=transferAnchor(resolve('target'));count.value=String(Math.min(Number(count.value)||12,48,a.available,b.available));}catch{}updateWindowHelp();calculate(true);host.scrollIntoView({block:'start'});fields.target.focus({preventScroll:true});}};
}
