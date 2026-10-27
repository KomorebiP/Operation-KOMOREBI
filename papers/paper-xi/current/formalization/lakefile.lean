import Lake
open Lake DSL

package paperxi_release where
  moreLeanArgs := #["-DmaxHeartbeats=3000000"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"

@[default_target]
lean_lib PaperXI where
  globs := #[.one `PaperXI]

lean_lib PaperXITerminal

lean_lib PaperXIAdditions
