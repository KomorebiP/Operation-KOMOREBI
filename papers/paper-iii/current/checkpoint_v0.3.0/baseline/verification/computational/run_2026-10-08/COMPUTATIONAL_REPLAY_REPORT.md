# Paper III computational replay, 8 October 2026

Fresh offline replays passed on isolated, byte-identical temporary copies. No authoritative source or mathematical statement was edited.

| Suite | Fresh result | Arithmetic and scope |
|---|---|---|
| Frozen finite release `VERIFY.sh` | 34 release files, 33 checksum entries, 41 map rows, 143 mapped declarations, 143 explicit audit targets | Offline integrity and static consistency checks. The saved namespace record contains 468 declarations and 229 theorem declarations. No fresh Lean run. |
| Strengthened `verify_strengthened.py` | 11 of 11 groups passed | Exact integer counts and modular examples combined with NumPy floating checks and seeds 2 and 4. The source-integrity group checks the frozen strengthened article. |
| Current visual `verify_examples.py` | 124 valid checker records passed, zero failed | Exact SymPy integers, rationals, matrices, and polynomial identities. All 5,461 words of lengths 0 through 6 are included in the independent path checks. |

The visual suite also rejected all four deliberately false controls: commuting the coefficient order, inferring nonzero transfer from reachability, inferring identity from trace and determinant, and claiming fixed-packet gauge covariance without commutation. These are expected control rejections, separate from the 124 passing checks.

The temporary-copy driver pinned and rechecked 34 finite-release files, 3 strengthened inputs, and 2 visual inputs. Every input hash remained unchanged. The visual suite generated its JSON only in temporary staging. Its complete fresh result is retained in `visual/result.json`.

Python 3.12.14, NumPy 2.3.5, SymPy 1.14.0, Bash 5.2.21, and GNU coreutils 9.4 were available. The requested cached dependency path was absent. Installed SymPy supplied the dependency without any network fetch. Assertions were active. The exact executable paths and relevant environment are in `environment.json`.

Each suite ran with a 120-second wall limit, a 2 MiB combined log limit, a 2 GiB address-space limit per process, a 90-second CPU limit per process, one CPU affinity core, and a conventional numerical-library thread cap of one. The thread setting is cooperative. The CPU budget is per process rather than aggregate descendant time. No timeout, resource failure, stderr output, or valid-check failure occurred.

The three version 2 manifests passed the computation-audit validator with the project root supplied. They record actual argv, source hashes before and after, result hashes, UTC start time, runtime, exit status, and caps. `manifest_validation.json` records the validation commands and outputs. `COMPUTATIONAL_REPLAY_REPORT.json` contains the complete interpretation and check list.

These runs reproduce finite evidence. They do not prove the universal analytic results, infinite convergence, or all statements in the edited monograph. The historical strengthened group called “exact coordinates and jets” uses floating arithmetic. Its transport group asserts endpoint unitarity and errors, rather than separately asserting each numerical factor's intertwining identity. The exact visual suite has independent endpoint accumulation and explicit fail-closed controls, while the numerical suite has not been reimplemented in full by a second method.

The finite verifier was invoked without `--full`. It checked saved formal artifacts and their internal consistency. No `lake` command, Lean compilation, or fresh kernel certification occurred.

From the package root, the isolated driver can replay a suite into a new result destination:

```bash
python3 verification/computational/run_2026-10-08/replay_isolated.py --suite finite --result verification/computational/new_replay/finite.json
python3 verification/computational/run_2026-10-08/replay_isolated.py --suite strengthened --result verification/computational/new_replay/strengthened.json
python3 verification/computational/run_2026-10-08/replay_isolated.py --suite visual --result verification/computational/new_replay/visual.json
```

For the full bounded provenance recipe, reuse the relevant `*_contract.json` with the computation-audit `run_experiment.py` runner, choose a fresh output directory, pin every path in `execution_artifacts`, and declare the driver's result file. The original bounded commands are recorded in the manifests. Numerical packages must be present to reproduce the strengthened and visual suites.
