import Lake
open Lake DSL

package KomorebiPadicProject where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @
  "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"

@[default_target]
lean_lib KomorebiPadic where
  srcDir := "lean"
  moreLeanArgs := #["-DwarningAsError=true"]
