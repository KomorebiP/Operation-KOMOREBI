const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

async function fixture(query = '?file=second') {
  const nodes = {};
  for (const key of ['#lean-run-search','#lean-run-file','[data-lean-run-count]','[data-lean-run-selection]',
    '#lean-run-command',...['work','name','path','mode','pin','issues','inspect'].map(x=>`[data-run-${x}]`)]) {
    nodes[key] = {value:'',hidden:true,textContent:'',listeners:{},
      addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(...children){this.children=children;this.value=children[0]?.value||'';}};
  }
  const files = [{id:'first',path:'one/Proof.lean',work:'paper-i',mode:'retained-project',input_files:2,issues:[],toolchain:'v4.34',url:'read/one.html'},
    {id:'second',path:'two/Proof.lean',work:'paper-ii',mode:'reconstructed-workspace',input_files:1,issues:['Missing import Test'],toolchain:'v4.34',url:'read/two.html'}];
  const root = {dataset:{catalog:'run.json'},querySelector:s=>nodes[s]};
  const location={href:'https://example.test/lean/run.html'+query};
  const window={listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}};
  vm.runInNewContext(fs.readFileSync('website/assets/lean-execution.js','utf8'),{
    document:{querySelector:()=>root,createElement:()=>({})},location,URL,window,
    history:{replaceState(a,b,url){location.href=String(url);}},
    fetch:async()=>({ok:true,json:async()=>({files})})
  });
  await new Promise(resolve=>setImmediate(resolve));
  return {nodes,files,location,window};
}

test('a source deep link selects its exact path, environment, and command',async()=>{
  const f=await fixture();
  assert.equal(f.nodes['[data-run-path]'].textContent,'two/Proof.lean');
  assert.match(f.nodes['[data-run-mode]'].textContent,/Reconstructed/);
  assert.match(f.nodes['#lean-run-command'].value,/--source 'two\/Proof.lean'/);
  assert.equal(f.nodes['[data-run-inspect]'].href,'../read/two.html');
  assert.equal(f.nodes['[data-run-issues]'].hidden,false);
});

test('filtering does not silently change the selected run command',async()=>{
  const f=await fixture();const before=f.nodes['#lean-run-command'].value;
  f.nodes['#lean-run-search'].value='one/';f.nodes['#lean-run-search'].listeners.input();
  assert.equal(f.nodes['#lean-run-file'].children.length,2);
  assert.equal(f.nodes['#lean-run-file'].value,'second');
  assert.equal(f.nodes['#lean-run-command'].value,before);
  f.nodes['#lean-run-file'].value='first';
  f.nodes['#lean-run-file'].listeners.change();
  assert.match(f.nodes['#lean-run-command'].value,/one\/Proof.lean/);
  assert.equal(new URL(f.location.href).searchParams.get('file'),'first');
});

test('an unknown deep link is reported instead of running a different file',async()=>{
  const f=await fixture('?file=unknown');
  assert.equal(f.nodes['[data-lean-run-selection]'].hidden,true);
  assert.match(f.nodes['[data-lean-run-count]'].textContent,/not in this catalogue/);
});

test('history restores the exact selected source even when a filter excludes it',async()=>{
  const f=await fixture();
  f.nodes['#lean-run-search'].value='one/';f.nodes['#lean-run-search'].listeners.input();
  f.nodes['#lean-run-file'].value='first';f.nodes['#lean-run-file'].listeners.change();
  f.location.href='https://example.test/lean/run.html?file=second';
  f.window.listeners.popstate();
  assert.equal(f.nodes['#lean-run-file'].value,'second');
  assert.match(f.nodes['#lean-run-command'].value,/two\/Proof.lean/);
});
