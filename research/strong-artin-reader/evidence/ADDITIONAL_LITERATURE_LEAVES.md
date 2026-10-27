# Additional checked literature leaves

Checked 8 October 2026. Bounded task: authenticate and extract the inherited Scholze torsion and Goldring–Shin holomorphic-limit inputs. The dependent manuscript claims are `fact:scholze_torsion`, `cor:scholze_attachment`, `fact:goldring_shin`, and `cor:goldring_shin_artin`. This is theorem-level source verification, not a full proof audit, current literature survey, or novelty claim.

## Scholze: residual eigensystems actually occurring in cohomology

Peter Scholze, *On torsion in the cohomology of locally symmetric varieties*, Annals of Mathematics (2) 182(3) (2015), 945–1066, DOI [10.4007/annals.2015.182.3.3](https://doi.org/10.4007/annals.2015.182.3.3). Checked publisher PDF, 122 pages; [primary PDF](https://annals.math.princeton.edu/wp-content/uploads/annals-v182-n3-p03-p.pdf).

Theorem 5.4.1 (p. 1058), Corollary 5.4.3 (p. 1060), and §5.4 setup (p. 1057) were read. Parameters: totally real/CM F; n≥1; rational p; conjugation-stable finite S containing p-places and F/F⁺ ramification; K⊂∏GL_n(O_Fv), arbitrary compact at S and full hyperspecial outside; algebraic ξ of Res_OF/Z GL_n on a finite free Z_p-module. Non-small levels use stack cohomology. A character ψ of the away-S Hecke algebra must occur in H^i(X_K,M_ξ,K⊗F̄_p). Corollary 5.4.3 gives a continuous semisimple residual representation, unique up to isomorphism, with

\[
\det(1-X\sigma_\psi(\operatorname{Frob}_v))
=\psi(P_v(X)),\qquad
P_v(X)=\sum_{j=0}^{n}(-1)^j q_v^{j(n+1)/2}T_{j,v}X^j,
\]

where T_0,v=1 and T_j,v is the elementary symmetric Satake function. Theorem 5.4.1 instead gives a continuous determinant over the cohomological Hecke image modulo I, with I^N=0 and N depending only on [F:Q],n.

**Version boundary:** Remark 5.4.6 (p. 1061) records Arthur/Mok stabilization dependencies for the general field range; it explicitly supplies an unconditional subrange: CM F containing an imaginary quadratic field, and S pulled back from rational primes including p and all F/Q ramification. Later resolution of those historical dependencies was outside this check.

**Project translation:** ψ(P_v) must be explicitly identified with the reduction of the project's chosen Q_v, including its Tate/Satake normalization. At a separating λ above p, occurrence and the remaining one-prime attachment assumptions remain premises. A field-valued specialization kills I. Neither arbitrary descent occurrence nor a determinant over the entire Hecke algebra without nilpotent quotient follows.

## Goldring, with appendix by Shin: a specified unitary holomorphic range

Wushi Goldring, with appendix by Sug Woo Shin, *Galois representations associated to holomorphic limits of discrete series*, Compositio Mathematica 150(2) (2014), 191–228, DOI [10.1112/S0010437X13007355](https://doi.org/10.1112/S0010437X13007355). Published PDF obtained from [Goldring's publications page](https://sites.google.com/site/wushijig/home/publications), link `galois_hlds.pdf` resolving to [author-hosted copy](https://drive.google.com/file/d/1udGKZ-lfKAvOP1BwbTLw-ZQzXunLRu51/view). 39 PDF pages include a cover. Publisher metadata lists both names; printed main article attributes Goldring and identifies Shin's appendix.

Theorem 1.2.1 (p. 194), §§2.3,3.1,3.3, and proof pp. 218–219 were read. U is a unitary Kottwitz datum with simple Q-algebra B, CM center F and totally real F⁺; G(U) is its PEL unitary similitude group; n²=dim_F End_B(V). π is cuspidal and π∞ is X-holomorphic limit of discrete series: compact-root regular, noncompact-root singular Harish–Chandra parameter in the prescribed chamber. Fix ι:Q̄_ℓ≅C. Prime ℓ admits the integral Kottwitz datum of §3.3, and reflex field E has a degree-one λ|ℓ. No ordinarity assumption on π_ℓ is stated.

Output: a semisimple ℓ-adic G_F-representation. It is unramified above rational p≠ℓ where π_p and G are unramified. For primes v of F split over F⁺ above such p,

\[
R_{\ell,\iota}(\pi)|_{W_{F_v}}^{ss}
\simeq\iota^{-1}\operatorname{rec}
\bigl(\pi_v\otimes|\cdot|^{(1-n)/2}\bigr).
\]

The proof uses a density-one set of these split primes. Good reduction requires unramified split matrix factors for B(Q_ℓ), a maximal completed order and a stable self-dual lattice. The proof chooses K=K_ℓK^ℓ with K_ℓ⊂G(Z_ℓ) and π^K≠0.

**Project translation:** the theorem concerns G(U), not arbitrary GL_n forms. Its finite-Satake corollary must retain an explicit matching finite alphabet for the displayed normalized split-prime parameters; density one makes those Frobenius constraints dense. Finite image then comes from the project's separate rigidity argument. The source does not itself conclude finite image, universal all-place matching, or existence of a whole family carrying a determinant through every singular point.

## Authentication and failures

Both primary PDFs downloaded successfully and extracted with `pdftotext -layout`; the theorem pages were also visually inspected to resolve overbars and local notation. The publisher's Goldring landing page presents an access option, so the openly linked primary author copy was used. Exact DOI cache lookups returned no helper-managed cache. Parent's prior cache ingest failed Git-ignore validation; no new cache initialization or successful ingest is claimed. Retained PDFs/text are private local verification inputs and must be omitted from the distributed ZIP; redistribute this paraphrased report and hashes instead.

Source identities, extraction hashes, locator provenance, and retention limits are in `ADDITIONAL_LITERATURE_LEAVES.json`. No full source proof was audited. Classification: both are known external realization results in their extracted ranges; applications to arbitrary finite-Satake descents remain conditional on occurrence and matching hypotheses.
