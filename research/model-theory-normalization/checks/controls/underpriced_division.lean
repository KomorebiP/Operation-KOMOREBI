module
public import BinaryExamples

example : (Komorebi.Binary.divEval (Komorebi.Binary.ofNat 255) (Komorebi.Binary.ofNat 13)).2 ≤ 10 := by decide +kernel
