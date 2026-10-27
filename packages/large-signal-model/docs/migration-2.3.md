# Migration from core 2.1.0 to 2.3.0

This is the core `komorebi-pr-lasm` lineage. The separate `komorebi-arc3-offline`
agent package also has a 2.2.0 release. Its numbering does not identify an
intermediate revision of this source tree. Do not install both distributions
into one Python environment because they share an implementation namespace.

## Intentional behavioral corrections

Continuous image values no longer produce rounded or clipped color coordinates.
`AtlasAnalysis.color` is `None` for non-categorical data. Inspect
`available_atlases` rather than assuming every input has a color atlas.
The corresponding color feature block is zero when the color atlas is absent.
Read the availability field to distinguish absence from observed color data.

Default Haar depth is the largest requested depth actually supported by both
image dimensions. An odd dimension permits only the root representation.
Explicit unsupported depths raise `ValueError`. No padding or crop is hidden.

The ultimate packetizer's exact archive and signature now refer to the original
categorical image. The legacy object/statistical proxy remains 64 by 64, and its
salient-point coordinates use that proxy. Arbitrary-shape exact analysis is not
a validated arbitrary-resolution interactive-action adapter.

Exact coordinate arrays own their data and reject ordinary mutation. Make an
explicit copy to build an approximate view. This is protection against accidental
mutation, not a security boundary against a caller changing NumPy flags.

Positive integer moduli and depths are enforced without truncating floats.
Invalid empty inputs, nonfinite values, complex inputs to the real-only APIs,
and integer arrays outside the conservative exact float64 conversion range
raise errors. The supported integer input range is [-2**53, 2**53].

A real orthogonal Fourier projector requires a binary selector invariant under
negating frequency indices. A general asymmetric complex spectral filter is not
this API. Use a separately specified complex operator instead of silently
throwing away an imaginary component.

Packet synthesis rejects unknown paths, duplicate paths, overlapping ancestors,
incomplete prunings and wrong coefficient shapes. Existing valid complete
prunings retain their behavior. Atlas weights must be finite and nonnegative,
with at least one nonzero value.

## Statistical correction

Candidate fits retain their resolution-specific output heads. Candidate scores
now use the same smallest nested state prefix plus the five common outcome
channels. Models with incomparable target prefixes are rejected. Log densities
on differently sized target spaces are no longer directly compared.

Scores use a training/validation split inside the supplied training records.
After scoring, each surviving candidate is refit on all those training records.
`refit_on_all_records=False` is available for explicit legacy comparisons.
The old and new headline RMSE numbers do not describe identical training
protocols. The reference files remain immutable.

`fit_report` records insufficient data, failed candidates and target-comparability
failures. All-zero candidate mass is an error rather than a NaN probability vector.
Clipped win, loss and change outputs remain model scores, not a newly established
calibration guarantee.

## New public APIs

`analyze_signal`, `SignalAnalysis1D`, `PolyphaseFIR`, `StreamingFIR`,
`polyphase_analyze`, `polyphase_synthesize`, `save_signal_archive`, and
`load_signal_archive` provide standalone finite signal operations. Archive schema
1 saves the source vector and analysis settings. It does not serialize a learned
model, graph, replay history or agent identity.
