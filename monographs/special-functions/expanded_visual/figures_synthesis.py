"""Six cross-series synthesis figures and bounded reproducible witnesses.

Run: python3 figures_synthesis.py from this directory.
All illustrated equalities are checked in the stated finite examples. Floating
Gamma quadrature and matrix residuals are not substitutes for analytic proofs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import csv
import hashlib
import json
import math
import platform
import sys
import time

import matplotlib
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import gamma, gammaln

from guide_style import COLORS, INK, MUTED, PALE, plt, save_figure

ROOT = Path(__file__).resolve().parent
AUTHORITY = ROOT / "evidence" / "synthesis_authority"
CORE = AUTHORITY / "manuscript"
CLAIMS = AUTHORITY / "SPECIAL_FUNCTIONS_CLAIM_INDEX.csv"
STEMS = [f"synthesis_{i:02d}" for i in range(1, 7)]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rf(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def rising(x: F, n: int) -> F:
    out = F(1)
    for j in range(n):
        out *= x + j
    return out


def binary_weight(a: F, b: F, n: int, r: int) -> F:
    return F(math.comb(n, r)) * rising(a, r) * rising(b, n-r) / rising(a+b, n)


def multi_weight(shapes: tuple[F, ...], degrees: tuple[int, ...]) -> F:
    n = sum(degrees)
    out = F(math.factorial(n), math.prod(math.factorial(r) for r in degrees))
    for s, r in zip(shapes, degrees):
        out *= rising(s, r)
    return out / rising(sum(shapes), n)


def qp(a: F, q: F, k: int) -> F:
    return math.prod((F(1)-a*q**j for j in range(k)), start=F(1))


def scalar_qracah(n: int, y: int, a: F, b: F, g: F, d: F, q: F) -> F:
    total = F(0)
    for k in range(min(n, y)+1):
        numerator = qp(q**(-n), q, k) * qp(a*b*q**(n+1), q, k)
        numerator *= qp(q**(-y), q, k) * qp(g*d*q**(y+1), q, k)
        denominator = qp(a*q, q, k) * qp(b*d*q, q, k)
        denominator *= qp(g*q, q, k) * qp(q, q, k)
        assert denominator != 0
        total += numerator / denominator * q**k
    return total


def compute() -> dict:
    # Independent direct polynomial evaluation checks the interleaved output.
    coeffs = tuple(F(j) for j in range(1, 7))
    packets = (coeffs[0::2], coeffs[1::2])
    restored = tuple(packets[j % 2][j // 2] for j in range(6))
    z = F(1, 3)
    original = sum(a*z**n for n, a in enumerate(coeffs))
    synthesized = sum(z**r * sum(a*(z*z)**n for n, a in enumerate(p))
                      for r, p in enumerate(packets))
    assert restored == coeffs and original == synthesized

    # Closed q=1/2 matrix identity is checked by rational squared coefficients.
    q = F(1, 2)
    c = q/(1+q*q)
    s2 = (1+q*q+q**4)/(1+q*q)**2
    assert c*c+s2 == 1 and c == F(2, 5) and s2 == F(21, 25)
    q_grid = [0.1, 0.25, 0.5, 0.75, 1.0]
    residuals = []
    for qq in q_grid:
        cc = qq/(1+qq*qq)
        ss = np.sqrt(1+qq*qq+qq**4)/(1+qq*qq)
        R = np.array([[cc, ss], [ss, -cc]])
        residuals.append(float(np.max(np.abs(R.T@R-np.eye(2)))))
    assert max(residuals) < 1e-14

    params = [(F(3, 4), F(1, 2)), (F(2), F(2)), (F(3, 2), F(1))]
    bridges = []
    for a, b in params:
        alpha = (2*a-1)/b
        assert alpha > 0
        val, err = quad(lambda u: np.exp((float(alpha)-1)*np.log(u)-u-gammaln(float(alpha))),
                        0, np.inf, epsabs=1e-10, epsrel=1e-10)
        assert abs(val-1) < 1e-9
        bridges.append({"a": rf(a), "beta": rf(b), "alpha": rf(alpha),
                        "kappa": rf(alpha/2), "signed_absolute_domain_a_gt_1": a > 1,
                        "gamma_integral": val, "quadrature_error_estimate": err})

    # Diagonal energies agree, while coherent sums distinguish these exact signs.
    plus, minus = (F(1), F(1)), (F(1), F(-1))
    E_plus, E_minus = sum(v*v for v in plus), sum(v*v for v in minus)
    assert E_plus == E_minus == 2
    assert sum(plus)**2 == 4 and sum(minus)**2 == 0

    shapes = (F(1), F(2), F(3))
    degrees = (1, 1, 1)
    direct = multi_weight(shapes, degrees)
    left_outer = binary_weight(F(3), F(3), 3, 2)
    left_inner = binary_weight(F(1), F(2), 2, 1)
    right_outer = binary_weight(F(1), F(5), 3, 1)
    right_inner = binary_weight(F(2), F(3), 2, 1)
    assert direct == left_outer*left_inner == right_outer*right_inner == F(3, 28)
    compositions = [(r0, r1, 3-r0-r1) for r0 in range(4) for r1 in range(4-r0)]
    all_weights = [multi_weight(shapes, r) for r in compositions]
    assert len(compositions) == 10 and sum(all_weights) == 1

    atoms, weights = (F(1, 4), F(3, 4)), (F(1, 2), F(1, 2))
    moments = [sum(w*x**k for x, w in zip(atoms, weights)) for k in range(3)]
    determinant = moments[0]*moments[2]-moments[1]**2
    assert moments == [F(1), F(1, 2), F(5, 16)] and determinant == F(1, 16)
    qa, qb, qg, qd, qq = F(1, 2), F(1, 2), F(4), F(1), F(1, 2)
    lattice = [qq**(-y)+qg*qd*qq**(y+1) for y in (0, 1)]
    scalar_rows = [[scalar_qracah(n, y, qa, qb, qg, qd, qq) for y in (0, 1)] for n in (0, 1)]
    assert qg*qq == qq**(-1) and lattice == [F(3), F(3)]
    assert scalar_rows == [[F(1), F(1)], [F(1), F(1)]]

    ids = ["Projector_Generated_Special_Functions_I.theorem.002",
           "Projector_Generated_Special_Functions_VIII.theorem.011",
           "Projector_Generated_Special_Functions_V.conjecture.021"]
    with CLAIMS.open(newline="", encoding="utf-8-sig") as handle:
        index = {r["claim_id"]: r for r in csv.DictReader(handle)}
    evidence_rows = [{"claim_id": i, "title": index[i]["title"],
                      "formalization_status": index[i]["formalization_status"]} for i in ids]
    return {
        "finite_reconstruction": {"coefficients": [rf(x) for x in coeffs],
            "packets": [[rf(x) for x in p] for p in packets],
            "evaluation_z": rf(z), "both_evaluations": rf(original), "exact": True},
        "two_channel": {"q": rf(q), "c": rf(c), "s_squared": rf(s2),
            "c_squared_plus_s_squared": "1", "q_grid": q_grid,
            "float_orthogonality_max_abs_residuals": residuals,
            "kernel_verification": "not performed"},
        "shape_parameter_bridges": bridges,
        "phase_witness": {"diagonal_energy_both": "2", "coherent_sum_squared_plus": "4",
                          "coherent_sum_squared_minus": "0", "exact": True},
        "refinement_tree": {"shapes": [rf(s) for s in shapes], "degrees": list(degrees),
            "left_outer_squared": rf(left_outer), "left_inner_squared": rf(left_inner),
            "right_outer_squared": rf(right_outer), "right_inner_squared": rf(right_inner),
            "common_squared_coefficient": rf(direct), "all_degree_3_compositions": compositions,
            "all_degree_3_weights": [rf(w) for w in all_weights], "all_weights_sum": "1",
            "exact": True},
        "positive_measure": {"atoms": [rf(x) for x in atoms], "weights": [rf(x) for x in weights],
            "moments_0_to_2": [rf(x) for x in moments], "hankel_determinant": rf(determinant),
            "scope": "Illustrative two-atom positive measure, not the infinite arithmetic measure."},
        "scalar_degeneracy": {"q": rf(qq), "alpha": rf(qa), "beta": rf(qb),
            "gamma": rf(qg), "delta": rf(qd), "N": 1, "lattice": [rf(x) for x in lattice],
            "rows": [[rf(x) for x in row] for row in scalar_rows],
            "all_used_denominators_nonzero": True, "exact": True},
        "indexed_claim_rows": evidence_rows,
        "non_claims": ["No universal arithmetic cancellation bound is tested.",
            "Finite-domain examples and floating residuals do not establish Lean kernel acceptance.",
            "The three reconstruction maps have different coordinate spaces; no identification of their ranges is asserted."]}


def title(ax, text):
    ax.set_title(text, loc="left", fontsize=13, fontweight="bold", pad=10)


def box(ax, xy, text, color=COLORS[0], size=11):
    ax.text(*xy, text, ha="center", va="center", fontsize=size,
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=color, lw=1.5))


def arrow(ax, p, q, color=MUTED):
    ax.annotate("", q, p, arrowprops=dict(arrowstyle="->", color=color, lw=1.6,
                                         shrinkA=8, shrinkB=8))


def reconstruction_figure():
    fig = plt.figure(figsize=(9.1, 3.8))
    ax = fig.add_axes([0.03, 0.15, 0.27, 0.75]); ax.axis("off")
    title(ax, "Coefficient packets")
    box(ax, (0.5, 0.84), "1, 2, 3, 4, 5, 6", size=12)
    arrow(ax, (0.5, 0.77), (0.27, 0.54)); arrow(ax, (0.5, 0.77), (0.74, 0.54))
    box(ax, (0.27, 0.47), "1, 3, 5"); box(ax, (0.74, 0.47), "2, 4, 6", COLORS[1])
    arrow(ax, (0.27, 0.37), (0.5, 0.19)); arrow(ax, (0.74, 0.37), (0.5, 0.19))
    ax.text(0.5, 0.09, "interleave: 6 coefficients", ha="center", fontsize=11)
    ax.text(0.5, -0.06, "2 channels × 3 entries", ha="center", fontsize=11, color=MUTED)

    ax = fig.add_axes([0.37, 0.24, 0.26, 0.64])
    h = np.linspace(-3, 3, 161); eta = np.linspace(-2, 2, 141)
    H, E = np.meshgrid(h, eta); a = 1.5
    intensity = np.abs(gamma(a+1j*E)/gamma(a))**2 / np.cosh(H/2)**(2*a)
    ax.imshow(intensity, extent=[-3, 3, -2, 2], origin="lower", aspect="auto", cmap="BuGn")
    title(ax, "Continuous coherent\nframe")
    ax.set_xlabel(r"displacement $h$"); ax.set_ylabel(r"frequency $\eta$")
    ax.set_xticks([-3, 0, 3]); ax.set_yticks([-2, 0, 2])
    ax.text(0.5, -0.31, r"unit window; measure $dh\,d\eta/(2\pi)$", transform=ax.transAxes,
            ha="center", fontsize=10.5)

    ax = fig.add_axes([0.73, 0.28, 0.24, 0.58])
    R = np.array([[0.5, np.sqrt(3)/2], [np.sqrt(3)/2, -0.5]])
    ax.imshow(R, vmin=-1, vmax=1, cmap="BrBG")
    for i, row in enumerate([[r"$1/2$", r"$\sqrt{3}/2$"], [r"$\sqrt{3}/2$", r"$-1/2$"]]):
        for j, val in enumerate(row):
            ax.text(j, i, val, ha="center", va="center", fontsize=13,
                    color="white" if R[i,j] > .75 else INK)
    title(ax, "Finite recoupling")
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, -0.16, r"$N=1:\quad R^{\mathsf{T}}R=I_2$", transform=ax.transAxes, ha="center", fontsize=12)
    ax.text(0.5, -0.29, "2 atlases, 2 coordinates", transform=ax.transAxes, ha="center", fontsize=11, color=MUTED)
    save_figure(fig, STEMS[0])


def shape_figure():
    fig = plt.figure(figsize=(9.0, 3.7))
    ax = fig.add_axes([0.08, 0.18, 0.48, 0.7]); u = np.linspace(1e-6, 7, 501)
    for a in [1, 1.5, 2]:
        ax.plot(u, np.exp((a-1)*np.log(u)-u-gammaln(a)), label=rf(F(a)))
    title(ax, r"One positive shape: Gamma$(\alpha)$")
    ax.set_xlabel(r"$u=e^y$"); ax.set_ylabel("probability density")
    ax.legend(title=r"$\alpha$", frameon=False); ax.set_ylim(0, 1.04); ax.set_xlim(0, 7)
    ax.grid()
    ax = fig.add_axes([0.64, 0.14, 0.33, 0.76]); ax.axis("off")
    title(ax, "Arithmetic → ladder")
    rows = [(r"$a=3/4,\ \beta=1/2$", r"$\alpha=1,\quad\kappa=1/2$", "positive kernel domain"),
            (r"$a=2,\ \beta=2$", r"$\alpha=3/2,\quad\kappa=3/4$", "principal arithmetic parameters"),
            (r"$a=3/2,\ \beta=1$", r"$\alpha=2,\quad\kappa=1$", "another admissible shape")]
    for i, (inp, out, note) in enumerate(rows):
        y = 0.83-i*0.29
        ax.text(0, y, inp, fontsize=12, color=COLORS[i])
        ax.text(0, y-0.09, out, fontsize=13)
        ax.text(0, y-0.17, note, fontsize=10.5, color=MUTED)
    save_figure(fig, STEMS[1])


def phase_figure():
    fig = plt.figure(figsize=(9.1, 3.6))
    for pos, sign, label in [([0.035, 0.28, 0.26, 0.59], 1, "Equal signs"),
                             ([0.34, 0.28, 0.26, 0.59], -1, "Opposite signs")]:
        ax = fig.add_axes(pos); title(ax, label)
        ax.axhline(0, color="#CBD4D8", lw=1)
        ax.annotate("", (1, 0.12), (0, 0.12), arrowprops=dict(arrowstyle="->", lw=3, color=COLORS[0]))
        ax.annotate("", (1+sign, -0.12), (1, -0.12), arrowprops=dict(arrowstyle="->", lw=3, color=COLORS[1]))
        ax.text(0.5, 0.31, r"$v_1=1$", ha="center", fontsize=12)
        ax.text(1+sign/2, -0.37, rf(F(sign)), ha="center", fontsize=12, color=COLORS[1])
        ax.text(1, -0.65, f"energy 2; sum² {4 if sign == 1 else 0}", ha="center", fontsize=11)
        ax.set_xlim(-0.2, 2.2); ax.set_ylim(-0.9, 0.7); ax.axis("off")
    ax = fig.add_axes([0.68, 0.2, 0.29, 0.68]); theta = np.linspace(0, np.pi, 151)
    ax.plot(theta, 4*np.cos(theta/2)**2, label="coherent sum²", color=COLORS[2])
    ax.axhline(2, color=COLORS[0], ls="--", label="diagonal energy")
    ax.set_xticks([0, np.pi/2, np.pi], ["0", r"$\pi/2$", r"$\pi$"])
    ax.set_xlabel(r"relative phase $\theta$"); ax.set_ylim(-0.1, 4.2)
    title(ax, "Same magnitudes")
    ax.legend(frameon=False, fontsize=10, loc="upper right"); ax.grid()
    save_figure(fig, STEMS[2])


def tree_figure():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    configs = [
        ("First combine shapes 1 and 2", [(0.5, .80, "(6, 3)"),(.28,.49,"(3, 2)"),
          (.78,.17,"(3, 1)"),(.10,.17,"(1, 1)"),(.46,.17,"(2, 1)")],
         [(0,1),(0,2),(1,3),(1,4)], r"$(9/28)\,(1/3)=3/28$"),
        ("First combine shapes 2 and 3", [(0.5,.80,"(6, 3)"),(.24,.17,"(1, 1)"),
          (.71,.49,"(5, 2)"),(.55,.17,"(2, 1)"),(.9,.17,"(3, 1)")],
         [(0,1),(0,2),(2,3),(2,4)], r"$(15/56)\,(2/5)=3/28$")]
    for ax, (heading, nodes, edges, product) in zip(axes, configs):
        ax.axis("off"); title(ax, heading)
        for i, j in edges: arrow(ax, nodes[i][:2], nodes[j][:2])
        for x, y, text in nodes: box(ax, (x,y), text, size=11)
        ax.text(.5, -.07, product, ha="center", fontsize=15, color=COLORS[0])
        ax.text(.5, 1.02, "node = (shape, degree)", ha="center", fontsize=10.5, color=MUTED)
        ax.set_xlim(-.04, 1.04); ax.set_ylim(-.2, 1.04)
    fig.subplots_adjust(wspace=.18, left=.025, right=.975, bottom=.12, top=.84)
    save_figure(fig, STEMS[3])


def measure_figure():
    fig = plt.figure(figsize=(9.1, 3.7))
    ax = fig.add_axes([.07,.48,.38,.38])
    title(ax, "A specified positive measure")
    ax.vlines([.25,.75], 0, [.5,.5], color=COLORS[0], lw=3)
    ax.scatter([.25,.75],[.5,.5], color=COLORS[0], s=60)
    ax.set_xlim(0,1); ax.set_ylim(0,.68); ax.set_xticks([.25,.75],[r"$1/4$",r"$3/4$"])
    ax.set_yticks([0,.5],["0",r"$1/2$"]); ax.set_ylabel("atom mass")
    ax = fig.add_axes([.07,.09,.38,.29]); ax.axis("off")
    tab = ax.table(cellText=[["1","1/2"],["1/2","5/16"]], cellLoc="center", loc="center", bbox=[.15,.34,.7,.6])
    tab.auto_set_font_size(False); tab.set_fontsize(13)
    for cell in tab.get_celld().values(): cell.set_edgecolor("#CDD8DA"); cell.set_facecolor(PALE)
    ax.text(.5,.06,r"$\det G=1/16>0$",ha="center",fontsize=13)

    ax = fig.add_axes([.57,.15,.4,.73]); ax.axis("off")
    title(ax, "A terminating scalar expression")
    box(ax,(.17,.76),"y = 0",size=11);box(ax,(.83,.76),"y = 1",size=11)
    arrow(ax,(.17,.69),(.5,.49));arrow(ax,(.83,.69),(.5,.49))
    box(ax,(.5,.42),r"$\mu=3$",COLORS[1],12)
    ax.text(.5,.22,r"$R_0=(1,1),\qquad R_1=(1,1)$",ha="center",fontsize=13)
    ax.text(.5,.05,r"$\sum_y w_y R_0(y)R_1(y)=1$",ha="center",fontsize=12)
    ax.text(.5,-.06,"for any normalized positive weights",ha="center",fontsize=10.5,color=MUTED)
    save_figure(fig, STEMS[4])


def evidence_figure(results):
    fig = plt.figure(figsize=(9.2, 3.7)); ax = fig.add_axes([.02,.03,.96,.9]); ax.axis("off")
    title(ax,"Three indexed claims, three different questions")
    headers=["Source row","Concrete calculation / target","Ledger status"]
    cells=[
      ["I · theorem.002", "6 coefficients → 2 × 3 packets\nF(1/3) = 543/243 in both routes", "Lean draft present\n(partial source link)"],
      ["VIII · theorem.011", "q = 1/2: c² = 4/25, s² = 21/25\nc²+s² = 1; 5-point float check", "queued"],
      ["V · conjecture.021", "For every ε > 0: |cₖ|²/Eₖ ≤ Cε k^ε\nno such uniform bound produced here", "conjectural goal"]]
    # Use the result, not a manually estimated rational witness.
    cells[0][1]="6 coefficients → 2 × 3 packets\nF(1/3) = "+results["finite_reconstruction"]["both_evaluations"]+" in both routes"
    table=ax.table(cellText=cells,colLabels=headers,cellLoc="left",colLoc="left",
                   colWidths=[.20,.53,.27],bbox=[0,.24,1,.67])
    table.auto_set_font_size(False);table.set_fontsize(10.6)
    for (i,j),cell in table.get_celld().items():
        cell.set_edgecolor("#CFDADC");cell.PAD=.045
        if i==0:cell.set_facecolor(COLORS[0]);cell.get_text().set_color("white");cell.get_text().set_fontweight("bold")
        elif i%2:cell.set_facecolor(PALE)
    ax.text(.01,.11,"Exact algebra decides the displayed identity. Floating residuals decide a bounded implementation check.", fontsize=11)
    ax.text(.01,.02,"Kernel acceptance requires a proof term and its successful build. A claim record supplies neither.",fontsize=11,color=MUTED)
    save_figure(fig, STEMS[5])


def main():
    began=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
    results=compute()
    reconstruction_figure();shape_figure();phase_figure();tree_figure();measure_figure();evidence_figure(results)
    evidence=ROOT/"evidence";evidence.mkdir(exist_ok=True)
    result_path=evidence/"synthesis_computations.json"
    result_path.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    input_paths=[Path(__file__),CLAIMS]+[CORE/(s+".tex") for s in ["arithmetic_core","shape_core","recoupling_core","corrections","evidence"]]
    output_paths=[result_path]+[ROOT/"figures"/(s+ext) for s in STEMS for ext in [".pdf",".png"]]
    manifest={
      "schema_version":1,"claim_id":"SPECIAL_FUNCTIONS_VISUAL_V0_2_SYNTHESIS_FINITE_WITNESSES",
      "repository":{"commit":"unversioned artifact workspace; no Git commit asserted","dirty":True},
      "command":"python3 figures_synthesis.py",
      "environment":{"software":["Python "+sys.version.split()[0],"NumPy "+np.__version__,"SciPy "+scipy.__version__,"Matplotlib "+matplotlib.__version__],"hardware":platform.platform()+"; "+platform.machine()},
      "mathematics":{"assertion_tested":"Finite reconstruction, phase loss, two-channel orthogonality, shape mapping, tree cancellation, moment Gram positivity, scalar q-Racah degeneracy, and source-row status lookup.",
        "coefficient_domain":"Exact rational arithmetic for algebraic witnesses; IEEE-754 double precision for Gamma quadrature and finite matrix residuals.",
        "conventions":"Moment indices start at zero. Shapes use rising Pochhammer. q-Racah uses the corrected v0.1 finite summation. Coherent phase-space measure is dh deta/(2pi).",
        "inputs":[{"path":str(p.relative_to(ROOT)),"sha256":digest(p)} for p in input_paths],
        "bounds":{"coefficient_count":6,"residue_modulus":2,"polynomial_evaluation_z":"1/3","q_grid":[.1,.25,.5,.75,1.0],"Gamma_shapes":[1,1.5,2],"tree_total_degree":3,"tree_child_shapes":[1,2,3],"scalar_N":1,"scalar_q":"1/2"},
        "non_claims":results["non_claims"]},
      "randomness":{"used":False,"generator":"none","seed":None},
      "run":{"started_at":started,"runtime_seconds":time.perf_counter()-began,"exit_status":0},
      "outputs":[{"path":str(p.relative_to(ROOT)),"sha256":digest(p)} for p in output_paths],
      "checks":[{"name":"rational residue reconstruction and independent polynomial evaluation","passed":True},
        {"name":"q=1/2 exact squared-coefficient identity and five-point floating orthogonality","passed":True},
        {"name":"three exact shape mappings and Gamma normalization quadrature","passed":True},
        {"name":"same diagonal energy, different coherent sums","passed":True},
        {"name":"two refinement routes agree; all ten degree-three probabilities sum to one","passed":True},
        {"name":"positive two-atom moment determinant and well-defined degenerate q-Racah counterexample","passed":True},
        {"name":"three IDs resolve in the preserved source claim index","passed":True}],
      "result":"Exact finite assertions verified; floating assertions conditional on stated tolerance and SciPy; no Lean build or uniform signed bound produced.",
      "residual_risks":["Quadrature error estimates are numerical, not interval certificates.","The illustrative two-atom positive measure is not the infinite arithmetic measure.","Evidence statuses are the retrieved 2026-08-02 ledger snapshot; no claim of exhaustive later formalization discovery."]}
    (evidence/"synthesis_computation_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"figures":6,"all_finite_assertions_passed":True,"max_float_orthogonality_residual":max(results["two_channel"]["float_orthogonality_max_abs_residuals"])}))


if __name__=="__main__":main()
