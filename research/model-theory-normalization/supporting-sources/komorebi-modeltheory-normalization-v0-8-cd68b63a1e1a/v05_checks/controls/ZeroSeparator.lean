import CertifiedExamples
open Komorebi.Discovery Komorebi.Discovery.Certified Komorebi.Discovery.CertifiedExamples
example : checkMembership AA O [] (![2] : Fin 1 → R) (.separation ![0]) = some false := by decide +kernel
