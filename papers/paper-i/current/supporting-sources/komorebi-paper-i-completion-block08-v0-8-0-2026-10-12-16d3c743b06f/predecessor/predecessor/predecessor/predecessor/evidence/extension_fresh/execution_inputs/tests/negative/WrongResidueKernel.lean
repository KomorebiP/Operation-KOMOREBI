import IntrinsicBoundaryConsumers
open scoped Pointwise
open PaperIBlock04Tests PaperIBlock03Tests
open Komorebi.PaperICompletion4.IntrinsicPrimary
-- The exact kernel is pX_p, not a proof of injectivity of the unquotiented map.
example : (primaryToGlobal (Module.AEval' repeatedOperator) quadratic).ker = ⊥ :=
  nonlinear_primary_global_kernel_exact
