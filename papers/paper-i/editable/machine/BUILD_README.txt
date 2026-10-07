Paper I machine-native final companion

Final PDF: Paper_I_Machine_Native_Final.pdf (94 pages)
Current executable payload: source/machine_v1.0.1/
Historical unchanged payload: source/machine_v1.0.0/

To compile the already-generated TeX without replaying Python:
  pdflatex -interaction=nonstopmode -halt-on-error Paper_I_Machine_Native_Final.tex
Run three times to stabilize contents and navigation.

To rebuild generated prose/catalog and replay the documented payload checks,
run build_companion.py with Python plus SymPy and a TeX installation. Set
PSC_PYTHON to the interpreter containing SymPy when it differs from python.

With the series layout (editable/machine and source at the release root):
  cd editable/machine
  PSC_SOURCE_ROOT=../../source python build_companion.py

The script automatically finds ../../source and source/provenance when run
from that layout. PSC_SOURCE_ROOT and PSC_MACHINE_ARCHIVE can override paths.
The source/provenance directory should contain
PSC_I_FINAL_MACHINE_RELEASE_v1.0.0.zip for the original-byte audit.

To reproduce the narrow derivation itself:
  PSC_SOURCE_ROOT=../../source python derive_v1_0_1.py
This rebuilds machine_v1.0.1 from the preserved machine_v1.0.0 payload and
replays the existing fixtures/gate plus the two zero-packet regressions.

Runtime implementation scope: six exact finite actions and two operation-
profile gates. The gate reads direct action_required_operations only. It does
not validate target hypotheses, transitive closure, or returned boundary guards.
The PDF documents that boundary explicitly.

Current source SHA-256:
37bf8f03dbbf66ce41f8b07a8e7be8fa5fca44176bdd56dd25b483f72736ff77

Corrections from v1.0.0:
- Two corollaries explicitly require every packet space to be nonzero.
- An unnumbered paragraph states empty-family and poset-height conventions.
- Source identities, locators, AST, record metadata, lock, and manifests agree.
All proof bodies and computational action implementations are unchanged.

Initial environment failure: default Python lacked SymPy, so the release gate
failed at EXECUTE_BLOCKIFY. An existing interpreter with SymPy1.14.0 resolved
that dependency. All current checks passed. No fresh Lean compilation is
claimed by this companion build; see the separate Lean guide for its scope.
