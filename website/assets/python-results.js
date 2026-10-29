// Render local Python results with text alternatives and explicit downloads.
export function createResults(container, plotlyURL) {
  let loader;
  const charts = [];
  const urls = [];
  let counter = 0;
  function downloadLink(parent, text, name, content, type = "text/plain;charset=utf-8") {
    const url = URL.createObjectURL(new Blob([content], {type}));
    urls.push(url);
    const link = document.createElement("a");
    link.href = url; link.download = name; link.textContent = text;
    parent.append(link);
  }
  function loadPlotly() {
    if (!loader) loader = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = plotlyURL;
      script.onload = () => resolve(window.Plotly);
      script.onerror = () => {loader = null; script.remove(); reject(new Error("Could not load the plotting library. Try again."));};
      document.head.append(script);
    });
    return loader;
  }
  function rowsFor(traces) {
    const rows = [];
    for (const [number, trace] of traces.entries()) {
      const name = trace.name || "Series "+(number+1);
      if (["surface", "heatmap"].includes(trace.type)) {
        trace.z.forEach((row, j) => row.forEach((z, i) => rows.push([name, trace.x?.[i] ?? i, trace.y?.[j] ?? j, z])));
      } else {
        (trace.y || []).forEach((y, i) => rows.push([name, trace.x?.[i] ?? i, y, trace.z?.[i] ?? ""]));
      }
    }
    return rows;
  }
  function csvCell(value) {
    let text = String(value);
    if (typeof value === "string" && /^[=+@\t\r-]/.test(text)) text = "'"+text;
    return '"'+text.replaceAll('"', '""')+'"';
  }
  function dataTable(parent, rows) {
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = `Data table (${Math.min(100, rows.length)} of ${rows.length} samples)`;
    const scroll = document.createElement("div");
    scroll.className = "table-scroll"; scroll.tabIndex = 0;
    scroll.setAttribute("role", "region"); scroll.setAttribute("aria-label", "Plot sample data");
    const table = document.createElement("table");
    const header = table.createTHead().insertRow();
    for (const name of ["Series", "x", "y", "z"]) {
      const th = document.createElement("th"); th.scope = "col"; th.textContent = name; header.append(th);
    }
    const body = table.createTBody();
    for (const row of rows.slice(0, 100)) {
      const tr = body.insertRow();
      row.forEach(value => {tr.insertCell().textContent = String(value);});
    }
    scroll.append(table); details.append(summary, scroll); parent.append(details);
  }
  function clear() {
    for (const chart of charts) window.Plotly?.purge(chart);
    charts.length = 0;
    urls.forEach(url => URL.revokeObjectURL(url)); urls.length = 0;
    container.replaceChildren(); counter = 0;
  }
  async function add(value, isCurrent) {
    if (!isCurrent()) return true;
    const number = ++counter;
    const section = document.createElement("section"); section.className = "python-figure";
    const heading = document.createElement("h3");
    heading.textContent = value.kind === "file" ? "Export: "+value.name : "Figure "+number;
    section.append(heading);
    const actions = document.createElement("div"); actions.className = "python-actions";
    if (value.kind === "file") {
      if (!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.(csv|json|txt)$/.test(value.name) || typeof value.content !== "string") throw new Error("Invalid result file.");
      downloadLink(actions, "Download "+value.name, value.name, value.content);
      section.append(actions); container.append(section); return true;
    }
    const description = document.createElement("p"); description.textContent = value.description;
    section.append(description);
    if (value.kind === "image") {
      if (typeof value.png !== "string" || !/^[A-Za-z0-9+/=]+$/.test(value.png)) throw new Error("Invalid PNG result.");
      const image = document.createElement("img");
      image.src = "data:image/png;base64,"+value.png; image.alt = value.description;
      const link = document.createElement("a"); link.href = image.src; link.download = `figure-${number}.png`; link.textContent = "Download PNG";
      section.append(image); actions.append(link); section.append(actions); container.append(section); return true;
    }
    if (value.kind !== "plot" || !Array.isArray(value.data) || !value.data.length || value.data.length > 12 || value.data.some(trace => ![undefined, "scatter", "bar", "heatmap", "surface", "scatter3d"].includes(trace.type))) throw new Error("Unsupported interactive plot.");
    const rows = rowsFor(value.data);
    if (rows.length > 50000) throw new Error("Plot exceeds 50,000 samples.");
    const chart = document.createElement("div"); chart.className = "python-chart"; chart.tabIndex = 0;
    chart.setAttribute("role", "img"); chart.setAttribute("aria-label", value.description);
    const note = document.createElement("p"); note.setAttribute("role", "status");
    note.textContent = "Loading the plot. The data table and downloads are available below.";
    const controls = document.createElement("div"); controls.className = "python-actions";
    section.append(chart, note, controls, actions);
    const csv = [["Series", "x", "y", "z"], ...rows].map(row => row.map(csvCell).join(",")).join("\n")+"\n";
    downloadLink(actions, "Download plot data (CSV)", `figure-${number}.csv`, csv, "text/csv;charset=utf-8");
    downloadLink(actions, "Download figure (JSON)", `figure-${number}.json`, JSON.stringify(value, null, 2), "application/json");
    dataTable(section, rows); container.append(section);
    try {
      const Plotly = await loadPlotly();
      if (!isCurrent()) return true;
      const is3d = value.data.some(trace => ["surface", "scatter3d"].includes(trace.type));
      const layout = {...value.layout, autosize: true, paper_bgcolor: "#fffefa", plot_bgcolor: "#fffefa", font: {size: 14}, margin: {l: 60, r: 30, b: 60, t: 65}};
      delete layout.width; delete layout.height;
      charts.push(chart);
      await Plotly.newPlot(chart, value.data, layout, {responsive: true, displaylogo: false, scrollZoom: false, toImageButtonOptions: {format: "png"}});
      if (!isCurrent()) {Plotly.purge(chart); return true;}
      note.textContent = is3d ? "Drag to rotate. Use the view buttons with a keyboard, or inspect the data table." : "Drag to zoom. Double-click or use Reset view to restore the axes.";
      async function view(label, update) {
        await Plotly.relayout(chart, update); note.textContent = label+" applied.";
      }
      function button(label, action) {
        const b = document.createElement("button"); b.type = "button"; b.textContent = label;
        b.addEventListener("click", () => Promise.resolve(action()).catch(error => {note.textContent = String(error);})); controls.append(b);
      }
      if (is3d) {
        button("Default view", () => view("Default view", {"scene.camera": {eye: {x: 1.25, y: 1.25, z: 1.25}, up: {x: 0, y: 0, z: 1}}}));
        button("Top view", () => view("Top view", {"scene.camera": {eye: {x: 0, y: 0, z: 2.5}, up: {x: 0, y: 1, z: 0}}}));
        button("Front view", () => view("Front view", {"scene.camera": {eye: {x: 0, y: -2.5, z: 0.1}, up: {x: 0, y: 0, z: 1}}}));
      } else {
        button("Reset view", () => view("Reset view", {"xaxis.autorange": true, "yaxis.autorange": true}));
      }
      button("Download PNG", () => Plotly.downloadImage(chart, {format: "png", filename: `figure-${number}`, width: 1200, height: 800}));
      return true;
    } catch (error) {
      note.textContent = "The plot could not be drawn. 3D plots require WebGL. Use the data table or downloads. "+String(error);
      return false;
    }
  }
  return {add, clear};
}
