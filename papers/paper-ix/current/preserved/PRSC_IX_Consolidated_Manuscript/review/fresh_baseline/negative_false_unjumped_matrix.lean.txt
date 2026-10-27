module
public import RecurrenceExamples
open KomorebiPaperIX FibonacciPackets Matrix
example : Companion.packet companion initial 2 0 1 = companion *ᵥ initial := by
 ext i
 fin_cases i <;> norm_num [Companion.packet, Companion.orbit, companion, initial, pow_two, Matrix.mul_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two]
