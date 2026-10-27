KOMOREBI P. — PAPER I
Final three-companion edition • 5 October 2026

Open START_HERE.html, or open the three PDFs in papers/.

1. Paper_I_Traditional_Final.pdf
   The expanded mathematical core, full written proofs, corrected worked
   models, exact figures and integrated visual atlas. Stable statement IDs
   connect it to the machine-native companion.

2. Paper_I_Lean_Guide_Final.pdf
   An explanatory guide to the actual Lean project: definitions, module
   architecture, proof walkthroughs, the complete 35-row scoped contract,
   dependency pins, build instructions and evidence boundaries.

3. Paper_I_Machine_Native_Final.pdf
   The machine representation and its actual interfaces, accompanied by
   the operative v1.0.1 records and runtime in source/machine_v1.0.1/.
   Includes all 108 stable records, 69 attached written proof bodies,
   typed signatures, the full action catalogue and exact worked examples.

WHAT IS FINALIZED
This package closes Paper I alone: all three companion documents are
complete. Papers II–XII are frozen by user request at their collected
source state. Their materials remain preserved, but no further companion
authoring is queued and no new final editions are claimed for them.
The series register records this boundary explicitly.

MATHEMATICAL CORRECTIONS
Two expanded-source corollaries now explicitly require every packet space
to be nonzero: support-pattern star classification and unweighted source-
component counting. Their existing proofs are retained. A preliminary
paragraph also defines the empty maximum and empty-poset height as zero.
See CORRECTIONS.txt and verification/mathematical_audit/ for counterexamples,
scope, and verification of the corrected texts. The audit was bounded to
the named areas; it was not an audit of every proof or a novelty review.

EVIDENCE
The traditional computational source was freshly checked: all 305 recorded
file hashes matched and all 33 Python tests passed. The current machine
release gate, exact fixture suite and narrow nonzero-packet regressions
also passed. The guide records current static comparisons against the
preserved Lean build evidence. No fresh Lean compilation was performed
during this edition preparation. Contract rows, mapped declarations, source
records, computational tests and universal mathematical proofs are different
objects and are not added together into a theorem count.

The machine runtime implements six exact finite actions and two profile
gates. A transport PASS compares the record's direct operation requirements
with supplied preservation flags; it does not establish target hypotheses,
inspect all transitive dependencies, or enforce returned boundary metadata.
The full operational boundary is documented in the machine-native PDF.

SOURCE LAYOUT
editable/                     Final LaTeX, figure assets and authoring scripts
source/traditional_v1.3.1/     Preserved corrected human, Lean and Python source
source/visual_guide_original/ Preserved exact visual models and source plates
source/machine_v1.0.0/         Preserved historical machine release
source/machine_v1.0.1/         Corrected operative machine source and runtime
source/provenance/            Original source archive
verification/                 Fresh checks, historical boundaries and audit
series/                       Twelve-paper register and source inventory
COMPANION_CROSSWALK.json       Stable IDs, printed locators and qualified maps
MANIFEST_SHA256.json           Package file hashes

REBUILD THE PDFS
With Python 3 and a TeX installation providing pdflatex, xelatex and the packages
used in the source preambles, run from this directory:

  python scripts/build_pdfs.py

This compiles the supplied final LaTeX three times, keeps build logs in
build/, and writes rebuilt PDFs to papers/. It does not rerun Lean or alter
the mathematical source. Each editable component also has its own build
notes and, where applicable, a separate data-regeneration script.

REPLAY COMPUTATIONAL CHECKS
Use an interpreter with the requirements listed by the relevant component.
The recorded successful machine checks used Python 3.12.14 and SymPy 1.14.0.
The initial environment lacked SymPy; that failed attempt is recorded.

  cd source/machine_v1.0.1
  python runtime/verify_release.py
  python runtime/exact_fixture_suite.py
  python runtime/nonzero_packet_regression.py

From source/traditional_v1.3.1/:

  python scripts/check_bundle.py --tests

The separate Lean guide gives the exact pinned toolchain and dependency
procedure. Preserved evidence is not a substitute for performing a fresh
build when a fresh build is required.

PROVENANCE
Final edition attribution: Komorebi P. Original sources are retained under
their original component versions. This package records an editorial and
companion release; it makes no change to the original licensing status.
Historical logs may retain the absolute paths of their execution environment.
New build instructions use paths relative to this package.
