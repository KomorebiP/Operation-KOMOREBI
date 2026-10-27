"""Presentation-only repairs of six inherited Paper VI figures.

Run from any directory with Python, NumPy, SciPy, Matplotlib installed. The
immutable bundled plotting sources supply every numerical model. This script
executes both their original and adjusted presentations and requires identical
curve samples, bars, heatmap arrays, axis limits, and mathematical labels before
saving the adjusted figures. It does not change a manuscript or source snapshot.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
import sys
import types

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE_SOURCE = ROOT / "source/complete/original_snapshot/companion/projector_transfer_semigroups/visuals.py"
EXT_SOURCE = ROOT / "source/strengthened/verification/generate_figures.py"
SOURCE_HASHES = {
    "core": "6e3af24ce000a72d7b0f77f6e697f89629d5ab3fdacfbe74aeebd5809a6919d1",
    "extension": "1fef29add88da6e4923e8951b59eadd9f91d06166f1e87949d81cf9eb6244f37",
}
CORE_TARGETS = {"01_transfer_semigroup_architecture", "18_bayesian_information_loss", "19_fractional_naturality"}
BEFORE = {}
AFTER = {}
CONTRASTS = []
HASHES_BEFORE = {}
HASHES_AFTER = {}
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42})
SAVEFIG = Figure.savefig
DATE = datetime.datetime(2026, 10, 9, tzinfo=datetime.timezone.utc)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arr_record(values):
    array = np.ascontiguousarray(np.asarray(values, dtype=float))
    return {"shape": list(array.shape), "sha256_float64": hashlib.sha256(array.tobytes()).hexdigest()}


def normalized(text):
    return " ".join(text.split())


def payload(fig, architecture=False):
    if architecture:
        # The seven ordered nodes and six successive arrows are specified by
        # the original source. Position, node shape, color, and font are layout.
        texts = [normalized(t.get_text()) for t in fig.axes[0].texts if t.get_text()]
        return {"node_labels": [t for t in texts if t in ["seed", "transfer", "project", "condition", "refine", "complete", "reconstruct"]],
                "descriptor": [t for t in texts if "semigroup / resolvent" in t],
                "title": normalized(fig.axes[0].get_title()),
                "arrow_count": sum(t.arrow_patch is not None for t in fig.axes[0].texts if hasattr(t, "arrow_patch"))}
    axes = []
    for ax in fig.axes:
        axes.append({
            "lines": [{"x": arr_record(line.get_xdata(orig=False)), "y": arr_record(line.get_ydata(orig=False)), "label": line.get_label(), "linestyle": line.get_linestyle()} for line in ax.lines],
            "bars": [{"x": float(p.get_x()), "y": float(p.get_y()), "width": float(p.get_width()), "height": float(p.get_height())} for p in ax.patches],
            "meshes": [arr_record(c.get_array()) for c in ax.collections if hasattr(c, "get_array") and c.get_array() is not None],
            "xlim": list(ax.get_xlim()), "ylim": list(ax.get_ylim()),
            "xlabel": normalized(ax.get_xlabel()), "ylabel": normalized(ax.get_ylabel()),
            "title": normalized(ax.get_title()),
            "text": [normalized(t.get_text()) for t in ax.texts if t.get_text()],
        })
    return {"axes": axes}


def save_selected(fig, directory, stem, after=False):
    if stem not in CORE_TARGETS:
        plt.close(fig)
        return
    key = f"core_figures/{stem}"
    (AFTER if after else BEFORE)[key] = payload(fig, stem.startswith("01_"))
    if after:
        assert AFTER[key] == BEFORE[key], f"Mathematical figure payload changed: {key}"
        for ext in ("pdf", "png"):
            path = HERE / f"{key}.{ext}"
            HASHES_BEFORE[str(path.relative_to(ROOT))] = sha(path)
            kw = {"bbox_inches": "tight"}
            if ext == "pdf":
                kw["metadata"] = {"CreationDate": DATE, "ModDate": DATE}
            else:
                kw["dpi"] = 220
            SAVEFIG(fig, path, **kw)
            HASHES_AFTER[str(path.relative_to(ROOT))] = sha(path)
    plt.close(fig)


def module_from_source(text, name):
    module = types.ModuleType(name)
    module.__file__ = str(CORE_SOURCE)
    module.__package__ = "projector_transfer_semigroups"
    exec(compile(text, str(CORE_SOURCE), "exec"), module.__dict__)
    return module


def replace_once(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old))
    return text.replace(old, new)


def build_core():
    source = CORE_SOURCE.read_text()
    assert sha(CORE_SOURCE) == SOURCE_HASHES["core"]
    sys.path.insert(0, str(CORE_SOURCE.parents[1]))
    original = module_from_source(source, "paper_vi_original_figures")
    original._save = lambda fig, directory, stem: save_selected(fig, directory, stem)
    original.make_visuals(HERE / "core_figures")

    start = source.index("    # 1. Program architecture.")
    end = source.index("    # 2. Packet block heatmap", start)
    architecture = '''    # 1. Program architecture: original order, compact readable layout.
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    labels = ["seed", "transfer", "project", "condition", "refine", "complete", "reconstruct"]
    positions = [(.10,.72),(.36,.72),(.62,.72),(.88,.72),(.88,.36),(.55,.36),(.20,.36)]
    ax.set_xlim(-.02,1.02);ax.set_ylim(0,1)
    nodes=[]
    for label, (x0, y0) in zip(labels, positions):
        nodes.append(ax.text(x0,y0,label,ha="center",va="center",fontsize=13,
                bbox={"boxstyle":"round,pad=.48","facecolor":"#edf5fa","edgecolor":"#245777","linewidth":1.2}))
    fig.canvas.draw()
    bounds=[node.get_bbox_patch().get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted()) for node in nodes]
    for i in range(len(labels)-1):
        xa,ya=positions[i];xb,yb=positions[i+1]
        if ya == yb:
            sign = 1 if xb > xa else -1
            begin=((bounds[i].x1 if sign > 0 else bounds[i].x0)+.012*sign,ya)
            finish=((bounds[i+1].x0 if sign > 0 else bounds[i+1].x1)-.012*sign,yb)
        else:
            begin=(xa,bounds[i].y0-.012);finish=(xb,bounds[i+1].y1+.012)
        ax.annotate("",xy=finish,xytext=begin,arrowprops={"arrowstyle":"->","lw":1.4,"color":"#245777"})
    ax.text(.5,.10,"semigroup / resolvent / Bayesian normalization /\\nfractional power",ha="center",va="center",fontsize=11.5)
    ax.set_xlim(-.02,1.02);ax.set_ylim(0,1)
    ax.axis("off")
    ax.set_title("Common operator language of the\\ntransfer-semigroup realization",fontsize=14,pad=12)
    _save(fig,out,"01_transfer_semigroup_architecture")
    stems.append("01_transfer_semigroup_architecture")

'''
    adjusted = source[:start] + architecture + source[end:]
    adjusted = replace_once(adjusted, 'plt.subplots(1,2,figsize=(11.8,4.8))', 'plt.subplots(2,1,figsize=(7.2,8.5))', count=2)
    adjusted = replace_once(adjusted, 'set_title("Defect grows from hidden within-packet evidence")', 'set_title("Defect grows from hidden\\nwithin-packet evidence")')
    adjusted = replace_once(adjusted, 'set_title("The information-loss packet is their difference")', 'set_title("The information-loss packet\\nis their difference")')
    adjusted = replace_once(adjusted, 'set_title("Generator defects transfer to fractional powers")', 'set_title("Generator defects transfer\\nto fractional powers")')
    adjusted = replace_once(adjusted, 'axes[0].legend(fontsize=8.5)', 'axes[0].legend(fontsize=11)')
    adjusted = replace_once(adjusted, 'axes[1].legend(fontsize=9)', 'axes[1].legend(fontsize=11)')
    mod = module_from_source(adjusted, "paper_vi_readable_figures")
    mod._save = lambda fig, directory, stem: save_selected(fig, directory, stem, after=True)
    mod.make_visuals(HERE / "core_figures")


def luminance(rgb):
    srgb = np.asarray(rgb[:3])
    linear = np.where(srgb <= .04045, srgb / 12.92, ((srgb + .055) / 1.055) ** 2.4)
    return float(linear @ np.array([.2126, .7152, .0722]))


def annotation_color(im, value):
    background = luminance(im.cmap(im.norm(value)))
    black = (background + .05) / .05
    white = 1.05 / (background + .05)
    contrast = max(black, white)
    assert contrast >= 4.5
    CONTRASTS.append(contrast)
    return "black" if black >= white else "white"


def build_heatmaps():
    source = EXT_SOURCE.read_text()
    assert sha(EXT_SOURCE) == SOURCE_HASHES["extension"]
    start = source.index("A = np.array(")
    end = source.index("# 2. Duhamel defect", start)
    block = source[start:end]

    def capture(self, filename, *args, **kwargs):
        stem = Path(filename).stem
        key = f"extension_figures/{stem}"
        (AFTER if after else BEFORE)[key] = payload(self)
        if after:
            assert AFTER[key] == BEFORE[key], f"Heatmap payload changed: {key}"
            path = HERE / f"{key}.pdf"
            HASHES_BEFORE[str(path.relative_to(ROOT))] = sha(path)
            SAVEFIG(self,path,metadata={"CreationDate":DATE,"ModDate":DATE})
            HASHES_AFTER[str(path.relative_to(ROOT))] = sha(path)

    Figure.savefig = capture
    try:
        for after in (False, True):
            adjusted = block
            if after:
                adjusted = replace_once(adjusted, 'ax.text(j+0.5,i+0.5,f"{B[i,j]:.3f}",ha="center",va="center")',
                    'ax.text(j+0.5,i+0.5,f"{B[i,j]:.3f}",ha="center",va="center",color=annotation_color(im,B[i,j]),fontsize=11)')
            exec(compile(adjusted,str(EXT_SOURCE),"exec"),{"np":np,"plt":plt,"expm":expm,"OUT":HERE/"extension_figures","annotation_color":annotation_color})
    finally:
        Figure.savefig = SAVEFIG


def main():
    build_core()
    build_heatmaps()
    assert len(AFTER) == 6
    inherited_hashes = {}
    for relative in HASHES_AFTER:
        path = Path(relative)
        original_dir = ROOT / ("source/complete/original_snapshot/manuscript/figures" if "core_figures" in path.parts else "source/strengthened/figures")
        inherited_hashes[relative] = sha(original_dir / path.name)
    report = {
        "status":"PASS_PRESENTATION_PAYLOAD_PRESERVATION",
        "scope":"Six inherited figure identities. No manuscript, proof, or immutable plotting source edited.",
        "source_hashes":SOURCE_HASHES,
        "sources":{"core":str(CORE_SOURCE.relative_to(ROOT)),"extension":str(EXT_SOURCE.relative_to(ROOT))},
        "changes":[
            "Core01: two rows of readable high-contrast boxes retain the seven nodes and six successive arrows.",
            "Core18 and core19: stack the same two panels vertically and enlarge the two fractional legends. Wrap existing title text only.",
            "Three extension packet-block heatmaps: contrast-aware black or white annotations and 10pt to 11pt annotation font. All cell values, color maps, ranges, and axis labels retained.",
        ],
        "payload_comparison":"Byte hashes of identical float64 curve coordinates and heatmap arrays, exact bar coordinates, exact axis limits, normalized existing titles and labels. Architecture node order and arrow count exact.",
        "minimum_annotation_contrast_ratio":min(CONTRASTS),
        "baseline_generated_payloads":BEFORE,
        "updated_generated_payloads":AFTER,
        "asset_hashes_before_this_run":HASHES_BEFORE,
        "asset_hashes_original_inherited_edition":inherited_hashes,
        "asset_hashes_after_this_run":HASHES_AFTER,
        "runtime":{"python":sys.version.split()[0],"numpy":np.__version__,"matplotlib":matplotlib.__version__},
        "visual_qa":"See FIGURE_VISUAL_AUDIT.json. Generation assertions are separate from rendered visual inspection.",
    }
    (HERE/"FIGURE_READABILITY_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"figure_identities":len(AFTER),"minimum_annotation_contrast_ratio":min(CONTRASTS)}))


if __name__ == "__main__":
    main()
