import {rational,text,coefficients,classify,normalizedTerms} from './sequence-hankel-orders-core.mjs';
const panel=document.querySelector('[data-hankel-orders]');
if(panel)start(panel);
async function start(root){
  const form=root.querySelector('#sho-form'),tInput=root.querySelector('#sho-t'),qInput=root.querySelector('#sho-q');
  const error=root.querySelector('#sho-error'),results=root.querySelector('#sho-results');
  try{
    const response=await fetch(root.dataset.coefficients);if(!response.ok)throw Error('Exact coefficients are unavailable.');
    const rows=coefficients(await response.json());
    const names={'1+1+1+1':'four simple roots','2+1+1':'one double root and two simple roots','2+2':'two double roots','3+1':'one triple root and one simple root'};
    function calculate(updateHistory=true){
      let field=tInput;
      try{
        error.hidden=true;tInput.removeAttribute('aria-invalid');qInput.removeAttribute('aria-invalid');
        const t=rational(tInput.value);if(!t.n)throw Error('Choose t nonzero; Theorem M covers the boundary.');
        field=qInput;const q=rational(qInput.value);if(!q.n)throw Error('Choose q nonzero; Theorem M covers the boundary.');
        const result=classify(t,q,rows),terms=normalizedTerms(t,q,8);
        const output=root.querySelector('#sho-order');output.dataset.order=String(result.order);
        output.textContent='Minimal eventual order '+result.order+'.';
        root.querySelector('#sho-detail').textContent='t='+result.t+', q='+result.q+'. The quartic has '+names[result.root_type]+
          '; h='+result.distinct_bases+' distinct exponential bases.'+
          (result.negative_full_collision?' The −2au collision lowers one additional degree.':'')+
          ' The recurrence starts at N=1; W₀=1 is retained separately.';
        const body=root.querySelector('#sho-terms');
        body.replaceChildren(...terms.map((value,index)=>{
          const tr=document.createElement('tr'),th=document.createElement('th'),td=document.createElement('td'),code=document.createElement('code');
          th.scope='row';th.textContent=String(index);code.textContent=value;td.append(code);tr.append(th,td);return tr;
        }));
        root.querySelectorAll('[data-order-t]').forEach(button=>button.setAttribute('aria-pressed',String(
          text(rational(button.dataset.orderT))===result.t&&text(rational(button.dataset.orderQ))===result.q)));
        const link=new URL('sequence-hankel-compression.html',location.href);
        link.searchParams.set('ho-t',result.t);link.searchParams.set('ho-q',result.q);link.hash='interior-order-calculator';
        root.querySelector('#sho-link').href=link.href;
        if(updateHistory){try{history.replaceState(history.state,'',link.href);}catch{}}
        results.hidden=false;
      }catch(problem){
        results.hidden=true;error.textContent=problem.message;error.hidden=false;
        field.setAttribute('aria-invalid','true');field.focus({preventScroll:true});
      }
    }
    const query=new URLSearchParams(location.search);
    if(query.has('ho-t'))tInput.value=query.get('ho-t');
    if(query.has('ho-q'))qInput.value=query.get('ho-q');
    form.addEventListener('submit',event=>{event.preventDefault();calculate();});
    root.querySelectorAll('[data-order-t]').forEach(button=>button.addEventListener('click',()=>{
      tInput.value=button.dataset.orderT;qInput.value=button.dataset.orderQ;calculate();
    }));
    form.hidden=false;calculate(false);root.dataset.ordersReady='true';
  }catch(problem){
    form.hidden=true;error.textContent='The exact calculator could not load. The worked example and complete proof remain available below.';error.hidden=false;
  }
}
