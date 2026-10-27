import CertifiedExamples
open Komorebi.Discovery Komorebi.Discovery.Certified Komorebi.Discovery.CertifiedExamples
example : checkMembership AA O [([],0)] (![1] : Fin 1 → R) (.combination [2]) = some true := by decide +kernel
