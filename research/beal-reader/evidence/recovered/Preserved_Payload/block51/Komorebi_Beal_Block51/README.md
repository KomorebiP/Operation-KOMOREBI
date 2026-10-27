# Komorebi Beal — Block 51: Integral monodromy and extension depth

Release: v5.1.0, 2026-09-19.

**The full Beal conjecture and the complete (3,5,7) signature remain
unresolved.** This block proves a sharp local depth theorem and applies it
as a necessary support restriction on the inherited reducible branch.

Start with `work51/REPORT.md`, `work51/PROOF_BOUNDARY.md`, and
`work51/VERIFICATION.md`. Detailed proofs are in `work51/notes/`.
The next research block is specified in `work51/CONTINUE_HERE.md`.

From the extracted root, run:

    python verify.py
    python verify.py --replay-predecessors

Python 3.10+ and its standard library suffice for the new checks and the
six selected historical replays. Other inherited scripts may have their
own dependencies and are outside this selected replay command.
No web access is needed for these replays. The runner uses isolated
copies and writes its report beside, not inside, the package by default.
It checks archived checksums before execution and treats timeouts as
inconclusive. See `work51/REPRODUCE.md` for scope and exact commands.

The original Block 49 full archive and Block 50 extension checkpoint are
preserved in `predecessor/`. Their recovered work directories are frozen.
Block 50's interrupted independent-review status remains explicit; this
release adds a fresh self-review, not a second-agent acceptance.

No new Lean proof is claimed. Earlier source and verification records are
retained with their inherited boundaries. Byte integrity is not proof of
mathematical correctness. The bundled third-party PDF was already part
of the user's Block 50 checkpoint; other source versions and applications
are recorded in `work51/source_records/SOURCE_CHECK.md`.
