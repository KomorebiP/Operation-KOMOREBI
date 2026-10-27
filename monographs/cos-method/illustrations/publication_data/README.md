# Publication figure inputs

The following files are byte-for-byte copies of members of the retained archive
`provenance/K-COS_Query_Adaptive_Spectral_Packetization_v0.1_Source.zip`:

- `adaptive_certificate_accuracy.csv`
- `adaptive_runtime_scaling.csv`
- `adaptive_tolerance_ladder.csv`

The exact member paths and SHA-256 digests are recorded in
`verification/figure_pass/publication_audit.json`. These are original experiment
records, not newly measured results.

`accuracy_extreme_summary.csv` contains two explicitly rounded values transcribed
from the accuracy chapter: at target log10 probability -5000, requests 1e-16 and
1e-18 achieved displayed ratio widths of approximately 3.05e-18 and 9.20e-20.
The chart uses these as rounded summaries, not as newly reconstructed full
interval endpoints. It does not replace the authoritative directed records.

All other empirical or model inputs are read directly from the unchanged
`engine/` CSV files, the corrected decimal width record in
`verification/proofread_checks/`, or the retained running-example record in
`verification/current_revision/`. The exact paths and hashes appear in the
per-figure manifest.
