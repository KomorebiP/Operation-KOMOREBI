/* Shared selection rules for the page, worker and regression tests. */
(function (root) {
  "use strict";
  const MAX_BYTES = 200 * 1024 * 1024;
  function size(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KiB";
    return (bytes / 1048576).toFixed(1) + " MiB";
  }
  function safePath(path) {
    return typeof path === "string" && path.length > 0 && !/[\\:\x00-\x1f]/u.test(path) &&
      path.split("/").every(part => part && part !== "." && part !== "..");
  }
  function validate(catalog) {
    if (catalog.version !== 1 || !/^[a-f0-9]{40}$/u.test(catalog.source_revision) ||
        !Array.isArray(catalog.works) || !Array.isArray(catalog.files)) throw new Error("Invalid file catalogue. Reload this page.");
    const works = new Set(catalog.works.map(work => work.id));
    const ids = new Set(), paths = new Set();
    for (const file of catalog.files) {
      if (ids.has(file.id) || paths.has(file.archive_path) || !safePath(file.archive_path) ||
          !safePath(file.url) || !file.url.startsWith("documents/files/") || /[?#%]/u.test(file.url) ||
          !Number.isSafeInteger(file.size) || file.size < 0 || !/^[a-f0-9]{64}$/u.test(file.sha256) ||
          (file.work !== null && !works.has(file.work))) throw new Error("Invalid file record. Reload this page.");
      ids.add(file.id); paths.add(file.archive_path);
    }
    return catalog;
  }
  function plan(catalog, selectedIds) {
    const chosen = new Set(selectedIds);
    const selected = catalog.files.filter(file => chosen.has(file.id) && !file.required);
    if (!selected.length) throw new Error("Choose at least one file.");
    if (selected.length !== chosen.size) throw new Error("Some selected files are unavailable. Reload this page.");
    const works = new Set(selected.map(file => file.work));
    const files = [...selected, ...catalog.files.filter(file => file.required && (file.work === null || works.has(file.work)))];
    files.sort((a, b) => a.archive_path.localeCompare(b.archive_path));
    const bytes = files.reduce((total, file) => total + file.size, 0);
    return {files, bytes, selectedCount: selected.length, noticeCount: files.length - selected.length,
      works: catalog.works.filter(work => works.has(work.id)), overLimit: bytes > MAX_BYTES};
  }
  const api = {MAX_BYTES, size, safePath, validate, plan};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.KomorebiDownloads = api;
})(typeof self !== "undefined" ? self : globalThis);
