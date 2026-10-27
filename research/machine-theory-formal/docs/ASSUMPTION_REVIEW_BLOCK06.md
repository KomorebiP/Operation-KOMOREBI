# Block06 assumption and proof-obligation map

Source Core4.2, unchanged Reviewed Core0.2, printed p16, source lines565–574.

| Obligation | Formal object / proof route | Boundary |
|---|---|---|
| Accessible sender | Attained alpha; Valid | No hidden case argument or default on impossible inputs |
| Whole-fibre commonality | Common; valid_iff_common; encoder_exists_iff | Pairwise compatibility is insufficient |
| One artifact for all recipients | Audience.Accepts universally quantifies i after fixing c | Separate private messages do not satisfy this contract |
| Fixed actual decoder | Audience.run i accepts background i and artifact only | No synthesized replacement decoder |
| Output and resources | completed Result with output/work/peakSpace; permission conjunct | Counters are supplied execution semantics, not measured host work |
| Finite image | finite case type and attainedFintype | Alphabet may be larger; no efficient search inferred |
| Minimum exists | image_size_exists and cover_size_exists, Nat.find | Feasibility is explicit; empty cases handled |
| Minima coincide | encoder_within_iff; cardinality_budget_iff; minimum_image_eq_cover | A redundant codebook need not be exactly used |
| One witness | minimum_common_artifact | Does not splice separate optimum coordinates |
| Alphabet capacity | decoded_alphabet_bound | Decoder installation/storage still charged separately |
| Source example | xor_accepts_iff; xor_sender_valid; xor_minimum_codebook | Exact Bool XOR model, not learned language |
| Source collision | individually_possible_not_common | Every case soluble does not imply one accessible artifact |

All statements are complete Lean terms under the declared foundations; actual build and axiom acceptance are recorded by the current final/fresh receipts. These notes are project-authored review, not independent peer review.
