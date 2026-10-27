# Paper I: Projector Resolved Seed Calculus

**Typed operator systems, seed rank, and exact packet coordinates**  
Komorebi P. · Release edition of 15 October 2026

Paper I develops a linear foundation for generating objects from seeds, resolving them into packets, and tracking the operators between those packets. The written argument, formal correspondence, worked examples, and computational implementation have their own evidence and stated scopes.

| Start here | Pages |
|---|---:|
| [Traditional manuscript](papers/Paper_I_Traditional_Final.pdf) | 105 |
| [Lean and evidence guide](papers/Paper_I_Lean_Guide_Final.pdf) | 44 |
| [Machine-native companion](papers/Paper_I_Machine_Native_Final.pdf) | 100 |

The traditional manuscript includes 10 main figures and 22 visual atlas plates.

## Sources and evidence

- [Editable manuscript and figure sources](editable/traditional/)
- [Current Lean source closure](formal/current/)
- [Formal reproduction instructions](formal/README.txt)
- [108-record correspondence map](formal/coverage/COVERAGE_108.json)
- [Accepted formal verification](formal/evidence/RELEASE_VERIFICATION.json)
- [Publication checks](verification/PUBLICATION_QA.json)
- [Python code](code/python/)
- [Detailed release report](RELEASE_REPORT.txt)

All 69 proof-level records have accepted formal correspondences at their stated scopes. The remaining records classify definitions, classical inputs, boundaries, and documentary material. These counts describe publication records rather than independent discoveries.

The recorded release audit checks 3,500 logical declarations: 3,499 ordinary logical replays and one identical upstream-name duplicate checked under a fresh name. It inventories 13 runtime helpers separately. The semantic correspondence review comprises 47 newly reviewed proof-level records and 22 retained predecessor acceptances.

The release records 96 exact finite or symbolic visual assertions and 33 companion tests. These computations cover their documented inputs and tolerances. The machine runtime implements six exact finite actions and two profile gates, with planner-only entries retaining that scope.

## Check the complete download

Extract the complete ZIP, enter this directory, and run:

```sh
python3 scripts/verify_integrity.py
```

The complete ZIP already contains the unchanged historical checkpoint at its required path. A separate assembly step is unnecessary for this download.

The original release manifest checks 2,176 recorded files. Upload preparation on 19 October 2026 verified the assembled release against that manifest and confirmed the three PDF page counts. This preparation did not execute a fresh Lean replay. The accepted October 15 compiler, replay, control, and semantic-review records remain available at the paths above.

Formal reproduction requires the separately provisioned pinned Lean 4.34.0-rc2 runtime and its authenticated dependency cache. Lean uses its official kernel. Noncomputable constructions are not presented as executable solvers.

## Provenance and terms

The original publication files and verification records retain their accepted bytes. The additional README and `github-upload/` directory document this upload preparation. Earlier editions remain under `source/` with their original evidence and scope.

Existing component notices are preserved, including the [original source licensing status](source/traditional_v1.3.1/LICENSE_STATUS.md). This packaging adds no license grant.

