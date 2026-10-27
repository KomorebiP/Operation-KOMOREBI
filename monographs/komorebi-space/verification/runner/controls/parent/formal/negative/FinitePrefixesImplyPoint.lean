import KomorebiSpace.FinitePrefixBoundary
-- Supplying separately inhabited prefixes does not supply a coherent global point.
example : Nonempty KomorebiSpace.FinitePrefixBoundary.escaping.Point := by
  exact KomorebiSpace.FinitePrefixBoundary.every_prefix_nonempty 0
