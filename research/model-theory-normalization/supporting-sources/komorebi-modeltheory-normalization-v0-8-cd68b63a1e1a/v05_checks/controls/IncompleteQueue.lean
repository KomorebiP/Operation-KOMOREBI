import CertifiedExamples
open Komorebi.Discovery Komorebi.Discovery.Certified Komorebi.Discovery.CertifiedExamples
example : replaySource A O (valid.take 3) = some answer := by decide +kernel
