const host = document.getElementById("python-playground");
const status = document.getElementById("python-status");
const out = document.getElementById("python-output");
const errors = document.getElementById("python-error");
const stop = document.getElementById("python-stop");
const preset = document.getElementById("python-preset");
const examples = [...document.querySelectorAll(".python-example")];
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
  const selected = examples.some(x => "#"+x.id === location.hash) ? location.hash.slice(1) : "packets";
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

function terminate(message) {
  worker?.terminate();
  worker = null;
  serial++;
  idle();
  status.textContent = message;
}

function createWorker() {
  const current = new Worker(new URL(host.dataset.worker, document.baseURI), {type: "module"});
  current.onmessage = ({data}) => {
    if (!active || data.id !== active.id) return;
    if (data.type === "status") status.textContent = data.text;
    if (data.type === "stdout") {stdout += data.text; out.textContent = stdout;}
    if (data.type === "stderr") {stderr += data.text; errors.textContent = stderr;}
    if (data.type === "error") {
      errors.textContent = stderr + data.text;
      terminate("Python stopped with an error. Review the error below, edit the code or reset it.");
    }
    if (data.type === "done") {
      const entry = manifest.examples[active.name];
      status.textContent = active.modified
        ? "Finished edited code. This output has not been compared with the published example."
        : stdout === entry.expected_output && !stderr
          ? "Finished. Output matches the published example."
          : "Finished, but output differs from the published example. Review the output and errors.";
      if (!stdout) out.textContent = "Finished without printed output.";
      idle();
    }
  };
  current.onerror = event => {
    event.preventDefault();
    errors.textContent = event.message || "The Python runtime could not start. Try reloading the page.";
    terminate("Python could not finish. The downloadable code is still available.");
  };
  return current;
}

host.addEventListener("click", async event => {
  const run = event.target.closest("[data-run]");
  const reset = event.target.closest("[data-reset]");
  if (reset) {
    terminate("Code restored. Press Run to start again.");
    document.getElementById("code-"+reset.dataset.reset).value = originals.get(reset.dataset.reset);
    out.textContent = "Run an example to see its output here.";
    errors.textContent = "None.";
    return;
  }
  if (!run || active) return;
  const name = run.dataset.run;
  const code = document.getElementById("code-"+name).value;
  const request = {id: ++serial, name, modified: code !== originals.get(name)};
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
    if (!manifest) {
      const response = await fetch(host.dataset.manifest);
      if (!response.ok) throw new Error("Could not load the published example record.");
      manifest = await response.json();
    }
    if (active !== request) return;
    worker ||= createWorker();
    worker.postMessage({id: request.id, code, example: name});
  } catch (error) {
    if (active !== request) return;
    errors.textContent = String(error);
    terminate("Python could not start. Reload the page or download the example.");
  }
});
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
