// A disposable module worker keeps Python off the reader's UI thread.
let python;
let libraryLoaded = false;
const loaded = new Set();
let graphicBytes = 0;
let graphicMessages = 0;
let manifest;
let currentId;
let outputSize = 0;
const LIMIT = 200000;
const send = (type, data = {}) => self.postMessage({type, id: currentId, ...data});

async function bytes(url, expected) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${url}: ${response.status}`);
  const raw = new Uint8Array(await response.arrayBuffer());
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", raw)),
    x => x.toString(16).padStart(2, "0")).join("");
  if (hash !== expected) throw new Error("Source checksum mismatch. Reload the page and try again.");
  return raw;
}

function output(type, text) {
  outputSize += text.length + 1;
  if (outputSize > LIMIT) throw new Error("Output limit reached. Reduce the amount printed and run again.");
  send(type, {text: text + "\n"});
}

self.onmessage = async ({data}) => {
  currentId = data.id;
  outputSize = 0;
  graphicBytes = 0;
  graphicMessages = 0;
  let globals;
  try {
    if (!python) {
      send("status", {text: "Loading Python. The first run may take a little while."});
      const {loadPyodide} = await import("./python/pyodide.mjs");
      python = await loadPyodide({indexURL: new URL("./python/", import.meta.url).href});
      python.setStdin({error: true});
      const response = await fetch(new URL("../downloads/python-playground.json", import.meta.url));
      if (!response.ok) throw new Error("Could not load the example source record.");
      manifest = await response.json();
      python.registerJsModule("komorebi_host", {emit(payload) {
        if (typeof payload !== "string" || payload.length > 2000000 || ++graphicMessages > 20 || (graphicBytes += payload.length) > 8000000) {
          throw new Error("Figure and export limit reached.");
        }
        const value = JSON.parse(payload);
        if (!["plot", "image", "file"].includes(value.kind)) throw new Error("Unknown display format.");
        send("display", {value});
      }});
      const helper = await bytes(new URL("../"+manifest.helper_url, import.meta.url), manifest.helper_sha256);
      python.FS.writeFile("/home/pyodide/komorebi_browser.py", helper);
    }
    if (data.revision !== manifest.collection_revision) throw new Error("The site was updated. Reload the page before running Python.");
    const entry = manifest.examples[data.example];
    if (!entry) throw new Error("Unknown preset. Reload the page and try again.");
    const parser = python.pyimport("pyodide.code");
    const importsProxy = parser.find_imports(data.code);
    const imports = importsProxy.toJs().map(name => name.split(".")[0]);
    importsProxy.destroy(); parser.destroy();
    const wanted = new Set([...entry.packages, ...imports.filter(name => ["numpy", "matplotlib", "sympy", "scipy"].includes(name))]);
    const wantsLibrary = data.example === "library" || imports.includes("komorebi_math");
    if (wantsLibrary) wanted.add("numpy");
    const missing = [...wanted].filter(name => !loaded.has(name));
    if (missing.length) {
      send("status", {text: "Loading "+missing.join(", ")+". This may take a little while."});
      await python.loadPackage(missing, {
        messageCallback: text => send("status", {text}),
        errorCallback: text => send("status", {text})
      });
      missing.forEach(name => loaded.add(name));
    }
    if (wantsLibrary && !libraryLoaded) {
      send("status", {text: "Loading the pinned Komorebi Math library."});
      const raw = await bytes(new URL("../"+manifest.library_url, import.meta.url), manifest.library_sha256);
      python.unpackArchive(raw, "zip", {extractDir: "/home/pyodide"});
      libraryLoaded = true;
    }
    python.runPython("import komorebi_browser as _browser\n_browser._reset()");
    if (loaded.has("matplotlib")) {
      python.runPython("import matplotlib\nmatplotlib.use('Agg', force=True)\nimport matplotlib.pyplot as _plt\n_plt.close('all')\n_plt.show = _browser._show_all");
    }
    python.setStdout({batched: text => output("stdout", text)});
    python.setStderr({batched: text => output("stderr", text)});
    globals = python.toPy({__name__: "__main__", uploaded_files: data.files || {}});
    send("status", {text: "Running. You can stop Python at any time."});
    const result = await python.runPythonAsync(data.code, {globals, filename: data.example+".py"});
    result?.destroy?.();
    if (loaded.has("matplotlib")) python.runPython("_browser._show_all()");
    send("done", {packages: [...wanted], library: libraryLoaded});
  } catch (error) {
    send("error", {text: String(error)});
  } finally {
    globals?.destroy();
  }
};
