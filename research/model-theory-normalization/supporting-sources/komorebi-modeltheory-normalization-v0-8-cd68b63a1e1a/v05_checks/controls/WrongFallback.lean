import CertifiedExamples
open Komorebi.Discovery Komorebi.Discovery.Certified Komorebi.Discovery.CertifiedExamples
example : guardedPrimeDiscover 2 2 1 AA O badProposer = none := by decide +kernel
