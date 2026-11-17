import {sequenceTransfer,transferAnchor,transferMatrix,transferProductEntry,transferCSV,transferJSON,transferLink} from './sequence-transfer-core.mjs';
import {composeScalarTransfers} from './sequence-graph-core.mjs';
import {canonicalID,normalizeText} from './sequence-atlas-search.mjs';
import {enhanceMath,clearMath} from './math-display.mjs';
import {mathLine,transferPolynomialPlain,transferPolynomialTeX,transferWitnessPlain,transferWitnessTeX,transferMatrixTeX,transferMatrixPlain,transferActionEquations,transferProductMath,transferIndexMath,transferCompositionMath} from './sequence-math.mjs';

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
  const indexMap=make('section'),indexNote=make('p','Source and target indices use separate original origins. The same local tail position does not imply equal sequence values or a shared recurrence.'),indexFormula=mathLine('source index = a+j; target index = b+j',String.raw`i_{\mathrm{source}}(j)=\alpha+j,\quad i_{\mathrm{target}}(j)=\beta+j`,'sr-transfer-index-equation');
  indexMap.id='tr-index-map';indexMap.append(make('h3','Original index alignment'),indexFormula,indexNote);
  const metrics=make('div');metrics.id='tr-certificate';metrics.className='sr-transfer-facts';
  const preview=make('div');preview.id='tr-kernel-preview';preview.className='sr-transfer-previews';
  const witness=make('details'),witnessText=make('p'),witnessIndexHelp=make('p'),
        witnessMath=mathLine('b_j = sum_(i=0)^j h_i a_(j-i)',String.raw`b_j=\sum_{i=0}^{j}h_i a_{j-i}`);
  witness.id='tr-convolution-witness';
  const witnessControls=make('div'),witnessIndexLabel=make('label','Tail position j'),witnessIndex=make('select'),
        witnessDirectionLabel=make('label','Coefficient calculation'),witnessDirection=make('select');
  witnessControls.className='sar-controls sr-witness-controls';witnessIndex.id='tr-witness-index';
  witnessDirection.id='tr-witness-direction';witnessIndexLabel.htmlFor=witnessIndex.id;
  witnessDirectionLabel.htmlFor=witnessDirection.id;
  for(const [value,label] of [['forward','Forward H · A = B'],['inverse','Inverse K · B = A']]){
    const option=make('option',label);option.value=value;witnessDirection.append(option);
  }
  witnessIndexLabel.append(witnessIndex);witnessDirectionLabel.append(witnessDirection);
  witnessControls.append(witnessIndexLabel,witnessDirectionLabel);
  witnessIndexHelp.id='tr-witness-indices';
  witness.append(make('summary','Inspect a coefficient calculation'),witnessControls,witnessIndexHelp,witnessText,witnessMath);summary.id='tr-summary';summary.setAttribute('role','status');summary.setAttribute('aria-live','polite');indices.id='tr-indices';domain.id='tr-domain';scope.textContent='This is an exact transfer of the displayed stored prefixes over Q. The kernel is constructed from the chosen target. It does not predict unrecorded values or establish a shared homogeneous recurrence.';links.append(sourceLink,document.createTextNode(' · '),targetLink);
  const detail=make('details'),description=make('p');detail.append(make('summary','Map, inverse, and normalization'),description);description.textContent='For the selected nonzero tails A and B, define H=B/A and K=A/B as ordinary formal series modulo z^L. Convolution by H sends A to B. Convolution by K recovers A. Each matrix row uses the full preceding prefix, not just one source value. Leading zero prefixes and their displayed index shifts remain attached. Different prefix lengths require a shift between classes with prescribed leading zeros. A negative shift applies only to a stream containing the required zeros. The calculation does not substitute EGF or compressed Taylor normalizations.';detail.append(mathLine('b_j = sum_(i=0)^j h_i a_(j-i)',String.raw`b_j=\sum_{i=0}^{j}h_i a_{j-i}`),mathLine('a_j = sum_(i=0)^j k_i b_(j-i)',String.raw`a_j=\sum_{i=0}^{j}k_i b_{j-i}`));
  const matrixDetails=make('details'),matrixIntro=make('p','Each matrix acts on anchored ordinary coefficients at local tail positions 0, 1, 2, ... . Its entries are h_(i-j) or k_(i-j) on and below the diagonal, and zero above it. Original sequence index shifts are recorded separately.'),matrixRule=mathLine('L(H)_(i,j) = h_(i-j) for 0<=j<=i; 0 for j>i',String.raw`\bigl(L(H)\bigr)_{i,j}=\begin{cases}h_{i-j}&0\le j\le i\\0&j>i\end{cases}`),matrixIdentity=mathLine('L(H)*L(K) = I',String.raw`L(H)L(K)=I`);
  matrixDetails.id='tr-matrices';
  matrixDetails.append(make('summary','Transfer matrix and inverse'),matrixIntro,matrixRule,mathLine('b = L(H)*a; a = L(K)*b',String.raw`\mathbf b=L(H)\mathbf a,\qquad\mathbf a=L(K)\mathbf b`));
  const matrixSizeLabel=make('label','Typeset matrix size'),matrixSize=make('select'),matrixCopy=make('button','Copy displayed matrices as LaTeX');matrixCopy.type='button';matrixSize.id='tr-matrix-size';matrixSizeLabel.htmlFor=matrixSize.id;matrixSizeLabel.append(matrixSize);
  const matrixHelp=make('p','The typeset display shows a leading square block. The exact tables below always retain the first eight rows and columns, or fewer when the window is shorter.');
  matrixHelp.id='tr-matrix-help';matrixSize.setAttribute('aria-describedby',matrixHelp.id);
  const matrices=make('div'),matrixAction=make('div');matrices.className='sr-matrices';matrixAction.id='tr-matrix-action';
  const product=make('section'),productControls=make('div'),productRow=make('select'),productColumn=make('select'),productOrder=make('select'),productStatus=make('p'),
        productEquation=mathLine('(L(H)L(K))[i,j] = delta(i,j)',String.raw`\bigl(L(H)L(K)\bigr)_{i,j}=\delta_{i,j}`,'sr-product-equation');
  product.id='tr-product-witness';productControls.className='sar-controls sr-product-controls';
  for(const [select,id,title] of [[productRow,'tr-product-row','Output row i'],[productColumn,'tr-product-column','Input column j'],[productOrder,'tr-product-order','Product order']]){
    select.id=id;const label=make('label',title);label.htmlFor=id;label.append(select);productControls.append(label);
  }
  for(const [value,label] of [['HK','L(H) × L(K)'],['KH','L(K) × L(H)']]){const option=make('option',label);option.value=value;productOrder.append(option);}
  const productHelp=make('p','Select one matrix-product entry to inspect its exact rational summands. Above-diagonal entries vanish by triangularity. The identity is certified only in the selected finite coefficient window.');
  productHelp.id='tr-product-help';for(const select of [productRow,productColumn,productOrder])select.setAttribute('aria-describedby',productHelp.id);
  productStatus.id='tr-product-status';productStatus.setAttribute('role','status');productStatus.setAttribute('aria-live','polite');
  product.append(make('h3','Verify one inverse-matrix entry'),productHelp,productControls,productEquation,productStatus);
  matrixDetails.append(matrixSizeLabel,matrixCopy,matrixHelp,matrices,matrixAction,matrixIdentity,product);
  const composePanel=make('details'),composeForm=make('form'),composeViaLabel=make('label','Intermediate scalar sequence B'),
        composeVia=make('input'),composeViaList=make('datalist'),composeRun=make('button','Verify three-sequence composition'),
        composeError=make('p'),composeOutput=make('div'),composeExport=make('button','Download composition JSON'),
        composeCopy=make('button','Copy composition LaTeX');
  composePanel.id='tr-compose';composeForm.id='tr-compose-form';composeForm.noValidate=true;
  composeVia.id='tr-compose-via';composeVia.maxLength=200;composeVia.autocomplete='off';
  composeVia.placeholder='Name or record ID';composeVia.setAttribute('list','tr-compose-via-choices');
  composeViaList.id='tr-compose-via-choices';composeViaLabel.htmlFor=composeVia.id;
  composeViaLabel.append(composeVia,composeViaList);composeRun.type='submit';composeExport.type=composeCopy.type='button';
  composeExport.disabled=composeCopy.disabled=true;composeError.id='tr-compose-error';
  composeError.hidden=true;composeError.setAttribute('role','alert');composeOutput.id='tr-compose-output';composeOutput.hidden=true;
  const composeExplanation=make('p','Choose a third scalar sequence B and verify A → B → C against the direct A → C transfer. Every map is a formal quotient of its anchored tails. For nonzero anchors this composition follows algebraically and is not evidence of a newly shared recurrence or an infinite identity.');
  composeForm.append(composeViaLabel,composeRun,composeError);
  const composeActions=make('div');composeActions.className='sp-actions';composeActions.append(composeExport,composeCopy);
  composePanel.append(make('summary','Compose through a third sequence'),composeExplanation,composeForm,composeOutput,composeActions);
  const tableWrap=make('div'),table=make('table'),thead=make('thead'),tbody=make('tbody'),caption=make('caption','Exact source, target, kernel, and round-trip coefficients');tableWrap.className='sar-scroll';tableWrap.tabIndex=0;tableWrap.setAttribute('role','region');tableWrap.setAttribute('aria-label','Exact transfer certificate');const head=make('tr');for(const label of ['Tail j','Source index','Target index','Source integer','Target integer','Kernel H','Inverse K','H times source','Recovered source','Residual']){const th=make('th',label);th.scope='col';head.append(th);}thead.append(head);table.append(caption,thead,tbody);tableWrap.append(table);
  const output=make('div'),csv=make('button','Download transfer CSV'),json=make('button','Download certificate JSON'),copy=make('button','Copy kernel coefficients'),copyInverse=make('button','Copy inverse coefficients'),share=make('button','Copy transfer link'),status=make('p'),fallbackLabel=make('label','Copy this exact text'),fallback=make('textarea');output.className='sp-actions';for(const button of [csv,json,copy,copyInverse,share])button.type='button';output.append(csv,json,copy,copyInverse,share);status.setAttribute('role','status');status.setAttribute('aria-live','polite');fallbackLabel.hidden=true;fallback.id='tr-copy-text';fallback.readOnly=true;fallback.rows=3;fallbackLabel.htmlFor=fallback.id;fallbackLabel.append(fallback);
  const research=make('details');research.id='tr-euler-research';research.append(make('summary','Euler/Fibonacci research interpretation'));const researchText=make('p'),researchSource=make('a','Read the complete transfer and transported-operation derivation');researchSource.href='collection/demonstrations/EULER_PACKETS.html#transfer-the-euler-sequence-to-fibonacci-values';research.append(researchText,researchSource);
  const resultNav=make('nav');resultNav.id='tr-result-nav';resultNav.setAttribute('aria-label','Inspect this transfer');
  for(const [title,id] of [
    ['Coefficient calculation','tr-convolution-witness'],
    ['Exact coefficients','tr-exact-data'],
    ['Transfer matrices','tr-matrices'],
    ['Compose three sequences','tr-compose']
  ]){
    const link=make('a',title);link.href='#'+id;
    link.addEventListener('click',()=>{const target=document.getElementById(id);if(target?.tagName==='DETAILS')target.open=true;});
    resultNav.append(link);
  }
  tableWrap.id='tr-exact-data';
  result.append(summary,resultNav,metrics,indices,indexMap,domain,links,scope,preview,witness,detail,research,output,status,fallbackLabel,tableWrap,matrixDetails,composePanel);host.append(result);let current,composition=null;
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
  function renderProduct(map,size,reset=false){
    const previousRow=Number(productRow.value),previousColumn=Number(productColumn.value);
    const initial=!productRow.options.length;
    for(const select of [productRow,productColumn]){
      select.replaceChildren();
      for(let k=0;k<size;k++){const option=make('option',String(k));option.value=String(k);select.append(option);}
    }
    productRow.value=String(initial||reset?Math.min(size-1,3):Math.max(0,Math.min(size-1,previousRow)));
    productColumn.value=String(initial||reset?0:Math.max(0,Math.min(size-1,previousColumn)));
    const witness=transferProductEntry(map,Number(productRow.value),Number(productColumn.value),productOrder.value,size);
    if(!witness.verified){
      productStatus.textContent='The exact matrix-product entry failed its identity check.';
      productEquation.hidden=true;throw Error(productStatus.textContent);
    }
    productEquation.hidden=false;
    const expression=transferProductMath(witness);
    productEquation.textContent=expression.plain;
    productEquation.setAttribute('data-math-latex',expression.tex);
    productStatus.textContent='Exactly verified: entry ('+witness.row+', '+witness.column+') = '+witness.value+
      '. '+(witness.terms.length?witness.terms.length+' rational summands.':'The entry is above the diagonal.');
    enhanceMath(product);
  }
  function renderMatrices(map){
    // Preserve the exact 8-by-8 tables. Only the typeset leading block is adjustable.
    const max=Math.min(8,map.count),previous=Number(matrixSize.value)||4,size=Math.max(1,Math.min(max,previous));
    matrixSize.replaceChildren();
    for(let n=1;n<=max;n++){const option=make('option',n+' × '+n);option.value=String(n);matrixSize.append(option);}
    matrixSize.value=String(size);
    const forward=transferMatrix(map,false),inverse=transferMatrix(map,true);
    clearMath(matrices);
    matrices.replaceChildren(matrix('Transfer L(H)',forward,transferMatrix(map,false,size),'H'),matrix('Inverse L(K)',inverse,transferMatrix(map,true,size),'K'));
    const action=transferActionEquations(map.rows,size);
    clearMath(matrixAction);
    const forwardBlock=make('div'),inverseBlock=make('div'),actionTitle=make('h3','Exact action on the selected coefficients');
    forwardBlock.append(make('h4','Forward image'),mathLine(action.forward.plain,action.forward.tex,'sr-matrix-vector-equation'));
    inverseBlock.append(make('h4','Inverse recovery'),mathLine(action.inverse.plain,action.inverse.tex,'sr-matrix-vector-equation'));
    const actionInfo=make('p','Both vectors begin at their nonzero anchors. Source index '+map.sourceAnchor.index+' and target index '+map.targetAnchor.index+' correspond to local position 0. Every entry is exact.');
    const actionGrid=make('div');actionGrid.className='sr-transfer-actions';
    actionGrid.append(forwardBlock,inverseBlock);matrixAction.replaceChildren(actionTitle,actionInfo,actionGrid);
    matrixIdentity.textContent='L_'+size+'(H)*L_'+size+'(K) = L_'+size+'(K)*L_'+size+'(H) = I_'+size;
    matrixIdentity.setAttribute('data-math-latex','L_{'+size+'}(H)L_{'+size+'}(K)=L_{'+size+'}(K)L_{'+size+'}(H)=I_{'+size+'}');
    renderProduct(map,size);
    enhanceMath(matrixDetails);
  }
  function renderWitness(map,reset=false){
    const old=Number(witnessIndex.value),j=reset?Math.min(2,map.count-1):Number.isSafeInteger(old)?Math.min(map.count-1,Math.max(0,old)):Math.min(2,map.count-1);
    witnessIndex.replaceChildren();
    for(const row of map.rows){const option=make('option',String(row.j));option.value=String(row.j);witnessIndex.append(option);}
    witnessIndex.value=String(j);
    const direction=witnessDirection.value==='inverse'?'inverse':'forward',row=map.rows[j];
    witnessIndexHelp.textContent='Local tail position '+j+' corresponds to source index '+row.sourceIndex+' and target index '+row.targetIndex+'.';
    witnessText.textContent=direction==='forward'
      ?'At tail position '+j+', forward convolution recovers the stored target '+row.target+'. Exact residual: '+row.residual+'.'
      :'At tail position '+j+', inverse convolution recovers the stored source '+row.source+'. Recovered value: '+row.recovered+'.';
    witnessMath.textContent=transferWitnessPlain(map.rows,j,direction);
    witnessMath.setAttribute('data-math-latex',transferWitnessTeX(map.rows,j,direction));
    enhanceMath(witness);
  }
  function suggestVia(){
    const q=normalizeText(composeVia.value);
    composeViaList.replaceChildren();
    for(const {entry,text} of names.filter(item=>!q||item.text.includes(q)).slice(0,20)){
      const option=make('option');option.value=entry.id;option.label=entry.title;composeViaList.append(option);
    }
  }
  function resolveVia(){
    const value=composeVia.value.trim();
    const entry=lookup.get(normalizeText(canonicalID(value)))||
      eligible.find(item=>normalizeText(item.title)===normalizeText(value));
    if(!entry)throw Error('Choose an intermediate scalar record by name or ID.');
    return entry;
  }
  function calculateComposition(){
    try{
      if(!current)throw Error('Build an exact source-to-target transfer first.');
      const source=lookup.get(normalizeText(current.sourceId)),
            via=resolveVia(),target=lookup.get(normalizeText(current.targetId));
      const map=composeScalarTransfers(source,via,target,current.count);
      if(!map.verified)throw Error('The exact three-sequence composition certificate failed.');
      const formulas=transferCompositionMath(map,Math.min(2,map.count-1));
      clearMath(composeOutput);
      const heading=make('h3',source.id+' → '+via.id+' → '+target.id);
      const summaryText=make('p',map.count+' exact coefficients agree with the direct transfer. Original index shift: '+map.indexShift+'. Window position shift: '+map.positionShift+'.');
      const rows=make('div'),table=make('table'),caption=make('caption','Three-sequence composition in original indices and exact rational coefficients'),thead=make('thead'),head=make('tr'),tbody=make('tbody');
      rows.className='sar-scroll';rows.tabIndex=0;rows.setAttribute('role','region');
      rows.setAttribute('aria-label','Exact three-sequence transfer composition');
      for(const field of ['Tail j','A index','B index','C index','H_AB','H_BC','Composed H_AC','Direct H_AC','Composed inverse']){
        const th=make('th',field);th.scope='col';head.append(th);
      }
      thead.append(head);
      for(const row of map.rows){
        const tr=make('tr');
        for(const value of [row.j,row.sourceIndex,row.viaIndex,row.targetIndex,row.first,row.second,row.composed,row.direct,row.inverse]){
          tr.append(make('td',String(value)));
        }
        tbody.append(tr);
      }
      table.append(caption,thead,tbody);rows.append(table);
      composeOutput.replaceChildren(heading,summaryText,
        mathLine(formulas.identity.plain,formulas.identity.tex,'sr-compose-equation'),
        mathLine(formulas.shifts.plain,formulas.shifts.tex,'sr-compose-equation'),
        make('h4','Coefficient composition witness'),
        mathLine(formulas.witness.plain,formulas.witness.tex,'sr-compose-equation'),
        make('p',map.scope),rows);
      composition={map,formulas};
      composeVia.removeAttribute('aria-invalid');composeError.hidden=true;composeExport.disabled=composeCopy.disabled=false;
      composeOutput.hidden=false;enhanceMath(composeOutput);
    }catch(problem){
      composeError.textContent=problem.message;composeError.hidden=false;
      composeVia.setAttribute('aria-invalid','true');
      composition=null;clearMath(composeOutput);composeOutput.replaceChildren();composeOutput.hidden=true;composeExport.disabled=composeCopy.disabled=true;
    }
  }
  function render(map,a,b,update){
    current=map;composition=null;clearMath(composeOutput);composeOutput.replaceChildren();composeOutput.hidden=true;composeError.hidden=true;composeVia.removeAttribute('aria-invalid');composeExport.disabled=composeCopy.disabled=true;result.hidden=false;fields.source.value=a.id;fields.target.value=b.id;suggest('source');suggest('target');fields.count.max=String(Math.min(48,map.sourceAnchor.available,map.targetAnchor.available));
    summary.textContent=`${map.count} coefficients verified exactly: forward transfer, inverse recovery, and kernel product.`;
    indices.textContent=`Source ${a.index_symbol||'n'}=${map.sourceAnchor.index}; target ${b.index_symbol||'n'}=${map.targetAnchor.index}. Leading stored zeros: ${map.sourceAnchor.position} and ${map.targetAnchor.position}. Window position shift: ${map.positionShift}. Original index shift: ${map.indexShift}. Tail j=0 starts at those anchors.`;
    const mapEquation=transferIndexMath(map);indexFormula.textContent=mapEquation.plain;indexFormula.setAttribute('data-math-latex',mapEquation.tex);
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
    renderWitness(map,true);
    sourceLink.href=a.url;sourceLink.textContent=a.id+' · '+a.title;targetLink.href=b.url;targetLink.textContent=b.id+' · '+b.title;tbody.replaceChildren();for(const row of map.rows){const tr=make('tr');for(const value of [row.j,row.sourceIndex,row.targetIndex,row.source,row.target,row.kernel,row.inverse,row.forward,row.recovered,row.residual])tr.append(make('td',String(value)));tbody.append(tr);}renderMatrices(map);
    research.hidden=!(a.id===euler.id&&b.id===fib.id||a.id===fib.id&&b.id===euler.id);if(!research.hidden){const values=euler.terms.map(BigInt),defects=values.slice(0,5).map((_,n)=>String(values[n+2]-values[n+1]-values[n]));researchText.textContent='The cited research uses signed even Euler values and F(n+1), including its required one-index Fibonacci shift. Its infinite formal identity is derived in the cited research. The Euler Fibonacci defects begin '+defects.join(', ')+'. The recurrence operation must be transported with the map and its boundary term. The Euler values do not satisfy the homogeneous Fibonacci recurrence.';}
    error.hidden=true;for(const field of Object.values(fields))field.removeAttribute('aria-invalid');fallbackLabel.hidden=true;status.textContent='';updateWindowHelp();host.dataset.transferReady='true';enhanceMath(result);if(update)history.replaceState(null,'',transferLink(location.href,map));
  }
  function calculate(update=false){try{const a=resolve('source'),b=resolve('target'),map=sequenceTransfer(a,b,count.value);if(!map.verified)throw Error('The exact transfer certificate failed.');render(map,a,b,update);}catch(problem){error.hidden=false;error.textContent=problem.message+(current?' The previous certificate remains available.':'');if(fields[problem.field])fields[problem.field].setAttribute('aria-invalid','true');}}
  form.addEventListener('submit',event=>{event.preventDefault();calculate(true);});
  composeForm.addEventListener('submit',event=>{event.preventDefault();calculateComposition();});
  composeVia.addEventListener('input',()=>{composeVia.removeAttribute('aria-invalid');suggestVia();});
  composeExport.addEventListener('click',()=>{if(composition)save(JSON.stringify(composition.map,null,2)+'\n','three-sequence-composition.json','application/json;charset=utf-8');});
  composeCopy.addEventListener('click',()=>{if(composition)clipboard([composition.formulas.identity.tex,composition.formulas.shifts.tex,composition.formulas.witness.tex].join('\n\n'),'Composition LaTeX copied.');});matrixSize.addEventListener('change',()=>{if(current)renderMatrices(current);});for(const select of [productRow,productColumn,productOrder])select.addEventListener('change',()=>{if(current)renderProduct(current,Number(matrixSize.value));});witnessIndex.addEventListener('change',()=>{if(current)renderWitness(current);});witnessDirection.addEventListener('change',()=>{if(current)renderWitness(current);});
  matrixCopy.addEventListener('click',()=>{if(!current)return;const n=Number(matrixSize.value);const equations=[
    transferMatrixTeX(transferMatrix(current,false,n),'H'),
    transferMatrixTeX(transferMatrix(current,true,n),'K'),
    'L_{'+n+'}(H)L_{'+n+'}(K)=L_{'+n+'}(K)L_{'+n+'}(H)=I_{'+n+'}',
    transferActionEquations(current.rows,n).forward.tex,
    transferActionEquations(current.rows,n).inverse.tex,
    transferProductMath(transferProductEntry(current,Number(productRow.value),Number(productColumn.value),productOrder.value,n)).tex
  ];clipboard(equations.join('\n\n'),'Displayed matrix LaTeX copied.');});
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
  composeVia.value=(eligible.find(entry=>entry.collection==='atlas'&&entry.kind==='lucas')||fib).id;suggestVia();
  const params=new URL(location.href).searchParams;fields.source.value=params.get('tr-source')||euler.id;fields.target.value=params.get('tr-target')||fib.id;fields.count.value=params.get('tr-count')||'12';suggest('source');suggest('target');updateWindowHelp();calculate();
  function validate(data){const a=lookup.get(normalizeText(canonicalID(data?.source||''))),b=lookup.get(normalizeText(canonicalID(data?.target||'')));if(!a||!b)throw Error('The saved transfer needs two available scalar records.');return {a,b,map:sequenceTransfer(a,b,data.count)};}
  return {snapshot:()=>current?{source:current.sourceId,target:current.targetId,count:current.count}:{source:fields.source.value,target:fields.target.value,count:Number(count.value)},validate,restore(data){const {a,b,map}=validate(data);fields.count.value=String(map.count);render(map,a,b,false);},source(entry){if(!lookup.has(normalizeText(entry.id)))return;fields.source.value=entry.id;try{const a=transferAnchor(entry),b=transferAnchor(resolve('target'));count.value=String(Math.min(Number(count.value)||12,48,a.available,b.available));}catch{}updateWindowHelp();calculate(true);host.scrollIntoView({block:'start'});fields.target.focus({preventScroll:true});}};
}
