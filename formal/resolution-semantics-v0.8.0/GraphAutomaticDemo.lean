import GraphAutomaticExamples

def main : IO Unit := do
  for (label, result) in KRS.Graph.AutomaticExamples.report do
    IO.println s!"{label}: {result}"
