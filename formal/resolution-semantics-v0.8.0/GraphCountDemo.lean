import GraphCountExamples

def main : IO Unit := do
  for (name, count) in KRS.Graph.CountExamples.report do
    IO.println (name ++ ": " ++ toString count)
