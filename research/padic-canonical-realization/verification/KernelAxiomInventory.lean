import KomorebiPadic
import Lean.Util.CollectAxioms
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  for (name, info) in env.constants.toList do
    if info.isTheorem then
      if let some idx := env.getModuleIdxFor? name then
        let mod := env.header.moduleNames[idx.toNat]!
        if mod.toString.startsWith "KomorebiPadic." then
          let axs ← collectAxioms name
          let text := String.intercalate "," (axs.toList.map Name.toString)
          liftIO <| IO.println s!"PROJECT_AXIOMS|{name.toString}|{mod.toString}|{text}"
