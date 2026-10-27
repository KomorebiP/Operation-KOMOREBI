# Primary-source check for Block 51

Checked 2026-09-19. This is theorem/application verification for a bounded
set of dependencies, not a literature-wide novelty search. The same
assistant carried out source inspection and application review. Search
snippets were not used as proof. Versioned primary PDFs were opened and
the relevant pages were also inspected as screenshots.

## Dolgachev--Lehavi

I. Dolgachev and D. Lehavi, *On isogenous principally polarized abelian
surfaces*, arXiv:0710.1298v3, 8 March 2008, Corollary 2.2, printed p.3.
Source: https://arxiv.org/pdf/0710.1298v3

A maximal isotropic subgroup of A[n], with n prime to the characteristic,
gives a principally polarized quotient with the stated pullback. The
source works over an algebraically closed field. Block 50 separately
proves descent of the polarization homomorphism by uniqueness and
Galois invariance. Apply n=7, characteristic zero. Do not infer descent
of a particular theta line bundle or membership in the Frey family.
The recovered PDF's SHA256 is
0dcfa76fdac989d5ede8025a7251ebf96a77a3d4c02b20b932dc6b51f716fd1e.
The original user checkpoint already included this copy and its text.

## Baker--Rabinoff

M. Baker and J. Rabinoff, *The skeleton of the Jacobian, the Jacobian of
the skeleton, and lifting meromorphic functions from tropical to
algebraic curves*, arXiv:1308.3864v1, 18 August 2013.
Source: https://arxiv.org/pdf/1308.3864v1
Theorem 2.9 (printed p.5) identifies the metric/edge pairing with the
analytic pairing; Remark 6.7 (printed p.16) treats the totally degenerate
period-matrix formulation used here.

Application: the two split ordinary self-nodes, each of thickness 7c,
give a two-loop graph with edge pairing 7c I_2. The source then identifies
the valuation pairing for the natural Jacobian. The tame Kummer step,
RM integral-content comparison, and change to the opposite lattice are
separate arguments in ARITHMETIC_SUPPORT.md, not supplied by citing the
source title. This source does not bound the global lattice depth.
No newly downloaded copy is bundled; the source was inspected online.

## Masley

J. M. Masley, *Solution of small class number problems for cyclotomic
fields*, Compositio Mathematica 33 (1976), 179--186.
Source: https://www.numdam.org/article/CM_1976__33_2_179_0.pdf
The Main Theorem on printed p.179, including the table and the concluding
phi(m)<=24 clause, gives h(Q(zeta_35))=1. The norm/extension-of-ideals
principle is also discussed on printed p.180.

Application: L=Q(sqrt(5),zeta_7) has index two in Q(zeta_35). Extension
followed by norm is multiplication by two on Cl(L), so Cl(L)[7]=0.
Together with the explicit old local restrictions and restriction of the
opposite class to L, this forces some eligible ramification. It does not
exclude a class once eligible support is present.
No newly downloaded copy is bundled; the source was inspected online.

## Stacks Project

Section 53.19, Nodal curves, tag 0C46, especially Lemma 53.19.3.
Source: https://stacks.math.columbia.edu/tag/0C46
Accessed 2026-09-19. The ordinary-node criterion is over a residue field.
It is consistent with the local polynomial audit, including characteristic
two. It is not cited as a ready-made relative mixed-characteristic
thickness theorem; the inherited dyadic argument supplies that additional
step. The new variable-prime proof excludes residue characteristics 2,3,5.

## Search and claim boundary

These exact primary results and their hypotheses were checked. No claim
that the local matrix theorem or its application is new to the literature
is made. No attempt was made here to reconstruct all citations underlying
Blocks 1--49. Those dependencies and limitations are retained, not silently
promoted into newly verified arithmetic theorems.
