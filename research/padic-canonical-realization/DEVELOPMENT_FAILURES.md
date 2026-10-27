# Block34 unsuccessful attempts and their resolution

1. ResidualBehavior's first draft included an unused CommRing assumption in two
pure word lemmas, attempted a non-definitional change before unfolding wordMap,
and used a nonexistent Set.image_range identifier. Explicit omission/unfolding
and direct set-image witnesses repaired the statements. No hypothesis was dropped
from any theorem that required it.
2. The canonical image codomain needed an explicit change from a subtype alias to
its underlying submodule for rewriting. The corrected generic proof compiled.
3. The mask residual-finiteness theorem needed an explicit Fintype instance for
its reachable source before constructing the quotient's finiteness instance.
4. A finite-difference proof unfolded the difference system before rewriting its
run law. Separating those steps fixed it. Warning-as-error also rejected a deprecated
push_neg tactic; the supported push Not form was used without disabling warnings.
5. Concrete scaling tests initially used natural nsmul numerals where an explicit
ZMod scalar was intended. Explicit finite-ring scalar annotations and a proved
3*2=1 mod5 equality replaced fragile normalization. No expected behavior changed.
6. While adding the residual-simulation field to the certificate, a text edit
also inserted a field declaration into its constructor. The compiler rejected that
syntax. The failed source is retained. A development loop did continue to later
probes using prior compiled objects; those passes are NOT authoritative evidence.
The field was corrected, dependent probes rerun, and the final runner clears all
project-local objects before checking the complete frozen source.

Predecessor archive/hash replay and runtime extraction succeeded in this turn.
Mathematical restriction witnesses are intentional counterexamples to stronger
claims, not failures of the proved statements. Additional final-run failures, if
any, are recorded by results/FINAL_RUN.json and must prevent release promotion.

All 17 authoritative final phases passed. No final-run timeout or failed assertion occurred.
