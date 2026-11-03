import { createCompiler } from './lean-wasm/index.js?v=20261102';
import { sourceHeader } from './lean-wasm/roots.js';
import { loadSourceBundle, sourceWorkspace } from './lean-source-bundle.js?v=20261102';

export function moduleSource(source, name) {
  if (!/^[\p{ID_Start}_][\p{ID_Continue}']*(\.[\p{ID_Start}_][\p{ID_Continue}']*)*$/u.test(name)) throw new Error('Invalid project module name.');
  // Prepared sources use ordinary import headers. This wrapper changes module
  // visibility for exported-only WASM artifacts, while retaining the proof body.
  const {prefix,body,moduleEnd}=sourceHeader(source),folder=name.split('.').slice(0,-1).join('/');
  const header=prefix.slice(0,moduleEnd)+'import Lean\n'+prefix.slice(moduleEnd);
  return header+(header.endsWith('\n')?'':'\n')+'run_cmd Lean.modifyEnv (fun env => env.setMainModule `'+name+')\n@[expose] public section\n'+body+
    '\nend\nrun_cmd do\n  IO.FS.createDirAll "/lib/lean/'+folder+'"\n  Lean.writeModule (← Lean.getEnv) "/lib/lean/'+name.replaceAll('.','/')+'.olean"\n';
}

export function outcome(result) {
  if (!result || result.exitCode !== 0) return 'failed';
  return result.errors.length ? 'warning' : 'passed';
}

export function withCompatibility(source,compatibility) {
  if(!compatibility)return source;
  const {prefix,body}=sourceHeader(source);
  return prefix+(prefix&&!prefix.endsWith('\n')?'\n':'')+compatibility+body;
}

export function withCompatibilityImport(source,module) {
  const {prefix,body}=sourceHeader(source);
  return prefix+(prefix&&!prefix.endsWith('\n')?'\n':'')+'import '+module+'\n'+body;
}
export function mapCompatibilityImport(text,source) {
  const {prefix}=sourceHeader(source),line=(prefix.match(/\n/g)||[]).length+1;
  return text.replace(/line (\d+)/g,(_,n)=>Number(n)===line?'browser compatibility import':'line '+(Number(n)>line?Number(n)-1:Number(n)));
}

export function mapDiagnostic(text,source,exported=false,compatibility='') {
  const {prefix:header,moduleEnd}=sourceHeader(source);
  const headerLines=(header.match(/\n/g)||[]).length;
  const sourceLines=source.split('\n').length;
  const added=(compatibility.match(/\n/g)||[]).length;
  return text.replace(/line (\d+)/g,(_,number)=>{
    const n=Number(number);
    if(exported){
      const importLine=(source.slice(0,moduleEnd).match(/\n/g)||[]).length+1;
      if(n===importLine||n>headerLines+1&&n<=headerLines+3)return 'browser module setup';
      if(n>sourceLines+3)return 'browser module export';
      return 'line '+(n<importLine?n:n<=headerLines+1?n-1:n-3);
    }
    if(added&&n>headerLines){
      if(n<=headerLines+added)return 'browser compatibility lemma';
      return 'line '+(n-added);
    }
    return 'line '+n;
  });
}

export function mapWorkspaceDiagnostic(diagnostic,source,exported=false,compatibility='',originalSource=null) {
  if(diagnostic.origin==='syntax-guard')return 'Browser syntax check: '+diagnostic.text;
  // Dependencies are parsed before the export wrapper is added, so their
  // parser locations are already in source coordinates. Elaboration locations
  // still refer to the generated wrapper and need the normal adjustment.
  const wrapped=exported&&diagnostic.origin!=='syntax-input';
  const mapped=mapDiagnostic(diagnostic.text,source,wrapped,compatibility);
  return originalSource===null?mapped:mapCompatibilityImport(mapped,originalSource);
}

const root = document.querySelector('[data-lean-local]');
if (root) start().catch(error => setStatus('Could not load the workspace: '+error.message,'failed'));
function el(name) { return root.querySelector('[data-local-'+name+']'); }
function setStatus(text,state='idle') {el('status').textContent=text;el('status').dataset.state=state;}
async function start() {
  const response=await fetch(new URL('examples.json',location.href));
  if (!response.ok) throw new Error('Source record unavailable.');
  const data=await response.json();
  if(window.top!==window){el('direct').hidden=false;el('direct-link').href=location.href;}
  let compiler=null, bootAbort=null, busy=false, generation=0, workspace, files, current=0;
  let catalog=null,catalogPending=null,openedGroup=null;
  let checkedDependencies=null;
  const drafts=new Map();
  const editor=el('code'), picker=el('example'), filePicker=el('file');
  const draftKey='komorebi-lean-browser-reload';
  const log=text=>{el('log').textContent=(el('log').textContent+'\n'+text).slice(-20000);};
  function dispose() {bootAbort?.abort();bootAbort=null;compiler?.dispose();compiler=null;checkedDependencies=null;}
  function controls(value) {
    busy=value;editor.readOnly=value;picker.disabled=value;filePicker.disabled=value;
    for(const name of ['run','restore','break','save'])el(name).disabled=value;
    el('stop').disabled=!value;el('clear').disabled=value;
    el('catalog-open').disabled=value||!catalog||!el('catalog-choice').value;
    el('catalog-choice').disabled=value||!catalog;
    el('catalog-search').disabled=value;el('catalog-ready').disabled=value;
  }
  function showFile() {
    const file=workspace.files[current];editor.value=files[current];
    el('inspect').hidden=!file.inspect;if(file.inspect)el('inspect').href=file.inspect;
    el('download').href=file.download;
    el('inspect').textContent=file.library?'Inspect pinned Mathlib source':file.generated?'Inspect browser compatibility source':'Inspect original source';
    el('download').textContent=file.library?'Download library source':file.generated?'Download compatibility source':'Download original';
    el('source').textContent=file.module+' · '+(file.library?'Pinned Mathlib '+file.revision.slice(0,8):file.generated?'Browser compatibility':'Original')+' SHA-256 '+file.sha256.slice(0,16)+'…';
  }
  function choose(id) {
    if(workspace){files[current]=editor.value;drafts.set(workspace.id,{files:[...files],current});}
    dispose();workspace=data.examples.find(e=>e.id===id)||data.examples[0];picker.value=workspace.id;
    const draft=drafts.get(workspace.id);files=draft?[...draft.files]:workspace.files.map(f=>f.text);current=draft?.current??files.length-1;filePicker.replaceChildren();
    workspace.files.forEach((f,i)=>{const option=document.createElement('option');option.value=String(i);option.textContent=f.module+(f.library?' · library source':'');filePicker.append(option);});
    filePicker.value=String(current);showFile();controls(false);el('output').textContent='No checks yet.';
    el('compat').hidden=!workspace.compatibility;
    el('compat-code').textContent=workspace.compatibility?.source||'';
    el('route').hidden=!workspace.exploratory;
    el('route-notes').textContent=workspace.exploratory?[
      ...(workspace.issues.length?workspace.issues:['The recorded import route uses available browser libraries. Run Lean to check the sources.']),
      ...(workspace.library?.length?['This route compiles '+workspace.library.length+' pinned Mathlib source module(s) before the retained sources. They are visible in the file picker and must pass Lean too.']:[]),
      ...(workspace.tactics?['A generated Mathlib.Tactic module supplies the available tactic subset. It is checked first and is visible in the file picker.']:[]),
      ...(workspace.legacy?['A generated version-compatibility module proves the newer dite_eq_left name using this runtime’s dif_pos. It is checked first and imported without changing the retained proof body.']:[])
    ].join('\n\n'):'';
    el('run').textContent='Load Lean and run';setStatus('Ready. Your first run downloads the compiler and required libraries.');
    const address=new URL(location.href);
    if(workspace.exploratory){address.searchParams.delete('example');address.searchParams.set('file',workspace.id.slice(7));}
    else{address.searchParams.delete('file');address.searchParams.set('example',workspace.id);}
    history.replaceState(null,'',address);
  }
  async function getCatalog() {
    if(catalog)return catalog;
    catalogPending??=(async()=>{
      const response=await fetch(new URL(data.collection_catalog||'catalog.json',location.href),{cache:'no-cache',credentials:'omit'});
      if(!response.ok)throw new Error('Retained source catalogue could not load.');
      const next=await response.json();
      if(next.schema!==1||next.revision!==data.revision||!Array.isArray(next.entries)||!Array.isArray(next.inputs))throw new Error('The source catalogue changed. Reload this page to use the current release.');
      catalog=next;renderCatalog();return catalog;
    })().catch(error=>{catalogPending=null;throw error;});
    return catalogPending;
  }
  function renderCatalog() {
    if(!catalog)return;
    const query=el('catalog-search').value.trim().toLowerCase(),ready=el('catalog-ready').checked;
    const entries=catalog.entries.filter(e=>(!ready||!e.issues.length)&&(!query||(e.label+' '+e.path).toLowerCase().includes(query)));
    const picker=el('catalog-choice');picker.replaceChildren();
    for(const entry of entries){const option=document.createElement('option');option.value=entry.id;option.textContent=entry.label+' · '+entry.path;picker.append(option);}
    picker.disabled=busy||!entries.length;el('catalog-open').disabled=busy||!entries.length;
    el('catalog-status').textContent=entries.length+' source files match. Import availability is a preflight check; Run Lean determines the actual result.';
  }
  async function openSource(id) {
    const ticket=++generation;dispose();controls(true);setStatus('Opening retained source and local dependencies…','running');
    const abort=new AbortController();bootAbort=abort;
    try {
      const collection=await getCatalog(),entry=collection.entries.find(e=>e.id===id);
      if(!entry)throw new Error('This file is not in the retained reading collection.');
      const prepared=data.examples.find(e=>!e.exploratory&&e.files.at(-1).path===entry.path);
      if(prepared){choose(prepared.id);return true;}
      if(data.examples.some(e=>e.id==='source-'+id)){choose('source-'+id);return true;}
      abort.signal.throwIfAborted();
      const bundle=await loadSourceBundle(collection.bundle,{signal:abort.signal,onProgress:m=>{if(ticket===generation)setStatus(m,'running');}});
      const next=await sourceWorkspace(collection,entry,bundle,{signal:abort.signal});
      if(ticket!==generation)return false;
      for(const file of next.files){file.download=URL.createObjectURL(new Blob([file.originalBytes],{type:'text/plain;charset=utf-8'}));delete file.originalBytes;}
      if(!data.examples.some(e=>e.id===next.id)) {
        data.examples.push(next);
        if(!openedGroup){openedGroup=document.createElement('optgroup');openedGroup.label='Opened retained sources';picker.append(openedGroup);}
        const option=document.createElement('option');option.value=next.id;option.textContent=next.title;openedGroup.append(option);
      }
      choose(next.id);return true;
    } catch(error) {
      if(ticket!==generation)return false;
      if(!workspace)choose(data.examples[0].id);
      setStatus('Could not open retained sources: '+error.message,'failed');return false;
    } finally {if(ticket===generation)controls(false);}
  }
  async function chooseId(id) {
    if(id?.startsWith('source-')&&!data.examples.some(e=>e.id===id))return openSource(id.slice(7));
    choose(id);return true;
  }
  el('catalog').addEventListener('toggle',()=>{if(el('catalog').open)getCatalog().catch(e=>{el('catalog-status').textContent=e.message;});});
  el('catalog-search').addEventListener('input',renderCatalog);
  el('catalog-ready').addEventListener('change',renderCatalog);
  el('catalog-open').addEventListener('click',()=>openSource(el('catalog-choice').value));
  picker.addEventListener('change',()=>choose(picker.value));
  filePicker.addEventListener('change',()=>{files[current]=editor.value;current=Number(filePicker.value);showFile();});
  editor.addEventListener('input',()=>{files[current]=editor.value;setStatus('Edited. Run the workspace to check these changes.');});
  el('restore').addEventListener('click',()=>{files=workspace.files.map(f=>f.text);showFile();setStatus('Original workspace restored. Run it to check.');});
  el('break').addEventListener('click',()=>{files[current]=editor.value+'\nexample : (1 : Nat) = 2 := by rfl\n';showFile();setStatus('Added a false equality. Run Lean to see why it fails.');});
  el('save').addEventListener('click',()=>{
    const url=URL.createObjectURL(new Blob([editor.value],{type:'text/plain;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download=workspace.files[current].module.split('.').pop()+'-edited.lean';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  el('stop').addEventListener('click',()=>{generation++;dispose();controls(false);el('output').textContent='Stopped. No result for this run.';setStatus('Stopped. This run produced no result.');el('run').textContent='Restart Lean and run';});
  el('clear').addEventListener('click',async()=>{
    dispose();for(const name of await caches.keys())if(name.startsWith('komorebi-lean-'))await caches.delete(name);
    el('run').textContent='Load Lean and run';setStatus('Downloaded compiler cache cleared. Your edits are still in this tab.');
  });
  async function isolate(ticket) {
    if(window.top!==window)throw new Error('Open this workspace in its own browser tab using the link above.');
    if (crossOriginIsolated) return true;
    if (!isSecureContext || !navigator.serviceWorker) throw new Error('This browser cannot start the local compiler. Open the page directly in a current desktop browser.');
    log('Preparing browser isolation for the local compiler…');
    const registration=await navigator.serviceWorker.register(new URL('sw.js',location.href),{scope:new URL('./',location.href).pathname});
    if(ticket!==generation)return false;
    await navigator.serviceWorker.ready;
    if(ticket!==generation)return false;
    if (!navigator.serviceWorker.controller) await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{navigator.serviceWorker.removeEventListener('controllerchange',changed);reject(new Error('Browser setup timed out. Reload this page and try again.'));},20000);
      function changed(){clearTimeout(timer);navigator.serviceWorker.removeEventListener('controllerchange',changed);resolve();}
      navigator.serviceWorker.addEventListener('controllerchange',changed);
    });
    if(ticket!==generation)return false;
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
      if (!await isolate(ticket))return;
      if (ticket!==generation)return;
      // Rewriting a live imported module can stall or retain old definitions.
      // Unchanged dependencies can stay imported; any dependency edit starts fresh.
      const dependencySource=JSON.stringify(files.slice(0,-1));
      const reuse=files.length>1&&compiler&&checkedDependencies?.source===dependencySource;
      if(files.length>1&&!reuse){dispose();log('Fresh compiler environment for changed project imports; cached downloads are reused.');}
      if(!compiler){
        const abort=new AbortController();bootAbort=abort;
        const created=await createCompiler({baseUrl:new URL('engine/',location.href).href,mathlibManifest:workspace.mathlib_manifest,syntaxCheck:'full',signal:abort.signal,onProgress:m=>{if(ticket===generation)log(m);},onStatus:m=>{if(ticket===generation)log(m);}});
        if(ticket!==generation){created.dispose();return;}
        compiler=created;
      }
      let warnings=reuse?checkedDependencies.warnings:false;
      const results=reuse?checkedDependencies.results.map(r=>'Reused unchanged checked dependency.\n'+r):[];
      if(reuse)log('Reusing unchanged checked dependencies in this compiler environment.');
      for(let i=reuse?files.length-1:0;i<files.length;i++) {
        setStatus('Checking '+workspace.files[i].module+'…','running');
        // Export dependencies only. The last file runs with its original source.
        const dependency=i<files.length-1;
        const compatibility=dependency?'':workspace.compatibility?.source||'';
        const versioned=workspace.legacy&&!workspace.files[i].generated&&!workspace.files[i].library;
        const proof=versioned?withCompatibilityImport(files[i],workspace.legacy):files[i];
        const source=dependency?moduleSource(proof,workspace.files[i].module):withCompatibility(proof,compatibility);
        const result=await compiler.run(source,undefined,dependency?{syntaxSource:proof}:{});
        if (ticket!==generation)return;
        const state=outcome(result);warnings ||= state==='warning';
        results.push(workspace.files[i].module+'\n'+(result.diagnostics.map(diagnostic=>mapWorkspaceDiagnostic(diagnostic,proof,dependency,compatibility,versioned?files[i]:null)).join('\n')||'No diagnostics.')+(result.output?'\n'+result.output:'')+'\nChecked in '+(result.compileMs/1000).toFixed(2)+' s.');
        el('output').textContent=results.join('\n\n');
        if(state==='failed'){setStatus('Lean reported errors. The workspace did not pass.','failed');return;}
        if(dependency&&i===files.length-2)checkedDependencies={source:dependencySource,results:[...results],warnings};
      }
      setStatus(warnings?'Checking completed with warnings. Review Lean’s response; a sorry warning means an unfinished proof.':workspace.compatibility?'Checking completed with no diagnostics. Browser compatibility lemma included.':'Checking completed with no diagnostics.',warnings?'warning':'passed');
    } catch(error) {
      if(ticket!==generation)return;
      el('output').textContent=String(error.message||error);setStatus('Checking could not complete. No successful result.','failed');dispose();
    } finally {
      if(ticket===generation){controls(false);el('run').textContent=compiler?'Run workspace':'Restart Lean and run';}
    }
  }
  el('run').addEventListener('click',run);
  const requested=new URL(location.href);
  await chooseId(requested.searchParams.has('file')?'source-'+requested.searchParams.get('file'):requested.searchParams.get('example'));
  const saved=sessionStorage.getItem(draftKey);
  if(saved){
    try{
      const draft=JSON.parse(saved);await chooseId(draft.id);
      if(workspace.id!==draft.id){setStatus('Your saved draft is preserved. Reload to retry loading its source.','failed');return;}
      if(Array.isArray(draft.files)&&draft.files.length===files.length&&draft.files.every(f=>typeof f==='string')){files=draft.files;current=Math.max(0,Math.min(Number.isInteger(draft.current)?draft.current:0,files.length-1));filePicker.value=String(current);showFile();}
      sessionStorage.removeItem(draftKey);if(draft.run)await run();
    }catch{setStatus('Browser setup finished. Run Lean to begin.');}
  }
  if(crossOriginIsolated)sessionStorage.removeItem(draftKey+'-attempt');
}
