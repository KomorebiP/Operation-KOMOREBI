# Source check and novelty boundary

Checked September 11, 2026.

Primary source: The Stacks Project, Section 91.2, tag 08S3,
"Deformations of rings and the naive cotangent complex".
https://stacks.math.columbia.edu/tag/08S3

In particular, Lemma 91.2.1 and its proof describe square-zero map-lifting
obstructions using a relation module and show that changing chosen lifts changes
the defect by the differential/derivation term. This is the standard background
for the relation-and-correction mechanism used here. The new Lean files prove
their concrete equations directly; this source is not imported as a new axiom.

Related caution: Stacks Section 98.23, tag 07YJ, explicitly distinguishes the
naive cotangent complex from the full cotangent complex and states the relevant
derived-base-change/Ext formula. The present code does not identify a bare
cotangent homology module with every arithmetic obstruction space.
https://stacks.math.columbia.edu/tag/07YJ

Classification: the general mechanism is standard deformation/obstruction
algebra. This work develops checked specialized formulations and connects them
to the existing Komorebi branch. No comprehensive novelty search or historical
priority claim was performed. The global Strong Artin hypotheses remain open.
