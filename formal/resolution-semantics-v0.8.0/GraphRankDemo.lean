import GraphRankExamples

def main : IO Unit := do
  for (label, result) in KRS.Graph.RankExamples.report do
    IO.println (label ++ ": " ++ result)
