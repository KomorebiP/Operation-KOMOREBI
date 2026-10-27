# Adversarial self-review

This review is by the same assistant. Separate programs are independent arithmetic
implementations, not an external mathematical reviewer.

1. The new primes have cyclotomic residue degree two. There are three prime ideals,
   not six. The orbit-average factor and all representative changes were checked.
2. The coefficient action and Frobenius action BOTH enter the pairing b with -b.
   Leaving out either sign would change the twist. Six Galois transports agree.
3. All three natural Kummer rows are zero. No false prime-field coefficient ratio
   is imposed there. F7 coefficients come from the inherited all-depth theorem
   and the no-minus all-inert support argument, not from a numerical guess.
4. The three new conductor columns alter every test. The frozen two-tuple list
   is not reused as a complete list for the enlarged conductor.
5. Both good and bad reduction are retained. New test primes lie outside beta's
   allowed support, but are not asserted good. The43 test is omitted whenever43
   could ramify. The29 zero argument is used only in the descended regime.
6. Pair membership uses one actual quartic, not independently chosen roots from
   different equation residues. Natural root-of-unity scales match the chosen
   integral cyclotomic test-prime generators.
7. Finite countervectors survive. The94-list is not relabeled empty. The support
   lower bounds are explicitly conditional on COMPLETE rational conductor<=2000.
8. The new count acceleration uses only exact int64 modular operations, with
   proven bounds far below2^63. Scalar and vector paths were cross-checked on
   small complete families; the separate full counter uses a different residue
   field and direct square-root multiplicities. It imports no primary arithmetic.
9. The all-depth audit finds the stated conditional logical chain sound, but
   does not independently validate analytical uniformization, half-precision,
   the actual endpoint normalization, or the global Frey-model hypotheses.
10. Source-file hashes preserve provenance. All final universal conclusions remain
    written conditional proofs. There is no new Lean or external acceptance.
