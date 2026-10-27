# Continue after Block 48

Read `REPORT.md` first. The original goal is Beal's conjecture; the active
subproblem is the complete primitive positive signature (3,5,7). Neither
is solved. Do not substitute an irreducibility theorem for a nonexistence
theorem.

## Accepted current results

1. The residual RM representation is absolutely irreducible if
   3990 does not divide C. Canonical proof:
   `notes/reducibility_local_inertia.md`, with `character_sieve.md`, the
   frozen Block47 proof, and their independent audits.
2. Absolute irreducibility implies weight-two trivial-character modular
   attachment to one of the four levels (3)^i(sqrt5)^j, i,j in {2,3},
   with the original local Weil–Deligne types retained. Read
   `notes/level_lowering.md` and `level_restricted_irred_review.md`.
3. The complete norm-2025 space has one remaining orbit,
   `2.2.5.1-2025.1-l`. It requires A,C odd, 418|B, and
   (A,C)=(5,9) or (6,2) modulo11. This is now based on all fourteen
   actual LMFDB forms, not a numerical-index dictionary.
4. Any primitive solution with 15|C must have 3990|C. The proof twists
   the attached form to the unique form at norm45 and excludes it at2.
   Read `notes/solution_divisibility_corollary.md` and the separate
   exact-data audit `notes/candidate_twisted45_audit.md`.

Together the local-inertia and twist proofs establish, for any hypothetical
primitive solution, residual reducibility iff 15|C iff 3990|C. Consequently
the status of reducibility on that branch is determined under the solution
hypothesis; what remains is to exclude the branch itself.

## Remaining mathematical obligations

| Obligation | Next discriminating action | Boundary |
|---|---|---|
| Exclude the necessarily reducible branch 3990|C | Study the global extensions of nu_real by chi*nu_real, or another Frey object with incompatible local behavior. | An independent irreducibility theorem would now be a contradiction route. The local torus character already agrees at every auxiliary C=0 prime; another finite character sieve cannot close this. |
| Last smallest-level orbit l | Use its fixed coefficient prime and exact local types or an appropriate modular covering. | More divisibility conditions on B alone are not nonexistence. A positive database CM flag is not a CM proof. |
| Other three levels | Execute a properly checked Hilbert modular form export at norms10125,18225,91125, excluding auxiliary7 from a mod7 sieve. | No runtime was available for this calculation. `computations/candidate_export.m` is unexecuted and not syntax-validated by Magma. |
| Full Beal | Cover the other exponent signatures by a proved uniform reduction or additional arguments. | A complete (3,5,7) proof would still not prove Beal. |

If an exporter becomes executable, first validate one known norm-2025
form against the retained database data. Then keep one actual form, one
coefficient prime above7 and one embedding throughout all auxiliary
comparisons. Record an exact coefficient-field model and both base primes
at every split auxiliary. Existence of separate compatible embeddings at
each prime is not the required global match.

## Routes that must not be silently reopened

- Bad7 has nonsplit torus Frobenius -1, monodromy 7v7(C)I2 and an explicit
  finite-flat torsion model. The sign agrees with the global character.
  Finite-flatness neither splits the Kummer extension nor proves good
  reduction or irreducibility.
- The surviving real ray character is the universal C=0 graph character.
  Any finite collection of those local character tests leaves compatible
  primitive residues. CRT does not turn them into an integer solution.
- The earlier coefficient-only stratification admits everywhere locally
  soluble families. Increasing prime-power precision or relabeling lanes
  does not supply a global contradiction.
- The actual raw hypergeometric coefficient has a denominator divisible
  by7. A factorial unit-tail theorem needs a new, proved normalization
  and comparison before it can be used here.
- The proposed norm45 twisted space is not empty. Its unique form is
  excluded by its actual trace -3 at norm4; the empty-space shortcut was
  tested and failed.

## Reproduction and evidence

Keep the package root layout `work48/`, `work47/`, `work46/`. The inherited
point-count data and code are loaded by their relative paths. The frozen
Block47 archive is also retained under `predecessor/`; its hash is the
ancestry key recorded in `TARGET_CONTRACT.md`.

Exact finite scripts use Python's standard library. Relevant entry points:

```sh
python3 work48/computations/candidate_local_checks.py
python3 work48/computations/candidate_complete_level.py
python3 work48/computations/candidate_independent_q11.py
python3 work48/computations/candidate_twisted45.py
python3 work48/computations/candidate_twisted45_independent.py
python3 work48/lean/check_formal.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The candidate scripts regenerate their named result snapshots. Preserve
the released archive unchanged and run in a new extraction for a fresh
audit. The character and bad7 computations also retain their explicit
contracts and version-two execution manifests. A manifest validates
execution provenance, not the interpretation of an external theorem.

The authoritative successful Lean run is `verification/formal_final/`.
The earlier `formal_run/` and `formal_verified/` directories are failed
environment diagnostics, not successful evidence. Read
`notes/formal_verification.md` before interpreting them. Eight public
theorems check local finite algebra; the global arithmetic is written.

All computations and reviews listed as completed in this checkpoint
actually completed. No external Magma job is running. Current-source
page bytes are pinned; numerical PV indices remain unused.
