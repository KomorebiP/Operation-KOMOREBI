const host = document.getElementById("python-playground");
const status = document.getElementById("python-status");
const out = document.getElementById("python-output");
const errors = document.getElementById("python-error");
const stop = document.getElementById("python-stop");
const preset = document.getElementById("python-preset");
const examples = [...document.querySelectorAll(".python-example")];
const {createResults} = await import(new URL(host.dataset.results, document.baseURI));
const results = createResults(document.getElementById("python-figures"), new URL(host.dataset.plotly, document.baseURI).href);
const outputDownload = document.getElementById("python-download-output");
const reportDownload = document.getElementById("python-download-report");
const uploadStatus = document.getElementById("python-upload-status");
let uploads = {};
let uploadRecords = [];
let uploadVersion = 0;
let report;
let rendering = Promise.resolve();
let visualErrors = 0;
const originals = new Map(examples.map(section => [section.id, section.querySelector("textarea").value]));
let worker;
let active;
let serial = 0;
let timer;
let manifest;
let stdout = "";
let stderr = "";
let selectedExample;

function select() {
  const selected = examples.some(x => "#"+x.id === location.hash) ? location.hash.slice(1) : "sequence-growth";
  const changed = selectedExample !== selected;
  if (active && changed) terminate("Stopped because the example changed.");
  preset.value = selected;
  for (const section of examples) section.hidden = section.id !== selected;
  if (changed) {
    const title = document.querySelector("#"+selected+" h2").textContent;
    status.textContent = title+" loaded. Press Run when you are ready.";
    document.getElementById("python-output-title").textContent = "Output: "+title;
    out.textContent = "Run this preset to see its output here.";
    errors.textContent = "None.";
    clearResults();
  }
  selectedExample = selected;
}

function idle() {
  clearTimeout(timer);
  active = null;
  stop.disabled = true;
  host.removeAttribute("aria-busy");
  host.querySelectorAll("[data-run]").forEach(button => {button.disabled = false;});
}

function clearResults() {
  results.clear(); report = null; outputDownload.disabled = true; reportDownload.disabled = true;
}
function saveReport(outcome, meta = {}) {
  if (!active) return;
  report = {outcome, preset: active.name, started_at: active.started, finished_at: new Date().toISOString(),
    code: active.code, code_sha256: active.codeHash, collection_revision: manifest?.collection_revision,
    library_revision: manifest?.library_revision, runtime_version: manifest?.runtime_version,
    pinned_package_versions: manifest?.packages, requested_packages: meta.packages || [],
    komorebi_loaded: meta.library || false, input_files: active.inputRecords, stdout, stderr,
    figures: active.figures, note: "This records a browser calculation, not proof verification. Uploaded file contents are omitted."};
  outputDownload.disabled = false; reportDownload.disabled = false;
}
function download(name, text, type = "text/plain;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([text], {type}));
  const link = document.createElement("a"); link.href = url; link.download = name;
  document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 30000);
}
async function checksum(raw) {
  return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", raw)), b => b.toString(16).padStart(2, "0")).join("");
}
async function getManifest() {
  if (!manifest) {
    const response = await fetch(host.dataset.manifest);
    if (!response.ok) throw new Error("Could not load the published example record.");
    manifest = await response.json();
  }
  return manifest;
}
const draftKey = name => "komorebi-python-draft-v1:"+name;
function updateDraftButtons() {
  for (const section of examples) {
    let saved = false;
    try {saved = !!localStorage.getItem(draftKey(section.id));} catch {}
    section.querySelector("[data-restore]").disabled = !saved;
    section.querySelector("[data-forget]").disabled = !saved;
  }
}
function terminate(message, outcome = "stopped") {
  saveReport(outcome);
  worker?.terminate();
  worker = null;
  serial++;
  idle();
  status.textContent = message;
}

function createWorker() {
  const current = new Worker(new URL(host.dataset.worker, document.baseURI), {type: "module"});
  current.onmessage = async ({data}) => {
    if (!active || data.id !== active.id) return;
    if (data.type === "status") status.textContent = data.text;
    if (data.type === "stdout") {stdout += data.text; out.textContent = stdout;}
    if (data.type === "stderr") {stderr += data.text; errors.textContent = stderr;}
    if (data.type === "error") {
      stderr += data.text;
      errors.textContent = stderr;
      terminate("Python stopped with an error. Review the error below, edit the code or reset it.", "error");
    }
    if (data.type === "display") {
      const request = active;
      if (data.value.kind !== "file") request.figures.push(data.value);
      rendering = rendering.then(async () => {
        if (active !== request) return;
        if (!await results.add(data.value, () => active === request)) visualErrors++;
      }).catch(error => {
        if (active !== request) return;
        visualErrors++; stderr += String(error)+"\n"; errors.textContent = stderr;
      });
    }
    if (data.type === "done") {
      const request = active;
      await rendering;
      if (active !== request) return;
      const entry = manifest.examples[active.name];
      status.textContent = visualErrors ? "Calculation finished, but a figure could not be drawn. Its data may still be available below." : active.modified
        ? "Finished edited code or uploaded data. This output has not been compared with the published example."
        : stdout === entry.expected_output && !stderr
          ? "Finished. Output matches the published example."
          : "Finished, but output differs from the published example. Review the output and errors.";
      if (!stdout) out.textContent = "Finished without printed output.";
      saveReport(visualErrors ? "display-error" : "completed", data);
      idle();
    }
  };
  current.onerror = event => {
    event.preventDefault();
    stderr += event.message || "The Python runtime could not start. Try reloading the page.";
    errors.textContent = stderr;
    terminate("Python could not finish. The downloadable code is still available.");
  };
  return current;
}

host.addEventListener("click", async event => {
  const codeDownload = event.target.closest("[data-download-code]");
  const save = event.target.closest("[data-save]");
  const restore = event.target.closest("[data-restore]");
  const forget = event.target.closest("[data-forget]");
  if (codeDownload) {download("komorebi-"+codeDownload.dataset.downloadCode+".py", document.getElementById("code-"+codeDownload.dataset.downloadCode).value); return;}
  if (save || restore || forget) {
    try {
      const name = (save || restore || forget).dataset[save ? "save" : restore ? "restore" : "forget"];
      const editor = document.getElementById("code-"+name);
      if (save) {
        const code = editor.value;
        if (code.length > 256000) throw new Error("Keep saved code under 256,000 characters.");
        const record = await getManifest();
        localStorage.setItem(draftKey(name), JSON.stringify({code, revision: record.collection_revision, saved_at: new Date().toISOString()}));
        status.textContent = "Draft saved in this browser. Download edited code for a separate copy.";
      } else if (restore) {
        const saved = JSON.parse(localStorage.getItem(draftKey(name)));
        if (!saved || typeof saved.code !== "string" || saved.code.length > 256000) throw new Error("No valid saved draft was found.");
        terminate("Saved draft restored. Press Run when ready.");
        editor.value = saved.code; clearResults();
      } else {
        localStorage.removeItem(draftKey(name)); status.textContent = "Saved draft deleted. The current editor is unchanged.";
      }
      updateDraftButtons();
    } catch (error) {status.textContent = "Could not use browser storage: "+String(error)+" You can download edited code instead.";}
    return;
  }
  const run = event.target.closest("[data-run]");
  const reset = event.target.closest("[data-reset]");
  if (reset) {
    terminate("Code restored. Press Run to start again.");
    document.getElementById("code-"+reset.dataset.reset).value = originals.get(reset.dataset.reset);
    out.textContent = "Run an example to see its output here.";
    errors.textContent = "None.";
    clearResults();
    return;
  }
  if (!run || active) return;
  const name = run.dataset.run;
  const code = document.getElementById("code-"+name).value;
  if (code.length > 256000) {status.textContent = "Keep code under 256,000 characters."; return;}
  clearResults(); rendering = Promise.resolve(); visualErrors = 0;
  const request = {id: ++serial, name, code, figures: [], started: new Date().toISOString(),
    files: {...uploads}, inputRecords: [...uploadRecords], modified: code !== originals.get(name) || Object.keys(uploads).length > 0};
  active = request;
  document.getElementById("python-output-title").textContent = "Output: "+document.querySelector("#"+name+" h2").textContent;
  stdout = ""; stderr = "";
  out.textContent = "Waiting for output…";
  errors.textContent = "None.";
  status.textContent = "Preparing Python…";
  stop.disabled = false;
  host.querySelectorAll("[data-run]").forEach(button => {button.disabled = true;});
  timer = setTimeout(() => terminate("Stopped after two minutes. Reduce the calculation or try again."), 120000);
  try {
    await getManifest();
    request.codeHash = await checksum(new TextEncoder().encode(code));
    if (active !== request) return;
    worker ||= createWorker();
    worker.postMessage({id: request.id, code, example: name, files: request.files, revision: manifest.collection_revision});
  } catch (error) {
    if (active !== request) return;
    stderr += String(error); errors.textContent = stderr;
    terminate("Python could not start. Reload the page or download the example.");
  }
});
document.getElementById("python-data-files").addEventListener("change", async event => {
  const version = ++uploadVersion;
  const files = [...event.target.files];
  uploadStatus.textContent = "Reading files locally…";
  try {
    if (files.length > 5 || files.reduce((n, f) => n+f.size, 0) > 4000000) throw new Error("Choose at most 5 files and 4 MB in total.");
    const next = {}; const records = [];
    for (const file of files) {
      if (file.size > 2000000 || !/^[A-Za-z0-9][A-Za-z0-9_. -]{0,100}\.(csv|json)$/i.test(file.name)) throw new Error("Use CSV or JSON files under 2 MB with simple filenames.");
      if (Object.hasOwn(next, file.name)) throw new Error("Choose distinct filenames.");
      const raw = await file.arrayBuffer();
      const text = new TextDecoder("utf-8", {fatal: true}).decode(raw);
      if (/\.json$/i.test(file.name)) JSON.parse(text);
      next[file.name] = text;
      records.push({name: file.name, bytes: file.size, sha256: await checksum(raw)});
    }
    if (version !== uploadVersion) return;
    uploads = next; uploadRecords = records;
    uploadStatus.textContent = records.length ? "Ready for the next run: "+records.map(f => f.name+" ("+f.bytes+" bytes)").join(", ") : "No data files selected.";
  } catch (error) {
    if (version !== uploadVersion) return;
    uploads = {}; uploadRecords = []; event.target.value = "";
    uploadStatus.textContent = "Files were not loaded. "+String(error);
  }
});
document.getElementById("python-clear-files").addEventListener("click", () => {
  uploadVersion++; uploads = {}; uploadRecords = [];
  document.getElementById("python-data-files").value = ""; uploadStatus.textContent = "No data files selected.";
});
document.getElementById("python-code-file").addEventListener("change", async event => {
  const file = event.target.files[0]; const name = selectedExample;
  if (!file) return;
  try {
    if (file.size > 256000 || !/\.py$/i.test(file.name)) throw new Error("Choose a .py file under 256 KB.");
    const code = new TextDecoder("utf-8", {fatal: true}).decode(await file.arrayBuffer());
    terminate("Python file opened in "+name+". Review the code before running it.");
    document.getElementById("code-"+name).value = code; clearResults();
  } catch (error) {status.textContent = String(error);}
  event.target.value = "";
});
outputDownload.addEventListener("click", () => {if (report) download("komorebi-"+report.preset+"-output.txt", report.stdout+(report.stderr ? "\nErrors:\n"+report.stderr : ""));});
reportDownload.addEventListener("click", () => {if (report) download("komorebi-"+report.preset+"-run.json", JSON.stringify(report, null, 2), "application/json");});
updateDraftButtons();
stop.addEventListener("click", () => terminate("Stopped. Press Run to start a fresh Python runtime."));
preset.addEventListener("change", () => {
  history.pushState(null, "", "#"+preset.value);
  select();
});
document.getElementById("python-picker").hidden = false;
document.getElementById("python-example-links").hidden = true;
window.addEventListener("hashchange", () => {
  if (!location.hash || examples.some(section => "#"+section.id === location.hash)) select();
});
window.addEventListener("pagehide", () => terminate("Python stopped when you left this page. Press Run to start again."));
select();
