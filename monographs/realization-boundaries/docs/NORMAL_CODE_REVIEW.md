# Independent review: actual normal-code meanings and oracle upper construction

## Claim and verdict

**Verdict: proved as written. No defect found in the final names/equality/addition or oracle-copy bridge.**

Source: `RealizationBoundaries/ComputableNormalCodes.lean`.
Reviewed SHA-256: `7d25e320d78e74e3132643c864c43bf427f42fe6fd9d894f90a3691b950cd3c2`.
Clean compiler receipt: `verification/development/ComputableNormalCodes_012.json`.

The raw codes denote the original ambient paired-prime groups, not an abstract replacement. Their equality and addition are proved to agree with actual group equality/addition. Native oracle-recursion proofs supply their computations. The redundant naming is then converted into a genuine bijective natural-domain copy, yielding the exact oracle-copy existence criterion.

## Exact bridge

* `pairedMask_exact` identifies the mask derived from the actual prime-counting index with membership in the original `pairedSelector`. No independent prime enumeration is substituted.
* `nativeNormalValue_surjective` obtains every actual paired-group element by the previously checked normal-form theorem, native rational representation and finite residue-list representation.
* `ResiduesEqual` compares exactly the prime coordinates below the maximum list length. Outside that bound both interpreted vectors vanish, and nonprime positions carry no data. `residuesEqual_iff` proves equality of the actual ambient vectors.
* `nativeNormalEqual_exact` combines native rational equality and finite residue equality. Its converse uses normal-form uniqueness and the proved infinitude of every paired selector. It is not an assumption that equality in an arbitrary quotient is decidable.
* `normalAddCell_cast` proves each genuine prime coordinate of the output correction equals the two input corrections plus the actual rational-section cocycle. The modular subtraction is protected by the explicit bound on the canonical rational residue.
* `normalAddResidues_exact` proves that equality at every prime, including those outside the computed loop. Its bound contains both input supports and every prime dividing the product of the two reduced denominators.
* `nativeNormalAdd_exact` then proves actual ambient group addition by cancellation of the cocycle terms.

The finite output array is deliberately a **redundant** residue representation. Its nonprime entries may be nonzero; every meaning/equality theorem consistently discards those entries.

## Genuine oracle computation

`pairedMask_oracleComputable` uses the genuine selector reduction to the supplied oracle, then the native primitive prime-counting/parity computations. `normalAddCell_oracleComputable` composes this actual oracle query with the primitive rational residue and list-index operations.

`residueLoop_oracleComputable` proves a complete finite loop by native relative primitive recursion. It is identified with the actual `List.ofFn` order by `residueLoop_eq_ofFn`.

`rawNormalAdd_oracleComputable` correctly wires the decoded input codes into this loop, computes the finite denominator/support bound, and encodes the returned rational/list pair using the actual product encoding. `rawNormalEqual_computable` is ordinary computable and needs no selector queries.

`pairedRawCodes` therefore supplies genuine names, zero, addition and equality for the original group. The imported `OracleRawGroupCodes.toOracleGroupCopy` computes least equality-class representatives, enumerates the infinite set of canonical representatives and searches for each raw code's canonical index. The searches have explicit termination witnesses from surjectivity and group infinitude. The resulting `namesEquiv` is bijective; duplicate raw strings are not silently treated as distinct group elements.

`pairedOracleCopy` uses that conversion. `paired_oracle_copy_iff` combines this actual upper construction with the existing lower reduction from an arbitrary oracle-computable copy.

The standard inverse-operation interface is explicit in `OracleCopyOperations.lean`, reviewed hash `d6db70a3a1f076b71865a647a8406c18249cc545a8fdd80bcf5fa0779b4ddf1d`. Its inverse test is an actual addition/equality test, termination follows from the bijective naming of the actual inverse element, and `inverse_computable` invokes proved total minimization. `inverse_spec` and `subtract_computable` complete the ordinary computable-group operations. No computability of the abstract inverse naming function is assumed.

## Obligation matrix

| Obligation | Result |
|---|---|
| Names cover the actual paired group | Passed |
| Equality reflects actual group equality for all raw codes | Passed |
| Nonprime/redundant residues treated consistently | Passed |
| Exact cocycle correction at every prime | Passed |
| All coordinates beyond the finite loop justified | Passed |
| Native loop and true oracle-query semantics | Passed |
| Product/list encoding wiring | Passed |
| Conversion to bijective natural names | Passed |
| Actual inverse/subtraction computations | Passed, via `OracleCopyOperations` |
| Polynomial-time or machine bit-cost bound | Out of scope |
| Uniformly finding a distinguished element in an arbitrary unmarked copy | Not asserted; the lower theorem is the usual nonuniform Turing-reduction existence statement |

## Failed review expectations and correction

The first independent runtime log, `ComputableNormalCodes_independent_review.log`, contains four false outputs followed by two true outputs. These were **reviewer test mistakes**: I compared full raw output arrays with manually sparsified arrays that set every nonprime position to zero. The source never promises that normalization.

The diagnostic log `ComputableNormalCodes_review_diagnostics.log` records the actual arrays:

| Test | Actual array | Extra entries beyond the expected sparse array |
|---|---|---|
| Selected prime 2, `1/2+1/2` | `[1,0,1,0,3]` | Indices 0 and 4 only |
| Selected prime 3, `1/3+2/3` | `[0,0,0,2,0,0,2,0,0,0]` | Index 6 only |
| Omitted prime 3, `1/3+2/3` | `[2,0,0,0,2,0,0,0,2,8]` | Indices 0, 4, 8 and 9 only |
| Mixed negative fractions, `-1/2+1/3` | `[1,0,1,0,1,0,0]` | Indices 0 and 4 only |

All discrepant positions are nonprime. The meaningful prime coordinates are the expected ones.

I corrected the tests to compare semantic normal forms using the proved `nativeNormalEqual` relation, including the rational coordinate as well as prime residues. The new log is separate, `ComputableNormalCodes_independent_review_corrected.log`; all six checks returned true. The original failed log remains preserved and is not accepted as a passing test.

The corrected cases check:

1. The selected prime-2 cocycle `-1` for `1/2+1/2=1`.
2. The selected prime-3 cocycle `-1` for `1/3+2/3=1`.
3. Zero correction when that prime is omitted.
4. Negative numerator and mixed denominator addition, `-1/2+1/3=-1/6`.
5. Equivalent reduced rational and prime-residue names.
6. Ignoring arbitrary nonprime slots and cancellation of a zero rational numerator.

No source change was necessary to repair these false expectations. This does not excuse arbitrary equality-test changes: the correction uses the exact raw-code equivalence specified by the source and already proved equal to actual group equality.

## Verification and provenance

Final upper interface and axiom checks: `verification/development/ComputableNormalCodes_upper_independent_review.log`, exit 0. The oracle-addition theorem, actual oracle-copy construction and exact copy criterion report only `propext`, `Classical.choice`, `Quot.sound`.

Independent kernel replay of the final module passed: `verification/development/ComputableNormalCodes_independent_replay.log`.

Review provenance is a separate-agent inspection of raw definitions and proofs, explicit reconstruction of the finite-to-infinite bridge, and branch-sensitive runtime checks. Universal correctness comes from the Lean proofs; the finite examples only check the implementation branches and encoding expectations.
