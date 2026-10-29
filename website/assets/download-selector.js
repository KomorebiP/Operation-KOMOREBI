"use strict";
(async () => {
  const form = document.querySelector("#zip-form");
  if (!form) return;
  const api = window.KomorebiDownloads;
  const loadStatus = document.querySelector("#zip-load-status");
  const picker = document.querySelector("#zip-work");
  const preset = document.querySelector("#zip-preset");
  const groups = document.querySelector("#zip-works");
  const summary = document.querySelector("#zip-summary");
  const progress = document.querySelector("#zip-progress");
  const build = document.querySelector("#zip-build");
  const cancel = document.querySelector("#zip-cancel");
  const save = document.querySelector("#zip-save");
  const controls = document.querySelector("#zip-controls");
  const selected = new Set(), added = new Set();
  let catalog, worker, chunks = [], downloadURL, serial = 0;
  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function discardZIP() {
    if (downloadURL) URL.revokeObjectURL(downloadURL);
    downloadURL = null; save.hidden = true; save.removeAttribute("href");
  }
  function update() {
    discardZIP();
    progress.textContent = "";
    if (!selected.size) {
      summary.textContent = "No files selected."; build.disabled = true;
    } else {
      const plan = api.plan(catalog, selected);
      summary.textContent = `${plan.selectedCount} selected ${plan.selectedCount === 1 ? "file" : "files"} from ${plan.works.length} ${plan.works.length === 1 ? "work" : "works"} + ${plan.noticeCount} notices · ${api.size(plan.bytes)} before compression.` +
        (plan.overLimit ? " This exceeds 200 MiB. Remove files or make separate ZIPs." : "");
      build.disabled = plan.overLimit;
    }
    for (const input of groups.querySelectorAll("input[data-file]")) input.checked = selected.has(input.dataset.file);
    for (const input of groups.querySelectorAll("input[data-category]")) {
      const files = catalog.files.filter(file => file.work === input.dataset.work && file.category === input.dataset.category && !file.required);
      const count = files.filter(file => selected.has(file.id)).length;
      input.checked = count === files.length;
      input.indeterminate = count > 0 && count < files.length;
    }
    for (const count of groups.querySelectorAll("[data-work-count]")) {
      const files = catalog.files.filter(file => file.work === count.dataset.workCount && !file.required);
      count.textContent = files.filter(file => selected.has(file.id)).length + " of " + files.length + " files selected";
    }
  }
  function checkbox(text) {
    const label = element("label", "", "zip-checkbox");
    const input = element("input"); input.type = "checkbox";
    input.id = "zip-choice-" + (++serial); label.htmlFor = input.id;
    label.append(input, element("span", text));
    return {label, input};
  }
  function addWork(id, mode) {
    if (!id) { loadStatus.textContent = "Choose a work to add."; picker.focus(); return; }
    if (added.has(id)) {
      const existing = [...groups.children].find(node => node.dataset.work === id);
      existing.open = true; existing.querySelector("summary").focus();
      loadStatus.textContent = "This work is already in your selection. Adjust its files below."; return;
    }
    added.add(id);
    for (const section of groups.children) section.open = false;
    const work = catalog.works.find(work => work.id === id);
    const files = catalog.files.filter(file => file.work === id && !file.required);
    for (const file of files) if (mode === "all" || (mode === "pdf" && file.category === "PDFs") || (mode === "reading" && file.reading)) selected.add(file.id);
    const section = element("details", "", "zip-work"); section.open = true; section.dataset.work = id;
    const heading = element("summary");
    heading.append(element("span", work.title), element("span", "", "zip-work-count"));
    heading.lastChild.dataset.workCount = id;
    section.append(heading);
    const routes = element("p", "", "zip-work-actions");
    const link = element("a", "Work and evidence"); link.href = work.url; routes.append(link);
    const remove = element("button", "Remove work", "zip-secondary"); remove.type = "button";
    remove.addEventListener("click", () => {
      for (const file of files) selected.delete(file.id);
      added.delete(id); section.remove(); update(); picker.focus();
    });
    routes.append(remove); section.append(routes);
    for (const kind of ["PDFs", "Manuscript sources", "Lean sources", "Code", "Worked examples", "Guides and records"]) {
      const items = files.filter(file => file.category === kind);
      if (!items.length) continue;
      const category = element("details", "", "zip-category");
      category.open = kind === "PDFs";
      category.append(element("summary", kind + " (" + items.length + ")"));
      const all = checkbox("Select all " + kind.toLowerCase());
      all.input.dataset.category = kind; all.input.dataset.work = id;
      all.input.addEventListener("change", () => {
        for (const file of items) { if (all.input.checked) selected.add(file.id); else selected.delete(file.id); }
        update();
      });
      category.append(all.label);
      const list = element("ul", "", "zip-file-list");
      for (const file of items) {
        const li = element("li");
        const choice = checkbox(file.path);
        choice.input.dataset.file = file.id;
        choice.input.addEventListener("change", () => {
          if (choice.input.checked) selected.add(file.id); else selected.delete(file.id);
          update();
        });
        li.append(choice.label);
        const meta = element("p", api.size(file.size), "zip-file-meta");
        if (file.reader_url) { const read = element("a", "Read file"); read.href = file.reader_url; meta.append(" · ", read); }
        li.append(meta); list.append(li);
      }
      category.append(list); section.append(category);
    }
    groups.append(section); update();
    loadStatus.textContent = "Work added. Adjust its files below or add another work.";
    heading.focus();
  }
  function stop(message) {
    if (worker) worker.terminate(); worker = null; chunks = [];
    controls.disabled = false; cancel.hidden = true;
    build.disabled = !selected.size || api.plan(catalog, selected).overLimit;
    progress.textContent = message;
  }
  try {
    if (!api || !window.Worker || !window.crypto?.subtle) throw new Error("The custom selector is unavailable in this browser. Use the ready-made ZIPs below.");
    const response = await fetch(form.dataset.index);
    if (!response.ok) throw new Error("The file list could not load. Reload this page or use the ready-made ZIPs below.");
    catalog = api.validate(await response.json());
    if (catalog.source_revision !== form.dataset.revision) throw new Error("The site was updated. Reload this page for the current file list.");
    form.hidden = false; loadStatus.textContent = "Choose a work to begin.";
    document.querySelector("#zip-add").addEventListener("click", () => addWork(picker.value, preset.value));
    document.querySelector("#zip-core-papers").addEventListener("click", () => {
      for (const work of catalog.works.filter(work => /^paper-[ivx]+$/u.test(work.id))) {
        if (!added.has(work.id)) addWork(work.id, preset.value);
      }
      loadStatus.textContent = "Core papers added using the chosen starting selection. Existing choices were kept.";
    });
    document.querySelector("#zip-clear").addEventListener("click", () => {
      selected.clear(); added.clear(); groups.replaceChildren(); update(); picker.focus();
      loadStatus.textContent = "Selection cleared. Choose a work to begin.";
    });
    form.addEventListener("submit", event => {
      event.preventDefault();
      if (worker || !selected.size) return;
      const plan = api.plan(catalog, selected);
      if (plan.overLimit) return;
      discardZIP(); chunks = [];
      controls.disabled = true; build.disabled = true; cancel.hidden = false;
      progress.textContent = "Preparing your ZIP…";
      try { worker = new Worker(form.dataset.worker); } catch { stop("The ZIP builder could not start. Use a ready-made ZIP below."); return; }
      const activeWorker = worker;
      worker.onmessage = event => {
        if (worker !== activeWorker) return;
        const data = event.data;
        if (data.type === "chunk") chunks.push(data.chunk);
        else if (data.type === "progress") progress.textContent = `Checking file ${data.completed + 1} of ${data.count} · ${api.size(data.loaded)} of ${api.size(data.total)}. ${data.name}`;
        else if (data.type === "error") { stop(data.message); build.focus(); }
        else if (data.type === "done") {
          const zip = new Blob(chunks, {type: "application/zip"});
          stop("Your ZIP is ready. Use Save ZIP to download it.");
          downloadURL = URL.createObjectURL(zip); save.href = downloadURL;
          save.download = "komorebi-selection-" + catalog.source_revision.slice(0, 8) + ".zip";
          save.textContent = "Save ZIP (" + api.size(zip.size) + ")"; save.hidden = false; save.focus();
        }
      };
      worker.onerror = () => { if (worker !== activeWorker) return; stop("The ZIP builder stopped. Try fewer files or use a ready-made ZIP below."); build.focus(); };
      worker.postMessage({catalog, selectedIds: [...selected]});
    });
    cancel.addEventListener("click", () => { stop("Cancelled. Your file selection is still available."); build.focus(); });
    const initial = new URLSearchParams(location.search).get("work");
    if (initial && catalog.works.some(work => work.id === initial)) { picker.value = initial; addWork(initial, "reading"); }
    window.addEventListener("pagehide", () => { if (worker) stop("Cancelled. Prepare the ZIP again when you return."); discardZIP(); });
  } catch (error) { loadStatus.textContent = error.message; }
})();
