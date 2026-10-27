# Exact memory for partition evidence

The current state is a candidate set V of possible worlds. Evidence filters this
set by intersection. The target map t supplies the values that remain possible.
A correction signature records these possible values after every admitted event.

For a cell map c, admitted events are exactly preimages of sets of cell labels.
The actual EvidenceAlgebra proves the total-event and intersection laws. Its
event collection includes each single cell and excludes events splitting a cell.

An attainable pair is (c(w),t(w)) for some world w. The pair type is the range of
this map, not the entire product of cell labels and target values. In particular,
unused target values do not add bits. The ambient target type need not be finite
or fully attained. Finite worlds make the attained pair type finite.

## Classification

Occupancy records which attained pairs meet V. A single-cell query and one target
value recover membership of each pair from the signature. Conversely, for a union
of cells, the occupied pairs with cell label in the union determine exactly the
remaining target values. Thus signature equality is equivalent to occupancy
equality, including empty candidates and contradictory results.

Every occupancy S is realized by taking the full preimage of S under the map from
worlds to attained pairs. This differs from the written proof's choice of one
representative per pair, but realizes the same records. Surjectivity onto the
attained range gives every included pair, and the fibre definition excludes all
others. `memoryEquiv` is an actual equivalence between attained signatures and
subsets of the pair type. It gives the exact count 2^r.

## Fixed binary memory

Choose a finite enumeration of the r attained pairs. Its occupancy indicator is
an r-bit vector. The readout takes target values of occupied pairs. A cell-union
filter removes pairs outside its cells. The Lean definitions prove exact readout
and update, including every finite event sequence.

For a competing exact memory using b bits, the inherited correction contract
forces different signatures to initialize different retained states. Equivalently,
compose occupancy realization with its encoder to obtain an injection from the
2^r occupancy records into the 2^b bit strings. Binary cardinality monotonicity
gives r <= b. This is a worst-case fixed-width state bound on all candidate
subsets. It is not a variable-length, average-bit or runtime bound.

The formal construction uses classical finite enumeration. Its proof of finite
encoding does not certify a compiled memory implementation or its performance.

## Source and boundaries

The source endpoint retains the raw world, cell and target maps and the
nonempty-cell hypothesis as surjectivity. The internal classification is valid
even with unused cell labels because it counts attained pairs only.

The source sensor has eight worlds, four cells and four attained pairs, giving
sixteen signatures and four necessary and sufficient bits. Its current target
set can coincide for two candidates that later calibration separates. Additional
examples test mixed-target cells, repeated targets across cells, unused targets,
one-cell constant targets and empty worlds. Negative controls test removal of
single-cell evidence, evidence splitting a cell, and a too-short fixed-bit claim.

Source: `source/core_v0.2.tex`, `r:occupancy`, with the immediately preceding
partition-evidence setup. Formal entry points are in `THEOREM_MAP.json`.
