#!/usr/bin/env python3
"""Compose the companion from authored explanations and exact archived source spans."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source/FD_Certified_Inference_Core_v1.0.0_Checked"
parts = []
records = []


def prose(s):
    parts.append(s.strip() + "\n")


def section(title):
    prose((r"\clearpage" if title == "Start with the returned object" else "") + r"\section{" + title + "}")


def excerpt(module, name, kind=None):
    path = SOURCE / "Komorebi" / (module + ".lean")
    lines = path.read_text().splitlines()
    pattern = re.compile(r"^(?:@\[[^]]+\]\s*)?(?:noncomputable\s+)?(?:private\s+)?(def|abbrev|theorem|lemma|structure)\s+" + re.escape(name) + r"\b")
    first = next(i for i, line in enumerate(lines) if pattern.search(line))
    last = first + 1
    next_declaration = re.compile(r"^(?:@\[[^]]+\]\s*)?(?:noncomputable\s+)?(?:private\s+)?(?:def|abbrev|theorem|lemma|structure)\s+")
    while (last < len(lines) and lines[last].strip()
           and not next_declaration.search(lines[last]) and not lines[last].startswith("end ")):
        last += 1
    block = "\n".join(lines[first:last])
    declkind = pattern.search(lines[first]).group(1)
    record = {"name": name, "file": "Komorebi/" + module + ".lean", "first_line": first + 1,
              "last_line": last, "kind": kind or ("full_proof" if declkind in ("theorem", "lemma") else "definition"),
              "excerpt_sha256": hashlib.sha256(block.encode()).hexdigest()}
    records.append(record)
    prose(r"\Needspace{4\baselineskip}")
    prose("%% SOURCE_EXCERPT " + json.dumps(record, separators=(",", ":")))
    prose(r"{\small\textcolor{teal}{\path{" + record["file"] + "}, lines " + str(first + 1) + "--" + str(last) + r".}\par}")
    parts.append(r"\begin{lstlisting}[style=BayesSource]" + "\n" + block + "\n" + r"\end{lstlisting}" + "\n")


common = (ROOT / "manuscripts/common.tex").read_text()
base_literate = re.search(r" literate=(.*?)\}\n\\lstset", common, re.S).group(1)
additional = r" {ι}{{$\iota$}}1 {υ}{{$\upsilon$}}1 {ζ}{{$\zeta$}}1 {‖}{{$\Vert$}}1 {•}{{$\bullet$}}1 {·}{{$\cdot$}}1 {⁻¹}{{$^{-1}$}}2 {⊗}{{$\otimes$}}1 {ₘ}{{$_m$}}1 {ᵐ}{{$^m$}}1 {ᵥ}{{$_v$}}1 {∂}{{$\partial$}}1 {⌊}{{$\lfloor$}}1 {⌋}{{$\rfloor$}}1 {⌈}{{$\lceil$}}1 {⌉}{{$\rceil$}}1 {⊤}{{$\top$}}1"
prose(r"\documentclass[11pt]{article}\input{common.tex}\usepackage{needspace}\renewcommand{\paperkind}{Lean companion}\setlength{\parskip}{0.35em}")
prose(r"\lstdefinestyle{BayesSource}{style=LeanCode,aboveskip=0.4em,belowskip=0.4em,literate=" + base_literate + additional + "}")
prose(r"\begin{document}\bayescover{Lean companion}{An executable proof map for the certified one-observation Gaussian solver. Actual definitions and complete proof excerpts are paired with their hypotheses, source locations, and evidence boundaries.}")
prose(r"""
\section*{The reading contract}
This companion explains how Certified Inference Core 1.0.0 turns finite rational model data into a returned gain, a posterior transport guarantee, and outward-rounded parameter intervals. It follows the actual project sources rather than presenting a new implementation. Every source listing is copied verbatim from the archived release, with its file and inclusive line span. Complete proof listings retain the entire declaration and proof body. Ambient namespaces, imports, finite-type instances, and previously declared variables are supplied by their source module and are not repeated in every listing. The listings become executable by opening their original modules in the pinned project.

The central entry point is \path{Komorebi.CachedPosterior.runCached}. Its selected gain updates and residual cache are exact rational operations. Its final certificate and output arrays are evaluated with outward-rounded dyadic arithmetic. A separate retained branch performs rounded full-gain updates. These are two different algorithms with different convergence arguments.

The archive records 117 successful active-module compilations and axiom reports for 543 named theorem or lemma declarations. Those are archived kernel checks from 12 September 2026. Fresh publication checks re-read the source bytes, manifest, successful receipts, attempted-source snapshots, logs, declaration locations, import records, and the listings printed here. A pinned Lean compiler was unavailable during this publication session, so no fresh Lean compilation is claimed. The archive contains no compiled \path{.olean} payloads. Their output hashes are preserved in receipts and agree across recorded dependency links, but cannot be rehashed from absent binaries.

The scope is finite-dimensional inference for one observation update. Model inputs are exact rational factors, the noise floor is positive, packet geometry is fixed, and posterior/output tolerances are positive rationals. Singular priors and rectangular observation operators are allowed. Returned intervals enclose the parameters of the certified Joseph Gaussian. They do not separately certify the Gaussian obtained by replacing those parameters with interval centers.
\tableofcontents
""")

section("Start with the returned object")
prose(r"""
A proof-oriented interface must say what a successful return means before asking how the program reaches one. The output record stores a verification precision, a rational candidate, a separate parameter precision, and interval arrays. The candidate contains the gain and the local energy bounds used in the distribution certificate. Precision fields identify the arithmetic graph that produced the certificate and arrays.
""")
excerpt("PosteriorOutputSolver", "Result")
excerpt("PosteriorOutputSolver", "ResultValid")
prose(r"""
\path{ResultValid} has seven conjuncts. The first two assert that the finite rational candidate and tolerance decisions pass. The third states the real distribution guarantee. The fourth and fifth assert coordinate enclosure and a uniform radius cap for the approximate Gaussian's parameters. The last two identify the selected output precision and actual evaluated arrays. A consumer can project the obligation it needs without interpreting a printed diagnostic string as evidence.

The transport distance in source is extended nonnegative real valued. Thus \path{ENNReal.ofReal} embeds the rational tolerance into that codomain. This does not change the practical inequality $W_2\le\varepsilon$ under the established nonnegativity hypotheses. It does avoid treating a potentially infinite distance as an ordinary real number before finiteness has been proved.
""")
excerpt("CachedPacketOutput", "runCached")
prose(r"""
The executable function first rejects a nonpositive output tolerance, then calls the cached solver. A successful candidate receives a computed parameter precision and represented arrays. A successful return is a logical event in this exact Lean program. The separate Python producer uses a provisional status until an emitted explicit instance is compiled.
""")

section("Soundness and guaranteed success are distinct theorems")
prose(r"""
The successful-return theorem does not ask callers to supply packet or noise validity as separate hypotheses. Those obligations are enforced by the executed checks and construction. Its only substantive input premise is an equality showing that this invocation returned this result.
""")
excerpt("CachedPacketOutput", "runCached_sound")
prose(r"""
The proof unfolds the program, separates the rejected branch, analyzes the optional cached-solver return, and combines three established facts: the solver's candidate/tolerance soundness, its posterior bound, and the interval representation specification. The use of \path{rfl} in the last conjuncts verifies origin, not numerical approximation.

Guaranteed success needs the mathematically admissible input class. It assumes a positive noise floor, valid complete output and input packet families, a supplied output seed, a scan covering every output label, and positive posterior and output tolerances. The initial gain and finite list of requested verification precisions are arbitrary. An appended sufficient-precision fallback removes dependence on the caller guessing a successful precision.
""")
excerpt("CachedPacketOutput", "runCached_terminates")
prose(r"""
This theorem proves that the program returns \emph{some} valid result. It therefore closes an existence obligation for the algorithm's own output, rather than saying only that outputs would be safe if produced. The finite fuel can be conservative. Mathematical success on unbounded exact integers/rationals does not promise that the bounded reference producer completes within a machine's time or memory limit.
""")
excerpt("CachedPacketOutput", "runCached_rejects_nonpositive_output_tolerance")

section("The exact model is represented by factors")
prose(r"""
The four finite types separate state coordinates $\iota$, observation coordinates $\kappa$, prior-factor columns $\upsilon$, and noise-factor columns $\omega$. Their cardinalities need not coincide. Factors make covariance positivity a theorem about construction. They do not put an unchecked positive-definiteness flag inside the input record.
""")
excerpt("RationalCertificateChecker", "RationalModel")
excerpt("RationalCertificateChecker", "prior")
excerpt("RationalCertificateChecker", "noise")
excerpt("RationalCertificateChecker", "innovation")
excerpt("RationalCertificateChecker", "residual")
prose(r"""
Write $P=LL^{\mathsf T}$, $R=TT^{\mathsf T}+\sigma I$, $S=HPH^{\mathsf T}+R$, and $F(B)=PH^{\mathsf T}-BS$. Positive $\sigma$ makes $R$ positive definite even if $T$ has deficient rank. The prior $P$ may remain singular. The exact posterior gain involves $S^{-1}$, but iteration and stopping can evaluate $F(B)$ without constructing that inverse.

Rational entries embed into actual finite-dimensional Euclidean spaces and continuous linear maps. The source proves compatibility of casts with matrix operations. The meaning of the rational model is consequently a real probability measure, not a symbolic tuple whose probabilistic interpretation is assumed later.
""")
excerpt("RationalModelSemantics", "posterior")
excerpt("RationalModelSemantics", "approximation")
prose(r"""
The target is the explicitly selected Gaussian posterior kernel evaluated at the supplied observation. The approximation is the gain-dependent Joseph law. All distribution statements below refer to those concrete measures.
""")

section("Why the target is a Bayesian posterior")
prose(r"""
The Gaussian semantics layer builds both orders of the same joint law. In the forward description, a prior draw passes through the affine Gaussian likelihood. In the reverse description, an observation draw passes through the displayed posterior kernel. Equality of those actual joint measures supplies disintegration.
""")
excerpt("FDGaussianConditioning", "fd_joint_disintegration")
prose(r"""
Taking the observation marginal identifies the evidence law. Mathlib's canonical posterior is a version of conditional probability, so its identification is an almost-everywhere statement under that evidence law. A conditional probability version can be modified on an evidence-null set without changing disintegration. The source retains this distinction rather than changing the quantifier to pointwise equality.
""")
excerpt("FDGaussianConditioning", "fdPosteriorKernel_eq_canonical")
prose(r"""
The solver certificate is pointwise for the chosen explicit kernel at the supplied rational observation. The mathematical statement relating this kernel to a canonical posterior version is evidence-almost everywhere. These are compatible conclusions. They answer different version questions.

Singular priors require no prior inverse in this chain. The positive-definite noise supplies the invertible innovation covariance. This is why the rotated example later can have rank-one prior support while its observation covariance is nonsingular.
""")
excerpt("FDGaussianConditioning", "canonicalPosterior_eq_josephGaussian")

section("A residual controls distribution error")
prose(r"""
The proof couples the exact posterior and approximate Joseph law using shared Gaussian ingredients. Its squared transport cost is derived from that actual coupling. Writing $K=PH^{\mathsf T}S^{-1}$ and $v=y-Hm$, the coupling cost is
\[
 \|(K-B)v\|^2+\tr((K-B)S(K-B)^{\mathsf T}).
\]
The identity $K-B=F(B)S^{-1}$ converts this to a residual expression. This is an upper bound on the optimal transport cost, since a particular coupling need not minimize the transport problem.
""")
excerpt("FDInexactGainCoupling", "inexactGainCoupling_cost_residual")
prose(r"""
The noise floor gives $\|S^{-1}\|\le\sigma^{-1}$. A Frobenius/operator-norm majorant then removes the inverse from the final stopping quantity:
\[
 W_2^2\bigl(\pi_y,\widehat\pi_{B,y}\bigr)
 \le\|F(B)\|_{\mathrm F}^2\frac{\sigma+\|v\|^2}{\sigma^2}.
\]
The right side is computed from the current gain, model factors, and observation. The source's explicit hypotheses make the roles of covariance positivity, positive noise floor, and its quadratic lower bound visible.
""")
excerpt("FDResidualEnergyCertificate", "posterior_wasserstein2Sq_le_residual_energy")
prose(r"""
No comparison to only a formal mean/covariance surrogate is used. The left side contains the actual target and approximation measures. A zero residual yields equality with the selected posterior law, while a small residual yields a quantitative whole-law certificate.
""")
excerpt("FDInexactGainCoupling", "gainPosteriorLaw_eq_of_residual_zero")

section("Packet geometry is checked, including completeness")
prose(r"""
Output packets $Q_a$ partition state directions. Input packets $D_b$ partition observation directions for local residual certification. Each family is a finite rational self-adjoint orthogonal resolution of the identity. Four obligations are checked: symmetry, idempotence, pairwise annihilation, and completeness. Missing the completeness clause could discard residual energy outside the listed packets.
""")
excerpt("RationalPacketCertificates", "RationalPacketsValid")
excerpt("RationalPacketCertificates", "checkRationalPackets")
excerpt("RationalPacketCertificates", "realPackets")
prose(r"""
The rational predicates construct real projector geometry using exact casts. In Euclidean space, self-adjoint disjoint projections give an energy partition. In particular, the sum of output-packet squared Frobenius energies equals the entire residual energy. The two-sided packet theorem similarly accounts for both output and observation directions in the final certificate.
""")
excerpt("PacketSelectiveAlgebra", "sum_left_energy")
prose(r"""
Packet labels can include zero projectors. What matters is the proved resolution. The seed supplies an actual label, so the chosen-output family is nonempty for the selection/convergence theorem. Duplicate scan entries are allowed. Scan coverage concerns which labels can be found, not a claim that every scanned label has positive energy.
""")

section("The finite checker and its semantic theorem")
prose(r"""
An arbitrary producer may propose a gain and conservative local upper bounds. The finite candidate predicate requires positivity, both complete packet families, every local residual-energy bound, and an innovation-vector energy bound. The checker decides those exact rational obligations.
""")
excerpt("RationalCertificateChecker", "RationalCandidate")
excerpt("RationalCertificateChecker", "ValidCandidate")
excerpt("RationalCertificateChecker", "checkCandidate")
excerpt("RationalCertificateChecker", "checkTolerance")
prose(r"""
The tolerance test avoids a square root. With $U=\sum_{a,b}u_{ab}$ and $V$ the innovation upper bound, it checks $U(\sigma+V)\le\varepsilon^2\sigma^2$ and nonnegative $\varepsilon$. The semantic theorem links passing Boolean decisions to the target law. Positivity of denominators is recovered from candidate validity, so algebraic division never silently assumes a nonzero noise floor.
""")
excerpt("RationalPosteriorCertificate", "checked_tolerance_bounds_posterior")
prose(r"""
The final rounded verifier does not execute the full exact-residual \path{checkCandidate}. It checks setup, constructs outward bounds, and executes the tolerance test. Construction soundness proves that its candidate would pass the exact checker. This operational distinction matters when counting full residual recomputations and describing the arithmetic boundary.
""")

section("Selected updates preserve unselected packets")
prose(r"""
Let $\eta=(\sigma+\tr S)^{-1}$ be the exact rational step. A selected update changes $B$ by $\eta Q_aF(B)$. Its residual satisfies
\[
 F(B^+)=F(B)-\eta Q_aF(B)S.
\]
Multiplying on the left by $Q_b$ kills the change whenever $b\ne a$, because $Q_bQ_a=0$. For the selected packet, idempotence gives the right innovation transition $I-\eta S$. These two identities justify the cache.
""")
excerpt("PacketSelectiveAlgebra", "packetStep")
excerpt("PacketSelectiveAlgebra", "unselected_residual")
excerpt("PacketSelectiveAlgebra", "selected_residual")
prose(r"""
Only output locality is asserted. An input subpacket can couple to other input directions through the innovation matrix. The retained \path{input_packet_effect} identity contains $SD_b$, and does not replace it with a diagonal or commuting expression. General input-block locality would need additional hypotheses.

The spectral transition contracts the selected energy by the proved full-update rate. Summing the energy partition produces global descent weighted by the energy of the chosen packet. This is the bridge from local algebra to a terminating selection policy.
""")

section("Maximum selection is an executed finite scan")
prose(r"""
The algorithm selects by exact rational energy. It does not assume a magical maximum oracle or a predetermined cyclic schedule. The recursive scan compares the incumbent energy to the next label and replaces it only under a strict inequality. Ties retain the incumbent.
""")
excerpt("GreedyPacketSelection", "winner")
excerpt("GreedyPacketSelection", "selectPacket_max")
excerpt("GreedyPacketSelection", "selected_energy_share")
prose(r"""
Coverage of the scan implies that the executed winner has at least every packet's energy. If there are $A$ output labels, it therefore captures at least $1/A$ of the total energy. Repeated labels do not change this pigeonhole argument. The supplied seed ensures $A>0$.

Combining this share with selected-packet descent yields the adaptive energy factor
\[
 q_{\rm adapt}=1-\frac{1-q}{A},\qquad
 q=\left(1-\frac{\sigma}{\sigma+\tr S}\right)^2.
\]
It lies in $[0,1)$ under the admissible model hypotheses. This is a conservative rate bound. It need not equal the measured contraction of a particular packet or trajectory.
""")
excerpt("GreedyPacketSelection", "adaptiveRate")
excerpt("GreedyPacketConvergence", "greedy_score_geometric")

section("Finite fuel reserves verification slack")
prose(r"""
The solver uses an explicit rational fuel expression, avoiding logarithm evaluation and an eigenvalue oracle. A Bernoulli-type envelope turns a geometric bound into a simple ceiling. The resulting fuel can substantially overestimate the update count that early stopping actually uses.
""")
excerpt("GeometricFuel", "toleranceFuel")
excerpt("GreedyPacketConvergence", "adaptiveFuel")
excerpt("GreedyPacketConvergence", "greedy_score_at_fuel")
prose(r"""
The cached score aims at $\varepsilon^2/4$, not merely $\varepsilon^2$. Once the exact score crosses that stricter threshold, the sufficient final precision can tolerate up to another $\varepsilon^2/4$ of score inflation and still pass the desired target. The construction therefore has ample strict slack. It does not depend on the rounded score decreasing monotonically with every precision increment.

The theorem permits every iterate at or above the computed fuel. The operational search stops at the first passing exact score, which may be much earlier. The coordinate example uses six updates despite a fuel of 410,093, and the rotated example uses four despite a fuel of 4,267. Those values demonstrate conservatism of this formula in the included cases, not a worst-case efficiency theorem.
""")

section("The cache invariant is proved for the executed update")
prose(r"""
The cached state stores a gain, one residual matrix per output label, their energies, and their total. The invariant links every stored quantity to the current gain's residual. It is an equation invariant, not an informal assertion that cached values remain approximately correct.
""")
excerpt("CachedPacketState", "State")
excerpt("CachedPacketState", "Valid")
excerpt("CachedPacketState", "initialState")
excerpt("CachedPacketState", "step")
prose(r"""
Only the selected residual is multiplied by the precomputed transition. Only its energy is recomputed. The total changes by subtracting the old selected energy and adding the new one. The gain changes by the selected residual. The preservation proof uses the selected/unselected identities and a finite-sum difference identity.
""")
excerpt("CachedPacketState", "step_valid")
prose(r"""
All of these updates are exact rationals. No rounding radius is hidden in \path{Valid}. This exactness is why the source can reuse untouched energies without carrying extra approximation errors.
""")

section("Cached execution equals the recomputed greedy trajectory")
prose(r"""
The cached total equals the full residual energy by the packet partition, and its score equals the model's direct residual score. The cache-based maximum also equals the recomputed maximum. These facts connect an efficient state representation to the previously proved gain iteration.
""")
excerpt("CachedPacketState", "score_eq")
excerpt("CachedPacketTrajectory", "chosen_eq")
excerpt("CachedPacketTrajectory", "trajectory_gain")
prose(r"""
The trajectory theorem is stronger than agreement at one exported final matrix. It proves equality for every natural update count from every valid initial cached state under valid output geometry. Consequently the cached solver inherits greedy convergence without treating a reference Python implementation as an oracle.

The origin theorem below further proves that a returned certificate gain came from an actual greedy iterate within the computed fuel. The final verifier cannot silently replace the proposed gain with an unrelated one.
""")
excerpt("CachedPacketOrigin", "cached_solver_gain_origin")

section("Search completeness closes the algorithmic existence step")
prose(r"""
The bounded search inspects the initial state's exact score, then advances until it passes or fuel is exhausted. A zero-fuel call still checks its current state. Soundness and completeness are separate induction arguments: a successful result satisfies the threshold, and a trajectory whose final permitted state passes guarantees some early-stopping result.
""")
excerpt("CachedPacketSearch", "search")
excerpt("CachedPacketSearch", "search_complete")
excerpt("CachedPacketSolver", "solveCached")
prose(r"""
The entry guard checks positive posterior tolerance, setup validity, and scan coverage. \path{prepare} computes the model step, innovation transition, and score weight once. The search begins from the actual cache constructor, whose validity is immediate. A successful cached state proceeds to independent rounded verification of its gain.

The solver termination proof composes established obligations rather than assuming convergence of an arbitrary cache: valid initialization, validity preservation, exact trajectory equivalence, geometric fuel sufficiency, search completeness, and final-certifier completeness.
""")
excerpt("CachedPacketSolver", "solveCached_terminates")

section("Outward dyadic arithmetic has its own soundness proof")
prose(r"""
A scalar ball is a rational center and absolute radius. Enclosure means $|x-c|\le r$. Its radius is not enforced by the record constructor alone. A proof of enclosure implies nonnegativity, and arithmetic lemmas propagate that proof through addition, multiplication, and finite sums.
""")
excerpt("RationalBall", "Ball")
excerpt("RationalBall", "Encloses")
excerpt("DyadicBall", "round")
excerpt("DyadicBall", "round_encloses")
prose(r"""
At fractional precision $p$, centers are rounded down to a multiple of $2^{-p}$. The radius is first inflated by the displacement of the center, then rounded up. This preserves enclosure for both positive and negative quantities. Integer parts are unbounded in this mathematical implementation, so the theorem is not an IEEE floating-point overflow guarantee.

The final candidate retains the gain unchanged. It evaluates each residual packet and innovation vector with outward arithmetic, then extracts conservative energy upper bounds. It is not a rounded gain update.
""")
excerpt("RoundedCandidate", "roundedCandidate")
excerpt("RoundedCandidate", "roundedCandidate_valid")

section("Finite verification precision is computed, not guessed")
prose(r"""
Magnitude and radius budgets bound score inflation by a computable coefficient times the dyadic mesh. The sufficient-precision function chooses a precision for a positive slack. Every precision above that threshold has the claimed inflation bound. Individual finite-precision scores need not be monotone for this theorem to work.
""")
excerpt("PrecisionCompleteness", "sufficientPrecision")
excerpt("PrecisionCompleteness", "rounded_score_le_with_slack")
excerpt("RoundedSolverSearch", "certifyGain")
excerpt("RoundedSolverSearch", "certifyGain_complete")
prose(r"""
The caller's finite probes are tried first and can find a cheap passing precision. The sufficient precision is appended regardless of whether the probe list is empty or contains repeated entries. The fallback is a theorem-backed finite completion mechanism for a gain with sufficient exact score slack.

A failed rounded check does not prove that the true posterior error is too large. Conservative bounds can fail while an exact or higher-precision bound would pass. A successful check, however, is sound. This asymmetry is part of the interface and prevents interpreting a verifier rejection as a statistical impossibility result.
""")

section("Output radius and posterior tolerance mean different things")
prose(r"""
For the returned gain $B$, the approximate Gaussian has exact rational mean $m+B(y-Hm)$ and Joseph covariance
\[
 (I-BH)P(I-BH)^{\mathsf T}+BRB^{\mathsf T}.
\]
The parameter graph encloses those entries. It does not directly enclose the exact posterior's coordinates merely because the law is close in $W_2$.
""")
excerpt("PosteriorOutput", "outputMean")
excerpt("PosteriorOutput", "outputCovariance")
excerpt("PosteriorOutputPrecision", "outputPrecision")
excerpt("PosteriorOutputPrecision", "represent_spec")
excerpt("PosteriorOutputSemantics", "approximation_eq_output_gaussian")
prose(r"""
Here $\varepsilon$ controls the target-to-approximation transport distance, and $\delta$ controls every reported interval radius around the approximation's exact parameters. They are independently supplied tolerances and have different codomains and purposes. Shrinking $\delta$ does not change the selected gain. Shrinking $\varepsilon$ can require more gain updates.

The approximation covariance is positive semidefinite by the Joseph construction under the checked model hypotheses. Independent rounding of its entries to interval centers need not preserve every covariance constraint. The enclosed exact covariance remains the semantic object certified by the result.
""")

section("Execution example I: a rectangular coordinate model")
prose(r"""
The first complete execution has two state coordinates and one observed coordinate. The prior covariance is $\operatorname{diag}(4,1)$, the observation is the sum of the two coordinates, noise variance is one, and the prior mean is zero. The exact gain is $(2/3,1/6)^{\mathsf T}$. Coordinate output packets form a complete pair and the input packet is the one-dimensional identity.
""")
excerpt("GeneratedCachedCoordinate", "model")
excerpt("GeneratedCachedCoordinate", "outputs")
excerpt("GeneratedCachedCoordinate", "inputs")
excerpt("GeneratedCachedCoordinate", "finalGain")
prose(r"""
Starting from the zero gain, the executed output labels are $0,1,0,1,0,1$. The innovation variance is six, the chosen trace-cap step is $1/7$, and three visits to each packet give $B=(228/343,57/343)^{\mathsf T}$. This observation operator is rectangular, so no theorem can be relying on an inverse observation matrix.

The posterior tolerance is $1/20$, the output radius cap is $1/1000$, the passing certificate precision is 12, and parameter precision is 32. The exact score $34/117649$ passes the stricter iteration threshold $\varepsilon^2/4=1/1600$. The outward certificate score $481/1048576$ passes $\varepsilon^2=1/400$.
""")
excerpt("GeneratedCachedCoordinate", "cached_return")
excerpt("GeneratedCachedCoordinate", "output_precision_computed")
excerpt("GeneratedCachedCoordinate", "mean_centers_computed")
excerpt("GeneratedCachedCoordinate", "mean_radii_computed")
excerpt("GeneratedCachedCoordinate", "covariance_radii_computed")
prose(r"""
These values are not merely computed outside Lean and compared to a manually written certificate. The explicit module checks the actual \path{runCached} return and obtains the universal output contract by successful-return soundness.
""")
excerpt("GeneratedCachedCoordinate", "output_return")
excerpt("GeneratedCachedCoordinate", "output_valid")

section("Execution example II: a singular prior and rotated packets")
prose(r"""
The second execution has $H=I_2$, $P=\begin{psmallmatrix}1&1\\1&1\end{psmallmatrix}$, $R=I_2$, and $y=(1,-1)$. The prior factor has only one column. Its rank-one prior is supported on the common-mode line, while the observation points in the difference direction. The common-mode and difference-mode rational projectors give a rotated complete packet family.
""")
excerpt("GeneratedCachedRotated", "model")
excerpt("GeneratedCachedRotated", "outputs")
excerpt("GeneratedCachedRotated", "inputs")
excerpt("GeneratedCachedRotated", "finalGain")
prose(r"""
All four selected labels are zero: the residual lies in the common-mode packet, and the difference packet has zero residual energy. The final gain has every entry $203/625$. Its exact score is $3072/390625$ and its rounded certificate score is $9111/1048576$. With $\varepsilon=1/4$, they pass $1/64$ and $1/16$ respectively.

Both the exact posterior and approximation mean are zero in this case. The exact posterior covariance has every entry $1/3$. The final approximate Joseph covariance has every entry $130379/390625$. That distinction remains certified by the law guarantee even though the selected observation produces matching means.
""")
excerpt("GeneratedCachedRotated", "cached_return")
excerpt("GeneratedCachedRotated", "covariance_centers_computed")
excerpt("GeneratedCachedRotated", "covariance_radii_computed")
excerpt("GeneratedCachedRotated", "output_return")
excerpt("GeneratedCachedRotated", "output_valid")
prose(r"""
The returned intervals are very narrow compared with the supplied radius cap. This does not make the approximate covariance equal to the exact posterior covariance. It means the finite output graph represents the approximate covariance accurately. The $W_2$ theorem supplies the separate target comparison.
""")

section("A checked counterexample prevents a false rounded-cache claim")
prose(r"""
The exact invariant cannot survive independent rounding of gain and residual centers without an additional error budget. The archived scalar example has prior variance one, observation coefficient one, noise variance one, observed value one, and zero initial gain. Its step is $1/3$. The ideal gain after one step is $1/3$, and the ideal residual is also $1/3$.

Rounding those two centers down independently to precision zero produces stored gain zero and stored residual zero. The true residual of the stored gain is one. Therefore the naive cached score reports zero, while the true score is two. This is an executed counterexample with valid setup, rather than a hypothetical concern about roundoff.
""")
excerpt("CachedRoundingBoundary", "naiveRounded")
excerpt("CachedRoundingBoundary", "naive_score_zero")
excerpt("CachedRoundingBoundary", "true_score_two")
excerpt("CachedRoundingBoundary", "naive_cache_invalid")
excerpt("CachedRoundingBoundary", "naive_final_verification_rejected")
prose(r"""
The independent final verifier evaluates the actual stored gain and rejects the false convergence signal for tolerance $1/10$. This gives a precise division of responsibilities: an internal heuristic or invalid cache can be misleading, but its claim does not bypass final certification. A future rounded selective cache needs a propagated cache-error invariant and its own termination proof. The existing exact invariant must not be relabeled as one.
""")

section("Negative controls test specific failure boundaries")
prose(r"""
The archive contains three intentionally invalid Lean controls. They were expected to fail, and their successful rejection is preserved separately from successful mathematical modules. A false rational equality tests ordinary proof rejection. A placeholder tests the warnings-as-errors route. A dropped radius tests that a zero-radius interval at zero cannot enclose a distinct rational.
\begin{center}\begin{tabularx}{\linewidth}{p{0.29\linewidth}Xr}\toprule
Control & Obligation intentionally violated & Archived exit\\\midrule
\path{FalseEquality} & An explicit false equality & 1\\
\path{Placeholder} & An admitted placeholder under warning rejection & 1\\
\path{DroppedRoundingRadius} & Enclosure of $1/1024$ by center zero and radius zero & 1\\\bottomrule
\end{tabularx}\end{center}

The radius control is copied here as a complete intentionally failing file fragment. It is not a proof excerpt from an accepted module.
""")
negative = SOURCE / "results/negative_controls/DroppedRoundingRadius.lean"
prose(r"\begin{lstlisting}[style=BayesSource]" + "\n" + negative.read_text().rstrip() + "\n" + r"\end{lstlisting}")
prose(r"""
The expected result is rejection. A tool report that only says the command completed would be ambiguous here. The archived JSON records nonzero exit status, \path{expected_rejection=true}, source hashes, and log hashes for each control.

Producer-side tests also reject malformed or unsupported inputs. They exercise parser policy and resource handling, while the Lean controls exercise proof and enclosure boundaries. Neither set proves a universal refinement theorem for the Python parser. An exported successful instance certifies the literal model and data appearing in its emitted Lean source.
""")

section("The rounded full-gain branch remains a separate result")
prose(r"""
The source also retains a solver in which failed verification is followed by a genuinely rounded full-gain update. Its convergence analysis tracks update error and chooses an update accuracy plus finite fuel. It is not the cached selective program with rounding switched on.
""")
excerpt("RoundedSolverSearch", "solveRounded")
excerpt("RoundedSolverSearch", "solveRounded_terminates")
prose(r"""
This theorem confirms that the retained full-update branch also guarantees a successful certified candidate for positive tolerance under admissible model and packet hypotheses. Its proof invokes the rounded-score-at-fuel theorem, final verification completeness, and bounded-search completeness. The distinction matters when a reader asks whether the release has finite-precision updates: yes for this full branch, while selective cached gain updates in the canonical branch remain exact rationals.

The seven-case bounded benchmark compares full Richardson, recomputed greedy selection, and cached greedy selection. The 21 benchmark modules certify static explicit final candidates. The two generated modules separately certify complete canonical program executions. Universal algorithm theorems and those two kinds of instance evidence should be counted separately.
""")

section("Rebuild the pinned project without overwriting the archive")
prose(r"""
The source archive preserves the exact release and failures. A new rebuild should use a working copy, because the original rebuild script deliberately regenerates active compiled caches, audit records, seals, and result files. The following commands are a reproducible route, not a claim that they were executed during this publication session.

Restore the separate Linux x86\_64 portable runtime, then confirm Lean 4.34.0-rc2 at commit \path{6a10ac8c22beadecabdbb0919c2b50214762f91d} and mathlib at \path{aeb72f1e9981b6d35b426b16dca7759be3e7ba06}. The source package contains restoration metadata and starter information, but not the large runtime payload parts. Its metadata describes a Linux runtime intended also for x86\_64 WSL2, rather than a native Windows compiler.
\begin{lstlisting}[language={},basicstyle=\ttfamily\small,breaklines=true,frame=single]
# Run from the publication directory, after extracting the source archive.
cp -a source/FD_Certified_Inference_Core_v1.0.0_Checked rebuild_work
cd rebuild_work
python3 checks/rebuild_release.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
\end{lstlisting}

The script compiles modules in \path{MODULE_ORDER.json}, uses one Lean thread and warnings as errors, runs negative controls and exact cache diagnostics, verifies the release seal, and reconciles benchmark reports. It removes active project caches for a clean project-source rebuild while reusing the pinned mathlib caches. This is not a clean rebuild of every external dependency from source.

For a new proof-producing Python example, emit a new module in the working copy, regenerate its inventory, and rebuild:
\begin{lstlisting}[language={},basicstyle=\ttfamily\small,breaklines=true,frame=single]
python3 checks/cached_posterior.py examples/adaptive_coordinate.json \
  --output results/local_cached.json \
  --emit-lean Komorebi/LocalCached.lean \
  --namespace LocalCached --try-precisions 4 12
python3 checks/build_inventory.py
python3 checks/rebuild_release.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
\end{lstlisting}

Treat \path{PASS_CACHED_PROVISIONAL} as provisional until the emitted module compiles. A reported \path{RESOURCE_LIMIT} is a bounded producer failure, not a refutation of mathematical finite termination. The default producer caps include dimension eight, 10,000 updates, rational bit limits, precision limits, scan limits, and input byte limits.

The publication's read-only check is narrower and can run without Lean:
\begin{lstlisting}[language={},basicstyle=\ttfamily\small,breaklines=true,frame=single]
python3 scripts/lean_inventory.py
\end{lstlisting}
It rechecks all 939 manifest entries, all 117 final active source/snapshot/log receipts, 288 direct project dependency records, 543 declaration locations and axiom reports, and every source-attributed listing in this companion. These source consistency results are fresh checks. The September kernel runs remain archived evidence.
""")

section("How to extend the proof without weakening the contract")
prose(r"""
A useful extension begins by choosing which invariant changes. Sequential filtering changes the target model over a sequence of observations and needs an explicit propagated state/posterior contract. Uncertain input data changes exact model semantics and requires an uncertainty interpretation. Rounded selective caching changes the exact residual equations and requires error bounds coupled to selection and convergence. A changing packet hierarchy changes the geometry that underpins energy completeness.

The present theorem chain gives concrete reuse points. Gaussian disintegration and residual transport estimates can support new candidate producers. The finite checker can certify any explicitly represented gain whose rational upper bounds pass. Output representation can enclose the Joseph parameters of any supplied rational gain. What cannot be reused unchanged is a trajectory termination proof when updates, selection, or cache equations have changed.

The release's current accomplishment is an integrated algorithmic theorem: within its declared input class, its own program returns a valid result, and every successful return has that result contract. Scope boundaries identify future work rather than leaving this scoped theorem unfinished. They also prevent a proof of one Gaussian update from being reported as a universal sequential Bayesian inference system.
""")

prose(r"\appendix\clearpage\section{Module order and declaration map}")
prose(r"""
The table follows the archived compilation order. Counts are named theorem/lemma declarations in \path{DECLARATIONS.json}; definitions and structures are not included. Support lemmas, concrete checks, and benchmark statements are counted together, so the total is not a count of independent discoveries. \path{ReleaseAxiomAudit} imports the entire project and prints axiom dependencies rather than introducing new mathematical declarations.
\begin{longtable}{r p{0.70\linewidth} r}
\toprule Order & Module & Count\\\midrule\endfirsthead
\toprule Order & Module & Count\\\midrule\endhead
""")
order = json.loads((SOURCE / "MODULE_ORDER.json").read_text())
declarations = json.loads((SOURCE / "DECLARATIONS.json").read_text())
for i, name in enumerate(order, 1):
    count = sum(d["module"] == name for d in declarations)
    prose(str(i) + r" & \path{" + name + "} & " + str(count) + r"\\")
prose(r"\bottomrule\end{longtable}")
prose(r"""
\clearpage\section{Evidence that accompanies the source}
\begin{longtable}{p{0.35\linewidth}p{0.59\linewidth}}
\toprule Artifact & Role\\\midrule\endfirsthead
\toprule Artifact & Role\\\midrule\endhead
\path{RELEASE_SCOPE.md} & The input/output finish line and named extensions.\\
\path{PROOF_NOTE.md} & The original mathematical proof route.\\
\path{DECLARATIONS.json} & All 543 named theorem/lemma source locations.\\
\path{AXIOM_AUDIT.json} & Complete named-declaration coverage and permitted axiom dependencies.\\
\path{FINAL_VERIFICATION_RECEIPT.json} & Archived final successful builds, failed attempts, environment pins, controls and diagnostic summary.\\
\path{MANIFEST_SHA256.txt} & 939 archived file digests.\\
\path{audit/} & Attempted-source snapshots, command receipts and exact process logs, including failed attempts.\\
\path{results/FORMAL_INSTANCES.json} & The two complete cached execution instances and their scopes.\\
\path{BENCHMARK_REPORT.md} & Controlled reference costs, timing methodology and limits.\\
\path{FAILURE_LOG.md} & Preserved failures and corrections.\\
\path{SELF_REVIEW.md} & Original internal adversarial review, with no external independence claim.\\
\path{RUNTIME_METADATA/} & Separate runtime restoration metadata and pins.\\
\path{reviews/lean_inventory.json} & Fresh publication-side byte, location, receipt, import and excerpt consistency results.\\\bottomrule
\end{longtable}

The archived axiom union is \path{Classical.choice}, \path{Quot.sound}, and \path{propext}. The check does not remove those foundations, prove Lean's kernel correct, or establish implementation refinement for all outside tools. It identifies the axioms reported for these named declarations and confirms that no added project axiom appears in that audit.

Archived final-module process time sums to 558.439 seconds. This is the sum of measured process durations, not an independently measured end-to-end wall-clock rebuild. The same distinction applies to hardware performance claims: verified mathematical results remain valid while bounded timings answer only their recorded experimental question.

The source, actual theorem contracts, execution-instance modules, failed controls, and read-only inventory make the publication reviewable at every major implication. A reader can begin at the output theorem, trace its obligations backward, and rerun the pinned working-copy build when the separate runtime is available.
\end{document}
""")

out = ROOT / "manuscripts/lean.tex"
out.write_text("\n".join(parts))
from collections import Counter
print(json.dumps({"output": str(out), "excerpts": len(records), "kinds": dict(Counter(r["kind"] for r in records)),
                  "lines": len(out.read_text().splitlines())}, indent=2))
