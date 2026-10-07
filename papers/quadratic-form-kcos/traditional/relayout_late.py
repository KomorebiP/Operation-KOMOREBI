#!/usr/bin/env python3
"""Publication-only chart derivatives from the unchanged archived CSV inputs.

No solver runs or new measurements occur here. Original images remain in
../engine/figures_final. Clean late figures are copied byte for byte.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "engine"
OUT = HERE / "figures_final"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
                     "legend.fontsize": 9, "xtick.labelsize": 10, "ytick.labelsize": 10})
RECORDS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return list(csv.DictReader((ENGINE / name).open(newline="")))


def chart(title, xlabel, ylabel, note=""):
    fig = plt.figure(figsize=(8, 5.7))
    ax = fig.add_axes([.13, .30, .83, .49])
    fig.text(.545, .95, title, ha="center", va="top", fontsize=13)
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_ylabel(ylabel, labelpad=8)
    ax.grid(True, alpha=.25)
    if note:
        fig.text(.13, .085, note, ha="left", va="bottom", fontsize=10, linespacing=1.4)
    return fig, ax


def legend(fig, ax, ncol=2):
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="center", bbox_to_anchor=(.545, .85),
               ncol=ncol, frameon=False, fontsize=9)


def add_line(ax, xs, ys, *, label, **kw):
    """Verify rendered artist coordinates equal the supplied CSV-derived arrays."""
    line, = ax.plot(xs, ys, label=label, **kw)
    assert np.array_equal(np.asarray(line.get_xdata()), np.asarray(xs))
    assert np.array_equal(np.asarray(line.get_ydata()), np.asarray(ys))
    return {"label": label, "x": list(xs), "y": list(ys)}


def finish(fig, name, csv_names, recipe, series, original_defect):
    fig.savefig(OUT / name, dpi=240, facecolor="white")
    plt.close(fig)
    RECORDS.append({"figure": name, "action": "layout derivative", "original_defect": original_defect,
                    "original_sha256": sha(ENGINE / "figures_final" / name),
                    "output_sha256": sha(OUT / name), "source_csv": csv_names,
                    "coordinate_recipe": recipe, "artist_coordinate_checks": "passed",
                    "series": series, "independent_visual_review": "pending"})


def main():
    source_names = ["realistic_skat_scenarios.csv", "realistic_streaming_invariance.csv",
                    "realistic_deep_tail_accuracy.csv", "realistic_large_deeper_tail.csv",
                    "reference_convergence.csv", "noncentral_exact_controls.csv",
                    "signed_precision_summary.csv", "interval_deep_tail_controls.csv",
                    "interval_precision_sweep_1e5000.csv"]
    before = {name: sha(ENGINE / name) for name in source_names}

    name = "figure_18_realistic_ld_effective_rank.png"
    rows = read("realistic_skat_scenarios.csv")
    fig, ax = chart("LD structure reshapes the SKAT spectrum", "", "Effective spectral rank")
    xs = list(range(len(rows))); ys = [float(r["effective_rank"]) for r in rows]
    bars = ax.bar(xs, ys, color="C0")
    assert np.array_equal([b.get_height() for b in bars], ys)
    ax.set_xticks(xs, ["gaussian LD\nmoderate", "gaussian LD\nstrong", "copy LD\nstrong fixed", "copy LD\nlarge fixed"])
    ax.set_ylim(0, 490)
    for x, y, row in zip(xs, ys, rows):
        ax.text(x, y + 8, f"median adjacent $r^2$={float(row['median_adjacent_within_block_r2']):.2f}",
                ha="center", va="bottom", fontsize=9)
    finish(fig, name, ["realistic_skat_scenarios.csv"], "row order; x=ordinal; y=effective_rank; r² labels rounded to two decimals as archived figure", [{"x": xs, "y": ys}], "Long rotated scenario names reduced chart sizing; wrapped without changing categories.")

    name = "figure_19_realistic_streaming_invariance.png"
    rows = read("realistic_streaming_invariance.csv")
    fig, ax = chart("Streaming is invariant to resident block size", "Resident variant block size", "Kernel relative error",
                    "Block size changes execution and memory footprint, not the exact operator.\nAll discrepancies remain at machine precision across Gaussian-LD and copy-LD controls.")
    series = []
    for scenario in dict.fromkeys(r["scenario"] for r in rows):
        group = [r for r in rows if r["scenario"] == scenario]
        series.append(add_line(ax, [float(r["block_size"]) for r in group], [float(r["kernel_relative_error"]) for r in group],
                               label=scenario.replace("_", " "), marker="o"))
    ax.set_yscale("log"); legend(fig, ax, 2)
    finish(fig, name, ["realistic_streaming_invariance.csv"], "group by scenario in CSV order; x=block_size; y=kernel_relative_error", series, "Green curve crossed both explanatory lines.")

    name = "figure_20_realistic_deep_tail_accuracy.png"
    rows = read("realistic_deep_tail_accuracy.csv") + read("realistic_large_deeper_tail.csv")
    fig, ax = chart("Realistic LD spectra remain accurate deep into the log tail", r"Tail depth $-\log_{10}p$", "Absolute discrepancy (decades)",
                    "Deepest corrected copy-LD point: log10(p) = -458.0.\nWorst discrepancy: 3.21e-12 decades. Zero discrepancies use the archived 1e-16 display floor.")
    xs = [-float(r["reference_log10_p"]) for r in rows]; ys = [max(abs(float(r["difference_decades"])), 1e-16) for r in rows]
    points = ax.scatter(xs, ys, s=35, color="C0")
    assert np.array_equal(np.asarray(points.get_offsets()), np.column_stack([xs, ys]))
    ax.set_yscale("log")
    finish(fig, name, ["realistic_deep_tail_accuracy.csv", "realistic_large_deeper_tail.csv"], "concatenate CSVs; x=-reference_log10_p; y=max(abs(difference_decades),1e-16) using archived zero floor", [{"x": xs, "y": ys}], "Upper-left explanatory text obscured the point cluster.")

    name = "figure_21_reference_convergence.png"
    rows = read("reference_convergence.csv")
    fig, ax = chart("A nominal reference can be under-resolved in the deep tail", "Reference COS grid size K", "Absolute discrepancy (decades)",
                    "The adaptive answer remained stable while the fixed-grid reference converged toward it.\nReference resolution is audited rather than assumed.")
    series = [add_line(ax, [float(r["reference_K"]) for r in rows], [abs(float(r["adaptive_minus_reference_decades"])) for r in rows], label="", marker="o")]
    ax.set_xscale("log", base=2); ax.set_yscale("log")
    finish(fig, name, ["reference_convergence.csv"], "CSV row order including repeated K; x=reference_K; y=abs(adaptive_minus_reference_decades)", series, "Long bottom note crossed the descending curve and extended outside the right axes.")

    name = "figure_22_noncentral_controls.png"
    rows = read("noncentral_exact_controls.csv")
    fig, ax = chart("Noncentral positive forms match exact\nnoncentral-chi-square controls", r"Tail depth $-\log_{10}p$", "Absolute discrepancy (decades)",
                    "Maximum observed discrepancy: 9.26e-15 decades.\nAll tested queries carried passing analytic truncation certificates.\nZero discrepancies use the archived 1e-16 display floor.")
    series = []
    for df, nc in dict.fromkeys((r["df"], r["nc"]) for r in rows):
        group = [r for r in rows if (r["df"], r["nc"]) == (df, nc)]
        series.append(add_line(ax, [-float(r["scipy_log10_p"]) for r in group], [max(abs(float(r["difference_decades"])), 1e-16) for r in group], label=f"df={df}, nc={nc}", marker="o"))
    ax.set_yscale("log"); legend(fig, ax, 3)
    finish(fig, name, ["noncentral_exact_controls.csv"], "group df,nc in CSV order; x=-scipy_log10_p; y=max(abs(difference_decades),1e-16) using archived zero floor", series, "Left rising curves crossed both bottom explanatory lines.")

    name = "figure_24_signed_certificate_boundary.png"
    rows = read("signed_precision_summary.csv")
    fig, ax = chart("Signed-form certification depends on spectral decay,\nnot tail depth alone", r"Tail depth $-\log_{10}p$", "Reported relative certificate bound",
                    "The low-rank Laplace control is numerically accurate but fails the analytic COS-series certificate.\nHigh-rank mixed spectra decay faster and remain certifiable deep into the tail.")
    series = []
    families = [("-0.02 chi2_80", "negative finite endpoint: certified", "o"),
                ("signed mixed multiscale rank 340", "mixed rank 340: certified", "s"),
                ("0.07*(chi2_2-chi2_2)", "mixed rank 4: value accurate, certificate rejects", "x")]
    for family, label, marker in families:
        group = [r for r in rows if r["family"] == family]
        series.append(add_line(ax, [float(r["tail_depth"]) for r in group], [float(r["certificate"]) for r in group], label=label, marker=marker))
    ax.axhline(1e-8, ls="--", color="C0", label="requested relative tolerance")
    ax.set_xscale("log"); ax.set_yscale("log"); legend(fig, ax, 2)
    finish(fig, name, ["signed_precision_summary.csv"], "explicit archived family order; x=tail_depth; y=certificate; tolerance=1e-8", series, "Long bottom note extended outside right axes and shrank the graph within the PDF.")

    name = "figure_24_interval_deep_tail_width.png"
    rows = read("interval_deep_tail_controls.csv")
    fig, ax = chart(r"Directed-rounding enclosures remain narrow through $10^{-5000}$", r"Tail depth $-\log_{10}p$", "Certified enclosure width (decades)")
    series = [add_line(ax, [-float(r["target_log10_p"]) for r in rows], [float(r["kcos_width_decades"]) for r in rows], label="", marker="o")]
    ax.set_xscale("log"); ax.set_yscale("log")
    for x, row in zip([.13, .42, .72], rows):
        fig.text(x, .10, f"Depth {-int(row['target_log10_p'])}: {float(row['multiplicative_ratio_minus_one']):.1e}", fontsize=10)
    fig.text(.13, .055, "Values below the plot are multiplicative ratio minus one.", fontsize=10)
    finish(fig, name, ["interval_deep_tail_controls.csv"], "CSV row order; x=-target_log10_p; y=kcos_width_decades; footer ratios=multiplicative_ratio_minus_one rounded as archived to .1e", series, "All three point labels crossed the blue line; rightmost label extended beyond axes.")

    name = "figure_25_interval_arithmetic_vs_analytic.png"
    rows = read("interval_precision_sweep_1e5000.csv")
    fig, ax = chart(r"The $10^{-5000}$ enclosure is dominated by analytic remainder," + "\nnot rounding", "Interval decimal precision", "Width in log10 probability",
                    "Increasing interval precision by 80 digits barely changes the total bound,\nwhile the arithmetic enclosure contracts by about 80 orders of magnitude.")
    series = []
    for field, label in [("total_width_decades_decimal", "Total certified width"), ("arithmetic_only_width_decades_decimal", "Arithmetic-only interval width")]:
        series.append(add_line(ax, [float(r["interval_dps"]) for r in rows], [float(r[field]) for r in rows], label=label, marker="o"))
    ax.set_yscale("log"); legend(fig, ax, 2)
    finish(fig, name, ["interval_precision_sweep_1e5000.csv"], "CSV row order; x=interval_dps; y=total_width_decades_decimal or arithmetic_only_width_decades_decimal", series, "Orange curve crossed both explanatory lines.")

    for name in ["figure_23_deep_tail_precision_envelope.png", "figure_26_accuracy_driven_refinement.png", "figure_27_imhof_p1e16_validation.png"]:
        source = ENGINE / "figures_final" / name
        shutil.copyfile(source, OUT / name)
        RECORDS.append({"figure": name, "action": "unchanged original", "original_sha256": sha(source),
                        "output_sha256": sha(OUT / name), "byte_identical": sha(source) == sha(OUT / name),
                        "independent_visual_review": "pending"})
    after = {name: sha(ENGINE / name) for name in source_names}
    assert before == after
    report = {"purpose": "Archived-data publication layout only; no fresh numerical claims",
              "source_csv_sha256": before, "source_csv_unchanged": before == after,
              "original_images_location": "../engine/figures_final", "figures": RECORDS,
              "note": "Native original generators for late plots were not present. Coordinate recipes preserve the archived CSV fields and visible original series; coordinate arrays are included for independent checking."}
    (HERE / "FIGURE_RELAYOUT_LATE.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
