# Independent audit of the Block 48 synthesis

Date: 2026-09-19. Primary verdict: **proved as written**, for the three
normalized claims below and with the explicitly declared arithmetic and
database inputs retained. No implication completing the primitive
(3,5,7) equation or Beal's conjecture has been proved.

This is an independent read-only review of the raw proofs, with this audit
as its only written artifact. The mathematical proof-audit workflow was
used. Existing independent finite enumerations were inspected and their
logical uses reconstructed; they were not rerun. Status headings were not
treated as evidence. Source statements already checked in the project's
durable source records were retained as external inputs, and the decisive
PV and Breuil–Diamond passages were also read in the locally authenticated
primary texts.

## Normalized claims

Throughout, A,B,C are positive pairwise-coprime integers satisfying
A³+B⁵=C⁷, K=Q(√5), and barρ is the rank-two residual RM representation
at seven of

    J = Jac(y²+(x³+B)y = 2Bx³+3Ax+B²),

in the geometric weight-two normalization. Absolute reducibility means
reducibility after extension to Fbar₇, and does not assert splitting over
the original coefficient field.

1. **Irreducibility:** if 3990 does not divide C, barρ is absolutely
   irreducible.
2. **Restriction on integer solutions:** 15|C implies 3990|C. The proof
   actually establishes the intermediate assertion that 15|C forces
   absolute reducibility of barρ.
3. **Candidate theorem at one level:** if barρ is directly congruent,
   with this normalization and one fixed coefficient prime and residual
   embedding, to a parallel-weight-two, trivial-character Hilbert newform
   at exact level (45)=(3)²(√5)², its orbit must be
   `2.2.5.1-2025.1-l`. Necessarily A,C are odd, 418|B, and
   (A,C) mod 11 is (5,9) or (6,2).

The direct comparison and exact level in claim 3 are hypotheses. Claim 3
does not put every solution into that level. The level ideal (45) has
norm 2025; the twisted ideal (3√5) has norm 45.

## Dependency graph reconstructed from the raw arguments

Let R mean that barρ is absolutely reducible, and I its negation.

The irreducibility chain is:

    canonical Block 47 theorem: R ⇒ 14|C;
    retained global character contract + exact ray quotient:
        R ⇒ one of two quadratic characters;
    q=11 smooth and nodal comparisons:
        R ⇒ ν is the character of Q(ζ₁₅)⁺/K;
    q=19 smooth comparison:
        R ⇒ 19|C;
    Weil pairing + the two RM coefficient embeddings:
        R ⇒ J[7]^ss = ν ⊕ ν ⊕ χν ⊕ χν;
    potentially good local reduction + scalar inertia + J[2]:
        R ⇒ 3|C and 5|C;
    coprimality of 15 and 266:
        R ⇒ 3990|C, equivalently 3990∤C ⇒ I.

The integer-solution chain is a separate argument:

    15|C + I
        ⇒ original local special types of conductor 2 at 3 and √5
        ⇒ type-preserving modular attachment at level (45)
        ⇒ automorphic twist by ν at exact level (3√5)
        ⇒ the unique norm-45 form, with a_(2)=-3
        ⇒ contradiction at the prime (2) of norm four.

Thus 15|C implies R. The already established implication R⇒266|C
then gives 15|C⇒3990|C. This proof does not use the newer local-inertia
implication R⇒15|C. There is therefore no circular dependency between
claims 1 and 2. The complete fourteen-form calculation at norm 2025 is
also unnecessary for this twist argument.

For claim 3 the complete database list and norm-four comparison first
leave a,f,h,l for odd C, and n for even C. Further necessary comparisons
exclude a at nineteen, f at twenty-nine, h at eleven, and n by correlated
comparison at both primes above eleven. The surviving l comparison
forces the stated parity and residue restrictions.

## The two delicate bridges

### From residual characters to the divisibility of C by three and five

The local-inertia proof does not confuse global semisimplification with
local splitting. Potential good reduction makes the inertia image H on
T₇J finite. Seven cannot divide |H|: an element of order seven in
GL₄(Q₇) would require the irreducible polynomial Φ₇, of degree six,
among its characteristic-polynomial factors. Maschke's theorem therefore
makes the residual H-action semisimple. Its four equal quadratic factors
force a scalar residual action, and injectivity of reduction on
prime-to-seven roots of unity makes the original inertia scalar too.

The quadratic twist has unramified T₇ and hence good reduction by NOS.
Its two-torsion is unramified and agrees with the original J[2]. The
action on the six Weierstrass roots is faithful on J[2]: its fifteen
nonzero classes correspond to the fifteen pairs of distinct roots.
Consequently the roots are unramified. Their integral differences then
force discriminant valuation at least Σnᵢ(nᵢ−1), where nᵢ are the
residue-root multiplicities.

At three the actual valuation is 6 while this bound is 12 or 30. At
five, normalized by v(√5)=1, it is 10 while the bound is 20 or 30.
The potential-good-reduction premises cover all branches: PV covers the
nonnegative-parameter cases in the exact stated range; the A-divisible
case at five has an explicit smooth model; at three the missing negative
valuation case has both the checked Liu invariant argument and the
independent two-triple-cluster argument. Thus neither prime has an
omitted A=0 or B=0 residue lane.

### From 15|C to the exact twisted norm-45 level

Primitivity makes A,B units at three and five. For t=-B⁵/A³,
v_l(t−1)=7v_l(C)>3 in the rational valuations used by PV Proposition
7.4. Its potentially multiplicative conclusion survives base extension
to K. Full monodromy has rank two; because N is linear over K₇ and
[K₇:Q₇]=2, the RM factor has monodromy rank one. Its local type is
η_v⊗Sp₂ with N nonzero.

The characteristic-zero determinant is cyclotomic by the separately
checked BCDF theorem, independently of residual reducibility. Thus
η_v² is trivial on inertia. At these odd residue characteristics the
quadratic inertial action is tame. The original conductor range {2,3},
used before choosing a modular lift, rules out the unramified special
case of conductor one. The original special type therefore has a
nontrivial quadratic inertia character and conductor two. This avoids
inferring an original conductor from a desired level of a modular lift.

The character ν is a globally defined totally even quadratic character;
its construction does not require R. At each of the two places, its
inertial restriction is the unique nontrivial quadratic character of
tame inertia. Twisting cancels η_v on inertia and leaves N nonzero.
For completeness, the conductor formula

    a(r,N)=a(r)+dim(V^I)−dim((ker N)^I)

gives 2 before twisting and 1 afterwards: before twisting both invariant
spaces vanish and a(r)=2; afterwards their dimensions are two and one,
and a(r)=0. Hence the new level is exact, rather than merely a divisor
of (3√5). No other finite place acquires ramification.

Breuil–Diamond's definition of a type is the equivalence class of
(r|I,N), and its Theorem 3.2.2 retains both parts. Thus using the
type-preserving attachment does retain the nonzero monodromy needed
here. Its existing weight-two, determinant, finite-flat and restricted
irreducibility checks are inputs of this synthesis, not consequences of
the norm-45 count.

Twisting the automorphic representation by ν(det) preserves cuspidality,
weight and trivial central character. The Hecke eigenvalues are
multiplied by ν(Frob), so the associated residual comparison twists by
the same character. Since ν(Frob_(2))=-1, the allowed quadratic factors
at norm four become T²−T+4 or T²+4 in the odd-C branches, and the
allowed eigenvalues become 1,4 in the even-C branch. The actual
norm-45 form has factor R=T²+3T+4. Its differences from the two
quadratics are respectively 4T and 3T, giving no common root modulo
seven, and R(1)=1, R(4)=4 modulo seven. This contradiction is valid in
all parity branches.

## Candidate correlation and exhaustive scope

The norm-2025 comparison retains one coefficient prime throughout. In
particular, for n the coefficient generator satisfies e²=18, hence
e=±2 modulo seven. The two eleven-adic traces are -e,e under that
same embedding. The underlying four-dimensional polynomials have
cubic coefficients 2e and -2e, which differ. Because J is defined over
Q, conjugate Frobenius lifts above eleven have equal full characteristic
polynomials. This remains valid in the bad-reduction lane, since the
modular comparison itself is unramified there. Choosing a different
embedding at each prime would invalidate the argument; the raw proof
does not do so.

The h/l comparison uses norms of their quadratic trace polynomials,
which are independent of the two possible F₄₉ embeddings. The complete
eleven table leaves precisely (A,B)=(5,0),(6,0) for l; seventh powering
is bijective modulo eleven and gives C=9,2 respectively. The norm-four
test gives A odd and B even; the nineteen test gives 19|B. Together
these give 418|B and the exact paired residues. None of these necessary
conditions alone is a contradiction.

The independent enumeration certificates cover all 110, 342 and 812
smooth pairs at eleven, nineteen and twenty-nine where required. The
global character test needs the first two primes; the candidate f test
needs twenty-nine. Bad-reduction lanes are separate written toric
comparisons, not silently discarded by smooth-pair enumerators. The
Hilbert newform lists and their Hecke values are imported exact LMFDB
inputs, not newly computed Hilbert spaces. Positive CM flags and an
unverified PV-index dictionary are not used in these exclusions.

## Obligation matrix

| Obligation | Disposition |
|---|---|
| Quantified solutions, coefficient field and normalization | Passed; fixed above and in the raw proofs |
| Inherited Block 46–47 character and RM contract | Retained declared arithmetic input |
| Two quadratic characters, both real signatures | Passed by reconstructing the unit quotient |
| q11/q19 character exclusions | Passed using the retained independent exhaustive certificates and bad-fiber proofs |
| Scalar-inertia, quadratic twist and J[2] implications | Passed |
| All potential-good local branches | Passed; exact source hypotheses and separate missing cases accounted for |
| Seven-specific modular attachment | Passed as a synthesis input; raw hypothesis proof and separate review inspected |
| Original special types and conductor two on 15|C | Passed; determinant and original conductor range precede modular lifting |
| Exact twisted level (3√5) | Passed; inertia is cancelled and monodromy persists |
| Norm-45 obstruction | Passed for both parity branches, with imported completeness and actual a_(2)=-3 |
| Complete norm-2025 exclusion except l | Passed under the normalized direct-comparison hypothesis |
| Fixed coefficient prime across split primes | Passed; essential to the n obstruction |
| Nonexistence for all primitive solutions | Not established |
| Full Beal conjecture | Out of scope |

## Reviewed revisions and verification actions

The following are hashes of the raw files actually reviewed, not inferred
claim-status identifiers.

| Raw proof or synthesis | SHA-256 |
|---|---|
| `work47/notes/mod7_good_reduction_irreducibility.md` | `fb939ab48ffd726781aabd41328e7a31c594502cc9585c22e7a4df0b4d7448a1` |
| `work48/notes/reducibility_local_inertia.md` | `6d7c417e9453fd6aca7635034eb491d8e04f4633410573f3e359d45e67a8afe1` |
| `work48/notes/character_sieve.md` | `80cbeb444c3bfed163022a169ea22e8de76be7c84e1148fc5b78cb1b20628a3a` |
| `work48/notes/level_lowering.md` | `ff74504680f23207c1fae030708582fa622f6699dfdf1057df9ec536f6d8ea63` |
| `work48/notes/modular_candidates.md` | `a43d7963b7c3854e7b4876ec0d762329a8af524cfe238f1082c935d3104ef1eb` |
| `work48/notes/solution_divisibility_corollary.md` | `bec978bc6f2e9a1f2ed3aab4e816d49c3b507b8e2ce6bd00893be8050983bd87` |
| `work48/REPORT.md` | `46ce5fdcfad0dd9cb347a444eec7ab219dcd9a3b935fad81d30bb30d1c0361ea` |
| `work48/CONTINUE_HERE.md` | `78415a9f0719aabd5fe04382974c6bc3542afe677f898442f804d99c312feebe` |

Further retained independent-review pins are:

| Review/certificate | SHA-256 |
|---|---|
| `notes/reducibility_local_inertia_audit.md` | `2c3301d5af7c71125410e1543155c1f1573f7406a672b4f88e5ec77f8370f502` |
| `notes/bad7_character_sieve_audit.md` | `32a402832b37053600ab245ff5f0b58296dcebeef65df915b8c4f0682e8dc2ae` |
| `notes/level_restricted_irred_review.md` | `9d58e5446dba51aacf657a4032b25276952508e447905c9017d9a8cbe7fa3226` |
| `notes/candidate_independent_audit.md` | `12b5693a1e9090e29f2ae1dff2fe1fc578df39b7c07f7aef585e0652e1e1c052` |
| `notes/candidate_twisted45_audit.md` | `f371c6d1570b69037f37880fa22c6337dda0d691faa20de8eb8dffdde765e41b` |
| `verification/candidate_independent_q11.json` | `07666337b5d1ed4d406939ce42c0955c065d1bf5329479b152548a6613044d18` |
| `verification/candidate_twisted45_independent.json` | `e3bca41df86cac100d625353afd710778032d781f9c0014354646b457aa94745` |
| `verification/character_sieve_run/result.json` | `d076033c76f62daff6f36a4faef2969411fb6df2ca60441317bbb8741fd3f3f8` |
| `verification/bad7_character_audit_run/result.json` | `f426dbc32cff22c0181c8c5ab27c5021406500fb71ec8813f459590211883900` |

The last table uses paths relative to work48. Primary PV and BD source
bytes inspected agree with `source_records/level_sources.json`: PV PDF
`d5983c0949129942c3510d9c3a8de1fbf8998e4b0e5b5d822ddf94a795048004`,
BD PDF `83fbf509af8b0d192d8f5adfcf0812c126a8bd0e128d56bcb65421eab1296a28`.
The primary-text locators were PV Proposition 7.4, Theorem 7.8 and the
special-type discussion in Theorem B's proof; BD §3.2's definition and
Theorem 3.2.2. The arithmetic boundary and additional source versions
remain those recorded in `source_records/level_source_audit.md`.

Actions were raw file reads, `rg` source-location searches, `sed` reads
of the primary-text extracts, and `sha256sum` checks. No finite field
enumeration, Hilbert-space computation or Lean run was newly performed
by this synthesis auditor. Hashes authenticate the reviewed bytes, not
the correctness of their mathematics.

## Exact remaining scope and strongest safe conclusion

There is no remaining missing implication in the three normalized
claims at the reviewed revisions. A useful logical clarification from
combining the first two proofs is that, **on hypothetical primitive
solutions under the retained arithmetic/database inputs**,

    barρ absolutely reducible ⇔ 15|C ⇔ 3990|C.

The forward implication to 15|C is the local-inertia argument, the
reverse implication is the twist argument, and the divisibility
equivalence is the corollary. Thus the remaining 3990|C branch is
forced into the reducible case by the present results. A future proof
of irreducibility there would be a contradiction route excluding that
branch; its reducibility is not still undetermined conditional on an
actual solution. This clarification was communicated to the parent
investigator. The final report and continuation note were updated to
state the equivalence and to identify exclusion of the necessarily
reducible branch as the remaining obligation. Those updated paragraphs
were read before fixing the hashes above. The five raw mathematical
proofs did not change during this final summary update.

No solution is produced by these implications. Nor do they eliminate
the surviving l comparison or all other possible level spaces. The
scope clarification has now been preserved in the report and continuation
notes. Further mathematics must exclude
the forced reducible branch and the remaining irreducible modular
candidates before a complete signature claim is available.
