# Data and evaluation policy

## Public training data

Bayesian calibration for version 0.3.0 uses only the official public
ARC-AGI-2 training challenges and training solutions. Official grids are not
redistributed in this repository.

## Parameter split

Task identifiers are partitioned deterministically by a BLAKE2 hash:

- approximately 80 percent for Bayesian calibration
- approximately 20 percent for a parameter holdout

The saved family priors and Bayesian regression are fitted only on the
calibration partition. The release report gives results for both partitions.

The holdout is a machine-level parameter holdout, not a claim that its tasks
were historically unseen by every earlier project version. Version 0.2.0 was
already audited across the full public training corpus.

## Public evaluation

Version 0.2.0 used the public evaluation split once after its declared freeze.
That result is retained only as historical material. Version 0.3.0 is not tuned
against those public-evaluation solutions, and the new calibration script has
no path that loads them.

## Competition test split

The test challenge file has no local solutions. It is used only to validate
runtime completion, output count, dimensions, color range, and two-attempt JSON
structure.

## Future development

New program families should be developed on public training tasks. A new
calibration file, source hash, parameter-holdout report, and runtime audit must
be recorded before any later external evaluation.
