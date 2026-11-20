// Progressive controls for the static worked-example reading edition.
// Author: Komorebi P. The examples remain usable without JavaScript.
const gallery=document.querySelector('#kernel-examples');
if(gallery){
  const examples=[...gallery.querySelectorAll('.sl-kernel-example')];
  const controls=gallery.querySelector('.sl-example-controls');
  if(controls){
    controls.hidden=false;
    controls.addEventListener('click',event=>{
      const button=event.target.closest('button[data-example-action]');
      if(!button)return;
      const open=button.dataset.exampleAction==='open';
      for(const example of examples)example.open=open;
    });
  }
  function revealExample(){
    let id;
    try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
    const target=document.getElementById(id);
    const example=target?.closest('.sl-kernel-example');
    if(!example||!gallery.contains(example))return;
    example.open=true;
    requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));
  }
  window.addEventListener('hashchange',revealExample);
  revealExample();
  let printState;
  window.addEventListener('beforeprint',()=>{
    if(printState)return;
    printState=examples.map(example=>example.open);
    for(const example of examples)example.open=true;
  });
  window.addEventListener('afterprint',()=>{
    if(!printState)return;
    examples.forEach((example,index)=>{example.open=printState[index];});
    printState=undefined;
  });
}
