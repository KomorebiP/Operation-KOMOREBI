import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : IsPrior (conditional (sharpP 0) sharpEvent) := by
  apply False.elim
  exact missing_event_conditional_not_prior (by
    constructor
    · intro i
      norm_num [conditional,FiniteInstruments.normalize,restrict_mass,sharpP_eventMass]
    · norm_num [conditional,FiniteInstruments.normalize,restrict_mass,sharpP_eventMass])
