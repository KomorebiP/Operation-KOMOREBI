import PaperIRelease.AlgebraPreorder
import PaperIRelease.AlgebraTransfer
import PaperIRelease.CategoryExport
import PaperIRelease.GrammarPaths
import Lean
open Lean Meta Elab Command
run_cmd do
  let parents : Array Name := #[`Komorebi.PaperIRelease.CategoryExport.evaluateTransported, `Komorebi.PaperIRelease.operatorWord, `Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap, `Komorebi.PaperIRelease.StrictPath, `Komorebi.PaperIRelease.CategoryExport.evaluate, `Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word]
  let runtimeNames : Array Name := #[`Komorebi.Seed.instReprOperatorExpr.repr._unsafe_rec, `Komorebi.PaperIRelease.CategoryExport.evaluateTransported._unsafe_rec, `Komorebi.PaperIRelease.operatorWord._unsafe_rec, `Komorebi.Seed.OperatorExpr.eval._unsafe_rec, `Komorebi.PacketNaturalityCompletion.Reachability.wordApply._unsafe_rec, `Komorebi.FiniteDifference.iteratedWeightedDiff._unsafe_rec, `Komorebi.FiniteAlgorithms.orbitClosureIter._unsafe_rec, `Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap._unsafe_rec, `Komorebi.PaperIRelease.StrictPath._unsafe_rec, `Komorebi.PaperIRelease.CategoryExport.evaluate._unsafe_rec, `Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word._unsafe_rec, `Komorebi.PathGraphKrylov.krylov._unsafe_rec, `Komorebi.FiniteDifference.iteratedDiff._unsafe_rec]
  for name in parents do
    let info ← getConstInfo name
    let axioms ← Lean.collectAxioms name
    let typ ← liftTermElabM <| Meta.ppExpr info.type
    let used := info.getUsedConstantsAsSet.toArray
    let partialRefs := used.filter (fun n => runtimeNames.contains n)
    let row := Json.mkObj [
      ("name", toJson name.toString), ("partial", toJson info.isPartial),
      ("unsafe", toJson info.isUnsafe), ("type", toJson typ.pretty),
      ("axioms", toJson (axioms.map Name.toString)),
      ("direct_constants", toJson (used.map Name.toString)),
      ("runtime_helper_references", toJson (partialRefs.map Name.toString))]
    liftIO <| IO.println ("DIAGNOSTIC_PARENT " ++ row.compress)
#print Komorebi.PaperIRelease.CategoryExport.evaluateTransported
#print axioms Komorebi.PaperIRelease.CategoryExport.evaluateTransported
#print Komorebi.PaperIRelease.operatorWord
#print axioms Komorebi.PaperIRelease.operatorWord
#print Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap
#print Komorebi.PaperIRelease.StrictPath
#print axioms Komorebi.PaperIRelease.StrictPath
#print Komorebi.PaperIRelease.CategoryExport.evaluate
#print axioms Komorebi.PaperIRelease.CategoryExport.evaluate
#print Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word
#print Komorebi.PaperIRelease.CategoryExport.evaluateTransported._unsafe_rec
#print axioms Komorebi.PaperIRelease.CategoryExport.evaluateTransported._unsafe_rec
#print Komorebi.PaperIRelease.operatorWord._unsafe_rec
#print axioms Komorebi.PaperIRelease.operatorWord._unsafe_rec
#print Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap._unsafe_rec
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap._unsafe_rec
#print Komorebi.PaperIRelease.StrictPath._unsafe_rec
#print axioms Komorebi.PaperIRelease.StrictPath._unsafe_rec
#print Komorebi.PaperIRelease.CategoryExport.evaluate._unsafe_rec
#print axioms Komorebi.PaperIRelease.CategoryExport.evaluate._unsafe_rec
#print Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word._unsafe_rec
#print axioms Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word._unsafe_rec

#print Komorebi.PaperIRelease.GrammarAlgebra.TypedData.pathMap._unary
#print Komorebi.PaperIRelease.GrammarAlgebra.TypedPath.word._unary
