import { createCompiler } from './lean-wasm/index.js';

export function moduleSource(source, name) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$/.test(name)) throw new Error('Invalid project module name.');
  // Prepared sources use ordinary import headers. This wrapper changes module
  // visibility for exported-only WASM artifacts, while retaining the proof body.
  const match = source.match(/^((?:import [^\n]+\n)+)/);
  if (!match) throw new Error('This workspace needs its original import header.');
  const header = match[1], body = source.slice(header.length), folder = name.split('.').slice(0,-1).join('/');
  return 'import Lean\n'+header+'run_cmd Lean.modifyEnv (fun env => env.setMainModule `'+name+')\npublic section\n'+body+
    '\nend\nrun_cmd do\n  IO.FS.createDirAll "/lib/lean/'+folder+'"\n  Lean.writeModule (← Lean.getEnv) "/lib/lean/'+name.replaceAll('.','/')+'.olean"\n';
}

export function outcome(result) {
  if (!result || result.exitCode !== 0) return 'failed';
  return result.errors.length ? 'warning' : 'passed';
}

const root = document.querySelector('[data-lean-local]');
if (root) start().catch(error => setStatus('Could not load the workspace: '+error.message,'failed'));
function el(name) { return root.querySelector('[data-local-'+name+']'); }
function setStatus(text,state='idle') {el('status').textContent=text;el('status').dataset.state=state;}
async function start() {
  const response=await fetch(new URL('examples.json',location.href));
  if (!response.ok) throw new Error('Source record unavailable.');
  const data=await response.json();
  let compiler=null, bootAbort=null, busy=false, generation=0, workspace, files, current=0;
  const editor=el('code'), picker=el('example'), filePicker=el('file');
  const draftKey='komorebi-lean-browser-reload';
  const log=text=>{el('log').textContent=(el('log').textContent+'\n'+text).slice(-20000);};
  function dispose() {bootAbort?.abort();bootAbort=null;compiler?.dispose();compiler=null;}
  function controls(value) {
    busy=value;editor.readOnly=value;picker.disabled=value;filePicker.disabled=value;
    for(const name of ['run','restore','break','save'])el(name).disabled=value;
    el('stop').disabled=!value;el('clear').disabled=value;
  }
  function showFile() {
    const file=workspace.files[current];editor.value=files[current];
    el('inspect').href=file.inspect;el('download').href=file.download;
    el('source').textContent=file.module+' · Original SHA-256 '+file.sha256.slice(0,16)+'…';
  }
  function choose(id) {
    dispose();workspace=data.examples.find(e=>e.id===id)||data.examples[0];picker.value=workspace.id;
    files=workspace.files.map(f=>f.text);current=files.length-1;filePicker.replaceChildren();
    workspace.files.forEach((f,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=f.module;filePicker.append(option);});
    filePicker.value=String(current);showFile();controls(false);el('output').textContent='No checks yet.';
    el('run').textContent='Load Lean and run';setStatus('Ready. Your first run downloads the compiler and required libraries.');
  }
  picker.addEventListener('change',()=>choose(picker.value));
  filePicker.addEventListener('change',()=>{files[current]=editor.value;current=Number(filePicker.value);showFile();});
  editor.addEventListener('input',()=>{files[current]=editor.value;setStatus('Edited. Run the workspace to check these changes.');});
  el('restore').addEventListener('click',()=>{files=workspace.files.map(f=>f.text);showFile();setStatus('Original workspace restored. Run it to check.');});
  el('break').addEventListener('click',()=>{files[current]=editor.value+'\nexample : (1 : Nat) = 2 := by rfl\n';showFile();setStatus('Added a false equality. Run Lean to see why it fails.');});
  el('save').addEventListener('click',()=>{
    const url=URL.createObjectURL(new Blob([editor.value],{type:'text/plain;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download=workspace.files[current].module.split('.').pop()+'-edited.lean';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  el('stop').addEventListener('click',()=>{generation++;dispose();controls(false);setStatus('Stopped. This run produced no result.');el('run').textContent='Restart Lean and run';});
  el('clear').addEventListener('click',async()=>{
    dispose();for(const name of await caches.keys())if(name.startsWith('komorebi-lean-'))await caches.delete(name);
    el('run').textContent='Load Lean and run';setStatus('Downloaded compiler cache cleared. Your edits are still in this tab.');
  });
  async function isolate() {
    if (crossOriginIsolated) return true;
    if (!isSecureContext || !navigator.serviceWorker) throw new Error('This browser cannot start the local compiler. Open the page directly in a current desktop browser.');
    log('Preparing browser isolation for the local compiler…');
    const registration=await navigator.serviceWorker.register(new URL('sw.js',location.href),{scope:new URL('./',location.href).pathname});
    await navigator.serviceWorker.ready;
    if (!navigator.serviceWorker.controller) await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{navigator.serviceWorker.removeEventListener('controllerchange',changed);reject(new Error('Browser setup timed out. Reload this page and try again.'));},20000);
      function changed(){clearTimeout(timer);navigator.serviceWorker.removeEventListener('controllerchange',changed);resolve();}
      navigator.serviceWorker.addEventListener('controllerchange',changed);
    });
    if (!crossOriginIsolated) {
      if (sessionStorage.getItem(draftKey+'-attempt')==='1') throw new Error('This browser did not enable the memory needed by Lean. Your edits are preserved.');
      sessionStorage.setItem(draftKey,JSON.stringify({id:workspace.id,files,current,run:true}));
      sessionStorage.setItem(draftKey+'-attempt','1');location.reload();return false;
    }
    return true;
  }
  async function run() {
    if (busy)return;files[current]=editor.value;controls(true);const ticket=++generation;
    el('output').textContent='Checking has not completed.';setStatus('Starting Lean on this device…','running');
    try {
      if (!await isolate())return;
      if (ticket!==generation)return;
      if(!compiler){
        const abort=new AbortController();bootAbort=abort;
        const created=await createCompiler({baseUrl:new URL('engine/',location.href).href,syntaxCheck:'full',signal:abort.signal,onProgress:m=>{if(ticket===generation)log(m);},onStatus:m=>{if(ticket===generation)log(m);}});
        if(ticket!==generation){created.dispose();return;}
        compiler=created;
      }
      await compiler.reset();
      let warnings=false;const results=[];
      for(let i=0;i<files.length;i++) {
        setStatus('Checking '+workspace.files[i].module+'…','running');
        // Export dependencies only. The last file runs with its original source.
        const source=i<files.length-1?moduleSource(files[i],workspace.files[i].module):files[i];
        const result=await compiler.run(source);
        if (ticket!==generation)return;
        const state=outcome(result);warnings ||= state==='warning';
        results.push(workspace.files[i].module+'\n'+(result.errors.join('\n')||'No diagnostics.')+(result.output?'\n'+result.output:'')+'\nChecked in '+(result.compileMs/1000).toFixed(2)+' s.');
        el('output').textContent=results.join('\n\n');
        if(state==='failed'){setStatus('Lean reported errors. The workspace did not pass.','failed');return;}
      }
      setStatus(warnings?'Checking completed with warnings. Review Lean’s response; a sorry warning means an unfinished proof.':'Checking completed with no diagnostics.',warnings?'warning':'passed');
    } catch(error) {
      if(ticket!==generation)return;
      el('output').textContent=String(error.message||error);setStatus('Checking could not complete. No successful result.','failed');dispose();
    } finally {
      if(ticket===generation){controls(false);el('run').textContent=compiler?'Run workspace':'Restart Lean and run';}
    }
  }
  el('run').addEventListener('click',run);
  choose(new URL(location.href).searchParams.get('example'));
  const saved=sessionStorage.getItem(draftKey);
  if(saved){
    sessionStorage.removeItem(draftKey);
    try{const draft=JSON.parse(saved);choose(draft.id);if(Array.isArray(draft.files)&&draft.files.length===files.length&&draft.files.every(f=>typeof f==='string')){files=draft.files;current=Math.min(draft.current,files.length-1);filePicker.value=String(current);showFile();}if(draft.run)await run();}catch{setStatus('Browser setup finished. Run Lean to begin.');}
  }
  if(crossOriginIsolated)sessionStorage.removeItem(draftKey+'-attempt');
}
