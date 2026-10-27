# Version 6 reading map and current boundary

**Operation Komorebi · Komorebi P. · 26 September 2026**

This running manuscript preserves the complete version-5 reading record, including all recovered earlier proof notes, and appends Continuation VI. The earlier reading maps and unresolved-status descriptions remain historical statements at their stated version. The current scope is the map below and the explicitly quantified theorems of Continuation VI.

The new result extends the exact dyadic valuation classification from pure shifted walls to arbitrary first omitted depths with prepared-polynomial degree at most 64. It also identifies an odd-multiplier dependence that the pure-wall examples could not reveal.

## Current result map

| Question | Current result | Location |
|---|---|---|
| Uniform precision after retaining depths $0,\ldots,M$ | Optimal exponent $4M+3$, unchanged | Foundations and Continuation IV |
| Whole tail at any first omitted depth $r$ | Exact finite-polynomial valuation reduction | Continuation IV |
| Canonical carry geometry of arbitrary $r$ | $r=b2^L-j$, where $j$ is the last minimizing carry index and $b$ is odd | Continuation VI, Section 2 |
| Regular terminal labels | Complete exact valuation atlas for every multiplier | Continuation VI, Section 3 |
| Irregular labels $17,33,49$ | Parameter-uniform coefficient certificates in every exceptional phase | Continuation VI, Sections 5–8 |
| Every depth with $\deg W_r\le64$ | Complete constant-or-simple-root dyadic valuation atlas | Continuation VI, Section 9 |
| Every $r$ with at most 195 binary ones | Included by the degree bound, without an upper size limit | Continuation VI, Corollary VI.9 |
| Repeated dyadic roots in this classified region | Excluded by the complete atlases | Continuation VI, Section 9 |
| Repeated roots at larger irregular terminal labels | Not excluded or fully classified | Current research boundary |
| Repeated roots over an algebraic extension | Not excluded by a dyadic-only atlas | Current research boundary |
| Lean checking or historical priority | Neither claimed | All continuation audit sections |

A classification on $\mathbb Z_2$ must not be called global squarefreeness. A prepared polynomial may have roots in an algebraic extension that the dyadic argument domain does not see. The resultant criterion in Continuation V remains a separate certificate of squarefreeness when its nonzero valuation is established.

## Notation added in this continuation

The target remains $E_{2N}$. The last retained depth is $M$, and the first omitted depth is $r=M+1$. A nonempty original tail has offset $x=N-r\ge0$; its analytic residual is also evaluated throughout $\mathbb Z_2$.

The finite carry cost is

\[
\lambda_r(q)=3q+s_2(r+q)-s_2(r),\qquad
\mu_r=\min_q\lambda_r(q),\qquad
j=\max\{q:\lambda_r(q)=\mu_r\}.
\]

For a nonconstant residual, the terminal tuple is

\[
L=v_2(r+j),\qquad b=(r+j)/2^L,\qquad \delta=L-L_j.
\]

The label $j$ is not the Euler row, $L$ is not the truncation depth, and $b$ is not a Bernoulli number. The tuple must be determined from the **last global carry minimum**, not from the first apparent local wall.

## New distinctions preserved in v6

| Tempting inference | Correct statement |
|---|---|
| Pure shifted-wall data cover every arithmetic depth | An arbitrary depth also has an odd multiplier; the terminal-carry theorem and parameter certificates are needed |
| Equal carry weights imply equal root geometry | False: at label 17 and distance 11, only $b\equiv1,41\pmod{64}$ have two roots |
| A parity-ball cutoff proves a global Gauss cutoff | The new uniform cutoff is coefficientwise after splitting parity |
| A finite-precision multiplier template defines an exact analytic family in the multiplier | Not asserted; the proof concerns actual positive integer multipliers with the stated terminal label |
| Classifying all $r<2^{195}$ requires enumerating them | Here it follows from the general degree bound and the degree-64 classification; the audit did not enumerate that interval |

## Evidence in this release

The incoming v5 ledger matched all 124 recorded file hashes. Seven new retained bounded scientific executions completed successfully: five new v6 audits, a fresh v4-foundation rerun, and a fresh v5 distribution/resultant rerun. All seven execution manifests passed the retained validator.

The new audits include 4,539 regular whole-ball certificates and 1,163 parameter-uniform irregular leaf certificates. These are distinct from sampled point checks. The proof of the finite-precision multiplier template extends the latter certificates to all admissible odd multipliers. The exact scope and nonclaims appear alongside the results.

One document-figure export initially failed because the output directory was not writable from the user-visible Python process. The directory permission was corrected and both figures were regenerated. No scientific calculation was lost or changed. Earlier v5 computational timeouts remain recorded in the historical notes.

## How the history is retained

The next part is the complete v5 Markdown reading record, preserved without rewriting its mathematical content. Its references to the then-current frontier are historical. Continuation VI is appended after that record and its reproduction appendix. Historical versions are also retained as separate source files in the bundle.
