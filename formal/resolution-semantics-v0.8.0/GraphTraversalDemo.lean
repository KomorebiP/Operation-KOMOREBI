import GraphTraversalExamples

def main : IO Unit := do
  for (label, result) in KRS.Graph.TraversalExamples.report do
    IO.println s!"{label}: {repr result}"
