module
public import BinaryExamples

example : (Komorebi.Binary.subEval [false,false,false,false] [true,false,false,false] false).1.2 = false := by decide +kernel
