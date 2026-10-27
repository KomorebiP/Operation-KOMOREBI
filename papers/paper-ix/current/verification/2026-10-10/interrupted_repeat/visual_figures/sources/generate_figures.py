#!/usr/bin/env python3
"""Exact arithmetic behind the final Euler visual guide.

Numerical coordinates in the figures are either theorem-derived integer bounds
or exact residues/valuations of the actual reciprocal coefficients. Floating
point is used only by Matplotlib to place those verified coordinates on a page.
This is a bounded illustration audit, not a proof of a universal theorem.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb, factorial
from pathlib import Path
import json
import platform
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
STARTED = datetime.now(timezone.utc).isoformat()
T0 = time.monotonic()
SCRIPT_HASH = sha256(Path(__file__).read_bytes()).hexdigest()
COUNTS = Counter()
TEAL, GREEN, GOLD, GRAY = "#164C51", "#668C75", "#A77D40", "#778486"
LIGHT = "#E9F0ED"
COLORS = [TEAL, GREEN, GOLD, GRAY]
plt.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 10.5,
    "axes.labelsize": 10.5, "axes.titlesize": 12,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
    "axes.edgecolor": "#9DAAA6", "axes.labelcolor": TEAL,
    "text.color": TEAL, "xtick.color": TEAL, "ytick.color": TEAL,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#DDE5E1", "grid.linewidth": .6,
    "pdf.fonttype": 42, "ps.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def check(condition, kind):
    assert condition, kind
    COUNTS[kind] += 1


def vi(n):
    n = abs(int(n))
    return None if n == 0 else (n & -n).bit_length() - 1


def v2(x):
    x = Fraction(x)
    return None if x == 0 else vi(x.numerator) - vi(x.denominator)


def vf(k):
    return k - k.bit_count()


def coeffs_fraction(N, j, limit):
    """Hurwitz convolution, over Q, with actual j!-normalized input."""
    g = [Fraction(factorial(j) * factorial(N*q), factorial(N*q+j))
         for q in range(limit+1)]
    c = [Fraction(1)]
    for n in range(1, limit+1):
        c.append(-sum(comb(N*n, N*q) * g[q] * c[n-q]
                      for q in range(1, n+1)))
    return c


def coeffs_independent(N, j, limit):
    """Independent ordinary-series inversion followed by factorial scaling."""
    a = [Fraction(factorial(j), factorial(N*q+j))
         for q in range(limit+1)]
    b = [Fraction(1)]
    for n in range(1, limit+1):
        b.append(-sum(a[q]*b[n-q] for q in range(1, n+1)))
    return [b[n]*factorial(N*n) for n in range(limit+1)]


def coeffs_mod(N, j, limit, bits):
    """Exact reciprocal coefficients modulo 2^bits, with odd denominators."""
    modulus = 1 << bits
    g = []
    for q in range(limit+1):
        f = Fraction(factorial(j)*factorial(N*q), factorial(N*q+j))
        check(f.denominator % 2 == 1, "odd_source_denominator")
        g.append((f.numerator*pow(f.denominator, -1, modulus)) % modulus)
    c = [1]
    for n in range(1, limit+1):
        c.append(-sum(comb(N*n, N*q)*g[q]*c[n-q]
                      for q in range(1, n+1)) % modulus)
    return c


def diff(values, n, steps, modulus=None):
    """Independent exact signed subset expansion of mixed differences."""
    ans = 0
    for mask in range(1 << len(steps)):
        offset = sum(steps[i] for i in range(len(steps)) if mask >> i & 1)
        sign = (-1)**(len(steps)-mask.bit_count())
        ans += sign * values[n+offset]
    return ans if modulus is None else ans % modulus


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight",
                metadata={"Creator": "Exact Euler figure generator", "CreationDate": None})
    fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def box(ax, x, y, w, h, text, face=LIGHT, fs=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.018,rounding_size=0.03",
                 facecolor=face, edgecolor=TEAL, linewidth=.8))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs)


# Independent rational checks, then exact finite illustrations at known precision.
rat = {j: coeffs_fraction(4, j, 12) for j in range(4)}
for j in range(4):
    other = coeffs_independent(4, j, 12)
    for n in range(13):
        check(rat[j][n] == other[n], "independent_rational_inversion")
check([rat[j][1] for j in range(4)] ==
      [Fraction(-1), Fraction(-1,5), Fraction(-1,15), Fraction(-1,35)],
      "first_row_benchmark")
bits = 256
modulus = 1 << bits
mod = {j: coeffs_mod(4, j, 255, bits) for j in range(4)}
for j in range(4):
    for n in range(13):
        f = rat[j][n]
        check(mod[j][n] == (f.numerator*pow(f.denominator, -1, modulus)) % modulus,
              "rational_modular_crosscheck")
b, B, beta = [1,1,4,2], [1,1,5,3], [0,0,3,1]
for j in range(4):
    for n in range(9):
        for H in range(1,9):
            check(vi(diff(mod[j],n,[H],modulus)) == vi(H)+b[j],
                  "sampled_first_difference_exact")
        for k in range(1,7):
            for H in range(1,5):
                value = vi(diff(mod[j],n,[H]*k,modulus))
                lower = k+vf(k)+k*vi(H)+beta[j]
                check(value is None or value >= lower, "sampled_factorial_bound")
                if j in (0,1):
                    check(value == lower, "sampled_homogeneous_equality")
    for k in range(1,5):
        for steps in product((1,2,3,4), repeat=k):
            lower = k+vf(k)+sum(vi(H) for H in steps)+beta[j]
            value = vi(diff(mod[j],0,steps,modulus))
            check(value is None or value >= lower, "sampled_mixed_factorial_bound")
            if j in (0,1):
                exact = k % 2 == 1 or sum(H % 2 == 0 for H in steps) % 2 == 0
                check((value == lower) == exact, "sampled_mixed_parity_rule")
            if j == 2:
                lower2 = 2*k+vf(k)+k//2+sum(vi(H) for H in steps)
                check(value is None or value >= lower2, "sampled_address_two_filtration")
for k in (1,2,4,8,16):
    for n in (0,3):
        for steps in ([1]*k, [2]*k, [1]*(k-1)+[2]):
            exact = ({1:4,2:6}.get(k,2*k+vf(k)+k//2)
                     +sum(vi(H) for H in steps))
            check(vi(diff(mod[2],n,steps,modulus)) == exact,
                  "sampled_address_two_power_order_exact")

# 01. The object and its normalization.
fig, ax = plt.subplots(figsize=(7.2,3.6))
ax.set(xlim=(0,1),ylim=(0,1)); ax.axis("off")
box(ax,.07,.67,.86,.22,
    r"$G_{N,j}(t)=j!\sum_{n\geq0}t^{Nn}/(Nn+j)!$")
box(ax,.07,.32,.86,.22,
    r"$G_{N,j}(t)^{-1}=\sum_{n\geq0}C_{N,j}(n)t^{Nn}/(Nn)!$")
ax.add_patch(FancyArrowPatch((.5,.66),(.5,.55),arrowstyle="-|>",mutation_scale=13,color=TEAL))
ax.text(.55,.605,"reciprocal",fontsize=10,va="center")
box(ax,.07,.025,.86,.18,
    r"$E_{Nn}^{(N,j)}=j!C_{N,j}(n)\quad$; row step $H$ = degree step $NH$")
ax.add_patch(FancyArrowPatch((.5,.31),(.5,.21),arrowstyle="-|>",mutation_scale=13,color=TEAL))
save(fig,"normalization")

# 02. Old and strengthened unit-step estimates: theorem-derived integers only.
fig, axes = plt.subplots(1,2,figsize=(7.2,3.65),sharey=True)
ns, ks = range(13), range(1,13)
old = np.array([[min(k,n) for n in ns] for k in ks])
new = np.array([[k for n in ns] for k in ks])
for ax, data, title in zip(axes,(old,new),(r"Earlier: $\min(k,n)$",r"Threshold free: $k$")):
    im = ax.imshow(data,origin="lower",aspect="auto",cmap="YlGnBu",vmin=0,vmax=12,
                   extent=(-.5,12.5,.5,12.5))
    ax.set_title(title,pad=10); ax.set_xlabel("starting row n")
    ax.set_xticks((0,4,8,12)); ax.set_yticks((1,4,8,12))
    ax.plot((0,12),(0,12),color="white",lw=1,ls="--",alpha=.8)
axes[0].set_ylabel("difference order k")
fig.colorbar(im,ax=axes,shrink=.85,pad=.035,label="proved valuation lower bound")
save(fig,"threshold")

# 03. A mixed-step signed stencil, with an exact rational example.
steps = [1,2,4]
stencil = [(sum(steps[i] for i in range(3) if mask >> i & 1),
            (-1)**(3-mask.bit_count())) for mask in range(8)]
check(sorted(x for x,s in stencil) == list(range(8)), "stencil_offsets")
stencil_value = diff(rat[0],0,steps)
check(v2(stencil_value) == 7, "stencil_exact_valuation")
fig, ax = plt.subplots(figsize=(7.2,2.85))
for x,s in stencil:
    ax.plot((x,x),(0,s),color=TEAL if s>0 else GREEN,lw=1.4)
    ax.scatter((x,),(s,),color=TEAL if s>0 else GREEN,s=90,zorder=3)
    ax.text(x,s+(.15 if s>0 else -.18),"+1" if s>0 else "−1",ha="center",va="bottom" if s>0 else "top")
ax.axhline(0,color=GRAY,lw=.8); ax.set(ylim=(-1.7,1.75),xlim=(-.5,7.5),xticks=range(8),yticks=(-1,0,1))
ax.set_xlabel("offset from the starting row"); ax.set_ylabel("signed weight")
ax.set_title(r"$\Delta_1\Delta_2\Delta_4$: eight exact signed samples",pad=12)
save(fig,"mixed_stencil")

# 04. Final common-step Euler congruence exponents at unit step.
orders = list(range(1,33))
vj01 = [k+vf(k) for k in orders]
vj2 = [vf(k)+max(k+4,2*k+k//2+1) for k in orders]
vj3 = [k+vf(k)+2 for k in orders]
fig, ax = plt.subplots(figsize=(7.2,4.2))
ax.plot(orders,vj01,color=TEAL,lw=1.8,label="j = 0, 1: exact")
ax.plot(orders,vj3,color=GRAY,lw=1.6,ls="--",label="j = 3: proved lower bound")
ax.plot(orders,vj2,color=GREEN,lw=2,label="j = 2: proved lower bound")
powers = [1,2,4,8,16,32]
ax.scatter(powers,[vj2[k-1] for k in powers],s=44,color=GREEN,edgecolor="white",lw=.7,zorder=4,
           label="j = 2: exact at powers of two")
ax.set(xlim=(0,33),ylim=(0,max(vj2)+8),xlabel="difference order k",ylabel="bits of divisibility for the original Euler coefficient")
ax.set_xticks((1,4,8,16,24,32)); ax.grid(axis="y"); ax.legend(loc="upper left",frameon=False,fontsize=9.4)
save(fig,"final_exponents")

# 05. The address-two envelope, in normalized coefficients.
fig, ax = plt.subplots(figsize=(7.2,4.1))
base2 = [k+vf(k)+3 for k in orders]
pair2 = [2*k+vf(k)+k//2 for k in orders]
envelope = [max(x,y) for x,y in zip(base2,pair2)]
ax.plot(orders,base2,color=GRAY,lw=1.5,ls="--",label=r"$k+v_2(k!)+3$")
ax.plot(orders,pair2,color=GOLD,lw=1.5,ls=":",label=r"$2k+v_2(k!)+\lfloor k/2\rfloor$")
ax.plot(orders,envelope,color=GREEN,lw=2.2,label="take the larger bound")
ax.scatter(powers,[envelope[k-1] for k in powers],color=GREEN,s=46,zorder=4,edgecolor="white",lw=.7,label="universally exact orders")
ax.set(xlim=(0,33),ylim=(0,max(envelope)+8),xlabel="difference order k",ylabel="normalized valuation lower bound")
ax.set_xticks((1,2,4,8,16,24,32)); ax.grid(axis="y"); ax.legend(frameon=False,loc="upper left",fontsize=9.4)
save(fig,"address_two_envelope")

# 06. Mixed cancellation at the first nontrivial even order.
mixed_examples = []
for steps2 in ([1,1],[1,2],[2,2],[1,4],[2,4],[3,4]):
    value = diff(rat[0],0,steps2)
    low = 2+vf(2)+sum(vi(H) for H in steps2)
    mixed_examples.append({"steps":steps2,"lower":low,"actual":v2(value),"value":str(value)})
check(mixed_examples[1]["value"] == "-33728", "mixed_counterexample_value")
check(mixed_examples[1]["actual"] == 6, "mixed_counterexample_valuation")
fig, ax = plt.subplots(figsize=(7.2,3.65))
x = np.arange(len(mixed_examples))
ax.bar(x-.16,[e["lower"] for e in mixed_examples],width=.31,color=GRAY,label="factorial baseline V")
ax.bar(x+.16,[e["actual"] for e in mixed_examples],width=.31,color=TEAL,label="exact valuation at n = 0, j = 0")
ax.set_xticks(x,[str(tuple(e["steps"])) for e in mixed_examples])
ax.set(xlabel="the two row steps",ylabel="dyadic valuation",ylim=(0,max(e["actual"] for e in mixed_examples)+1))
ax.grid(axis="y"); ax.set_axisbelow(True); ax.legend(frameon=False,fontsize=9.5)
save(fig,"mixed_cancellation")

# 07. First-difference isometry, theorem lines and sampled exact arithmetic.
fig, ax = plt.subplots(figsize=(7.2,3.9))
t = list(range(7))
for j in range(4):
    vals = [vi((factorial(j)*diff(mod[j],0,[1<<s],modulus)) % modulus) for s in t]
    check(vals == [s+B[j] for s in t], "plotted_original_metric")
    ax.plot(t,[s+B[j] for s in t],color=COLORS[j],lw=1.6,ls="--" if j==1 else "-",label=f"j = {j}, B = {B[j]}")
    ax.scatter(t,vals,s=35,color=COLORS[j],marker="s" if j==1 else "o",zorder=3)
ax.set(xticks=t,xlabel=r"$v_2(H)$",ylabel=r"$v_2(E_{4H}^{(4,j)}-E_0^{(4,j)})$",ylim=(0,12))
ax.grid(axis="y"); ax.legend(frameon=False,ncol=2,fontsize=9.5)
save(fig,"metric")

# 08. Least row periods: theorem-derived exponents.
fig, ax = plt.subplots(figsize=(7.2,3.9))
r = list(range(1,13))
for j in (0,2,3):
    ax.step(r,[max(0,s-B[j]) for s in r],where="mid",lw=1.8,color=COLORS[j],label=("j = 0, 1" if j==0 else f"j = {j}"))
ax.set(xticks=r,xlabel=r"precision r in modulus $2^r$",ylabel=r"$\log_2$(least row period)",ylim=(-.35,11.8))
ax.grid(axis="y"); ax.legend(frameon=False,fontsize=10)
save(fig,"periods")

# 09. Exact permutations of permitted residues modulo 256.
residue_data = []
fig, axes = plt.subplots(2,2,figsize=(7.2,5.0))
for j, ax in enumerate(axes.flat):
    p = 1 << max(0,8-B[j])
    es = [(factorial(j)*mod[j][n]) % 256 for n in range(2*p)]
    image = [((es[n]-factorial(j)) % 256) // (1<<B[j]) for n in range(p)]
    check(sorted(image) == list(range(p)), "complete_residue_permutation")
    for n in range(p):
        check(es[n] == es[n+p], "finite_period_repeat")
    residue_data.append({"j":j,"modulus":256,"B":B[j],"period":p,
                         "Euler_residues":es[:p],"scaled_residues":image})
    ax.scatter(range(p),image,s=12 if p>32 else 30,color=COLORS[j])
    ax.set_title(f"j = {j}: {p} rows, {p} permitted residues",fontsize=10.5,pad=8)
    ax.set_xlabel("row n"); ax.set_ylabel("scaled residue")
    ax.set(xlim=(-.5,p-.5),ylim=(-.5,p-.5))
    if p<=8: ax.set_xticks(range(p)); ax.set_yticks(range(p))
    else: ax.set_xticks((0,p//2,p-1)); ax.set_yticks((0,p//2,p-1))
    ax.grid(alpha=.5)
fig.tight_layout(h_pad=1.2,w_pad=1.4)
save(fig,"residue_permutations")

# 10. A finite metric matrix, quotienting address two by its exact scale.
qvals = residue_data[2]["scaled_residues"]
distance_in = np.zeros((8,8)); distance_out = np.zeros((8,8))
for n in range(8):
    for m in range(8):
        if n==m:
            distance_in[n,m]=distance_out[n,m]=np.nan
        else:
            distance_in[n,m] = vi(n-m)
            distance_out[n,m] = vi(qvals[n]-qvals[m])
            check(distance_in[n,m]==distance_out[n,m], "finite_scaled_isometry")
fig, axes = plt.subplots(1,2,figsize=(7.2,3.5))
cmap=plt.get_cmap("YlGnBu").copy(); cmap.set_bad("#F1F3F1")
for ax,data,title in zip(axes,(distance_in,distance_out),(r"input: $v_2(n-m)$",r"output: $v_2(y_n-y_m)$")):
    im=ax.imshow(data,cmap=cmap,vmin=0,vmax=2,origin="lower")
    ax.set(xticks=range(8),yticks=range(8),xlabel="row m",ylabel="row n")
    ax.set_title(title,pad=10)
fig.colorbar(im,ax=axes,shrink=.8,pad=.04,ticks=(0,1,2),label="shared low-bit precision")
save(fig,"isometry_matrices")

# 11. Known exact-law shifts at small ranks.
bs = {2:[1,2],4:[1,1,4,2],8:[1,1,1,1,4,3,2,2]}
fig, axes = plt.subplots(1,2,figsize=(7.2,3.25),sharey=True)
for ax, original, title in zip(axes,(False,True),(r"normalized scale $b_{N,j}$",r"Euler scale $B_{N,j}$")):
    data=np.full((3,8),np.nan)
    for ri,N in enumerate((2,4,8)):
        for j,bj in enumerate(bs[N]): data[ri,j]=bj+(vi(factorial(j)) if original else 0)
    cmap=plt.get_cmap("YlGnBu").copy(); cmap.set_bad("#F5F6F4")
    ax.imshow(data,origin="upper",vmin=1,vmax=7,cmap=cmap,aspect="auto")
    for ri in range(3):
        for j in range(8):
            if not np.isnan(data[ri,j]):
                ax.text(j,ri,str(int(data[ri,j])),ha="center",va="center",color="white" if data[ri,j]>=5 else TEAL,fontsize=11)
    ax.set(xticks=range(8),yticks=range(3),yticklabels=("N = 2","N = 4","N = 8"),xlabel="address j")
    ax.set_title(title,pad=10)
save(fig,"rank_scales")

# 12. Exact rational counterexamples at larger upper-half addresses.
counterexamples=[]
for N,j,pred,actual in ((16,9,6,7),(32,18,7,6),(32,19,6,7)):
    c=coeffs_fraction(N,j,2)
    first=v2(c[1]-c[0]); second=v2(c[2]-c[0])
    check(second == actual and first+1 == pred, "upper_half_counterexample")
    counterexamples.append({"N":N,"j":j,"first_valuation":first,
                            "step_two_valuation":second,"naive_prediction":pred,
                            "C0":str(c[0]),"C1":str(c[1]),"C2":str(c[2])})

# 13. Analytic slopes: certified coefficient bounds, no real growth claim.
degrees=list(range(1,65))
fig, ax=plt.subplots(figsize=(7.2,4.0))
ax.plot(degrees,degrees,color=TEAL,lw=1.8,label="j = 0, 1: exact coefficient valuation")
ax.plot(degrees,[max(2*d+d//2,d+3) for d in degrees],color=GREEN,lw=2,
        label="j = 2: coefficient lower bound")
powers2=[4,8,16,32,64]
ax.scatter(powers2,[5*d//2 for d in powers2],s=42,color=GREEN,edgecolor="white",lw=.7,zorder=4,
           label="j = 2: exact along powers of two")
ax.plot(degrees,degrees,color=GRAY,lw=1,ls="--",alpha=.8,label="j = 3: proved lower bound")
ax.set(xlim=(0,66),ylim=(0,170),xlabel="Taylor degree d",ylabel=r"dyadic valuation of the degree-d coefficient")
ax.set_xticks((1,4,8,16,32,48,64)); ax.grid(axis="y"); ax.legend(frameon=False,fontsize=9.2,loc="upper left")
save(fig,"analytic_slopes")

# Durable exact plotted data, separate from rendering coordinates.
data={"scope":"Exact finite illustration data; theorem-derived curves are not numerical evidence for universal proofs.",
      "coefficient_definition":"C_N,j(n)=(Nn)![t^(Nn)](j! sum_q t^(Nq)/(Nq+j)!)^(-1)",
      "modular_precision_bits":bits,"modular_rows":255,"rational_crosscheck_rows":12,
      "assertion_counts":dict(sorted(COUNTS.items())),"total_assertions":sum(COUNTS.values()),
      "rational_first_rows":{str(j):[str(x) for x in rat[j][:5]] for j in range(4)},
      "mixed_stencil":{"steps":steps,"offset_weights":stencil,"value":str(stencil_value),"valuation":v2(stencil_value)},
      "mixed_order_two":mixed_examples,"residue_permutations":residue_data,
      "upper_half_counterexamples":counterexamples,
      "theorem_derived_unit_step_exponents":{"orders":orders,"Euler_j01":vj01,"Euler_j2":vj2,"Euler_j3":vj3},
      "known_exactness":"j0/j1 all homogeneous orders; j2 powers of two; no complete higher-order j3 formula claimed"}
data_path=FIG/"exact_figure_data.json"
data_path.write_text(json.dumps(data,indent=2)+"\n")
outputs=[{"path":str(p.relative_to(ROOT)),"sha256":sha256(p.read_bytes()).hexdigest()}
         for p in sorted(FIG.glob("*.pdf"))]+[{"path":str(data_path.relative_to(ROOT)),"sha256":sha256(data_path.read_bytes()).hexdigest()}]
manifest={
    "schema_version":1,"claim_id":"Euler-final-visual-exact-illustrations-2026-10-06",
    "repository":{"commit":"unavailable; isolated publication source snapshot","dirty":True},
    "command":"python3 sources/generate_figures.py",
    "environment":{"software":[f"Python {platform.python_version()}",f"Matplotlib {matplotlib.__version__}",f"NumPy {np.__version__}"],"hardware":platform.machine()},
    "mathematics":{
        "assertion_tested":"Finite exact coefficients, periods, residue bijections, sample difference valuations, mixed parity, and explicit failed extensions used in the visual guide",
        "coefficient_domain":"Fraction over Q and exact modular arithmetic Z/2^256 Z; rendering alone uses floating point",
        "conventions":"v2(0)=infinity, represented by None; original E_{4n}=j! C_j(n); all step differences act on rows",
        "inputs":[{"path":"sources/generate_figures.py","sha256":SCRIPT_HASH}],
        "bounds":{"rank_four_modular_rows":255,"precision_bits":256,"independent_rational_rows":12,
                  "sample_base_rows":[0,8],"sample_homogeneous_orders":[1,6],"sample_homogeneous_steps":[1,4],
                  "sample_mixed_orders":[1,4],"sample_mixed_step_alphabet":[1,2,3,4],
                  "power_orders":[1,2,4,8,16],"upper_half_cases":[[16,9],[32,18],[32,19]]},
        "non_claims":["No bounded run proves a universal congruence or analytic radius.","The theorem-derived curves use separately audited algebraic statements.","These checks do not newly formalize any result in Lean."]},
    "randomness":{"used":False,"generator":"not used","seed":None},
    "run":{"started_at":STARTED,"runtime_seconds":round(time.monotonic()-T0,6),"exit_status":0},
    "outputs":outputs,"checks":[{"name":key,"assertions":value,"result":"PASS"} for key,value in sorted(COUNTS.items())],
    "result":f"PASS: {sum(COUNTS.values())} exact bounded assertions; 12 vector figures generated",
    "residual_risks":["This v1 manifest records script input hash but does not impose machine-checkable resource limits.","Plotting-library layout is checked separately by PDF rendering review."]}
(FIG/"figure_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"status":"PASS","assertions":sum(COUNTS.values()),"vector_figures":len(list(FIG.glob('*.pdf'))),"runtime_seconds":manifest['run']['runtime_seconds']},indent=2))
