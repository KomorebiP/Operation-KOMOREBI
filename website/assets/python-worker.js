// A disposable module worker keeps Python off the reader's UI thread.
let python;
let libraryLoaded = false;
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
    }
    if (data.example === "library" && !libraryLoaded) {
      send("status", {text: "Loading NumPy and the pinned Komorebi Math library."});
      await python.loadPackage("numpy", {
        messageCallback: text => send("status", {text}),
        errorCallback: text => send("status", {text})
      });
      const raw = await bytes(new URL("../"+manifest.library_url, import.meta.url), manifest.library_sha256);
      python.unpackArchive(raw, "zip", {extractDir: "/home/pyodide"});
      libraryLoaded = true;
    }
    python.setStdout({batched: text => output("stdout", text)});
    python.setStderr({batched: text => output("stderr", text)});
    globals = python.toPy({__name__: "__main__"});
    send("status", {text: "Running. You can stop Python at any time."});
    const result = await python.runPythonAsync(data.code, {globals, filename: data.example+".py"});
    result?.destroy?.();
    send("done");
  } catch (error) {
    send("error", {text: String(error)});
  } finally {
    globals?.destroy();
  }
};
