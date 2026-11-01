import GraphExamples

def main : IO Unit := do
  for (name, result) in KRS.Graph.Examples.report do
    IO.println (name ++ ": " ++ reprStr result)
