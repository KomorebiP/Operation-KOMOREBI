# Audit of the exact local input needed for global rigidity

This is an application audit and adversarial self-review of preserved written
mathematics, not a fresh independent review of all upstream cluster arguments.
The new theorem needs characteristic-zero traces, not just residual local
splitting. This note identifies where the stronger input comes from.

## 1. RM compatibility and characteristic zero

For a totally toric Jacobian over a local field, the canonical analytic
uniformization gives torus T and period lattice Y. For every positive integer
r the characteristic-zero generic points give an exact sequence
0 -> T[7^r] -> J[7^r] -> Y/7^rY ->0. The compatible limit gives the Tate
sequence. Its construction is functorial in endomorphisms, hence the RM action
preserves the torus filtration. The toric subspace is two-dimensional overQ7
and stable under the quadratic field E, so it is one-dimensional overE; the
same applies to the quotient. If the Galois actions on the two rational
pieces are scalar chi*psi and psi, the RM trace is psi*(chi+1).
A quadratic twist by psi makes it chi+1.

This argument needs no integral splitting and is invariant under a change of
stable lattice. All exact trace identities therefore survive passage to the
fixed global basis and reduction modulo 7^n.

## 2. The four fixed places

At2, the normalized even-C semistable model has two nonsplit loops. Over
K_(2), Frobenius on each graph generator is -1. Thus both graph and period
lattices carry the same unramified quadratic character psi. The preserved
nu classification gives nu(Frob_(2))=-1 and no ramification at 2. Twisting
cancels psi. The residual cyclotomic value on Frobenius is4, separated from1.
Source: work47/notes/evenC_torus_frobenius.md and
work48/notes/character_sieve.md. The extra dyadic thickness note is NOT used
as a substitute for this full local trace identity.

At3 and 5, work49/notes/local_types.md proves the twist itself is split totally
toric over K_(3), K_(sqrt5), respectively. It verifies Galois-invariant twins
and trivial graph signs after the exact radicand twist. Their period pairings
are (7v_3(C)-3)I2 and (14v_5(C)-5)I2. The actual torus and period lattice are
split, so the characteristic-zero graded characters are chi and 1, regardless
of whether the natural torsion extension splits. Frobenius cyclotomic values
are9 and 5, separated from1 modulo 7. Nontrivial natural residual inertia at
these primes is compatible with an exactly trivial diagonal CORRECTION.

At7, work48/notes/bad 7_torus_monodromy.md proves the two graph generators and
period lattices have the unramified quadratic action psi overK_(7), and gives
the exact generic torsion sequence for ANY positive torsion level, including
7-powers. Apply it successively at 7^r, not only at 7, to obtain the Tate
sequence. The character_sieve note gives nu=psi locally. Twisting again
produces chi and 1. Since K_(7)/Q7 is unramified, the mod 7 cyclotomic inertia
has order6, so a separating inertia element exists. We do NOT assign the
nonunit value49 to chi_7 of a Frobenius lift at 7.

At every fixed place, these exact traces plus the globally oriented diagonal
characters satisfy B53.1. It follows that eta_n is trivial on the FULL local
Galois group, not only inertia or the residual quotient.

## 3. Every variable bad place, not only beta support

The natural-lattice period argument in work51/notes/ARITHMETIC_SUPPORT.md
(section2) supplies the content t=1+v_7(v_q(C)) at every q|C outside 2,3,5,7.
Split toric inertia has the form I+tau*N with N nilpotent of square zero.
Multiplying by the integral tame parameter preserves content at least1.
Thus N_tau in 7M2(O) for EVERY inertia element. This divisibility is preserved
under integral changes of the natural-lattice basis. The Frobenius-at-three
basis of that note (section1) is such a basis, and has a GLOBAL lower-left
ideal7^nO. These are the two simultaneous hypotheses needed in B53.2.

If the natural lattice had been replaced by an arbitrary endpoint first,
entrywise divisibility of its inertia would not be automatic. The proof
explicitly forbids that substitution.

## 4. Ramification exhaustiveness and the class group

The sextic discriminant is 2^12*3^6*5^5*C^14. Away from2,3,5,7 and divisors
of C, the natural 7-adic representation has good-reduction unramified action.
nu has finite ramification only at 3,5. This exhausts the finite places. The
image of eta reduced modulo 7^m is a7-group, so real inertia of order2 is
trivial. The applicable class-field quotient is Cl(K), not a finite-modulus
ray class group, and not Cl(K(zeta7)). Both the elementary norm-Euclidean
argument and Minkowski's bound give Cl(K)=1. No unramified7-character remains.

## 5. Source fingerprints

The original Block52 ZIP contains the original Block51 ZIP. The following
paths are relative to the extracted Block51 root, not files newly authored
in Block53. Their hashes were recomputed from the clean extraction.

| Frozen relative path | SHA256 |
|---|---|
| `work47/notes/evenC_torus_frobenius.md` | `3ab575c044ba137ca8e39184330075e04460e29023928938239d0862f408a44a` |
| `work48/notes/bad 7_torus_monodromy.md` | `8c970f3e4cf00b0fd437394b86984c6121d7ddb0bd293ffdbbcc5640c2930508` |
| `work48/notes/character_sieve.md` | `80cbeb444c3bfed163022a169ea22e8de76be7c84e1148fc5b78cb1b20628a3a` |
| `work49/notes/local_types.md` | `9d7284d9a050acf4de2db9d7e85a1b91eed6ad01590c41cd199ec2f1538d2bfc` |
| `work49/notes/extension_route.md` | `15a3e88c0a662d74775470ddce33e387ec9dc17fc77264c2179bf929793f7a15` |
| `work50/notes/extension_geometry.md` | `5a7242dbec90c1de3b03297e0bc7b26dfb2ee19b7e616ab90ea72734848ae3ac` |
| `work50/notes/local5_dyadic_thickness.md` | `9892dcb1f9ca70c816a375e0b6cfaf4e2927c5a4bb85c3fe06d238958cc2040d` |
| `work51/notes/LOCAL_DEPTH_THEOREM.md` | `dc9a7712c6c9eab074a2900c9c31d60bc4d28992a1af55f9b94657c9094dcb43` |
| `work51/notes/ARITHMETIC_SUPPORT.md` | `2b1d0aa33e085e3dbb7a41670dbdc763d8932ee5487a8850d32145094738d866` |

The machine-readable record is ../source_records/INHERITED_INPUT_HASHES.json.
The package verifier also replays the nested original archives, including
their own byte-integrity checks. Source fingerprints establish exact inputs,
not mathematical truth by themselves.

## 6. Review and dependency status

The fixed-prime local_types note contains its historical review status in its
original text. That historical text has not been rewritten. This new audit
checks the stronger input's mathematical implication and the passage to the
actual RM trace. It does not pretend that a title, hash, test count, or
self-review is an independent certificate of the upstream geometry. These
inputs remain explicit H4--H5 in TARGET_CONTRACT.md.
