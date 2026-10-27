# Exact computation audit for the Beal conjecture piece

Audit date: 8 October 2026, America/Chicago. Execution timestamps are recorded in UTC. The source checkpoint is Block 80, version 8.0.0, dated 22 September 2026.

## Verdict and mathematical scope

The current Block 80 finite operator and supplied target evaluator have been reproduced from unchanged original bytes and checked by an additional independent exact implementation. The ranks, full null bases, coefficient conventions, own conductor Frobenius rows and affine origin invariance agree.

No actual arithmetic affine target has been supplied. No global primitive has been numerically evaluated and no surviving pattern is eliminated. Computational success does not prove inherited Frey geometry, Poitou–Tate, Neukirch's theorem, integral realization or general Beal.

The bounded conductor sieve concerns the complete ramification support of the opposite class beta. The bound is that each ramifying rational prime is at most 2000. It is not a bound on a conductor product or on every divisor of the integer C. The eight necessary tuples form four coefficient conjugate pairs. They are not Galois representations or integer solutions.

## Current contract

The base field is Q(sqrt5). Its unit phi=(1+sqrt5)/2 belongs to the base field. The coefficient field is k=F49=F7[w]/(w²−5). These two radicals have distinct roles. Field entries supplied to the evaluator use the integer code a+7b for a+bw, with 0≤a,b<7.

The published linear matrices have entries in F7 and are extended to k. Their computation does not assume coefficient descent. The ordinary localization image has dimension 10 over k inside a local space of dimension 24. Fourteen independent Sigma unit relations cut out that image. Six fixed local constraints and nine toric constraints give A=EJ of size 15 by 10.

| Pattern | rank A | homogeneous k dimension | affine cokernel k dimension | remaining ordinary character support |
|---|---:|---:|---:|---|
| A | 7 | 3 | 8 | 307, 797, 1483 |
| B | 7 | 3 | 8 | 307, 797, 1483 |
| C | 8 | 2 | 7 | 307, 1483 |
| D | 7 | 3 | 8 | 307, 797, 1483 |

These are homogeneous differences relative to one bare primitive. They do not determine its absolute inertia. The general affine cardinalities, if nonempty, are 49³,49³,49²,49³. The smaller 343,343,49,343 counts require the additional common pointwise semilinear frame condition. Neither list establishes nonemptiness or counts actual representations.

For an actual target t(p0), the criterion is N t(p0)=0, where N is the full left null matrix. The source data do not evaluate t(p0). Its toric rows include −hc and the unknown local values of p0. Substituting a zero target would be a synthetic calculation.

## Source and implementation checks

The authenticated source archive hash is `cd5ed533e11d5d7202afc38293bf47d8134f94b758738d3931a317e808cddc0e`. The current primary and separate certificates are identical byte for byte. Their SHA256 is `6317fe77a6267034ee0153d4ce3e9084e22406bc58011622f4b94d5081185880`.

The primary code uses the w basis, binary exponentiation, Bareiss cyclotomic norms and row reduction. The original separate code uses the phi basis, another powering order, products of cyclotomic conjugates, independently lifted self units, determinant expansion and complete null bases. The two programs import no arithmetic from each other. They share the same frozen arithmetic input facts. This is arithmetic implementation independence within the project, not external mathematical acceptance of its geometric premises.

The ordinary residue generator only needs a nonzero seventh quotient. Its full multiplicative order is not imposed. The beta generator checks use the appropriate residue degree. At a conductor prime, the Frobenius is calculated with that same prime as uniformizer. It is not silently replaced by an unramified test prime. The beta inertia scale is converted from its frozen convention to the ordinary local Artin convention.

The original source builder reconstructs the current input fixture from the pinned Block 79 tangent data, Block 70 support table and fixture, and the degree two reciprocity notes. The fixture was deleted and regenerated in both fresh archive mode and portable science mode. Full result content was compared. No cached status flag was accepted in place of a scientific result.

The 166 bundled scientific source and input snapshots total 2,040,655 bytes. Every snapshot is byte identical to its original payload. The complete source table is `computation/EXACT_SOURCE_PINS.json`.

## New independent audit

The additional script `computation/independent80_audit.py` imports no primary arithmetic. It uses SymPy's explicit GF(7) domain for rank and exact integer determinants for rank minors. It checks L J=0, A=EJ, N A=0 and A K=0 with the full stored null bases. The five matrices L,J,A,N,K were certified separately for each pattern, giving 20 rank and minor records.

It compares all 2,401 field products under the change between the w and phi bases. It verifies that w²−5 is irreducible over F7. Direct repeated multiplication gives phi^48=(1,35) and 3^48=(43,0) modulo49 in the w basis. The unit log witnesses are therefore (0,5) and (6,0). Their determinant modulo7 is 5. Every stored phi residue row at the support is zero.

The seven own conductor checks independently evaluate scalar cyclotomic roots modulo q², the unit pi_q/q and its seventh residue symbol. They agree with the separate Hensel calculation and the original self row signs. The seven primes are 197,337,547,673,743,883,1933. The degree two columns at 307,797,1483 retain their original distinct normalization.

The archived evaluator is loaded only as the implementation under test. Its decisions are compared with independent exact augmented ranks. There are 2,940 basis target tests across all 49 coefficient scalars, 1,960 image target reconstructions and 1,960 origin shift checks. The audit rejects 36 invalid scalar encodings, including booleans, negative integers, floats and 49. These basis tests do not enumerate all 49^15 targets.

Three separate symbolic expressions cancel exactly: the fixed local primitive differential, its fixed trace equation and the Frobenius lift gauge identity. These exact identities support the written algebra. They do not instantiate the actual global cochain.

## Original current finite ranges

The unchanged Block 80 primary and separate engines each make 592 residue symbol evaluations, 12,348 Frobenius lift identity checks and 560 synthetic image tests. The separate engine also checks seven own conductor units and 16 rank minor certificates.

The original supplied target self test makes 84 image and nonimage tests, 40 origin shift checks, 16 malformed target rejections and 12,348 prime field fixed primitive cases. The latter range is six choices for each of two nonzero character values and seven choices for each of three scalar values. Counts refer to evaluations of finite assertions. They do not count arithmetic solutions.

The fresh Block 80 archive verifier rebuilt all four scientific JSONs and the fixture, compared both main results completely, verified pinned source lineage and rejected nine deliberate corruptions. Its optional flag also executed the immediate Block 79 default verifier. This does not imply a new full earlier history replay.

## Historical scientific evidence

The exact Block 70 default archive replay rebuilt all twelve scientific result JSONs and its fixture, checked all complete results, and rejected nine deliberate corruptions. The final refinement is 18→14→12→8. All eight tuples have exactly nine support primes and natural ratio6. The forced common support is 307,337,547,883,1483,1933.

| New test prime | eligible good pairs | degree one counts | required degree two counts |
|---:|---:|---:|---:|
| 2129 | 647,216 | 2,129 | 157 |
| 2269 | 735,156 | 2,271 | 90 |
| 2311 | 762,630 | 2,317 | 110 |

These are complete target specific existence or exclusion calculations for the frozen eighteen tuples. They are not complete good polynomial lists at those primes. A degree two count is omitted only after an exact trace obstruction or an already found positive witness justifies omission. Bad reduction remains permitted when the paired products vanish. A nonzero beta value alone is not grounds to reject that bad alternative.

The new portable command plans reproduce the original scientific algorithms directly from the bundled source snapshots. They do not execute an argv from an untrusted historical report. Every declared complete JSON is compared by a canonical hash. The Block 68 backend environment fields follow the original verifier's comparison convention. The scientific code itself is unchanged.

Every portable scientific replay for Blocks 67 through 80 passed at the unchanged documented ranges. The portable Block 69 run compared all 17 complete scientific JSONs and completed in475.410396 seconds; Block 70 completed in203.785775 seconds. Both had a900 second wall cap,2 GiB per process address space cap,800 second per process CPU cap, two cores of affinity and a conventional one thread cap. These are execution resource limits, not mathematical bounds.

The final per run status, actual argv, runtime and limits are listed in `computation/RUN_SUMMARY.json`. This table distinguishes successful finite runs, the corrected Block 67 interpretation, and the inconclusive Block 69 archive attempt. The portable 69 success does not change the earlier archival timeout record or establish its archived integrity and corruption-control replay.

The legacy Block 71 primary JSON hardcodes the unit-domain metadata as 2304. Its actual original loop examines 2352 units:49²−7²=49×48. The original separate JSON already reports 2352. The quotient size 49 and each fiber size 48 agree. A new exact metadata correction enumerates all 2401 ring elements and confirms 2352 units in `computation/unit-domain71-run/correction.json`. This corrects one published count; it changes no original source, output, accepted period or gauge assertion. Existing executed portable71 manifests retain their original metadata pin, with this correction explicitly attached.

## Provenance and distributed reproduction

Each new reusable run has a version 2 manifest recording actual argv, environment versions, UTC start, elapsed time, exit status, enforced resource caps, full input hashes before and after, declared scientific results and logs. The authoring environment was Python 3.12.14, NumPy 2.3.5 and SymPy 1.14.0 on Linux. The finite code is deterministic and uses exact arithmetic. NumPy accelerates bounded integer arrays and introduces no floating point proof step.

The original complete nested archive contains third party papers. It is excluded from the distribution. Archive mode observation manifests remain authentic records of that original input hash. Repeating their complete root hash validation requires re supplying that exact original archive. The separate portable science manifests pin only bundled inputs and can be fully validated from this distribution. These two provenance scopes must not be conflated.

`computation/MANIFEST_VALIDATION.json` schema checks all records and performs distributed root hash validation for the portable records. It retains failed statuses. The helper records aggregate log and wall limits. Linux memory and CPU limits are per process, while the thread limit uses conventional environment variables that a child library may ignore. Limits do not authenticate a mathematical bound.

## Failures and residual obligations

The unchanged Block 67 scientific verifier passed, but the generic archive wrapper rejected its documented success label `PASS`. The failed wrapper record is retained. A separately pinned interpretation check verifies the successful scientific subprocess and its eight original output hashes without altering the failure record. The portable scientific replay passed independently.

The Block 69 archive mode attempt reached the wrapper's 840 second wall cap without a final report. It is resource inconclusive and is not recorded as a completed fresh archival replay. A process inventory diagnostic also failed on `ps -C` and succeeded with a default inventory. Full details are in `computation/COMPUTATION_FAILURES.md`.

The final frozen guide and reader evidence chapter have a separate independent computation QA in `READER_COMPUTATION_QA.md`. The guide's exact matrix, support, inertia conversion, rank and synthetic-target values agree with the fresh evidence. Its captions retain the primewise bound and the unevaluated arithmetic target. That QA's first run mistakenly used a cyclotomic residue degree as the degree of an inert base-field place in its own test of h. It failed at 337. The immutable failed script and manifest remain; a separately versioned script uses the correct all-inert norm q² and passes. No guide or historical scientific value changed.

The original rejected generator check, syntax failure, false zero product draft and earlier failed exclusion routes remain preserved. Deliberate tamper tests are expected rejections. They are not mathematical counterexamples or hidden production failures.

The remaining arithmetic decision is to evaluate the canonical class N t(p0) for an actual primitive and compatible local geometry. Even a zero first stage class leaves the upper q stage and integral Frey realization. Unrestricted beta ramification, higher depths, the minus component, other modular branches and the other exponent signatures remain outside the finite classification. Nothing in this audit closes general Beal.
