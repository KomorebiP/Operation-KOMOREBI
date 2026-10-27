# Polyphase atlas: author review

Status: PASS for all 16 formulas, worked examples, generated figures, and declared finite coefficient checks. Final master-PDF layout inspection is a separate integration step.

Owned source: `chapters_polyphase.tex`, `figures_polyphase.py`. Generated plates: `figures/P01_*.pdf` through `figures/P16_*.pdf`, with paired PNGs. Exact run data, three execution-input hashes, and 32 output hashes are in `polyphase_checks.json`.

## Computational contract

The generator uses Python integers and `fractions.Fraction` for identities. Algebraic cube-root cancellation is represented exactly in Q[zeta]/(zeta²+zeta+1). Haar amplitudes are represented as rational multiples of sqrt(2); their inverse and energy are checked without floating point. Matplotlib and NumPy supply rendering coordinates, including the positions of complex roots and real Haar amplitudes.

The successful command was `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_polyphase.py`, from the guide root. It generated 16 vector PDF plates and 16 PNG previews in approximately eight seconds. The JSON records actual Python, NumPy, and Matplotlib versions, command argv, start time, run duration, conventions, bounds, and cooperative thread caps. No hard CPU or memory cap was needed for these deterministic bounded checks. No random sampling is used.

The embedded computation manifest was validated with the computation-audit skill's `validate_manifest.validate`, including all 32 output hashes. All three recorded input hashes were also checked explicitly. The manifest is version 1, so its stated legacy provenance limitations remain. The scratch workspace has no recorded git revision; source-file hashes identify this run.

## Uniform mathematical reductions

These derivations justify the uniform identities independently of the finite checks.

1. **Split and synthesize (P01–P02).** Every nonnegative integer has a unique representation n=Mm+r with m≥0 and 0≤r<M for a positive integer M. The term a_n z^n occurs exactly once in sum_r z^r sum_m a_(Mm+r)(z^M)^m. The identities therefore hold in a formal power-series ring over any coefficient ring.

2. **Fibonacci jump law (P03–P04).** With the column state v_n=(F_n,F_(n+1))^T, v_(n+1)=T v_n for T=[[0,1],[1,1]]. Put A=T^M. Its determinant is (-1)^M, and tr(T^M) satisfies the Lucas recurrence with initial traces 2 and 1, so tr(T^M)=L_M. Cayley–Hamilton gives A²-L_M A+(-1)^M I=0. Applying it to v_(Mm+r) proves g_(m+2)=L_M g_(m+1)-(-1)^M g_m for every nonnegative starting offset r. A residue-channel representative additionally satisfies r<M. For M=2, the initial pairs (E_0,E_1)=(0,1) and (O_0,O_1)=(1,2) give numerator u and 1-u over denominator 1-3u+u².

3. **Phase selector (P05).** Over a characteristic-zero field containing a primitive Mth root zeta, the coefficient multiplier is M^(-1) sum_j zeta^(j(n-r)). It is one if M divides n-r and zero otherwise, by the finite geometric-series identity. The complex presentation is one valid coefficient extension. The address-splitting identity itself does not require roots of unity. No square root or complex phase is imported into an undeclared coefficient field.

4. **Refinement and route agreement (P06–P07).** Write the parent index m=Lj+ell. Then Mm+r=LMj+(r+Mell), yielding the stated powers u^ell and child address r+Mell. Both displayed 2×3 and 3×2 routes reconstruct the same n and hence produce final residue n mod 6 and internal index floor(n/6). Intermediate labels may differ.

5. **Carry matrix (P08).** On packet basis e_r, C_M e_r=e_(r+1) for r<M-1 and C_M e_(M-1)=u e_0. Each basis state wraps exactly once in M steps, proving C_M^M=uI. Synthesis sends the action to multiplication by z. The finite example includes every new boundary coefficient.

6. **Product carry law (P09).** A product term has exponent M(i+j)+(r+s). Euclidean division of r+s gives output residue (r+s) mod M and the additional block factor u^floor((r+s)/M). Summing all pairs proves the displayed formula over a commutative coefficient ring. The figure includes every cross term, rather than only same-residue products.

7. **EGF routing (P10).** Apply the ordinary routing identity to the normalized coefficient b_n=a_n/n! over a characteristic-zero field. The factorial is tied to original n=Mm+r, not to internal m. The routed series in u is not silently declared an EGF in u.

8. **Secant/tangent parity (P11).** Formal cosine is even with constant coefficient one, so its formal reciprocal is even. Formal sine is odd, so sine/cosine is odd. The up/down EGF sec(z)+tan(z) therefore splits into the indicated even and odd normalized coefficient streams. The positive integer count dictionary and the tangent offset-one reindexing follow the authenticated OEIS records for A000111, A000364, and A000182. Integer stream splitting and factorial-weighted EGF routing are explicitly distinguished.

9. **Binary refinement (P12–P13).** Appending a binary zero preserves the digit sum; appending a one increases it by one. Reduction modulo two gives copying/complementing for Thue–Morse. Summing the even and odd recurrences in the formal series produces the denominators 1-z² and the explicit affine constant terms. The odd integer-weight update is linear only after adjoining the constant coordinate one.

10. **Haar bank (P14).** The real matrix H=2^(-1/2)[[1,1],[1,-1]] satisfies H^T H=I and H²=I. It preserves pair energy and recovers both original amplitudes. The two filter channels are normalized amplitudes, not ordinary arithmetic means or sequence-recurrence coefficients.

11. **Discarding a channel (P15).** B-A=7z-11z³ is a nonzero polynomial in the kernel of the even-channel projection. The two explicitly distinct inputs with identical retained outputs prove noninjectivity. This is a finite counterexample with a universal implication, not a statistical estimate.

12. **Operation square (P16).** For P=E(z²)+zO(z²), multiplication by 1+z gives even packet E+uO and odd packet E+O. This proves the channel matrix [[1,u],[1,1]]. Synthesis returns the full scalar result, including terms introduced beyond the finite input boundary.

## Finite implementation checks

| Plates | Exact surrogate and tested range |
|---|---|
| P01–P02 | Full split/synthesis equality for Fibonacci prefixes through indices 17 and 11 |
| P03 | 30 block states and 30 coefficients in each rational channel |
| P04 | 550 recurrence instances: strides 1–10, all canonical residues, internal m=0–9 |
| P05 | 36 selectors: three residues and original exponents 0–11 in the exact cyclotomic ring |
| P06–P07 | Both parent reconstructions and both refinement routes for original indices 0–17 |
| P08 | Four complete packet states, zero through three carries, preserving full support |
| P09 | The nine-term product example, plus 40 additional exact products for moduli 2–6 and input lengths 1–8 |
| P10 | Exact rational EGF split/synthesis for 14 Fibonacci values, including the 6! versus 3! counterexample |
| P11 | Independent rational division of sine/cosine through original exponent 11, parity checks and count comparison |
| P12–P13 | Both binary recurrences for n=0–255; 256 generating-identity coefficients for Thue–Morse; integer-weight parity equality |
| P14 | Exact algebraic inverse and energy 10+4=14 on the stated four amplitudes |
| P15 | Exact two-input projection collision and nonzero odd-channel difference |
| P16 | Full seven-coefficient worked result and 40 additional input lengths, retaining complete output support |

No finite prefix is presented as proof of a uniform recurrence or formal-series identity. No convergence theorem, asymptotic estimate, OEIS novelty claim, or recovery guarantee is inferred from these tests.

## Visual inspection

All 16 generated PNG plates were inspected on four contact sheets, covering every coefficient, channel label, formula, and diagram. P09 was additionally reopened at native resolution after spacing its left row labels away from the box edge. P08's label was corrected to the singular “1 carry.” The initial contact-sheet review missed one P05 label overlap: final assembled-page QA found that the superscript in the lower cube-root label touched the blue root marker. Its label was moved left/down and vertically centered; the regenerated P05 figure was then reopened at native resolution and has clear spacing. All exact checks passed again. The repaired master-PDF page still requires its integration-level render check.

Each plate has one central exact figure. Colors preserve channel identities. Original indices and internal indices remain visibly distinct. No AI-generated assets are used.

The final P05 repair changes exactly one rendering statement. Reversing that statement recovers the independently audited generator hash `d068a24b8eec15a3a06e337dec88405c0ee8e5a49377391c4452687b01d8344a`. The repaired generator hash is `47a22c42b89d907faddf03edd0e2de3b508400436445099fc2256eb04415baf0`. Chapter prose and all mathematics are unchanged. The before/after figure hashes and exact one-line bridge are recorded in `polyphase_checks.json`.

## Final mathematical proofreading

Scope: all 16 newly authored lessons, all 16 generator sections, and these review notes. The formulas and examples use matching variables, offsets, normalizations, and column-state orientation. There are exactly 16 lesson calls and one volume declaration. No unresolved mathematical or LaTeX-token issue remains at author review.

The independent mathematical reviewer identified one boundary ambiguity: P04's table includes M=1 at offset one, which is not a canonical residue representative. The caption now calls it a starting offset, allows general nonnegative offsets for the jump formula, and separately states the canonical channel range. The recurrence and every numeric table entry are unchanged. The generic complex selector explicitly fixes a positive integer modulus and a valid residue.
