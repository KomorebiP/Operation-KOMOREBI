import PaperIRelease.GraphReachability
import Mathlib.Order.Antisymmetrization
import Mathlib.Order.WellFoundedSet
variable {I : Type*} (r : I → I → Prop)
#synth IsPreorder I (Relation.ReflTransGen r)
#check Set.Finite.isPWO
#check Set.IsPWO.exists_le_minimal
#check Antisymmetrization.instPartialOrderAntisymmetrization
#check instPartialOrderAntisymmetrization
#check Minimal
#check Relation.ReflTransGen.head_induction_on
#check Relation.ReflTransGen.tail_induction_on
#check AlgebraGeneratedHull
#check Komorebi.PacketNaturalityCompletion.FullBlocks.restrictBlocks
#print Komorebi.PacketNaturalityCompletion.StrictNaturality.AlgebraGeneratedHull
