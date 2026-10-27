# Block48: the full smallest Hilbert level reduces to one named form

Status: exact finite checks on imported primary database data; conditional modular consequences. At level `(45)=3²(sqrt(5))²`, all fourteen LMFDB Galois orbits have now been checked. Thirteen are excluded under the direct normalized residual comparison. The only possible orbit is **2.2.5.1-2025.1-l**, and it requires **C odd, A odd, 418|B, and (A,C)≡(5,9) or (6,2) mod 11**. This does not eliminate that final form, address every other level, or prove Diophantine nonexistence. No PV numerical-index dictionary is used for this full-level result.

## 1. Data obtained, rather than inferred from indices

The complete LMFDB search at base field `2.2.5.1`, level norm 2025 returns 14 Galois orbits, all at the ideal `(45)=3^2(sqrt(5))^2`. Exactly five rows display a CM flag: `2.2.5.1-2025.1-c,d,e,h,l`. All fourteen individual form pages were read and retained. The five flagged forms are displayed first below because they initiated the refinement; §6 gives the complete fourteen-orbit calculation. The [LMFDB reliability statement](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/Reliability) says its eigenform data is computed rigorously, while a positive CM flag is strong evidence rather than a proof. Our named-form exclusions use the actual Hecke eigenvalues and do not require CM status. Their first twenty Hecke values include both primes above eleven and nineteen, and the prime of norm four. These are exact displayed eigenvalues, not reconstructions from PV's list of survivor indices.

Let `f_c`, etc., denote those canonical LMFDB forms, and let `e` denote the generator used on each individual page. The relevant data are:

| Form suffix | Coefficient field | a_(2), norm 4 | Traces above 11 | Traces above 19 |
|---|---|---:|---|---|
| c | Q | 4 | 0, 0 | 1, 1 |
| d | Q | -4 | 0, 0 | -1, -1 |
| e | Q | 1 | 0, 0 | 4, 4 |
| h | Q[e]/(e²+9e+19) | 0 | -e-9, e | 0, 0 |
| l | Q[e]/(e²-9e+19) | 0 | -e+9, e | 0, 0 |

Both quadratic coefficient fields are isomorphic to Q(sqrt(5)), because their defining polynomials have discriminant 5. Seven is inert in them; in particular there is one coefficient-field prime above seven, and two residue embeddings related by Frobenius. The comparisons below use rational eigenvalues or the norm of a quadratic trace polynomial, so do not depend on choosing between those embeddings.

Primary pages: [search at norm 2025](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/?field_label=2.2.5.1&level_norm=2025&count=100), [c](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-c), [d](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-d), [e](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-e), [h](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-h), [l](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-l). Checked 2026-09-19, LMFDB release displayed as 1.2.1. These mutable pages are pinned here by the SHA256 values in `verification/candidate_local_checks.json` and the retrieval manifest.

## 2. Definite local exclusion of c, d, e, conditional on the modular comparison

Assume a primitive solution A³+B⁵=C⁷ with C odd, and assume the rank-two residual representation of

    J_AB = Jac(Z² = X⁶+10BX³+12AX+5B²)

is **directly, with the same normalization**, congruent modulo seven to the weight-two, trivial-nebentypus representation of one of the named forms. Its determinant at the K-prime `(2)` is then 4 modulo seven. This is the comparison hypothesis used below; no unspecified Tate or quadratic twist is inserted.

Block46's written proof establishes good reduction at two and gives the following full four-dimensional Frobenius polynomials at the K-prime of norm four:

| A,B parity | Full polynomial |
|---|---|
| A even, B odd | (T²+T+4)² |
| A odd, B even | (T²+4)² |

Every eigenvalue of the rank-two representation must be a root of the corresponding quadratic. A modular form with trace `a` has polynomial `R_a=T²-aT+4`. Exact polynomial resultants are

    Res(T²+T+4, R_a) = 4(a+1)²,
    Res(T²+4, R_a) = 4a².

Thus its trace must be -1 or 0 modulo seven, respectively. The values 4, -4, and 1 are neither -1 nor 0 modulo seven. This excludes the named forms **c, d, e** for odd C, regardless of the chosen prime or embedding of a coefficient field. Equivalently, the four-dimensional polynomial `(T²-aT+4)²` fails the exact comparison in each case; the certificate checks this equality directly.

For h and l the trace is zero, so only A odd, B even can survive at two. This is a new candidate-specific restriction obtained from actual eigenvalues.

## 3. Even C: all five named forms fail at two

Block47's `notes/evenC_torus_frobenius.md` establishes the full four-dimensional Frobenius polynomial `(T+1)²(T+4)²` at the K-prime of norm four when C is even, using the integral semistable filtration and the nonsplit nodes over F4. Every residual subquotient eigenvalue is therefore either -1 or -4 modulo seven. For each of the five forms, `R_a=T²-aT+4` evaluates nontrivially at both elements:

| Form | a | R_a(-1) mod 7 | R_a(-4) mod 7 |
|---|---:|---:|---:|
| c | 4 | 2 | 1 |
| d | -4 | 1 | 4 |
| e | 1 | 6 | 3 |
| h,l | 0 | 5 | 6 |

Thus **all five named forms are excluded when C is even**, subject to the same direct modular comparison. This is a coprimality argument on full-polynomial eigenvalues; it does not assume a separate trace normalization of the RM factor. Combined with §2, c,d,e are excluded for either parity of C.

## 4. Eleven distinguishes h from l and excludes h

The characteristic-seven reductions of both quadratic coefficient polynomials are irreducible: their discriminant is 5, a nonsquare modulo 7. A fixed residual comparison over F49 gives, on underlying F7 vector spaces, the norm of the rank-two characteristic polynomial. At either base prime above eleven this is

    h: T⁴+9T³+41T²+99T+121,
    l: T⁴-9T³+41T²-99T+121.

These expressions are independent of the choice between the two coefficient-field embeddings. Because eleven splits in K, the full rational Frobenius polynomial of J_AB at eleven is also its full polynomial at either K-prime above eleven.

The complete Block47 table has 110 smooth pairs (A,B) mod 11. Comparing the full polynomials modulo 7 gives **zero pairs for h**, and exactly **(5,0),(6,0) for l**. A new independent enumeration by the candidate auditor, using F121=F11[u]/(u²-2), recomputed all 110 pairs and reproduced the result.

If 11|C, the multiplicative-prime comparison requires modular trace ±12 modulo 7. Those values lie in F7, whereas the roots of either candidate trace polynomial do not. Equivalently direct substitution of ±12 in X²±9X+19 is nonzero mod 7. Thus the bad-reduction branch is impossible for both candidates.

It follows that **h is excluded for either parity of C**. For l,

    11|B and A≡5 or 6 mod 11.

The equation further pairs these residues as (A,C)≡(5,9) or (6,2) mod 11. This is an actual candidate distinction not present in an unlabelled boundary comparison that squares the trace: h and l have opposite traces at eleven, and their squares coincide up to the fixed coefficient-field isomorphism. We have not supplied a numerical-index match proving which of PV's 9,12 corresponds to h.

## 5. Combining with the exact nineteen calculation

The forms h and l have trace zero at both primes above nineteen. Block47's exact enumeration of the Beal curve, independently replayed there, proves that a good-reduction trace-zero match at nineteen forces B=0 mod 19. If 19 divides C, the standard multiplicative-prime comparison gives trace ±20, nonzero mod 7, so that branch cannot match trace zero.

Consequently a direct residual congruence to **l**, after the exclusions above, implies

    C odd, A odd, 418 divides B, (A,C)≡(5,9) or (6,2) mod 11.

No contradiction follows from these divisibility conditions alone. The independent all-fourteen-orbit refinement in §6 is what makes l exhaustive at this level. It does not rely on PV's printed elimination exceptions: the PV transcript includes auxiliary prime seven, and using those generic bounds at residual characteristic seven would require checking that auxiliary separately or omitting it in a rerun. For completeness, the same imported local table shows that c and d would require 19|C, while e has no possible branch at nineteen: e has trace 4, the good-reduction match set is empty, and ±20 is ±1 modulo 7. The e exclusion at nineteen therefore applies even without the odd-C condition, under the same local modular comparison hypotheses.

## 6. Complete fourteen-orbit refinement

The complete search and all fourteen individual form pages are retained; no absent numerical-index dictionary or positive CM flag is used in the following exclusions. The base field has narrow class number one (class number one and a unit of norm -1), so the database's character convention supplies the intended trivial-character space. The [LMFDB completeness statement](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/Completeness) and quadratic browse bound cover norm 2025.

All fourteen eigenvalues at the prime `(2)` of norm four are rational. Thus the comparison at two has no coefficient-field or residue-embedding ambiguity:

| Form suffix | a_(2) | Odd C passes at two? | Even C passes at two? | Further decisive test |
|---|---:|---|---|---|
| a | 0 | yes | no | excluded at 19 |
| b | 3 | no | no | — |
| c | 4 | no | no | — |
| d | -4 | no | no | — |
| e | 1 | no | no | — |
| f | 0 | yes | no | excluded at 29 |
| g | -2 | no | no | — |
| h | 0 | yes | no | excluded at 11 |
| i | 3 | no | no | — |
| j | -2 | no | no | — |
| k | -3 | no | no | — |
| l | 0 | yes | no | retains the conditions above |
| m | -2 | no | no | — |
| n | 2 | no | yes | excluded by both-prime correlation at 11 |

For odd C, the allowed traces are -1 and 0 modulo seven, as proved above. For even C, the eigenvalues are chosen from {-1,-4}; determinant 4 forces the distinct pair, since the repeated products 1 and 16 are not 4 modulo 7. Thus the only possible trace is -5≡2 mod 7. These tests leave a,f,h,l in the odd-C branch, and n in the even-C branch.

**Form a at nineteen.** Both displayed Hecke traces are -5. Its underlying four-dimensional polynomial would be `(T²+5T+19)²`. None of the 342 smooth Beal residue pairs gives this polynomial modulo 7. If 19|C, the necessary traces ±20 are also different from -5 modulo 7. Thus a is excluded. The point-count comparison was independently replayed on all 342 pairs.

**Form f at twenty-nine.** Both traces are 10. Exactly 812 pairs (A,B) mod 29 satisfy A³+B⁵≠0. The isomorphisms `(A,B) -> (u⁵A,u³B)`, induced by `X -> uX, Z -> u³Z`, divide them into 29 explicitly retained orbits. Exact point counts over F29 and F841 give no match with `(T²-10T+29)²` modulo 7. If 29|C, the necessary traces ±30 differ from 10 modulo 7. This excludes f. A fresh auditor separately counted all 812 smooth pairs rather than only orbit representatives and confirmed zero matches.

**Form n and a fixed embedding at eleven.** Its coefficient field is `Q(e)`, e²=18, and its two Hecke values above eleven are **-e,e in that same field**. Modulo seven, e maps to 2 or 5; both primes of the maximal order over seven are unramified, since the field discriminant is 8. Fix one prime and one embedding throughout the comparison. The values -e and e then lie in F7 and are distinct. A rank-two F49 comparison forces the underlying full polynomials at the two K-primes above eleven to be

    (T²+eT+11)² and (T²-eT+11)².

Their T³ coefficients are 2e and -2e, which differ modulo 7. But J_AB is defined over Q, so its full four-dimensional Frobenius polynomials at the two split K-primes agree. This remains valid if J is ramified at eleven: choose conjugate Frobenius lifts in G_Q; the full Jacobian representation gives equal characteristic polynomials, and the modular representation is unramified there, so its polynomial does not depend on the lift. Therefore n is excluded. Allowing a different coefficient embedding at each prime would erase this contradiction; the argument explicitly keeps one embedding.

Together with the h exclusion from §4, these calculations leave only l in the entire level `(45)`. In particular no candidate in this level can match the even-C branch. The surviving l conditions do not yet give a contradiction.

## 7. Relation to PV indices and the source ambiguity

The pinned repository is `lucasvillagra/GFE-5p3` at commit `e88f914c577ab6cf9a45e5cdd82c1993477fb423`. Its complete recursive tree was read: no additional indexed eigenvalue export is hidden among the other outputs. The code remains an unlabelled polynomial/norm relaxation, as audited in Block47.

[PV arXiv:2512.17845v1, proof of Theorem A, §7.4](https://arxiv.org/html/2512.17845v1#S7.SS4) identifies smallest-level index 3 as CM by Q(sqrt(-3)), and explicitly gives zero trace at the primes above eleven. Thus the Block47 restriction 11|A attaches to that numerical candidate on the source's own statement. The same passage describes indices 9,12 using Q(zeta15)/K, a degree-four extension rather than a quadratic CM inducing field. We do not silently replace that phrase by Q(zeta5)/K.

The database displays five CM-flagged orbits and exact trace data compatible with identifying the degree-two orbits h,l as the cyclotomic-CM pair, but an exact PV↔LMFDB index dictionary has not been certified. In particular this note does **not** relabel the c,d,e exclusions as a certified exclusion of PV index 3. Such a relabelling would need a verified complete match of the level/character/CM(-3) sublist or a direct Hecke fingerprint from PV's indexed decomposition. The canonical-form local exclusions do not require that additional identification.

There is also a source-level ambiguity at higher levels: the printed seven-element CM categories in the proof have field/specialization assignments inconsistent with conductor parity and with its own Lemmas 4.4–4.5. A separate self-contained classification below is useful for checking these assignments; it is not a numerical-index repair.

## 8. Quadratic CM-field classification and conductor parity

Suppose f is a CM form of parallel weight two and trivial nebentypus, whose level is supported on 3 and p5=(sqrt5). Its quadratic inducing field L/K is unramified outside the level, since the induced-character conductor contains the relative discriminant. Choose a compatible-system characteristic distinct from a place under consideration.

The standard conductor-discriminant formula for induction and the fundamental-unit description of Q(sqrt5) are arithmetic inputs to this written argument. The Minkowski bound sqrt5/2<2 gives class number one for K. Its unit group is generated by -1 and phi=(1+sqrt5)/2. Removing even valuations by a square leaves S-squareclass representatives `(-1)^a phi^b 3^c (sqrt5)^d`, with exponents zero or one. Total negativity requires a=1 and b=d. Thus the only possible negative classes are

    -1, -3, D5=-phi*sqrt5=-(phi+2), 3D5.

At the unique dyadic completion K2, an unramified quadratic extension of Q2, -3 is a square: x0=1+2phi satisfies x0²+3=8(phi+1), and v2(x0²+3)=3>2v2(2x0)=2, so Hensel's lemma applies. The element D5 is the discriminant of `X²-(phi-1)X+1`; its reduction has no root in F4, so it gives the unramified quadratic extension of K2. The class -1 ramifies, since Q2(i)/Q2 is ramified and unramified base change preserves that ramification. The class 3D5 equals -D5 locally up to the square -3, and its character is the product of the ramified character of -1 and the unramified character of D5, so it also ramifies. Therefore only

    L3=K(sqrt(-3)), L5=K(sqrt(D5))=Q(zeta5)

remain. The last equality follows from zeta5+zeta5^(-1)=phi-1.

At a finite place unramified in L/K, the conductor exponent of a two-dimensional induced character with unramified determinant is even. For an inert place it is twice the character conductor; at a split place the two local characters have inverse inertia restrictions, hence equal conductor exponents. Therefore:

| Level | Possible quadratic CM field |
|---|---|
| 3² p5² | L3 or L5 |
| 3² p5³ | L5 only |
| 3³ p5² | L3 only |
| 3³ p5³ | no CM form under these hypotheses |

At primes above eleven, L3/K is inert and L5/K splits. At primes above nineteen, L3/K splits and L5/K is inert. Thus the respective category-level restrictions are 11|A for L3 and 19|B for L5. The categorical proof avoids changing a printed field assignment by guesswork. This written argument received an independent read-only proof audit in this block; it is not being inferred solely from a bounded finite calculation.

## 9. Reproduction and retrieval limits

Run `python3 work48/computations/candidate_local_checks.py` and `python3 work48/computations/candidate_complete_level.py`. The first script parses the complete search and the five initially retrieved form pages, compares h,l at eleven, and checks the nineteen and two restrictions. The second parses all fourteen form pages and checks every norm-four trace, the full q29 orbit partition, the a/f exclusions, and both possible fixed embeddings in the n correlation. Both import the previously certified q11/q19 point-count tables. Neither evaluates downloaded code or calls Sage/Magma.

LMFDB's [quadratic browse page](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/browse/2/) gives maximum level norm 4999 for K. Norm 2025 is within that range; the other levels have norms 10125, 18225, 91125 and lie outside this stated range. This is a reason that the smallest-level database retrieval is productive, not proof that no isolated higher-level data exists.

The public web tool could read overview/browse pages but not targeted URLs. Ordinary public HTTP reads fetched the search and all fourteen form pages successfully, the final nine in a sequential second pass. Subsequent exact Sage export requests returned genuine exports only for b,d, and a CAPTCHA page for the others. Those failures are recorded; they are not form data, and no CAPTCHA bypass was attempted. No fresh Hilbert modular form space or eigenvalue calculation was run.

An unexecuted Magma program, `computations/candidate_export.m`, uses the documented primary APIs to recompute each of the four spaces, pre-filter with auxiliary seven removed, and print exact field/integral-basis/prime/trace/residue records with the same map throughout each form. It has not received Magma syntax or runtime validation; it is not evidence that those computations completed. Its fresh indices are explicitly not identified with historical PV indices.

Remaining useful exports are: all p=7 survivors at the two p5-exponent-three levels; exact field models and integral bases; fixed coefficient primes above seven; both base-prime eigenvalues at split auxiliaries; and an indexed-decomposition fingerprint sufficient to match PV ordering. For all fourteen smallest-level forms, the retained short Hecke data already supports the stated local conclusions without waiting for those exports.

## 10. Independent review boundary

The candidate audit independently recomputed the complete q11 table with distinct finite-field arithmetic and confirmed h exclusion and the l residue restriction. The separate `notes/bad7_candidate_q2_audit.md` verifies the norm-four exclusions for both C parities. Both audits retain the explicit direct modular-comparison hypothesis and make no indexed-form or global nonexistence claim.

The independent complete-level audit additionally recounts every smooth pair at nineteen and twenty-nine and checks all fourteen imported norm-four eigenvalues. Its executable code and receipts are retained in the candidate audit files.

## 11. Targeted lookup at proposed twisted level of norm 45

A final ordinary [LMFDB search at level norm 45](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/?field_label=2.2.5.1&level_norm=45&count=100) gives a unique match, `2.2.5.1-45.1-a`, weight (2,2), dimension 1, at ideal `[45,15,-6w+3]=(3sqrt5)`. Thus this proposed twisted level is nonempty. No empty-space shortcut follows. This lookup makes no assertion that the suggested twist or its level-lowering application is valid. The complete response and exact-count receipt are `source_records/candidate_lmfdb_45_search.html` and `verification/candidate_level45_lookup.json`.

## 12. Unique norm-45 form: conditional twisted exclusion at two

The [individual form page](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-45.1-a) was successfully retrieved. Its coefficient field is Q and its Hecke value at the prime of norm four is **-3**. This is actual source data, not an inferred base-change value. The page and lookup receipt are retained.

Suppose, as additional hypotheses, a quadratic twist is unramified at two with Frobenius value -1, and its normalized residual rank-two representation is compared to the unique weight-two, trivial-character form at exact level `(3sqrt5)`. The form polynomial at two is `R=T²+3T+4`. Twisting the previously established full Jacobian Frobenius polynomials gives:

| Branch | Roots of the twisted full representation satisfy | Exact obstruction modulo seven |
|---|---|---|
| C odd, A even, B odd | T²-T+4=0 | gcd(R,T²-T+4)=1 |
| C odd, A odd, B even | T²+4=0 | gcd(R,T²+4)=1 |
| C even | T=1 or T=4 | R(1)=1, R(4)=4 modulo seven |

Hence the unique norm-45 form is excluded under those twist/comparison hypotheses for either parity of C. The two odd-branch resultants are 64 and 36, respectively, both 1 modulo seven.

Run `python3 work48/computations/candidate_twisted45.py`; the output is `verification/candidate_twisted45.json`. It parses the actual form page and performs exact polynomial gcds and evaluations modulo seven. **This finite calculation does not establish the twist, a conductor drop, irreducibility, or level-lowering applicability.** In particular no new unconditional implication from 15|C is claimed here; that belongs to the separately audited local/global argument.
