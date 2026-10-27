import CircuitObstructions
open CircuitObstructions CircuitObstructions.Examples
example : packet swapBoundary swapCircuit swapSuffix false .target = true := by decide
