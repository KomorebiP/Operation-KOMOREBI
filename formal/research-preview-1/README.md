# Komorebi
## Representations, obstructions, and verified computation

**Komorebi P. · Research Preview 1 · Release candidate 1**

Komorebi studies how mathematical objects can be transformed and represented without losing the behavior we want to understand. The recurring questions are concrete: what prevents a simpler representation from working, what corrections restore it, and what can be removed once those corrections are understood?

This first research preview presents one complete mathematical development within that broader program: prime-power Cartier systems. It connects integer polynomial masks to a uniquely determined formal series, a finite machine for its coefficients, and a canonical minimum-cardinality linear realization. The exact claim is stated below and mapped to source in [CLAIMS.md](CLAIMS.md).

The development was produced through human–machine collaboration. Its evidence is the mathematical argument, formal source, recorded kernel checks, and separately labeled computations. This release does not certify other Komorebi projects by association.

## The result

Let $p$ be prime, $r>0$, and $A,B\in\mathbb Z[z]$, with

$$
p\nmid B(0),\qquad A(0)\equiv B(0)\pmod{p^r}.
$$

There is a unique $F\in(\mathbb Z/p^r\mathbb Z)[[z]]$ satisfying

$$
F(0)=1,\qquad B(z)F(z)=A(z)F(z^p).
$$

The formal development constructs a finite linear machine that returns every coefficient of $F$ by reading base-$p$ digits least-significant first. It derives the actual correction formula, proves finite closure, and preserves the output through reductions in layers, degrees, coefficient support, permitted ideals, and correlated states.

The final reachable-observable realization is **canonical up to a unique linear isomorphism preserving the initial state, digit transitions, and output**. It has minimum cardinality among finite linear realizations of the same function on **all digit words**, over the same coefficient ring and alphabet.

“Minimum” does not mean a minimum deterministic automaton, a fastest implementation, or a unique literal matrix. “Finite precision” does not mean one finite machine for all precisions.

## Read and run

Start with the [technical note](THEOREM_NOTE.md), which includes a worked example. The [claim register](CLAIMS.md) gives theorem names and source locations. The [review guide](REVIEW_GUIDE.md) traces the main dependencies, and [attribution and related work](ATTRIBUTION.md) distinguishes classical context from this development's formal construction.

From this directory, with Python 3.10 or later:

```bash
python -B demo.py
python -B tools/check_release.py
```

The demo compares a finite Cartier reference implementation with a separately computed Mahler recurrence for three masks. It is a finite check, not a theorem prover or the minimal-realization compiler. The release checker verifies file identity, claim anchors, local links, and retained axiom coverage. **Neither command runs Lean.**

[REPRODUCE.md](REPRODUCE.md) gives the separate proof-build path. The formal source is under `padic/lean/KomorebiPadic/`.

## What this package contains

| Component | Purpose |
|---|---|
| Mathematical note and claim register | State the result, hypotheses, proof route, and limits. |
| Frozen Lean source | Preserve the Block 34 mathematical checkpoint without edits. |
| Selected historical evidence | Record the build and axiom checks performed for that checkpoint. |
| Python references and tests | Make small computations inspectable and compare independent calculation routes. |
| Reproduction tools | Separate artifact checks, finite experiments, and a fresh Lean replay. |

The retained source inventory has 92 production modules and 1,120 declared theorems. Those are inventory counts, not counts of independent discoveries. Historical evidence stays under `padic/evidence/`; new checks are recorded separately.

## Future research

The finite-precision theorem is a result in its own right. The next questions concern efficient verified execution, state maps between precisions, possible inverse-limit machines, and the range of other systems to which the same construction principles apply.

Those directions are described in [FUTURE_RESEARCH.md](FUTURE_RESEARCH.md), with their present starting points and the additional results each would require. They are not claims of this release and are not prerequisites for publishing it. In particular, coefficient compatibility does not by itself prove state compatibility, and canonicality up to isomorphism does not select canonical matrices.

## Verification and publication status

This is an unpublished release candidate. The preserved mathematical source has retained verification under Lean `4.34.0-rc2` and the pinned mathlib revision. A fresh clean local proof replay has now passed for the unchanged release source using the restored pinned runtime and dependency cache. The [reproduction checkpoint](github/REPRODUCTION_STATUS.md) distinguishes that completed run from the still-pending fresh public bootstrap and GitHub-hosted run. [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md) records that gate and the remaining distribution approval.

The efficient, formally refined executable polynomial/lattice compiler is not delivered here. The reference implementations are not claimed to be formally equivalent as executable code to Lean's noncomputable constructions. No historical-priority or broad universal-theory claim is made.

Corrections should identify a claim or file, the exact input where relevant, and the observed discrepancy. [CONTRIBUTING.md](CONTRIBUTING.md) describes the correction process. Rights and distribution terms are recorded in [RIGHTS.md](RIGHTS.md).

## GitHub staging

The candidate now includes read-only workflow definitions, issue templates, and a
private-only upload helper. [GitHub setup](GITHUB_SETUP.md) describes the proposed
remote and clean-history path. The repository has not been created or pushed by
this preparation. The [maintainer checklist](MAINTAINER_CHECKLIST.md) keeps actual
remote checks and publication approval separate from local preparation.
