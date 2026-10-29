// Render local Python results with text alternatives and explicit downloads.
export function createResults(container, plotlyURL) {
  let loader;
  const charts = [];
  const urls = [];
  const observers = [];
  const colors = ["#0067a5", "#b54b00", "#007d60", "#963f87", "#6b58a3", "#89532d", "#353d46"];
  let counter = 0;
  const titleText = title => typeof title === "string" ? title : title?.text || "";
  function axisStyle(axis = {}) {
    return {automargin: true, tickfont: {size: 16}, gridcolor: "#dce1e5", zerolinecolor: "#87939c",
      ...axis, title: {text: titleText(axis.title), standoff: 16, font: {size: 17}, ...(typeof axis.title === "object" ? axis.title : {})}};
  }
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
        trace.z.forEach((row, j) => row.forEach((z, i) => {if (z != null) rows.push([name, trace.x?.[i] ?? i, trace.y?.[j] ?? j, z]);}));
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
    observers.forEach(observer => observer.disconnect()); observers.length = 0;
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
    heading.textContent = value.kind === "file" ? "Export: "+value.name : titleText(value.layout?.title) || "Figure "+number;
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
      chart.classList.toggle("python-chart-3d", is3d);
      const data = value.data.map((trace, index) => {
        if (["surface", "heatmap"].includes(trace.type)) return trace;
        const color = colors[index % colors.length];
        return {...trace, line: {color, width: is3d ? 5 : 3, ...trace.line},
          marker: {color, size: is3d ? 5 : 8, ...trace.marker}};
      });
      const layout = {...value.layout, title: undefined, showlegend: false, autosize: true,
        paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
        font: {family: "system-ui, sans-serif", size: 16, color: "#25343e"},
        hoverlabel: {font: {size: 16}}, margin: {l: 72, r: 48, b: 72, t: 28, ...value.layout?.margin},
        xaxis: axisStyle(value.layout?.xaxis), yaxis: axisStyle(value.layout?.yaxis)};
      if (is3d) {
        layout.margin = {l: 36, r: 36, b: 36, t: 36};
        layout.scene = {aspectmode: "cube", camera: {eye: {x: 1.65, y: 1.65, z: 1.25}}, ...value.layout?.scene};
        for (const axis of ["xaxis", "yaxis", "zaxis"]) {
          layout.scene[axis] = {tickfont: {size: 14}, nticks: 5, gridcolor: "#cbd4dc", showbackground: true,
            backgroundcolor: "#f3f6f8", ...layout.scene[axis]};
        }
      }
      const originalCamera = structuredClone(layout.scene?.camera || {});
      let compact = chart.clientWidth < 600;
      const defaultCamera = () => ({...originalCamera, eye: Object.fromEntries(
        Object.entries(originalCamera.eye || {}).map(([axis, distance]) => [axis, distance * (compact ? 1.6 : 1)]))});
      if (is3d) layout.scene.camera = defaultCamera();
      delete layout.width; delete layout.height;
      charts.push(chart);
      await Plotly.newPlot(chart, data, layout, {responsive: true, displaylogo: false, displayModeBar: false, scrollZoom: false});
      if (!isCurrent()) {Plotly.purge(chart); return true;}
      // Resize when the containing panel changes, not just on window resize.
      const observer = new ResizeObserver(() => {
        if (!isCurrent() || !chart.isConnected) return;
        const nextCompact = chart.clientWidth < 600;
        if (is3d && compact !== nextCompact) {
          compact = nextCompact;
          Plotly.relayout(chart, {"scene.camera": defaultCamera()}).catch(error => {note.textContent = String(error);});
        }
        Plotly.Plots.resize(chart);
      });
      observer.observe(chart); observers.push(observer);
      note.textContent = is3d ? "Drag to rotate. Use the view buttons with a keyboard, or inspect the data table." : "Drag to zoom. Double-click or use Reset view to restore the axes.";
      const series = data.map((trace, index) => ({trace, index})).filter(({trace}) => !["surface", "heatmap"].includes(trace.type));
      if (series.length > 1) {
        const fieldset = document.createElement("fieldset"); fieldset.className = "python-series";
        const legend = document.createElement("legend"); legend.textContent = "Series to show"; fieldset.append(legend);
        for (const {trace, index} of series) {
          const label = document.createElement("label");
          const check = document.createElement("input"); check.type = "checkbox"; check.checked = trace.visible !== "legendonly" && trace.visible !== false;
          const swatch = document.createElement("span"); swatch.className = "python-series-swatch"; swatch.setAttribute("aria-hidden", "true");
          swatch.style.borderColor = trace.line?.color || colors[index % colors.length];
          swatch.style.borderStyle = trace.line?.dash?.includes("dot") ? "dotted" : trace.line?.dash && trace.line.dash !== "solid" ? "dashed" : "solid";
          label.append(check, swatch, document.createTextNode(trace.name || "Series "+(index+1)));
          check.addEventListener("change", () => Plotly.restyle(chart, {visible: check.checked ? true : "legendonly"}, [index]).catch(error => {note.textContent = String(error);}));
          fieldset.append(label);
        }
        section.insertBefore(fieldset, chart);
      }
      async function view(label, update) {
        await Plotly.relayout(chart, update); note.textContent = label+" applied.";
      }
      function button(label, action) {
        const b = document.createElement("button"); b.type = "button"; b.textContent = label;
        b.addEventListener("click", () => Promise.resolve(action()).catch(error => {note.textContent = String(error);})); controls.append(b); return b;
      }
      if (is3d) {
        button("Default view", () => view("Default view", {"scene.camera": defaultCamera()}));
        button("Top view", () => view("Top view", {"scene.camera": {eye: {x: 0, y: 0, z: compact ? 4 : 2.5}, up: {x: 0, y: 1, z: 0}}}));
        button("Front view", () => view("Front view", {"scene.camera": {eye: {x: 0, y: compact ? -4 : -2.5, z: 0.1}, up: {x: 0, y: 0, z: 1}}}));
      } else {
        button("Reset view", () => view("Reset view", {"xaxis.autorange": true, "yaxis.autorange": true}));
      }
      const enlarge = button("Enlarge plot", async () => {
        const expanded = chart.classList.toggle("python-chart-large");
        enlarge.textContent = expanded ? "Standard size" : "Enlarge plot";
        enlarge.setAttribute("aria-pressed", String(expanded));
        await Plotly.Plots.resize(chart);
      });
      enlarge.setAttribute("aria-pressed", "false");
      button("Download PNG", async () => {
        // Include the title and legend in the image as well as on the page.
        const exportChart = document.createElement("div"); exportChart.className = "python-chart";
        Object.assign(exportChart.style, {position: "fixed", left: "-10000px", width: "1200px", height: "900px"});
        document.body.append(exportChart);
        try {
          const exportLayout = {...layout, width: 1200, height: 900, autosize: false,
            title: {text: titleText(value.layout?.title), x: 0.05, font: {size: 23}},
            showlegend: true, legend: {orientation: "h", y: 1.1, x: 0},
            margin: {...layout.margin, t: 135}};
          await Plotly.newPlot(exportChart, chart.data, exportLayout, {displayModeBar: false});
          await Plotly.downloadImage(exportChart, {format: "png", filename: `figure-${number}`, width: 1200, height: 900});
        } finally {Plotly.purge(exportChart); exportChart.remove();}
      });
      return true;
    } catch (error) {
      note.textContent = "The plot could not be drawn. 3D plots require WebGL. Use the data table or downloads. "+String(error);
      return false;
    }
  }
  return {add, clear};
}
