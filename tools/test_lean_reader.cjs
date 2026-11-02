const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function fixture(url='https://example.test/lean/paper-i/index.html?keep=1&q=real#files'){
  const listeners={},input={value:'',addEventListener:(name,fn)=>listeners['input:'+name]=fn};
  const form={hidden:true,querySelector:()=>input,addEventListener:(name,fn)=>listeners['form:'+name]=fn};
  const items=['formal/Main.lean theorem real','formal/Other.lean def Γ'].map(value=>({dataset:{leanSearch:value},hidden:false}));
  const status={textContent:''},location={href:url};
  vm.runInNewContext(fs.readFileSync('website/assets/lean-reader.js','utf8'),{
    document:{querySelector:s=>s==='.lean-filter'?form:s==='.lean-count'?status:null,querySelectorAll:()=>items},
    window:{addEventListener:(name,fn)=>listeners[name]=fn},location,URL,
    history:{replaceState:(a,b,value)=>{location.href=value.href;}}
  });
  return {form,input,items,status,listeners,location};
}
test('shared queries filter declaration names and retain unrelated address state',()=>{
  const f=fixture();assert.equal(f.form.hidden,false);assert.deepEqual(f.items.map(x=>x.hidden),[false,true]);
  f.input.value='OTHER Γ';f.listeners['input:input']();assert.deepEqual(f.items.map(x=>x.hidden),[true,false]);
  const url=new URL(f.location.href);assert.equal(url.searchParams.get('keep'),'1');assert.equal(url.hash,'#files');
  assert.equal(url.searchParams.get('q'),'OTHER Γ');assert.equal(f.status.textContent,'1 of 2 files');
});

test('source outline filters names and kinds without modifying source or its address',()=>{
  for(const wide of [false,true]){
    const listeners={},input={value:'',addEventListener:(n,f)=>listeners['input:'+n]=f};
    const form={hidden:true,querySelector:()=>input,addEventListener:(n,f)=>listeners['form:'+n]=f};
    const entries=['theorem energy','def Γ'].map(value=>({dataset:{leanDeclaration:value},hidden:false}));
    const status={textContent:''},outline={open:false,querySelector:s=>s==='.lean-outline-filter'?form:status,querySelectorAll:()=>entries};
    vm.runInNewContext(fs.readFileSync('website/assets/lean-reader.js','utf8'),{
      document:{querySelector:s=>s==='[data-lean-outline]'?outline:null},
      window:{matchMedia:()=>({matches:wide}),addEventListener:(n,f)=>listeners[n]=f}
    });
    assert.equal(outline.open,wide);assert.equal(form.hidden,false);
    input.value='DEF γ';listeners['input:input']();assert.deepEqual(entries.map(e=>e.hidden),[true,false]);
    input.value='missing';listeners['input:input']();assert.match(status.textContent,/0 of 2/);
    listeners['form:reset']();assert.ok(entries.every(e=>!e.hidden));
    let prevented=false;listeners['form:submit']({preventDefault(){prevented=true;}});assert.equal(prevented,true);
  }
});
test('empty results, reset, restored page state and browser history remain usable',()=>{
  const f=fixture();f.input.value='missing';f.listeners['input:input']();
  assert.ok(f.items.every(x=>x.hidden));assert.match(f.status.textContent,/0 of 2/);
  f.listeners['form:reset']();assert.ok(f.items.every(x=>!x.hidden));
  assert.equal(new URL(f.location.href).searchParams.has('q'),false);
  f.location.href='https://example.test/lean/paper-i/index.html?q=Main';f.listeners.popstate();
  assert.equal(f.input.value,'Main');assert.deepEqual(f.items.map(x=>x.hidden),[false,true]);
  f.input.value='restored native value';f.listeners.pageshow();assert.equal(f.input.value,'Main');
  let prevented=false;f.listeners['form:submit']({preventDefault(){prevented=true;}});assert.equal(prevented,true);
});
