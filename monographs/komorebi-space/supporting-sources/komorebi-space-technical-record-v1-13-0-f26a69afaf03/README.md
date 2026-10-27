# Komorebi Space: technical record

This archive preserves the accepted formal baseline and the evidence for successive publication revisions.

- `accepted_verification/`, `publication/`, and `visual_revision/` retain every parent payload file byte for byte. Their statements describe the corresponding historical verification or visual-guide revision.
- `monograph_proofread/` records the current final monograph proofreading: exact source identities and changes, editorial reviews, build attempts and logs, PDF page coverage, and final render-image hashes. The full-page PNGs are reproducible and are not included.
- `monograph_proofread/parent/` preserves the complete immediate parent publication ZIP and its external verification JSON. The prior technical README and checksum manifest are preserved beside that folder.

The current monograph PDF identity is recorded in `monograph_proofread/final_summary.json`. The current publication ZIP and this technical ZIP receive a separate independent delivery-verification report. Archive self-hashes are not embedded inside their own archives.

Production Lean, worked-example implementations, PDF/PNG figure assets, and the visual and Lean guide PDFs remain unchanged. The sole figure-source adjustment changes font-size commands in Figure 2 and is recorded with its exact hashes. The current work is an editorial revision; it does not claim a new full Lean compilation. Failed or superseded build attempts are retained with their reports so that the final accepted artifact can be distinguished from them.
