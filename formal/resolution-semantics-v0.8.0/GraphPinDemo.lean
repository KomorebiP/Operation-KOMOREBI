import GraphPinExamples

def main : IO Unit := do
  for (label, count) in KRS.Graph.PinExamples.report do
    IO.println s!"{label}: {count}"
