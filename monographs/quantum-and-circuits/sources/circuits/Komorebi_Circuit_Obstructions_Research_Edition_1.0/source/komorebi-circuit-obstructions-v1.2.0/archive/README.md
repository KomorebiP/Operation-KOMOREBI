# Historical checkpoints

The ZIP files in `checkpoints/` are byte-identical copies of the ten conversation artifacts available at consolidation. `INDEX.json` lists sizes and SHA-256 hashes. The most recent Complete Packets and Projection checkpoint is the sole active mathematical source for this release. Its embedded predecessor was replayed through its documented runner.

The other ZIPs preserve earlier fusion, quotient, boundary, and restoration routes. They were byte-preserved, not all newly re-reviewed as current theorems. Embedded “continue” prompts describe past exploratory states and are not instructions for the current release.

Use `python scripts/verify.py --history` from the repository root to reproduce the active source checkpoint in an isolated build directory. Do not extract over the maintained source tree or overwrite historical baselines.
