"use strict";
importScripts("vendor/fflate-0.8.3.js", "download-core.js" + new URL(self.location.href).search);

self.onmessage = async event => {
  try {
    const {catalog, selectedIds} = event.data;
    const plan = KomorebiDownloads.plan(KomorebiDownloads.validate(catalog), selectedIds);
    if (plan.overLimit) throw new Error("This selection exceeds 200 MiB. Create two smaller ZIPs.");
    const base = new URL("../", self.location.href);
    let downloaded = 0;
    const zip = new fflate.Zip((error, chunk, final) => {
      if (error) throw error;
      // Transfer a fresh buffer so compression internals retain their own data.
      const output = chunk.slice();
      self.postMessage({type: "chunk", chunk: output}, [output.buffer]);
      if (final) self.postMessage({type: "done"});
    });
    function add(name, raw) {
      const file = name.toLowerCase().endsWith(".pdf") ? new fflate.ZipPassThrough(name) : new fflate.ZipDeflate(name, {level: 6});
      zip.add(file);
      file.push(raw, true);
    }
    for (let index = 0; index < plan.files.length; index++) {
      const file = plan.files[index];
      const url = new URL(file.url, base);
      if (url.origin !== base.origin || !url.pathname.startsWith(base.pathname + "documents/files/")) throw new Error("Invalid download location.");
      self.postMessage({type: "progress", loaded: downloaded, total: plan.bytes,
        completed: index, count: plan.files.length, name: file.path});
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 60000);
      let raw;
      try {
        const response = await fetch(url.href, {credentials: "omit", signal: controller.signal});
        if (!response.ok || response.redirected) throw new Error("Could not fetch " + file.path + ". Try again.");
        const reader = response.body.getReader();
        const chunks = [];
        let length = 0;
        while (true) {
          const {done, value} = await reader.read();
          if (done) break;
          length += value.length;
          if (length > file.size) { await reader.cancel(); throw new Error("File size changed: " + file.path); }
          chunks.push(value);
        }
        if (length !== file.size) throw new Error("Incomplete download: " + file.path);
        raw = new Uint8Array(length);
        let offset = 0;
        for (const chunk of chunks) { raw.set(chunk, offset); offset += chunk.length; }
      } finally { clearTimeout(timeout); }
      const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", raw));
      const sha = Array.from(digest, byte => byte.toString(16).padStart(2, "0")).join("");
      if (sha !== file.sha256) throw new Error("File integrity check failed: " + file.path + ". Reload and try again.");
      add(file.archive_path, raw);
      downloaded += file.size;
    }
    const encoder = new TextEncoder();
    const manifest = {version: 1, source_revision: catalog.source_revision, scope: catalog.scope,
      works: plan.works.map(work => ({...work, url: new URL(work.url, base).href})),
      files: plan.files.map(file => ({...file, url: new URL(file.url, base).href,
        reader_url: file.reader_url ? new URL(file.reader_url, base).href : null}))};
    add("CONTENTS.json", encoder.encode(JSON.stringify(manifest, null, 2) + "\n"));
    add("SHA256SUMS", encoder.encode(plan.files.map(file => file.sha256 + "  " + file.archive_path).join("\n") + "\n"));
    add("README.txt", encoder.encode("Komorebi download selection\n\n" + catalog.scope +
      "\n\nSource revision: " + catalog.source_revision + "\n\nCONTENTS.json lists every file, its checksum and its online reading link.\n" +
      "License and authorship notices are included. Markdown and TeX sources may refer to files outside this selection.\n" +
      "For complete sources and build instructions: " + new URL("collection/DOWNLOADS.html#obtain-a-full-component", base).href + "\n"));
    zip.end();
  } catch (error) {
    self.postMessage({type: "error", message: error.name === "AbortError" ? "A file download timed out. Try again or choose fewer files." : error.message});
  }
};
