"""Presentation-only repairs of Paper VIII figures 01, 17, 18, and 22.

Inputs are the exact inherited sanitized measurement corpus and six architecture
labels in the preserved source generator. No benchmarks are run by this script.
Run from any directory. By default it writes PDFs under staged/; use
--output-dir ../figures to regenerate the publication assets deliberately.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
plt.rcParams.update({
    "font.size": 9.5, "axes.titlesize": 10.5, "axes.labelsize": 9.5,
    "legend.fontsize": 8.5, "pdf.fonttype": 42, "ps.fonttype": 42,
})
METADATA = {
    "Creator": "Paper VIII presentation repair generator",
    "CreationDate": datetime(2026, 10, 9, tzinfo=timezone.utc),
    "ModDate": datetime(2026, 10, 9, tzinfo=timezone.utc),
}


def save(fig, out, stem):
    fig.savefig(out / f"{stem}.pdf", bbox_inches="tight", metadata=METADATA)
    plt.close(fig)


def architecture(out, model):
    labels = ["packet coordinates", "operator representation", "cost and error model",
              "compiler decision", "device schedule", "declared output"]
    wrapped = ["packet\ncoordinates", "operator\nrepresentation", "cost and\nerror model",
               "compiler\ndecision", "device\nschedule", "declared\noutput"]
    assert [s.replace("\n", " ") for s in wrapped] == labels
    fig, ax = plt.subplots(figsize=(11.2, 2.8))
    for i, label in enumerate(wrapped):
        ax.add_patch(FancyBboxPatch((i - .42, -.16), .84, .32,
                                   boxstyle="round,pad=.03", fill=False, linewidth=1.2))
        ax.text(i, 0, label, ha="center", va="center", linespacing=1.2)
        if i < len(labels)-1:
            ax.annotate("", xy=(i+.54, 0), xytext=(i+.44, 0),
                        arrowprops={"arrowstyle":"->", "lw":1.2})
    ax.set(xlim=(-.55,len(labels)-.45), ylim=(-.35,.35))
    ax.axis("off")
    ax.set_title("A packet computation is specified before it is scheduled")
    model["01"] = {"labels":labels, "directed_edges":[[i,i+1] for i in range(5)]}
    save(fig, out, "01_packet_compilation_architecture")


def output_contracts(df, out, model):
    rows = df[df["suite"] == "bdlr_product"].copy()
    pivot = rows.pivot_table(index="n", columns="method", values="median_ms", aggfunc="first")
    methods = [m for m in ["gpu_dense_torch_float32", "gpu_packet_compressed_product",
               "gpu_packet_product_materialized", "cpu_packet_compressed_product"]
               if m in pivot.columns]
    labels = {"gpu_dense_torch_float32":"GPU dense torch float32",
              "gpu_packet_compressed_product":"GPU packet compressed product",
              "gpu_packet_product_materialized":"GPU packet product materialized",
              "cpu_packet_compressed_product":"CPU packet compressed product"}
    fig, ax = plt.subplots(figsize=(8.0, 5.4))
    x = np.arange(len(pivot.index))
    width = .82 / len(methods)
    for j, method in enumerate(methods):
        ax.bar(x+(j-(len(methods)-1)/2)*width, pivot[method], width=width, label=labels[method])
    ax.set_xticks(x, [str(int(v)) for v in pivot.index])
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("median time in milliseconds")
    ax.set_title("Compressed factors and explicit matrices are different outputs", pad=42)
    ax.legend(loc="lower center", bbox_to_anchor=(.5,1.005), ncol=2, fontsize=7.8)
    ax.grid(axis="y", alpha=.2)
    model["17"] = {"dimensions":[int(x) for x in pivot.index],
                   "method_order":methods, "legend_labels":[labels[m] for m in methods],
                   "median_ms":{m:[float(x) for x in pivot[m]] for m in methods}}
    save(fig, out, "17_output_contract_timings")


def discovery(df, out, model):
    rows = df[(df["suite"] == "hidden_permuted_blocks") &
              (df["method"] == "cpu_packet_detect_then_apply")].sort_values("n")
    dense = [float(df[(df["case_id"]==cid) & (df["method"]=="cpu_dense_numpy")]
                   ["median_ms"].iloc[0]) for cid in rows["case_id"]]
    fig, ax = plt.subplots(figsize=(7.4,4.6))
    ax.plot(rows["n"], rows["structure_discovery_ms"], marker="o", label="one time discovery")
    ax.plot(rows["n"], rows["median_ms"], marker="o", label="packet application")
    ax.plot(rows["n"], dense, marker="o", label="dense application")
    for j, (_, row) in enumerate(rows.iterrows()):
        last = j == len(rows)-1
        ax.annotate(f"reuse {int(row['reuse_count'])}",
                    (row["n"], row["structure_discovery_ms"]),
                    xytext=((-5 if last else 5),-14), textcoords="offset points",
                    ha=("right" if last else "left"), va="top")
    ax.set_yscale("log")
    ax.set_xlabel("dimension")
    ax.set_ylabel("time in milliseconds")
    ax.set_title("Structure discovery must be amortized")
    ax.grid(alpha=.25)
    ax.legend()
    model["18"] = {"dimensions":[int(x) for x in rows["n"]],
                   "case_ids":list(rows["case_id"]),
                   "structure_discovery_ms":[float(x) for x in rows["structure_discovery_ms"]],
                   "packet_median_ms":[float(x) for x in rows["median_ms"]],
                   "matched_dense_median_ms":dense,
                   "reuse_count":[int(x) for x in rows["reuse_count"]]}
    save(fig, out, "18_discovery_amortization")


def contract_counts(df, out, model):
    counts = df.groupby(["timing_scope","output_contract"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9.2,5.2))
    left = np.zeros(len(counts))
    y = np.arange(len(counts))
    for contract in counts.columns:
        values = counts[contract].to_numpy()
        ax.barh(y, values, left=left, height=.62, label=str(contract).replace("_"," "))
        left += values
    labels = [str(x).replace("_"," ") for x in counts.index]
    wrapped = [s.replace("host to device compute device to host",
                         "host to device compute\ndevice to host") for s in labels]
    assert [x.replace("\n"," ") for x in wrapped] == labels
    ax.set_yticks(y, wrapped)
    ax.invert_yaxis()
    ax.set_xlabel("recorded rows")
    ax.set_ylabel("timing scope")
    ax.set_title("The corpus separates timing scope from output contract")
    ax.grid(axis="x",alpha=.2)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(.5,-.17), ncol=4, fontsize=8.0)
    model["22"] = {"timing_scopes":list(counts.index),
                   "output_contracts":list(counts.columns),
                   "counts":[[int(v) for v in row] for row in counts.to_numpy()],
                   "total_recorded_rows":int(counts.to_numpy().sum())}
    save(fig, out, "22_benchmark_contracts")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE/"staged")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    data = json.loads((HERE/"raw_inputs/benchmark_results_sanitized.json").read_text())
    df = pd.DataFrame(data["results"])
    model = {"measurement_status":"inherited corpus; no new hardware timings",
             "schema_version":data["schema_version"]}
    architecture(out,model)
    output_contracts(df,out,model)
    discovery(df,out,model)
    contract_counts(df,out,model)
    (out/"plotted_models.json").write_text(json.dumps(model,indent=2)+"\n")


if __name__ == "__main__":
    main()
