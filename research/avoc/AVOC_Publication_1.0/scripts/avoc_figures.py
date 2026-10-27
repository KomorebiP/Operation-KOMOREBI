#!/usr/bin/env python3
"""Reproducible, exact-data AVOC publication figures; decimals only at rendering."""
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from math import comb
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
DATA = json.loads((ROOT / "reviews/exact_example_results.json").read_text())
OUT.mkdir(exist_ok=True)
NAVY, BLUE, TEAL, AMBER, RED, GREY, PALE = "#17324d", "#2865a5", "#16867d", "#ca8732", "#b74d50", "#697887", "#edf3f8"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
    "axes.titlesize": 15, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#bcc9d4", "axes.labelcolor": NAVY, "text.color": NAVY,
    "xtick.color": GREY, "ytick.color": GREY,
    "figure.facecolor": "white", "axes.facecolor": "white", "pdf.fonttype": 42,
    "savefig.facecolor": "white", "savefig.dpi": 180})
CATALOGUE = []


def save(fig, stem, caption, kind="exact-data plot"):
    fig.savefig(OUT / (stem + ".pdf"), bbox_inches="tight", pad_inches=.18)
    fig.savefig(OUT / (stem + ".png"), bbox_inches="tight", pad_inches=.18)
    CATALOGUE.append({"stem": stem, "caption": caption, "kind": kind})
    plt.close(fig)


def canvas(title, size=(8, 4.7)):
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title(title, loc="left", pad=20, weight="bold")
    return fig, ax


def box(ax, x, y, w, h, text, color=BLUE, fontsize=12, fill=PALE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                              linewidth=1.3, edgecolor=color, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color=NAVY)


def arrow(ax, p, q, color=GREY, dashed=False):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=16,
                              linewidth=1.4, color=color, linestyle="--" if dashed else "-"))


fig, ax = canvas("Choose the next artifact action")
box(ax, 3.55, 4.6, 2.9, .8, "Current evidence\nRemaining budget", fontsize=11)
box(ax, .3, 2.65, 2.8, 1.1, "Inspect warm\nCheck a cached\ncandidate", TEAL, 11)
box(ax, 3.6, 2.65, 2.8, 1.1, "Generate cold\nBuild and check\na candidate", BLUE, 11)
box(ax, 6.9, 2.65, 2.8, 1.1, "Stop\nKeep the current\nsolution", GREY, 11)
for x in [1.7, 5, 8.3]: arrow(ax, (5, 4.52), (x, 3.83))
box(ax, 2.1, .65, 5.8, 1.0, "Checked success enables deployment\nRejection still consumes the stage fee", AMBER, 11)
arrow(ax, (1.7, 2.57), (3.3, 1.73)); arrow(ax, (5, 2.57), (5, 1.73))
save(fig, "01_artifact_choices", "Warm inspection and cold generation are separately charged actions. Successful checking enables deployment. A rejected check consumes its stage fee; stopping is always available.", "source-based schematic")

fig, ax = canvas("From declared evidence to a policy guarantee", (8, 5.4))
labels = [("Sampling contract", "Fixed identity, source law and schedule"),
          ("Recorder refinement", "Terminal samples equal a source prefix"),
          ("Exact calibration", "Predeclared finite-grid confidence bands"),
          ("Value transport", "Q bounds and finite-horizon regret"),
          ("Execution", "Selected checked transitions and accounting")]
for i, (head, body) in enumerate(labels):
    y = 4.9 - i * 1.02
    box(ax, .8, y, 8.4, .74, head + "\n" + body, TEAL if i == 0 else BLUE, 12)
    if i: arrow(ax, (5, y + 1.00), (5, y + .81))
ax.text(5, -.1, "Physical source integrity and durable storage need their own justification.", ha="center", fontsize=11, color=GREY)
save(fig, "02_evidence_chain", "The guarantee is a dependency chain. Formal recorder refinement supplies observed-prefix correspondence inside the declared source model. It does not authenticate a physical provider or prove durable storage.", "source-based schematic")

fig, (ax, bx) = plt.subplots(1, 2, figsize=(8, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
ax.bar([0, 1], [36, 21], color=[GREY, TEAL], width=.55)
ax.set_xticks([0, 1], ["Original", "Checked\nwidth-one"]); ax.set_ylabel("Abstract cost per call")
ax.set_ylim(0, 43); ax.set_title("Same semantics, lower cost", loc="left", weight="bold")
for x, y in [(0, 36), (1, 21)]: ax.text(x, y + 1, str(y), ha="center", weight="bold")
bx.axis("off")
for i, text in enumerate(["1,000 deployment calls", "Gross saving:\n1,000 × (36 − 21) = 15,000", "Warm setup: 133   →   net 14,867", "Cold setup: 196   →   net 14,804"]):
    bx.text(.02, .87 - i * .21, text, transform=bx.transAxes, fontsize=12)
fig.tight_layout(w_pad=2.4)
save(fig, "03_rank_one_costs", "The archived rank-one affine example has abstract original cost 36 and selected cost 21. At 1,000 calls the gross saving is 15,000. Warm and cold setup costs 133 and 196 give deterministic net savings 14,867 and 14,804. These are model costs, not measured timings.")

fig, ax = plt.subplots(figsize=(8, 4.4))
q = [F(i, 5000) for i in range(4700, 5001)]
warm = [p * 15000 - 133 for p in q]
ax.plot(list(map(float, q)), list(map(float, warm)), color=TEAL, lw=2.8, label="Warm expected net: 15,000q − 133")
ax.axhline(14804, color=BLUE, lw=2.4, label="Certain cold net: 14,804")
cross = F(4979, 5000)
ax.axvline(float(cross), color=AMBER, ls="--", lw=1.7)
ax.scatter([float(cross)], [14804], color=AMBER, zorder=5)
ax.annotate("Equal at q = 4979/5000\n(0.9958)", xy=(float(cross), 14804), xytext=(.96, 14600),
            arrowprops={"arrowstyle": "->", "color": AMBER}, color=NAVY)
ax.set_xlabel("Warm success probability q"); ax.set_ylabel("Expected net model saving")
ax.set_title("A cheaper warm stage can lose through uncertainty", loc="left", weight="bold")
ax.set_xlim(.94, 1.001); ax.legend(loc="lower right", frameon=False, fontsize=10)
fig.tight_layout()
save(fig, "04_cold_warm_crossing", "For 1,000 calls and a certainly successful cold stage, warm wins exactly when 15,000q − 133 ≥ 15,000 − 196, equivalently q ≥ 4979/5000. Stage fees are charged regardless of success. This is the two-stage expected-net comparison for the stated example.")

fig, ax = plt.subplots(figsize=(8, 4.1))
names = ["Before a stage", "After warm stage", "After cold stage"]
spent, remaining = [0, 133, 196], [196, 63, 0]
ax.barh(names, spent, color=AMBER, label="Charged / spent", height=.5)
ax.barh(names, remaining, left=spent, color=TEAL, label="Remaining", height=.5)
for i, (a, b) in enumerate(zip(spent, remaining)):
    if a: ax.text(a / 2, i, str(a), ha="center", va="center", color="white", weight="bold")
    if b: ax.text(a + b / 2, i, str(b), ha="center", va="center", color="white", weight="bold")
ax.set_xlim(0, 220); ax.set_xlabel("Model budget units"); ax.invert_yaxis()
ax.set_title("Every allowed stage preserves spent + remaining = 196", loc="left", weight="bold")
ax.legend(loc="lower right", frameon=False, fontsize=10); fig.tight_layout()
save(fig, "05_budget_accounting", "The concrete initial budget 196 becomes spent 133 plus remaining 63 after warm inspection, or spent 196 plus remaining 0 after cold generation. The fee is reserved and consumed on the allowed stage, including a rejection.")


def q_plot(ax, bands, points, title, xlim):
    for i, (name, lo, hi, color) in enumerate(bands):
        lo, hi = F(lo), F(hi)
        ax.plot([float(lo), float(hi)], [i, i], color=color, lw=7, solid_capstyle="round")
        if points[i] is not None:
            ax.scatter([float(points[i])], [i], color="white", edgecolor=NAVY, zorder=5, s=70)
        ax.text(float(lo), i + .19, str(lo), ha="center", fontsize=10, color=color)
        if hi != lo: ax.text(float(hi), i + .19, str(hi), ha="center", fontsize=10, color=color)
    ax.set_yticks(range(len(bands)), [row[0] for row in bands]); ax.invert_yaxis()
    ax.set_xlim(*xlim); ax.set_ylim(len(bands) - .5, -.55)
    ax.axvline(0, color=GREY, lw=.8); ax.set_xlabel("Certified Q interval in model units")
    ax.set_title(title, loc="left", weight="bold")


fig, ax = plt.subplots(figsize=(8, 4.8))
q_plot(ax, [("Warm Q enclosure", -88, 328, TEAL), ("Warm true Q range", 120, 200, AMBER),
           ("Cold exact Q", 60, 60, BLUE), ("Stop", 0, 0, GREY)],
       [F(120), None, F(60), F(0)], "Abstract quote fixture: conservative Q bounds", (-115, 355))
ax.text(.98, .03, "Initial: untried; setup 0; continuation h = 1\nTwo total actions: stage, then deploy\nWarm lower-Q: 120 − 208 = −88",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=11)
fig.tight_layout()
save(fig, "06_robust_q_bands", "This is the abstract uncertainModel quote-planning fixture, in the initial untried state with setup costs 0 and continuation horizon h = 1, hence two total actions: stage and then deploy. Warm nominal Q = 120 and local radius 208 give [−88, 328], while cold has Q = 60 and stop has Q = 0. The inherited lower-Q selector chooses cold even though the exact warm stage-then-deploy Q range [120, 200] exceeds cold 60. The range is a two-action expected Q range, not a primitive one-step reward. Quoted gross amounts 200 and 60 are abstract planning data. At calls = 1 the rankOneProgram original cost is 36, so these gross amounts cannot be supplied by an actual BoundedArtifact saving, which is at most 36.")

fig, ax = plt.subplots(figsize=(8, 4.3))
r = DATA["robust_calibrated"]
lo, hi = map(F, r["warm_interval"])
q_plot(ax, [("Inspect warm", lo, hi, TEAL), ("Generate cold", 60, 60, BLUE), ("Stop", 0, 0, GREY)],
       [F(r["warm_nominal"]), F(60), F(0)], "Abstract quote fixture: calibration changes the choice", (-10, 245))
ax.axvline(float(lo), color=TEAL, linestyle="--", lw=1.2)
ax.text(.97, .03, "Initial: untried; setup 0; continuation h = 1\nTwo total actions\n1738/25 > 60 and 1738/25 > 0",
        transform=ax.transAxes, ha="right", fontsize=11)
fig.tight_layout()
save(fig, "07_dominance_certificate", "For the same abstract quote-planning fixture, the n = 500, k = 400 fine-grid calibration gives warm nominal Q = 722/5 and radius 1872/25, hence [1738/25, 5482/25]. The state is initially untried, setup costs are 0, and continuation horizon h = 1 gives two total actions. The warm lower bound exceeds the distinct cold upper bound 60 and stop upper bound 0. Competitor dominance excludes self-comparison. These are abstract planning values rather than artifact-backed savings: at calls = 1, quoted gross amounts 200 and 60 exceed the rankOneProgram original cost 36 and cannot be realized by an actual BoundedArtifact saving. The numerical values were reproduced by exact arithmetic; no new Lean planner invocation was made.")

fig, ax = plt.subplots(figsize=(8, 4.4))
n, k, m, alpha = 10, 10, 10, F(1, 10)
envelopes = [F(i + 1, m) ** 10 for i in range(m)]
colors = [TEAL if value > alpha / (n + 1) else GREY for value in envelopes]
ax.bar([float(F(2 * i + 1, 2 * m)) for i in range(m)], list(map(float, envelopes)),
       width=.088, color=colors)
ax.axhline(float(alpha / (n + 1)), color=AMBER, ls="--", label="Threshold α/(n+1) = 1/110")
ax.set_yscale("log"); ax.set_ylim(1e-11, 2); ax.set_xlim(0, 1)
ax.set_xlabel("Uniform grid cells for the candidate probability p")
ax.set_ylabel("Exact cell envelope, plotted on a log scale")
ax.set_title("Retain cells whose binomial envelope exceeds the threshold", loc="left", weight="bold")
ax.axvspan(.6, 1, color=TEAL, alpha=.06)
ax.text(.95, .43, "Retained hull\n[3/5,1]", transform=ax.transAxes, ha="right",
        color=TEAL, fontsize=12, bbox={"facecolor": "white", "edgecolor": "none", "alpha": .96, "pad": 5})
ax.legend(loc="upper left", frameon=False, fontsize=10); fig.tight_layout()
save(fig, "08_grid_calibration", "For n = k = 10, m = 10 and alpha = 1/10, the exact envelope of cell [l, u] is u^10. Retaining cells above 1/110 gives the conservative hull [3/5, 1]. Fractions are exact; logarithmic bar heights are decimal renderings.")

fig, ax = plt.subplots(figsize=(8, 3.6))
for y, lo, hi, color in [(1, F(3, 5), F(1), GREY), (0, F(361, 500), F(433, 500), TEAL)]:
    ax.plot([float(lo), float(hi)], [y, y], lw=9, color=color, solid_capstyle="round")
    ax.text(float(lo), y + .2, str(lo), ha="center", fontsize=11)
    ax.text(float(hi), y + .2, str(hi), ha="center", fontsize=11)
ax.axvline(.8, color=AMBER, ls="--", lw=1.6)
ax.text(.8, -.42, "Observed proportion 400/500 = 4/5", ha="center", color=AMBER, fontsize=11)
ax.set_yticks([1, 0], ["Original quote band", "Fixed-checkpoint\ncalibration band"])
ax.set_xlim(.55, 1.03); ax.set_ylim(-.6, 1.5); ax.set_xlabel("Probability p")
ax.set_title("500 checked reports: an exact conservative interval", loc="left", weight="bold")
fig.tight_layout()
save(fig, "09_calibration_n500", "The archived synthetic fixture has n = 500, k = 400, m = 1000 and alpha = 1/100. The independent integer envelope evaluator and inherited Python calibration both return [361/500, 433/500]. The observed proportion 4/5 is a statistic; the wider band is the certified interval under the stated sampling law.")

fig, ax = canvas("Completion order changes the first report's success rate", (8, 4.5))
ax.text(2.0, 5.35, "Attempt order", ha="center", weight="bold")
ax.text(6.3, 5.35, "Completion order", ha="center", weight="bold")
ax.text(9.25, 5.35, "First success?", ha="center", weight="bold", fontsize=11)
for i, row in enumerate(DATA["completion_order"]["four_cases"]):
    y = 4.3 - i * 1.05
    ax.text(.15, y, "Mass 1/4", va="center", fontsize=10)
    for start, bits in [(1.45, row["attempt_bits"]), (5.75, row["reported_bits"])]:
        for j, bit in enumerate(bits):
            box(ax, start + j * 1.1, y - .3, .85, .6, "S" if bit else "R", TEAL if bit else RED, 12)
    arrow(ax, (3.75, y), (5.4, y))
    ax.text(9.2, y, "YES" if row["reported_bits"][0] else "NO", ha="center", va="center", color=TEAL if row["reported_bits"][0] else RED, weight="bold")
ax.text(5, .05, "Attempts are independent fair bits. Successes finish before rejections.\nEvery operation is logged and every intent is resolved. First-report success = 3/4.", ha="center", fontsize=11)
save(fig, "10_completion_order_four_cases", "Four equiprobable pairs of fair attempted outcomes produce three first-report successes when success completes earlier. The first stored success probability is 3/4 although each attempted success probability is 1/2. Every run is complete and accepted. S denotes success and R rejection.", "exact finite-case schematic")

fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.4, 4.5), gridspec_kw={"width_ratios": [2.5, 1]})
ks = list(range(21)); masses = [F(comb(20, k), 2 ** 20) for k in ks]
ax.bar(ks, list(map(float, masses)), color=[AMBER if k >= 10 else BLUE for k in ks], width=.85)
ax.set_xticks([0, 5, 10, 15, 20]); ax.set_xlabel("Successes among 20 fair attempts")
ax.set_ylabel("Exact binomial class mass"); ax.set_title("The first ten reports can all succeed", loc="left", weight="bold", fontsize=13)
ax.text(.02, .94, "All successes finish first", transform=ax.transAxes, fontsize=10)
event = F(DATA["completion_order"]["lower_bound_event_mass"])
bx.bar([0, 1], [.1, float(event)], color=[GREY, AMBER], width=.6)
bx.set_xticks([0, 1], ["Allocated\nα", "Bias-event\nmass"]); bx.set_ylim(0, .75)
bx.text(0, .12, "1/10", ha="center", fontsize=10)
bx.text(1, float(event) + .025, "308333\n/524288", ha="center", fontsize=10)
bx.set_ylabel("Probability"); bx.set_title("Exceeds α", loc="left", weight="bold", fontsize=13)
fig.tight_layout(w_pad=2)
save(fig, "11_completion_order_twenty", "In the fair 20-attempt model, the event of at least 10 successes has exact mass 308333/524288. Under success-first completion, that event makes the first 10 stored reports all successes and returns [3/5, 1], excluding the attempted parameter 1/2. This lower bound already exceeds alpha = 1/10. The complete count-class miss mass is 616667/1048576.")

fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.4, 4.6), gridspec_kw={"width_ratios": [1.55, 1]})
ax.axis("off"); ax.set_xlim(0, 5); ax.set_ylim(0, 5)
ax.text(.1, 4.5, "First bit    Second bit    Complete?", weight="bold", fontsize=11)
for i, row in enumerate(DATA["completion_conditioning"]["deadline_cases"]):
    y = 3.65 - i * .78
    first, second = row["bits"]
    ax.text(.55, y, "S" if first else "R", color=TEAL if first else RED, weight="bold")
    ax.text(2, y, "S" if second else "R", color=TEAL if second else RED, weight="bold")
    ax.text(3.35, y, "Yes" if row["complete"] else "No", color=TEAL if row["complete"] else GREY)
ax.text(.1, -.02, "Report the second bit only if the first was successful.\nEvery pair has mass 1/4. Completion has mass 1/2.", fontsize=10, va="bottom")
bx.bar([0, 1], [.5, 1], color=[BLUE, AMBER], width=.6)
bx.set_xticks([0, 1], ["Unconditional", "Given\ncompletion"]); bx.set_ylim(0, 1.17)
bx.set_ylabel("First-bit success probability")
for x, y, txt in [(0, .5, "1/2"), (1, 1, "1")]: bx.text(x, y + .025, txt, ha="center")
fig.suptitle("Predictable availability does not justify\nconditioning on completion", x=.03, ha="left", weight="bold", fontsize=14)
fig.tight_layout(rect=(0, 0, 1, .88), w_pad=2.2)
save(fig, "12_completion_conditioning", "The source deadline example has two independent fair bits. The second report is available exactly when the first bit succeeds, a rule depending only on the past. Completion probability is 1/2, but first-bit success conditional on completion is 1. Unconditional issued-bad bounds therefore cannot be read as conditional guarantees.", "exact finite-case schematic")

fig, ax = canvas("Pending intents and immutable terminal history", (8, 5.0))
box(ax, .4, 4.3, 2.1, .8, "Unseen\noperation ID", GREY, 11)
box(ax, 3.9, 4.3, 2.1, .8, "Pending intent", BLUE)
arrow(ax, (2.58, 4.7), (3.82, 4.7)); ax.text(3.2, 5.05, "begin", ha="center", fontsize=11)
for x, text, color in [(0.4, "Terminal success\nadds true once", TEAL), (3.9, "Terminal rejection\nadds false once", RED), (7.4, "Terminal fault\nadds no binary\nsample", GREY)]:
    box(ax, x, 1.7, 2.1, 1.15, text, color, 11)
    arrow(ax, (4.95, 4.22), (x + 1.05, 2.93), color)
ax.text(5, .55, "Matching completion removes the pending entry.\nExact replay changes nothing. Conflicting reuse is rejected.", ha="center", fontsize=12)
save(fig, "13_recorder_lifecycle", "The defined recorder uses one global operation-ID namespace. A matching completion removes the pending intent and appends one success, rejection or fault. Binary successes and rejections count once, while faults add no binary sample. Replays are idempotent and conflicts reject the command word.", "source-based schematic")

fig, ax = plt.subplots(figsize=(8, 4.2))
labels = ["Empty", "Begin", "Finish\nsuccess", "Replay\nsuccess", "Late\nbegin"]
ax.step(range(5), [0, 0, 1, 1, 1], where="post", color=TEAL, lw=3, label="Terminal binary samples")
ax.plot(range(5), [0, 1, 0, 0, 0], "o--", color=BLUE, lw=2, label="Pending operations")
ax.scatter(range(5), [0, 0, 1, 1, 1], color=TEAL, s=45, zorder=4)
ax.set_xticks(range(5), labels); ax.set_yticks([0, 1]); ax.set_ylim(-.12, 1.5)
ax.set_ylabel("Count"); ax.set_title("Replaying a completed operation consumes no new sample", loc="left", weight="bold")
ax.text(3.1, .22, "Changed success → rejection\nis rejected at command index 4", fontsize=11, color=RED)
ax.legend(loc="upper left", frameon=False, fontsize=10); fig.tight_layout()
save(fig, "14_replay_idempotence", "In the exact four-command example, begin creates one pending operation, finish adds one successful sample, and both replayed finish and late begin leave terminal count 1 and pending count 0. Appending a conflicting rejection fails at zero-based command index 4.")

fig, ax = canvas("Reconcile the commit without rerunning the action", (8, 5.2))
box(ax, .5, 4.35, 2.55, .9, "Checkpoint\nnext sequence = r", BLUE)
box(ax, 3.8, 4.35, 2.55, .9, "One selected\nexternal operation", AMBER)
box(ax, 7.1, 4.35, 2.4, .9, "Durable commit\nresult + after-state", TEAL, 11)
arrow(ax, (3.13, 4.8), (3.72, 4.8)); arrow(ax, (6.43, 4.8), (7.02, 4.8))
box(ax, 2.6, 2.3, 4.8, 1.0, "Acknowledge matching commit\nCheck sequence and exact\nbefore-state and after-state", BLUE, 11)
arrow(ax, (8.3, 4.27), (6.4, 3.38)); arrow(ax, (1.78, 4.27), (3.7, 3.38))
box(ax, .5, .3, 4.0, 1.0, "New checkpoint\nnext = r + 1\nOne charged transition", TEAL, 11)
box(ax, 5.5, .3, 4.0, 1.0, "Duplicate acknowledgement\nExact no-op\nNo external operation", GREY, 11)
arrow(ax, (4.0, 2.22), (2.5, 1.38)); arrow(ax, (6.0, 2.22), (7.5, 1.38))
ax.text(5, -.1, "Unfinished intent: reject recovery; no inferred verdict or automatic retry", ha="center", color=RED, fontsize=10)
save(fig, "15_recovery_protocol", "The commit recovery model validates sequence, exact pre-state and post-state projections. A new matching receipt replays one checked logical transition. A duplicate acknowledgement preserves the checkpoint, budget and belief exactly. Physical atomic durable storage is an explicit backend obligation.", "source-based schematic")

fig, ax = canvas("Four different kinds of assurance", (8, 5.4))
rows = [("Formal mathematics", "Universal statements about the specified Lean models", BLUE),
        ("Archived build evidence", "Pinned prior compilation, axiom audit and negative controls", TEAL),
        ("Fresh bounded checks", "69,905 recorder words and exact publication examples", AMBER),
        ("Physical operations", "Authenticity, source law, storage and runtime correspondence", RED)]
for i, (head, body, color) in enumerate(rows):
    y = 4.65 - i * 1.28
    box(ax, .35, y, 9.3, .97, head + "\n" + body, color, 12)
ax.text(5, -.3, "Passing one layer supplies evidence for that layer's stated contract.", ha="center", fontsize=11, color=GREY)
save(fig, "16_assurance_boundaries", "Universal formal theorems, archived build receipts, fresh finite implementation checks and physical operational assumptions are separate evidence layers. This publication reran the bounded Python checks and exact examples. It did not rerun Lean compilation or validate a live provider.", "assurance schematic")

fig, ax = canvas("A receipt is bound to the exact artifact and generation", (8, 5.4))
box(ax, .3, 4.35, 2.8, 1.15, "Protected identity\nStatement, dependency\nbytes and environment", BLUE, 10.5)
box(ax, 3.6, 4.35, 2.8, 1.15, "Registered ticket\nGeneration and artifact\nProof data", TEAL, 10.5)
box(ax, 6.9, 4.35, 2.8, 1.15, "Receipt\nExact ticket subject\nand approval flag", AMBER, 11)
for x in [1.7, 5, 8.3]: arrow(ax, (x, 4.27), (5, 3.28))
box(ax, 1.1, 2.05, 7.8, 1.15, "Validate exact identity and receipt subject\nRecheck the proof against the declared context", BLUE, 12)
arrow(ax, (5, 1.97), (5, 1.42))
box(ax, 2.25, .3, 5.5, 1.05, "Admit once and consume the pending ticket\nStale generation or substituted bytes: reject", TEAL, 11)
ax.text(5, -.16, "A provenance fingerprint supplies no assumption that finite hashes are injective.", ha="center", fontsize=10, color=GREY)
save(fig, "17_exact_artifact_binding", "ArtifactBinding.validate checks exact protected identity, exact receipt subject, approval and a freshly checked derivation. Acceptance consumes the pending ticket. The model binds statement and dependency byte snapshots, source bytes, environment and generation. A fingerprint is provenance data; hash injectivity is not assumed.", "source-based schematic")

fixture_path = ROOT / "source/AVOC_Formal_v0.41.0/examples/staged_affine/certain.json"
affine_fixture = json.loads(fixture_path.read_text())
matrix, offset = affine_fixture[1][3], affine_fixture[1][4]
assert matrix == [[1] * 4 for _ in range(4)] and offset == [1, 2, 3, 4]
rank_one_checks = 0
for x in product(range(5), repeat=4):
    dense = [(sum(row[j] * x[j] for j in range(4)) + offset[i]) % 5 for i, row in enumerate(matrix)]
    width_one = [(sum(x) + d) % 5 for d in offset]
    assert dense == width_one
    rank_one_checks += 1
assert rank_one_checks == 625
fig = plt.figure(figsize=(8.3, 4.8))
grid = fig.add_gridspec(2, 4, width_ratios=[3.2, .45, .8, 3.2], height_ratios=[3, 1.2], wspace=.4)
aa, eq, ll, rr = [fig.add_subplot(grid[0, i]) for i in range(4)]
for ax, matrix, title in [(aa, [[1] * 4 for _ in range(4)], "A: 4 × 4"),
                          (ll, [[1] for _ in range(4)], "L"),
                          (rr, [[1] * 4], "R: 1 × 4")]:
    ax.imshow(matrix, cmap=plt.cm.Blues, vmin=0, vmax=2, aspect="equal")
    for i, row in enumerate(matrix):
        for j, value in enumerate(row): ax.text(j, i, str(value), ha="center", va="center", fontsize=13, color=NAVY)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, weight="bold", fontsize=13)
    for spine in ax.spines.values(): spine.set_visible(False)
eq.axis("off"); eq.text(.5, .5, "=", transform=eq.transAxes, ha="center", va="center", fontsize=24)
bottom = fig.add_subplot(grid[1, :]); bottom.axis("off")
bottom.text(.01, .65, r"$y=Ax+d=L(Rx)+d\quad\mathrm{in}\ \mathbf{F}_5,\qquad d=(1,2,3,4)$", fontsize=14)
bottom.text(.01, .08, "Sum the four inputs once, broadcast the result, then add the four offsets.", fontsize=12)
fig.suptitle("The concrete affine artifact has a width-one certificate", x=.04, ha="left", weight="bold", fontsize=15)
fig.subplots_adjust(top=.82, bottom=.08)
save(fig, "18_rank_one_factorization", "For the actual four-input, four-output F5 source, A is the all-ones matrix and d = (1, 2, 3, 4). Its width-one factorization A = LR uses the all-ones column and row. The checked affine implementation computes L(Rx) + d with the same semantics. The archived abstract execution costs are 36 for the original and 21 for the selected implementation. The diagram's direct matrix and compressed evaluation were also compared on all 625 F5 input vectors.", "exact finite-field schematic")

for row in CATALOGUE:
    row["pdf_sha256"] = hashlib.sha256((OUT / (row["stem"] + ".pdf")).read_bytes()).hexdigest()
    row["png_sha256"] = hashlib.sha256((OUT / (row["stem"] + ".png")).read_bytes()).hexdigest()
(ROOT / "reviews/figure_catalogue.json").write_text(json.dumps(CATALOGUE, indent=2) + "\n")
(ROOT / "reviews/figure_render_checks.json").write_text(json.dumps({"status": "passed",
    "matplotlib": matplotlib.__version__, "figures": len(CATALOGUE),
    "rank_one_finite_field_inputs_checked": rank_one_checks,
    "rank_one_input_family": "Every vector in F5^4, represented by 0..4 coordinates",
    "affine_fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
    "exact_data_sha256": hashlib.sha256((ROOT / "reviews/exact_example_results.json").read_bytes()).hexdigest(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "non_claims": ["Plotting uses decimal conversion only for rendering", "No new Lean compilation"]}, indent=2) + "\n")
print(json.dumps({"figures": len(CATALOGUE), "output": str(OUT)}))
