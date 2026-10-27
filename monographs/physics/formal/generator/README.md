# Checked free-Dirac strong generator

This overlay extends the byte-preserved Block 49 source archive in the parent directory. It checks the full strong generator and its exact domain in coefficient and physical torus spaces. It does not contain formal centered-resolvent or quadratic-rate proofs.

`KomorebiPhysics/Relativistic3DGeneratorBridge.lean` is the accepted source. `CheckGeneratorBridge.lean`, `AuditGeneratorBridge.lean`, and `PositiveGeneratorSmoke.lean` are positive checks. The four `NegativeGenerator*.lean` files are deliberate rejection tests; the placeholder is intentionally invalid and must not become an active import. `PhysicsRelease.lean` is the explicit operator-and-generator import entry point, not an assertion that the old aggregate physics root was freshly checked.

Run `python replay_generator.py --kit /path/to/exact-kit --work-dir /path/to/new-directory` from any directory. The script requires Linux x86-64 or WSL2 and the previously provided Lean 4.34.0-rc2 offline kit. It does not download dependencies. The complete kit is not in this source package.

The accepted production results are in the main package's `audit/closeout_2026-10-21/formal/`. The whole-book `RELEASE_VERIFICATION.md` states the current scope, failures, and remaining tasks. Original project code is MIT-licensed under the package's root grant. Third-party dependencies retain their own terms.
