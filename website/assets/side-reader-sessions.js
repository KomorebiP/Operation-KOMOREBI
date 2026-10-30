"use strict";
(function (root) {
  const core = typeof module === "object" && module.exports ? require("./side-reader-core.js") : root.KomorebiSideReader;
  const sides = ["left", "right"];
  const number = (value, fallback = 0, min = 0, max = 1e8) => typeof value === "number" && Number.isFinite(value) && value >= min && value <= max ? value : fallback;
  function pdfHash(value) {
    if (typeof value !== "string" || value.length > 200) return null;
    const params = new URLSearchParams(value.replace(/^#/u, ""));
    if ([...params.keys()].some(key => !["page", "zoom"].includes(key)) || params.getAll("page").length !== 1 || params.getAll("zoom").length > 1) return null;
    const page = params.get("page");
    if (!/^[1-9]\d{0,5}$/u.test(page || "")) return null;
    const zoom = params.get("zoom");
    if (zoom !== null) {
      const parts = zoom.split(",");
      if (![1,3].includes(parts.length) || !( ["auto", "page-fit", "page-width", "page-height"].includes(parts[0]) ||
          (/^\d+(?:\.\d+)?$/u.test(parts[0]) && Number(parts[0]) >= 1 && Number(parts[0]) <= 10000))) return null;
      if (parts.slice(1).some(part => !/^-?\d{1,8}$/u.test(part))) return null;
    }
    return "page=" + page + (zoom === null ? "" : "&zoom=" + zoom);
  }
  function position(value, url) {
    if (!value || value.url !== url) return null;
    const html = value.html;
    return {url, html:html && typeof html === "object" ? {
      anchor:typeof html.anchor === "string" && html.anchor.length <= 512 && !/[\x00-\x1f]/u.test(html.anchor) ? html.anchor : "",
      offset:number(html.offset, 0, -1e8), x:number(html.x), y:number(html.y),
      ratio:number(html.ratio, 0, 0, 1), progress:number(html.progress, 0, 0, 1), extent:number(html.extent), width:number(html.width, 0, 0, 20000)
    } : null, pdf:pdfHash(value.pdf), rotation:[0,90,180,270].includes(value.rotation) ? value.rotation : 0};
  }
  function snapshot(value, base, data) {
    if (!value || value.schema !== 1) return null;
    const left = core.canonical(value.left, base, data.pages), right = core.canonical(value.right, base, data.pages);
    if (!left || !right) return null;
    return {schema:1, left, right, view:["both","left","right"].includes(value.view) ? value.view : "both",
      width:[35,40,45,50,55,60,65].includes(value.width) ? value.width : 50,
      focus:value.focus === true, send:{left:value.send?.left === true, right:value.send?.right === true},
      positions:{left:position(value.positions?.left, left), right:position(value.positions?.right, right)},
      updatedAt:number(value.updatedAt, 0, 0, 1e14)};
  }
  function library(raw) {
    const empty = {schema:1, remember:true, last:null, bookmarks:[]};
    try {
      if (typeof raw !== "string" || raw.length > 512000) return empty;
      const value = JSON.parse(raw);
      if (value.schema !== 1) return empty;
      const names = new Map();
      for (const entry of (Array.isArray(value.bookmarks) ? value.bookmarks : []).slice(0,50)) {
        if (!entry || typeof entry.name !== "string" || !entry.name.trim() || entry.name.trim().length > 80 || /[\x00-\x1f]/u.test(entry.name)) continue;
        // Keep unavailable bookmarks so a catalogue change does not silently delete them.
        if (!entry.session || JSON.stringify(entry.session).length > 20000) continue;
        names.set(entry.name.trim(), {name:entry.name.trim(), session:entry.session});
      }
      return {schema:1, remember:value.remember !== false, last:value.last || null, bookmarks:[...names.values()]};
    } catch { return empty; }
  }
  function withBookmark(current, name, session) {
    name = name.trim();
    if (!name || name.length > 80 || /[\x00-\x1f]/u.test(name)) throw new Error("Choose a session name of up to 80 characters.");
    const bookmarks = current.bookmarks.filter(entry => entry.name !== name);
    if (bookmarks.length >= 50) throw new Error("Delete a saved session before adding another.");
    return {...current, bookmarks:[...bookmarks, {name, session}]};
  }
  function writeLibrary(storage, key, value) {
    try { storage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
  }
  function initialSession(current, href, base, data, navigationType = "navigate") {
    if (!current.remember) return null;
    const last = snapshot(current.last, base, data), url = new URL(href);
    if (!last) return null;
    if (!url.search) return last;
    const params = url.searchParams;
    if (navigationType === "reload" && core.canonical(params.get("left"), base, data.pages) === last.left &&
        core.canonical(params.get("right"), base, data.pages) === last.right &&
        Number(params.get("width") || 50) === last.width && (params.get("view") || "both") === last.view) return last;
    return null;
  }
  function create(options) {
    const {base, data, getState, getFrame, isCurrent, restoreSession, titleFor} = options;
    const $ = id => document.getElementById(id);
    const key = "komorebi.reader.sessions.v1:" + new URL(base).pathname;
    const message = text => {$("side-session-status").textContent = text;};
    let storage, saved;
    try { storage = window.localStorage; saved = library(storage.getItem(key)); } catch { saved = library(null); }
    let resume = snapshot(saved.last, base, data);
    let timer, blocked = false;
    const watched = {}, cached = {}, pdfs = {}, restoring = {};
    const active = (side, doc) => isCurrent(side) && getFrame(side).contentDocument === doc;
    function store(value, text) {
      if (!writeLibrary(storage, key, value)) {
        if (!blocked || text) message("This browser could not save the session. Use Copy link to this pair to keep the document addresses.");
        blocked = true;
        return false;
      }
      saved = value; blocked = false;
      if (text) message(text);
      return true;
    }
    function latest() {
      try {
        const value = storage.getItem(key);
        if (value !== null) saved = library(value);
      } catch {}
      return saved;
    }
    function htmlPosition(side) {
      const frame = getFrame(side), doc = frame.contentDocument, win = frame.contentWindow;
      let anchor = doc.elementFromPoint(Math.max(1, doc.documentElement.clientWidth / 2), Math.min(64, win.innerHeight / 4));
      anchor = anchor?.closest(".reading-block[id],.source-line[id],.claim[id],h1[id],h2[id],h3[id],h4[id],h5[id],h6[id],section[id]");
      if (!anchor) {
        const headings = doc.querySelectorAll("main h1[id],main h2[id],main h3[id],main h4[id],main h5[id],main h6[id]");
        for (let n = headings.length - 1; n >= 0; n--) if (headings[n].getClientRects().length && headings[n].getBoundingClientRect().top <= 64) {anchor = headings[n]; break;}
      }
      const rect = anchor?.getBoundingClientRect();
      return {anchor:anchor?.id || "", offset:rect ? -rect.top : 0, x:win.scrollX, y:win.scrollY,
        ratio:Math.min(1, win.scrollY / Math.max(1, doc.documentElement.scrollHeight - win.innerHeight)),
        progress:rect ? Math.max(0, Math.min(1, -rect.top / Math.max(1, rect.height))) : 0, extent:rect?.height || 0, width:win.innerWidth};
    }
    function captureVisible() {
      const state = getState();
      for (const side of sides) {
        if (!isCurrent(side) || getFrame(side).closest(".side-pane").hidden || restoring[side]) continue;
        try {
          const pdf = pdfs[side];
          cached[side] = {url:state[side], html:htmlPosition(side), pdf:pdf?.url === state[side] ? pdf.hash : null,
            rotation:pdf?.url === state[side] ? pdf.app.pdfViewer.pagesRotation : 0};
        } catch {}
      }
    }
    function capture() {
      captureVisible();
      const state = getState(), positions = {};
      for (const side of sides) positions[side] = restoring[side]?.saved.url === state[side] ? restoring[side].saved : cached[side]?.url === state[side] ? cached[side] : null;
      return snapshot({...state, schema:1, positions, updatedAt:Date.now()}, base, data);
    }
    function rememberNow(force = false) {
      clearTimeout(timer);
      if (!latest().remember || !force && document.visibilityState === "hidden") return;
      const last = capture();
      if (last) store({...saved, last});
    }
    function changed() {
      const state = getState();
      for (const side of sides) if (restoring[side] && restoring[side].saved.url !== state[side]) delete restoring[side];
      clearTimeout(timer);
      if (saved.remember) timer = setTimeout(() => rememberNow(), 650);
    }
    function complete(side) {
      const task = restoring[side];
      if (task?.htmlDone && task.pdfDone) {
        delete restoring[side]; captureVisible(); changed();
      }
    }
    function restorePdf(side, record) {
      const task = restoring[side];
      if (!task || task.pdfDone || record.url !== task.saved.url || !active(side, record.doc) || getFrame(side).closest(".side-pane").hidden) return;
      const hash = task.saved.pdf, app = record.app;
      // PDF.js reads this before its initial view and emits documentinit afterwards.
      app.initialBookmark = hash;
      if (!app.pdfDocument || !app.isInitialViewSet) return;
      record.touched = false;
      const apply = () => {
        if (!active(side, record.doc) || record.touched) return;
        app.pdfViewer.pagesRotation = task.saved.rotation;
        app.pdfLinkService.setHash(hash);
      };
      apply(); record.hash = hash; task.pdfDone = true; complete(side);
      // An uneven-page PDF can adjust its initial view once page sizes resolve.
      Promise.resolve(app.pdfViewer.pagesPromise).then(() => requestAnimationFrame(apply)).catch(() => {});
    }
    function restore(side) {
      const task = restoring[side];
      if (!task || !isCurrent(side) || getState()[side] !== task.saved.url || getFrame(side).closest(".side-pane").hidden) return;
      const frame = getFrame(side), doc = frame.contentDocument;
      if (!task.htmlDone && !task.htmlPending) {
        task.htmlPending = true;
        Promise.resolve(frame.contentWindow.MathJax?.startup?.promise).catch(() => {}).then(() => requestAnimationFrame(() => {
          if (restoring[side] !== task || !active(side, doc)) return;
          const html = task.saved.html, win = frame.contentWindow;
          if (html) {
            const anchor = html.anchor && doc.getElementById(html.anchor);
            if (anchor) {
              for (let parent = anchor.parentElement; parent; parent = parent.parentElement) if (parent.matches("details")) parent.open = true;
              const rect = anchor.getBoundingClientRect();
              const offset = Math.abs(win.innerWidth - html.width) < 32 ? html.offset :
                html.extent && html.offset >= 0 && html.offset <= html.extent ? html.progress * rect.height : html.offset * (html.width || win.innerWidth) / win.innerWidth;
              if (task.focus) {
                if (!anchor.hasAttribute("tabindex")) anchor.tabIndex = -1;
                anchor.focus({preventScroll:true});
              }
              win.scrollTo(html.x, rect.top + win.scrollY + offset);
            } else win.scrollTo(html.x, html.width === win.innerWidth ? html.y : html.ratio * Math.max(0, doc.documentElement.scrollHeight - win.innerHeight));
          }
          task.htmlDone = true; complete(side);
        }));
      }
      if (!task.pdfDone && pdfs[side]) restorePdf(side, pdfs[side]);
    }
    function watch(side) {
      const frame = getFrame(side), doc = frame.contentDocument;
      if (!doc || !isCurrent(side)) return;
      if (watched[side] !== doc) {
        watched[side] = doc;
        frame.contentWindow.addEventListener("scroll", changed, {passive:true});
        const nested = doc.querySelector("iframe.pdf-reader");
        if (nested) {
          let connecting;
          const connect = async () => {
            try {
              const app = nested.contentWindow.PDFViewerApplication;
              if (!app || connecting === app) return;
              connecting = app;
              await app.initializedPromise;
              if (!active(side, doc)) return;
              const record = {app, doc, url:getState()[side], hash:null, touched:false};
              pdfs[side] = record;
              for (const event of ["pointerdown", "keydown", "wheel", "touchstart"]) nested.contentDocument.addEventListener(event, () => {record.touched = true;}, {passive:true});
              app.eventBus.on("updateviewarea", event => {
                if (!active(side, doc) || restoring[side]?.saved.pdf && !restoring[side].pdfDone) return;
                record.hash = pdfHash(event.location?.pdfOpenParams) || record.hash;
                changed();
              });
              app.eventBus.on("documentinit", () => restorePdf(side, record));
              app.eventBus.on("documentloaded", () => restorePdf(side, record));
              restorePdf(side, record);
              if (!record.hash && app.pdfDocument) record.hash = pdfHash("page=" + app.page + "&zoom=" + (Number(app.pdfViewer.currentScaleValue) ? Number(app.pdfViewer.currentScaleValue) * 100 : app.pdfViewer.currentScaleValue));
              changed();
            } catch {}
          };
          nested.addEventListener("load", connect);
          connect();
        } else delete pdfs[side];
      }
      restore(side); changed();
    }
    function prepare(session, focus = false) {
      for (const side of sides) {
        const value = session.positions[side];
        if (value) restoring[side] = {saved:value, htmlDone:!value.html, pdfDone:!value.pdf,
          focus:focus && (session.view === side || session.view === "both" && side === "left")};
        else delete restoring[side];
      }
    }
    function list() {
      const select = $("side-session-list"), previous = select.value;
      select.replaceChildren(new Option("Choose a saved session", ""));
      for (const entry of saved.bookmarks) {
        const available = Boolean(snapshot(entry.session, base, data));
        select.add(new Option(entry.name + (available ? "" : " (document unavailable)"), entry.name));
      }
      select.value = saved.bookmarks.some(entry => entry.name === previous) ? previous : "";
      selection();
    }
    function selection() {
      const entry = saved.bookmarks.find(row => row.name === $("side-session-list").value);
      $("side-session-open").disabled = !entry || !snapshot(entry.session, base, data);
      $("side-session-delete").disabled = !entry;
    }
    $("side-session-remember").checked = saved.remember;
    $("side-session-resume").hidden = !resume;
    if (resume) $("side-session-last").textContent = titleFor(resume.left) + " · " + titleFor(resume.right);
    $("side-session-resume-button").addEventListener("click", () => {
      if (!resume) return;
      prepare(resume, true); restoreSession(resume); resume = null;
      $("side-session-resume").hidden = true;
      message("Your previous reading session is open.");
    });
    $("side-session-remember").addEventListener("change", () => {
      const remember = $("side-session-remember").checked;
      saved = {...latest(), remember, last:remember ? capture() : null};
      if (!remember) {resume = null; $("side-session-resume").hidden = true; clearTimeout(timer);}
      store(saved, remember ? "This browser will remember your last reading session." : "The automatic session has been cleared. Named sessions are still available.");
    });
    $("side-session-save").addEventListener("submit", event => {
      event.preventDefault();
      try {
        const name = $("side-session-name").value.trim(), session = capture();
        if (!session) throw new Error("Wait for the document list to finish loading.");
        const next = withBookmark(latest(), name, session);
        if (store(next, "Saved “" + name + "” in this browser.")) {
          list(); $("side-session-list").value = name; selection();
        }
      } catch (error) {message(error.message);}
    });
    $("side-session-list").addEventListener("change", selection);
    $("side-session-open").addEventListener("click", () => {
      const entry = latest().bookmarks.find(row => row.name === $("side-session-list").value);
      const session = entry && snapshot(entry.session, base, data);
      if (!session) {message("A document in that session is no longer in the reading catalogue."); return;}
      prepare(session, true); restoreSession(session); message("Opened “" + entry.name + "”.");
    });
    $("side-session-delete").addEventListener("click", () => {
      const name = $("side-session-list").value;
      const current = latest();
      if (name && store({...current, bookmarks:current.bookmarks.filter(row => row.name !== name)}, "Deleted “" + name + "”.")) {list(); $("side-session-list").focus();}
    });
    window.addEventListener("pagehide", () => rememberNow(true));
    document.addEventListener("visibilitychange", () => {if (document.visibilityState === "hidden") rememberNow(true);});
    window.addEventListener("storage", event => {
      if (event.key !== key) return;
      const before = saved;
      saved = library(event.newValue);
      $("side-session-remember").checked = saved.remember;
      if (!saved.remember) {resume = null; $("side-session-resume").hidden = true;}
      if (JSON.stringify(before.bookmarks) !== JSON.stringify(saved.bookmarks) || before.remember !== saved.remember) {
        list(); message("Saved reading sessions were updated in another tab.");
      }
    });
    list();
    if (!storage) message("Browser storage is unavailable. You can still copy a link to the current pair.");
    return {changed, captureVisible, watch, restore, prepare,
      focusCurrent(side) {
        if (!isCurrent(side)) return false;
        const frame = getFrame(side), win = frame.contentWindow, html = htmlPosition(side);
        const target = html.anchor && frame.contentDocument.getElementById(html.anchor);
        if (target) {
          if (!target.hasAttribute("tabindex")) target.tabIndex = -1;
          target.focus({preventScroll:true});
        } else frame.focus();
        frame.scrollIntoView({block:"nearest"});
        win.scrollTo(html.x, html.y);
        return true;
      },
      initial() {
        const session = initialSession(saved, location.href, base, data, performance.getEntriesByType("navigation")[0]?.type);
        if (!session) return null;
        prepare(session); resume = null; $("side-session-resume").hidden = true; return session;
      }};
  }
  const api = {pdfHash, snapshot, library, withBookmark, writeLibrary, initialSession, create};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.KomorebiReaderSessions = api;
})(globalThis);
