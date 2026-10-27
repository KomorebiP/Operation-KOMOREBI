# Fresh self-review of the interrupted Block 50 checkpoint

Date: 2026-09-19. Reviewer: the same assistant performing Block 51.
This is not an independent second-agent or human review and is not a Lean
certificate. The historical checkpoint's incomplete independent-review
status remains unchanged. Its files are preserved byte for byte.

## Restoration and scope

The complete Block 49 bundle and the later Block 50 extension checkpoint
were recovered from the user's Library. Their recorded archive hashes and
all 284 Block 49 payload checksums / 12 Block 50 checkpoint checksums
matched. Block 50's declared base is the recovered Block 49 archive.

The six documented finite computations were executed in an isolated copy.
Every execution exited successfully and reproduced the frozen JSON result.
The commands and actual execution records are in
`verification/predecessor_replay/REPLAY.json`.

This review reads `work50/notes/extension_geometry.md` completely and
checks its algebraic implications against its stated hypotheses. It also
reads the dyadic proof and its inherited audit. It does not re-prove the
full modular and arithmetic chain of Blocks 1--49 or authenticate every
historical external claim afresh.

## Results by section

1. **Alternating duality.** The determinant pairing is alternating and
   nondegenerate. Composing with the trace pairing gives a nondegenerate
   F_7 pairing because the trace on F_49 is nondegenerate. Commutativity
   of scalar multiplication proves self-adjointness. Twisted duality
   preserves, rather than reverses, the indicated extension orientation.
   No missing assumption was found in this algebraic argument.

2. **Principal polarizations along stable RM lattice moves.** A k-line
   is isotropic by self-adjointness and alternation, using 2 invertible.
   Its F_7 dimension is half that of the full torsion space. The source
   Dolgachev--Lehavi, arXiv:0710.1298v3, Corollary 2.2, was inspected in
   the versioned primary paper, including the PDF page. It gives the
   quotient polarization over the algebraic closure. The separate
   uniqueness-under-isogeny and Galois-descent argument is valid for the
   polarization homomorphism; it is not a theta-line-bundle descent claim.
   Iteration stays among principally polarized RM abelian surfaces, not
   necessarily among Frey Jacobians. No extension-realization theorem is
   inferred for an arbitrary Selmer class.

3. **Coupling identity.** Direct multiplication gives the two cocycle
   laws and
   `[alpha] cup [beta] = -delta(a mod 7^n)` with the displayed
   multiplicative coboundary convention. The extra factor chi(g)^(-1)
   is the coefficient action in the cup product. Depth one lifts, so
   cup-zero holds there. Higher depth requires an actual character lift;
   equality of residual characters alone does not supply it.

4. **Counterexample to automatic cup-zero.** The integer matrices,
   integral lattice change, determinant and nilpotence checks replayed.
   The invariant-line argument establishes absolute irreducibility of
   the compact abstract group. The local tame relation and U_3(F_7)
   exponent-seven argument prove nonzero cup. This is not a global Galois
   or geometric counterexample. Block 51 reobtains it at (t,h,n)=(1,1,3)
   and extends it to a sharp family.

5. **Natural Kummer support.** Given the inherited finite-flat condition
   at seven, natural unramifiedness away from three and five, and the
   class-number/unit statements for Q(sqrt(5)), the span of [phi], [3],
   [sqrt(5)] follows by valuations and the unit group. The nonzero
   coefficients at three and five follow from their natural monodromy.
   These inputs remain conditional on their inherited proof boundaries.
   The dyadic polynomial, Hessian and smoothing identities were checked
   again exactly. The geometric passage to thickness and Tate periods
   remains a written proof, not a finite arithmetic certificate.
   The actual relative coefficients have not been computed.

6. **Ray characters.** Exact trial division and power-residue checks
   reproduce the prime 1504231 and the local splitting tests. For every
   n>=2, 1+7^(n-1)t is a character modulo 7^n. Any lift of its indicated
   inertia value has order 49, impossible in the abelian local image
   when v_7(q-1)=1. Thus the higher connecting obstruction is genuinely
   nonzero. Its toric pseudotrace calculation is valid modulo 7^n.
   None of this realizes the pair of characters inside the actual Frey
   representation. Block 51 supplies a new necessary monodromy cost for
   such a realization.

## Findings and remaining review boundary

No mathematical error was found in the directly checked arguments under
these explicit hypotheses. No independent-review acceptance is created.
The old interruption was an availability/usage-limit error, recorded in
`work50/verification/extgeo_checkpoint.json`; it was not a counterexample
or a failed arithmetic test. This continuation supplies fresh self-review
and reproducible evidence without rewriting that historical event.

The elementary local theorem of Block 51 does not depend on the quotient
polarization theorem or on the natural Kummer-support assertion. Its
arithmetic support corollary does depend on the inherited representation,
local splitting and class-group inputs listed in ARITHMETIC_SUPPORT.md.
The optional ray-character/Kummer corollaries additionally use the
coupling identity and stated natural Kummer support.
