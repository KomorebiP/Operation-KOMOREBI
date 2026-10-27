# Centered Dirac verification runner

`verify_centered.py` creates a new evidence directory and refuses to overwrite it.
It does not download or modify project sources. It copies the actual local import
closure, project configuration and supplied controls into an exact snapshot,
compiles the closure into an initially empty object directory, and imports only
that directory plus the pinned external proof cache.

Dependency packages without a build directory are recorded and omitted from
the search path. The restored `Cli` package is one such source-only package.
Every direct external import from production, controls and generated auditors
must resolve to an actual object authenticated by the pinned runtime manifest.
The compiler checks transitive imports during the fresh builds. All dependency
Git revisions remain mandatory, including a package with no build directory.

Example from the task workspace:

```sh
python3 -B physics_next/gate_tools/verify_centered.py \
  --project physics_next/work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49 \
  --runtime physics_next/runtime/Komorebi_Portable_Lean_4.34.0-rc2 \
  --controls /absolute/path/to/CONTROL_MANIFEST.json \
  --out-dir physics_next/verification/centered_run01
```

The merged controls manifest has schema `komorebi.physics.centered-controls.v1`.
Its `controls` array contains `id`, `kind`, `path`, and, for rejections,
`expected_regex`. Kinds are `positive`, `elaboration_reject`, and `policy_reject`.
Paths are relative to the manifest's parent directory and must start with
`positive_controls/` or `negative_controls/`. Include both policy control files
under `control_sources/` in the merged collection. Their entries are provided in
`control_sources/POLICY_CONTROL_ENTRIES.json`.

The custom-axiom control must first compile successfully. Its isolated module is
then imported into the recursive axiom auditor and rejected there. A missing
import, unknown identifier, timeout, resource exhaustion, or parser error cannot
count as a successful negative control.

The auditor inventories every imported environment constant owned by the five
root modules, including definitions and generated helpers. It rejects unsafe or
partial declarations and any transitive axiom other than `propext`,
`Classical.choice`, or `Quot.sound`. Each root module also receives actual
`leanchecker` replay. This replay uses the same Lean kernel and imported
dependencies, not a second independent proof assistant.

The shipped runtime manifest is pinned. Before and after the proof run, every
declared runtime file or symlink is checked against it, except the nine mutable
dependency Git index files. Their actual hashes and exclusions are still
recorded. This deliberately does not turn the historical all-files identity
failure into a pass. Compiler, source and cached-proof bytes must match.

The passing receipt binds exact source snapshots, command logs, declared
runtime endpoints, declaration inventory, controls and freshly generated local
objects. Failed attempts retain their output and a failing receipt. The runner
does not itself certify the entire physics history, sampled spatial lattices,
interacting physics, or cosmological production.
