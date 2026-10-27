# What LANA specifies about the integral region

Base: RR5, archive SHA-256
`79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`.
Checked 2026-10-25. This file extracts definitions from the pinned LANA survey and distinguishes them from the still missing original-IUT dictionary. No IUT compatibility or abc theorem is proved here.

## Exact source

LANA Project, *Project LANA Interim Report on IUT Theory*, revision 1.0.1, July 20, 2026. TeX commit `293bdd89463473ae13d40834d70fb4b7ba81da1f`, blob SHA-1 `35a2507a5bc5bfc1835067dbdb6776e4bc4a3152`, UTF-8 byte SHA-256 `13c60b0669644b0e5dea72adfdb55b1dad367ff91f5b11fadf75e48ac0e66f51` (189256 bytes). The complete pinned source was retrieved through GitHub and the sections below were read. No full external source is included in this checkpoint.

Stable locator: <https://github.com/katobungen/LANA_report_202607/blob/293bdd89463473ae13d40834d70fb4b7ba81da1f/LANA_report_202607.tex>.

The PDF inspected in RR5 has SHA-256 `aa53093aa8d69dbce5f8fb4f541069a418650260dee1ef532917aa8db89606c7` and 50 pages. Its first page says July 20, 2026. Source indices below refer to the 2726-line pinned TeX, not GitHub HTML line numbers.

## Definition-level dictionary

| Object | What the pinned survey specifies | Location and limit |
|---|---|---|
| BPS | An etale-unit portion of local group/monoid actions, with compact structure, together with a value-group portion. Its isomorphisms preserve both portions. | Section 4.1; TeX 1260–1344. This is explicitly a simplified replacement for the original prime-strip. |
| Value line | An oriented one-dimensional real vector space with nonzero local pilots and nonzero sum over bad places. With product-formula kernel fixed, the survey treats it as a pointed oriented line. | TeX 1295–1330. The underlying line is not enough; the pilot marking matters. |
| Log-shell | A finite-place lattice obtained from the logarithmic image of local units, divided by \(2p_v\); its native version contains the ring of integers. Four versions distinguish ring-theoretic/abstract and Frobenius/etale constructions. | Section 5.1; TeX 1460–1524. Identifications of versions require the reconstruction and Kummer comparison. |
| Small container | Product of local fields. | Section 5.2, TeX 1538–1540. |
| Large local container | Finite direct sum, indexed by the procession label \(j\), of tensor products of local-field factors. The last factor belongs to \(j,v\); preceding factors include copies at places above the same rational place. | Section 5.2(a), TeX 1542–1556. This is an algebra with many components, not a single unspecified real line. |
| Integral container | Replace local fields by integer rings in the direct-sum decomposition, equivalently take the integral closure after tensoring integral factors. | Section 5.2(c), TeX 1570–1581. |
| Shell container | Replace local fields by log-shell lattices and field tensor products by integral tensor products. | Section 5.2(b), TeX 1562–1567. It need not equal the integral container. |
| Holomorphic hull | The smallest module over the integral container containing the given region. | Section 5.2(d), TeX 1584–1586. Raw measurable volume and hull volume are different. |
| Volume | The survey stipulates procession-normalization: integral container volume one, with the stated effect of multiplication at one rational prime. | Section 5.2(e), TeX 1588–1595. This compressed description does not by itself give all component weights. Ordinary higher-dimensional Haar scaling requires a determinant exponent. |
| LGP action | At a bad place, the \(j\)-component inserts the corresponding root of \(q_v\) to the power \(j^2\) in the final tensor factor. Good components are one. The reconstructed monoid action is by powers of this element. | Section 5.2(f), TeX 1598–1613; Section 6.2, Step 7, TeX 2008–2016. Here the acting \(\mathbb N\) is additive: one acts by LGP, zero by the identity. |
| Possible output | A region of the form LGP times \(U\), where \(U\) is a suitable subset of the shell container, with the rational enlargement shown in the source. | Section 6.2, Step 8, TeX 2019–2024. The word suitable is not replaced there by a complete predicate. |
| Final bound | Transport a family of possible output regions, form their union and its holomorphic hull, then take the normalized determinant and log-volume. | Section 8.1, TeX 2238–2288. The bound concerns this construction, not an independently chosen region with matching raw volume. |

This dictionary is verified as an extraction from the survey. Its equivalence with every required piece of the original IUT definitions remains unverified. In particular, the survey itself states that its BPSs, shells and containers simplify the originals (Section 0.2, TeX 426–428).

## What the indeterminacies say

Section 6, TeX 1696–1704, describes three sources of variation.

- **Ind1:** choices identifying the local Galois group with a quotient of a fundamental group, producing automorphism ambiguity.
- **Ind2:** choices realizing the unit quotient from a unit monoid with its group action and compact structure.
- **Ind3:** the reconstructed shell does not itself reconstruct the native integral container. A family of adelic measurable subsets replaces that integral object.

The last item does not license every independently selected measurable subset. Section 7.3, TeX 2199–2203, links Ind3 to upper semi-compatibility: images under the relevant log/Kummer operations must remain within a common shell. It also uses the entire vertical log sequence. The survey gives neither a complete admissible-set parameter space nor a proof that an arbitrary dilation of one \(S\) stays in that space.

In Section 8.2, TeX 2318–2320, the report explicitly notes that merely having an isomorphism of BPSs supplies too little information and calls for a more precise meaning of link. Therefore the missing compatibility cannot be supplied by the abstract connectedness of that groupoid.

## The eta maps and the unresolved choice

Section 9.2, TeX 2503–2522, describes \(S\) as a region in the shell container used as an integral structure. The reconstructed action gives \(M=1\cdot S=\mathrm{LGP}\,S\). The comparison \(\eta^{\rm anab}_S\) sends the marked source pilot to the output pilot represented by \(M\). The native comparison \(\eta^q\) instead uses the diagonal region formed by the native \(q_v\)-fractional ideals. Equation (9-1) asks for equality of these comparisons for a suitable \(S\).

The target is described by identifying adelic measurable regions with equal volumes. To read this as a real log-volume line, zero/infinite-volume regions and the normalization/linear structure must be handled. The survey's compact description is not a replacement for those type restrictions in a formal statement.

Two linear maps out of the same one-dimensional real line agree if they agree on one fixed nonzero vector. Thus, **after** source/target identifications and admissibility have been justified, equality of the two pilot images suffices. This elementary fact does not construct an admissible \(S\).

## First missing source-dependent lemma

The first unresolved arrow in a definition-level use of this survey is:

> Construct an explicit admissible parameter space, including the Ind1–3 choices and vertical comparisons, whose regions \(S\) map to exactly the relevant original-IUT outputs, and prove that the stated hull bound applies to that same family.

Only after that arrow has been supplied does it make sense to test whether the native pilot lies in its output orbit or in the closure required by the RR5 numerical criterion. The separate orbit-membership assertion remains open in the report (Section 10.5). The missing definition-level bridge here is a limitation of this compressed survey as an input to our proof, not a proof that the original theory has no admissibility conditions.

In particular, \(S\) must not be identified with an original-IUT holomorphic-hull approximant \(H\in\Phi(P)\) without a proved dictionary. Such a hull approximant is chosen after \(P\) is given; changing the initial integral region is a different operation.

## What rescaling can and cannot do

For a fixed local realization, scalar multiplication commuting with LGP scales the raw output and its holomorphic hull by the same scalar. The independent derivation is in `scaling_review.md`. If the output has raw log-volume \(h\) and hull overhead \(\delta\), then any scalar dilation which makes its raw log-volume equal a target \(h_*\) has hull log-volume \(h_*+\delta\). A fixed hull cap \(b\) therefore still requires

\[
h_*+\delta\le b.
\]

Moreover the dilation has to preserve containment in the prescribed shell and its valuation lies in the available local scalar group. Neither property follows from equality of pilot degrees. Whether these rescalings are allowed Ind1–3 transformations is unverified. Equal pilot degree cannot be forced by an unrestricted choice of \(S\) in an argument that still claims to use the source's bounded output family.

Status: source extraction verified; actual IUT admissibility dictionary, admissible orbit membership, and uniform quantitative bridge unverified. No ABC exponent or finiteness conclusion changes.
