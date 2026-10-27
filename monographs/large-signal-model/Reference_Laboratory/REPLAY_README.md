# Reference laboratory replay

All 29 reference scripts were freshly replayed with the supplied exact inputs and declared dependencies. The current source-bound result is verification/reference_replay.json. Outputs were regenerated during that run, so the original package's old MANIFEST and SHA256SUMS describe the preserved original archive rather than this refreshed output tree. The original package is included as Original_Reference_Package.zip; use a fresh extraction of that file when running --verify-hashes before replay.

These finite and exact-arithmetic checks do not replace the Lean proofs. To replay the refreshed laboratory after installing requirements-reference.txt, use python run_reference_checks.py --session your_session. Generated reports and figures are part of the run, not a new mathematical proof. The retained historical README's --verify-hashes command applies to a pristine extraction of Original_Reference_Package.zip.
