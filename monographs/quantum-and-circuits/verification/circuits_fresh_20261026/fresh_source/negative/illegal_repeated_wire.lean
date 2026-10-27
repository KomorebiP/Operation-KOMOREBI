import CircuitObstructions
open CircuitObstructions
def bad : Gate Bool := .cnot false false (by decide)
