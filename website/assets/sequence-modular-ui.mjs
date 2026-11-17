import {validateFamily} from './sequence-family-core.mjs';
import {modularCSV} from './sequence-modular-core.mjs';
import {mathLine} from './sequence-math.mjs';
import {enhanceMath} from './math-display.mjs';
import {node,indexedTable,job,download,plotValues,copyTools,plotExports,svg} from './sequence-research-common.mjs';
export function mountModular(host,{family}={}){
  if(!host)return null;host.classList.add('sg-tool');host.innerHTML=`<form id="md-form"><div class="sar-controls"><label for="md-k">Step count k<input id="md-k" type="number" min="2" max="16" value="2"></label><label for="md-r">Reciprocal power r<input id="md-r" type="number" min="1" max="8" value="1"></label><label for="md-c">Step weight c<input id="md-c" type="number" min="1" max="5" value="1"></label><label for="md-seedMode">Initial values<select id="md-seedMode"><option value="tail">Nonzero tail</option><option value="zero">k−1 zeros, then one</option><option value="custom">My initial values</option></select></label><label for="md-seeds">k initial values<input id="md-seeds" value="0, 1" maxlength="2000"></label><label for="md-modulus">Modulus m<input id="md-modulus" type="number" min="2" max="256" value="7"></label><label for="md-maximum">Complete states to search<input id="md-maximum" type="number" min="1" max="20000" value="5000"></label></div><div class="sp-actions"><button type="submit">Compute modular certificate</button><button type="button" id="md-cancel" disabled>Cancel modular search</button><button type="button" id="md-current">Use current k-step family</button><button type="button" id="md-share">Copy modular link</button><button type="button" id="md-csv">Download modular CSV</button><button type="button" id="md-json">Download modular certificate</button></div></form><p id="md-status" role="status" aria-live="polite"></p><p id="md-error" role="alert" hidden></p><div id="md-result"></div>`;
  const $=id=>host.querySelector('#md-'+id),runner=job(),clipboard=copyTools(host);
  if(!family){
    $('current').disabled=true;
    $('current').title='Open the family explorer before using this shortcut.';
    const link=node('a','Open the family explorer');
    link.href='sequence-research.html#generalized';
    $('current').after(link);
  }let current=null,requestId=0;const fields=['k','r','c','seedMode','seeds'];
  function read(){return {params:validateFamily('linear',Object.fromEntries(fields.map(k=>[k,$(k).value]))),modulus:Number($('modulus').value),maximum:Number($('maximum').value)};}
  function validate(s){if(!s)throw Error('Choose valid modular parameters.');validateFamily('linear',s.params);if(!Number.isSafeInteger(s.modulus)||s.modulus<2||s.modulus>256||!Number.isSafeInteger(s.maximum)||s.maximum<1||s.maximum>20000)throw Error('Choose a modulus from 2 to 256 and a search bound from 1 to 20,000.');return s;}
  function fail(error){$('error').hidden=false;$('error').textContent=error.message;}
  function frequency(result){const counts=Array(result.modulus).fill(0);for(const v of result.values)counts[v]++;const picture=svg('svg',{viewBox:'0 0 800 240',class:'sg-frequency',role:'img','aria-label':'Residue frequencies in the displayed finite window'});picture.append(svg('rect',{width:800,height:240,fill:'var(--sq-bg,#fff)'}));const max=Math.max(1,...counts);for(let i=0;i<counts.length;i++){const bar=svg('rect',{x:45+i*730/counts.length,y:200-160*counts[i]/max,width:Math.max(1,730/counts.length-2),height:160*counts[i]/max,fill:'var(--sq-link,#185a43)'});bar.append(svg('title',{},`Residue ${i}: ${counts[i]} displayed terms`));picture.append(bar);}picture.append(svg('text',{x:45,y:225,fill:'currentColor','font-size':13},`Residues 0–${result.modulus-1}; counts from ${result.values.length} displayed values`));return picture;}
  function deferredPanel(label,build){
    const details=node('details');details.className='sg-data-panel';
    const summary=node('summary',label);details.append(summary);
    details.addEventListener('toggle',()=>{
      if(details.open&&!details.dataset.filled){
        details.append(build());details.dataset.filled='true';
      }
    });
    return details;
  }
  function render(result){$('result').replaceChildren();$('result').append(node('h3',result.certified?`Certified cycle: period ${result.period}, preperiod ${result.preperiod}`:'No repeated complete state within the chosen bound'),node('p',`Recurrence order ${result.model.order}. ${result.scanned} complete states inspected modulo ${result.modulus}.`),node('p',result.scope));if(result.certified)$('result').append(node('p',`The state at n=${result.preperiod} repeats at n=${result.repeatIndex}: (${result.repeatedState.join(', ')}).`));
    const detail=node('details');detail.append(node('summary','Recurrence, initial state and certificate interpretation'),mathLine('a(n) = sum_(j=1)^d b(j) a(n-j), n >= d',String.raw`a_n=\sum_{j=1}^{d}b_j a_{n-j},\qquad n\ge d`,'sr-modular-equation'),node('p','Here d is the recurrence order. The coefficients b(1), …, b(d) are reduced modulo m.'),node('p','Coefficients: '+result.coefficients.join(', ')),node('p','Initial complete state: '+result.initialState.join(', ')),node('p','A repeated value alone does not certify a cycle. The certificate checks every coordinate of the recurrence state. A noninvertible transition can have a preperiod.'));detail.addEventListener('toggle',()=>{if(detail.open)enhanceMath(detail);});$('result').append(detail);
    const chart=node('div'),inspection=node('p'),plotControls=node('div'),
      plotPrev=node('button','Previous window'),plotNext=node('button','Next window'),
      startLabel=node('label','Plot start index'),startInput=node('input'),
      sampleNote=node('p');let plotStart=0;
    chart.id='md-chart';inspection.setAttribute('role','status');
    plotControls.id='md-plot-controls';plotControls.className='sg-plot-controls';
    plotControls.hidden=result.values.length<=128;
    for(const button of [plotPrev,plotNext])button.type='button';
    plotPrev.id='md-plot-back';plotNext.id='md-plot-next';
    startInput.id='md-plot-start';startInput.type='number';
    startInput.min='0';startInput.max=String(Math.max(0,result.values.length-1));
    startInput.step='1';startInput.value='0';
    startLabel.htmlFor=startInput.id;startLabel.append(startInput);
    plotControls.append(plotPrev,startLabel,plotNext);
    sampleNote.className='sg-plot-note';sampleNote.id='md-plot-note';
    startInput.setAttribute('aria-describedby',sampleNote.id);
    function drawPlot(start){
      if(!Number.isSafeInteger(start)||start<0||start>=result.values.length){
        sampleNote.textContent='Enter a plot start index from 0 to '+Math.max(0,result.values.length-1)+'.';
        startInput.value=String(plotStart);return;
      }
      plotStart=start;
      const end=Math.min(start+128,result.values.length);
      const values=result.values.slice(start,end);
      plotValues(chart,values.map(String),{offset:start,modulus:result.modulus,
        label:'Modular recurrence orbit, indices '+start+' through '+(end-1),
        inspect:(local,v)=>{inspection.textContent='n='+(start+local)+'; residue '+v+' modulo '+result.modulus;}});
      inspection.textContent='Select a plotted point to inspect its exact index and residue.';
      sampleNote.textContent=(end===result.values.length&&start===0
        ?'The plot shows all '+result.values.length+' retained residue samples.'
        :'Plot positions '+start+'–'+(end-1)+' of '+result.values.length+' retained residue samples.')
        +' The search inspected '+result.scanned+' complete states; the certificate retains up to 256 residue samples and 64 initial state snapshots.';
      plotPrev.disabled=start===0;plotNext.disabled=end===result.values.length;
      startInput.value=String(start);
    }
    plotPrev.addEventListener('click',()=>drawPlot(Math.max(0,plotStart-128)));
    plotNext.addEventListener('click',()=>drawPlot(Math.min(result.values.length-1,plotStart+128)));
    startInput.addEventListener('change',()=>drawPlot(Number(startInput.value)));
    drawPlot(0);
    $('result').append(plotControls,chart,inspection,sampleNote,
      deferredPanel('Residue frequency chart ('+result.modulus+' residue classes)',()=>frequency(result)),
      deferredPanel('Retained modular values ('+result.values.length+' rows)',()=>indexedTable(
        ['n','a(n) mod m'],result.values.map((v,n)=>[n,v]),'Retained exact modular values')),
      deferredPanel('Initial recurrence states ('+result.states.length+' rows)',()=>indexedTable(
        ['State position n','Complete state'],result.states.map((state,n)=>[n,'('+state.join(', ')+')']),'Initial complete recurrence-state snapshots')));
    const exports=node('div');exports.className='sp-actions';
    plotExports(exports,chart,'modular',clipboard.status);$('result').append(exports);}
  async function compute(update=false){const token=++requestId;runner.cancel();try{const s=validate(read());$('error').hidden=true;$('cancel').disabled=false;$('status').textContent='Searching exact complete states…';const result=await runner.run({type:'modular',...s});if(token!==requestId)return;current=result;render(result);$('status').textContent=result.certified?'A repeated complete state certifies the displayed cycle.':'The search reached its limit without finding a repeated complete state. No period is asserted.';host.dataset.modularReady='true';if(update){const url=new URL(location.href);url.search='';url.hash='modular-dynamics';url.searchParams.set('modular',JSON.stringify(s));history.replaceState(null,'',url.href);}}catch(error){if(token!==requestId)return;if(error.name==='AbortError')$('status').textContent='Modular search cancelled.';else fail(error);}finally{if(token===requestId)$('cancel').disabled=true;}}
  function restore(s,run=true){validate(s);const p=validateFamily('linear',s.params);for(const k of fields)$(k).value=String(p[k]);$('r').disabled=p.seedMode!=='tail';$('modulus').value=String(s.modulus);$('maximum').value=String(s.maximum);if(run)compute();}
  $('seedMode').addEventListener('change',()=>{if($('seedMode').value!=='tail')$('r').value='1';$('r').disabled=$('seedMode').value!=='tail';});
  $('form').addEventListener('submit',event=>{event.preventDefault();compute(true);});$('cancel').addEventListener('click',()=>runner.cancel());$('current').addEventListener('click',()=>{const value=family?.value();if(!value||!['linear','kbonacci'].includes(value.engine)){fail(Error('Choose a k-step family in the family explorer first.'));return;}restore({params:value.params,modulus:Number($('modulus').value),maximum:Number($('maximum').value)});});$('share').addEventListener('click',()=>{try{const s=validate(read()),url=new URL(location.href);url.search='';url.hash='modular-dynamics';url.searchParams.set('modular',JSON.stringify(s));clipboard.copy(url.href,'Modular link copied.');}catch(error){fail(error);}});$('csv').addEventListener('click',()=>{if(current)download(modularCSV(current),'modular-orbit.csv','text/csv;charset=utf-8');else fail(Error('Compute a modular result first.'));});$('json').addEventListener('click',()=>{if(current)download(JSON.stringify(current,null,2)+'\n','modular-certificate.json');else fail(Error('Compute a modular result first.'));});
  try{const raw=new URL(location.href).searchParams.get('modular');if(raw){if(raw.length>5000)throw Error('The modular link is too long.');restore(JSON.parse(raw),false);}}catch(error){fail(error);}compute();
  return {snapshot:()=>validate(read()),validate,restore};
}
