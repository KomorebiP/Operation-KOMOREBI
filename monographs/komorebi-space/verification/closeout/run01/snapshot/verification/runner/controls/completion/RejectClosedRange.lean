import KomorebiSpace.DiagonalRangeObstruction

open KomorebiSpace.DiagonalRegularization

-- Deliberate mutation: deleting the negation must not elaborate.
example : IsClosed (Set.range T) := T_not_closed_range
