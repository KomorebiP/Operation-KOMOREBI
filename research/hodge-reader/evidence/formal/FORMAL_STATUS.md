# Hodge Lean source audit

Audit date: 9 October 2026. Source review is complete. Current Lean elaboration is **blocked before elaboration**, so this edition claims no current Lean compiler pass.

## Normalized claim and primary verdict

**Verdict: conditional on named input.** The geometric interpretation of `infinite_promoted_class` depends on seed algebraicity and two algebraicity-preserving operations supplied as hypotheses. The file encodes their logical composition. It does not prove those geometric inputs or the general rational Hodge conjecture.

The authoritative input is `evidence/originals/Hodge_Infinite_Class_Web_v4.lean`. Its SHA-256 is:

```text
ebd414a30a63b27b6eb6f9f88f4ac2202aa404db7719aa9998ea06216d460186
```

The copy in this directory has identical bytes. The original was not edited. Declaration locations below refer to that exact revision. `declarations.json` is a static inventory, not an elaborator result.

## Exact final statement

At lines 203–222, the predicate is arbitrary:

```lean
AlgPacket : Nat → List Nat → Prop
```

The three inputs are:

```lean
pullbackAlg :
  ∀ {d k : Nat} {a : List Nat},
    AlgPacket d a → AlgPacket (d*k) (scalePacket k a)

tateJoinAlg :
  ∀ {m : Nat} {a : List Nat},
    AlgPacket m a → AlgPacket m (a ++ [1, m-1])

hSeed : AlgPacket 33 seed33
```

For each `k : Nat`, the conclusion is:

```lean
AlgPacket (33*k) (promotedPacket k)
```

Here `seed33 = [7,19,28,10,13,22]`, `scalePacket k a` multiplies each list entry by `k`, and `promotedPacket k` appends `[1,33*k-1]` to the scaled seed. The proof applies `pullbackAlg` once to `hSeed`, then applies `tateJoinAlg` once. Its final simplification expands the list definition and `towerDegree`. There is no hidden construction of a cycle in these steps.

This is a logically valid implication under the displayed hypotheses. Whether this exact Lean script elaborates in its author's environment is separate from that manual logical review. The source provides neither a toolchain pin nor a Mathlib revision.

## Dependency graph

| Leaf | Role | Audit status |
|---|---|---|
| Definitions of the three lists and degrees | Internal source definitions | Reviewed |
| `hSeed` | Algebraicity of the degree-33 seed, if the predicate is interpreted geometrically | Explicit assumption |
| `pullbackAlg` | Closure under coordinate scaling | Explicit assumption |
| `tateJoinAlg` | Closure under appending a complementary pair | Explicit assumption |
| Two applications and simplification | Internal implication proof | Manually reviewed, compiler replay blocked |
| A concrete meaning of `AlgPacket` | Comparison with actual varieties, cohomology and Chow cycles | Not supplied |
| Deep geometric theorem statements and their admissible domains | External geometric leaves | Outside this Lean file |

No circular dependency is hidden in the final proof. The algebraicity conclusion is obtained from assumed algebraicity inputs. It cannot be presented as an unconditional proof that establishes its seed.

## Declaration map

The source has **17 theorem declarations**, **19 definitions**, **2 abbreviations**, and **6 `#eval` commands**. Seven theorem scripts invoke `native_decide`.

| Declaration and starting line | Exact source-level content | Publication boundary |
|---|---|---|
| `units33_exact`, 27 | Filtered units modulo 33 equal the displayed 20-entry list | One finite list equality |
| `seed33_complete_hodge_balance`, 33 | Mapping `residueSum33` over that unit list gives twenty copies of 99 | Complete unit-orbit arithmetic for this one seed |
| `seed33_sum`, 38 | The six seed entries sum to 99 | One arithmetic equality |
| `residue_exponent_scaling`, 52 | For positive natural `k,b`, `k*(b-1)+(k-1)=k*b-1` | Natural-number identity, not a residue-map theorem |
| `scaled_seed_sum`, 64 | Six named multiples sum to `99*k` for every natural `k` | Arithmetic identity |
| `tate_pair_sum`, 69 | For positive `k`, `1+(33*k-1)=33*k` | Arithmetic identity |
| `promoted_packet_sum`, 74 | Eight named entries sum to `4*(33*k)` for positive `k` | Sum at the chosen representative |
| `promotedPacket_sum`, 80 | The same sum equality in the actual list representation | Does not prove every unit translate of every promoted packet is balanced |
| `promoted_full_conductor`, 96 | A specified nested gcd equals 1 for every natural `k` | Arithmetic gcd identity. No conductor of a geometric motive is defined |
| `coordinate_one_trivializes_stabilizer`, 101 | If `u<m` and `u%m=1`, then `u=1` | An identity for a residue representative. No permutation stabilizer is defined |
| `power_map_degree_composition`, 106 | `(r*s)^5=r^5*s^5` | No map or geometric map degree is defined |
| `klein_torus_degree`, 111 | `33^4=1185921` | Numerical equality. A torus lattice index or map degree is not formalized |
| `klein_matrix_identity`, 167 | The concrete list-matrix product is `33` times the displayed identity matrix | Exact concrete integer matrix certificate |
| `kleinC_row_sums`, 172 | All six row sums of the concrete matrix are 11 | Exact concrete list equality |
| `kleinC_column_sums`, 177 | All six column sums are 11 | Exact concrete list equality |
| `residue_pullback_exponent_identity`, 187 | The concrete transposed matrix product plus ten times the ones vector equals the target exponent vector | Exact exponent-vector certificate. The geometric residue comparison is not defined |
| `infinite_promoted_class`, 210 | The two closure hypotheses carry the assumed seed to every promoted list | Conditional implication for an arbitrary predicate |

The seven `native_decide` scripts are the three seed/unit equalities and the four concrete matrix/vector equalities. The six `#eval` commands are requested evaluations. No output from those commands was produced by the current blocked elaboration attempt, and an evaluation command is not itself a theorem.

## Domain and trust checks

The file imports `Mathlib` as a whole. A comment-stripped token inventory finds no local `sorry`, `admit`, or `axiom` declaration. This is a statement about the source text, not a claim that all imported dependencies are axiom-free. No `#print axioms` report or pinned transitive dependency inventory is supplied. The compiled decision tactic also has a computational trust boundary, so the absence of local axiom declarations should not be expanded into a blanket claim of kernel-only arithmetic verification.

The matrix representation uses lists. `dot` and `vecAdd` use `List.zipWith`, which truncates mismatched lists. `transposeN` uses `getD` with zero outside a short row. The displayed matrices and vectors have the matching dimensions required for these concrete certificates. The file does not prove a generic equivalence with the usual dimension-indexed matrix operations for arbitrary lists.

The final abstract theorem quantifies over `k=0` as well as positive `k`. Its logic remains valid because its closure assumptions quantify over all natural degrees and scales. The resulting degree-zero packet is not an admissible Fermat variety packet. Geometric interpretation must supply positivity and any degree, dimension, character and nonzero-residue restrictions. In particular, the raw gcd identity at `k=0` does not establish a degree-zero geometric conductor. The positive sum lemmas explicitly carry `0<k`, while the final abstract theorem does not.

The only complete unit-orbit balance formally stated is at degree 33. The promoted sum theorem checks the displayed representative. The source does not supply the reduction-of-units argument proving balance for all promoted unit orbits. A proof of that arithmetic extension, where used in the monograph, belongs to the manuscript and finite audit rather than this file's formal coverage.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Source revision and working-copy preservation | Passed | Matching SHA-256 values in `environment.json` |
| Local placeholder and declaration inventory | Passed as static source inspection | `declarations.json` |
| Exact final hypothesis/conclusion map | Passed | Original source, lines 203–222 |
| Internal logical implication under those hypotheses | Passed by manual review | One pullback application followed by one join application |
| Current Lean source elaboration | Not addressed by a working compiler | Attempt aborts before elaboration |
| Historical exact toolchain replay | Not addressed | No original toolchain or Mathlib revision pin |
| Concrete geometric instantiation of `AlgPacket` | Conditional | Not defined in the source |
| Seed algebraicity and closure inputs | Conditional | Supplied as arguments, not proved here |
| Universal promoted unit-orbit balance | Not addressed by this file | Only degree-33 orbit and representative sums stated |
| Actual Chow correspondence construction | Out of scope | No schemes, cycles, Chow groups or correspondences defined |
| General rational Hodge conjecture | Out of scope | No universal smooth projective variety target defined |

## Compiler recovery and failed replay

The initial environment had no `lean`, `lake`, or `elan` on `PATH`. The known extracted runtime and Mathlib directories were empty after workspace pruning.

A surviving local archive was restored into a scoped scratch directory. No network download was attempted. The archive is 343,842,845 bytes and has SHA-256:

```text
6fe3ce97a58f44e2b3567d455b994eacec5bfe9ae7774f2a573444480ba813fe
```

The first extraction emitted ownership-setting errors. Re-extraction with `--no-same-owner` completed. `lake --version` returned:

```text
Lake version 5.0.0-6caaee8 (Lean version 4.19.0)
```

Both `lean --version` and an attempt to elaborate the unchanged Hodge source exited with status 1 and:

```text
error: failed to locate application
```

Setting `LEAN_SYSROOT` did not resolve that location failure. There is also no surviving Mathlib source or compiled-object archive in the inspected prior environment. A functioning Lean binary alone would therefore not reproduce the original import. Because the historical Hodge source was unpinned, the restored 4.19.0 runtime would in any event be a compatibility probe rather than an exact historical replay.

The precise command attempts and errors are preserved in `compiler_probe.log` and `environment.json`. No `.olean` for this Hodge source was created and no theorem pass is claimed.

## Strongest safe statement and next check

The recovered file gives explicit Lean proof scripts for a finite degree-33 arithmetic seed, concrete integer matrix certificates, elementary universal natural-number identities, and a conditional algebraicity implication. The scripts contain no local placeholders. Their geometric scope is limited by the arbitrary predicate and its three explicit hypotheses. The current edition has inspected those scripts and their assumptions, but has not compiler-verified them.

The cheapest next formal check is to recover the author's exact Lean/Mathlib pair, compile the untouched source, and save the compiler output and `#print axioms` results in a separate probe module. That would settle elaboration and transitive axiom reporting. To turn the conditional algebraicity theorem into a concrete geometric theorem, the missing work is a defined, admissible `AlgPacket` interpretation together with actual seed, pullback and join theorems for that interpretation. Compiler success on the current abstract source would not remove this construction obligation.

Proofreading self-review: no change to original mathematical tokens. Coverage is the complete 237-line Lean source and this report. Manuscript claims elsewhere are reviewed by the independent publication audit.
