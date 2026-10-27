# Assumption review — Block 08

**New source admission: Core 5.3, label `r:lowerbound`.** The book and all 30 preceding substantive modules are unchanged.

| Formal object | Required premise and checked boundary |
|---|---|
| `Tree E Bool C h` | Literal finite report tree. `Bool` is the binary alphabet. A horizon is not the actual depth. |
| `Model.Valid` | Nonempty current support, uniformly permitted experiment, actual post-state update, exactly the live children, common successful terminal. |
| `Scope.immutable` | The complete modeled state is unchanged. A destructive reset fails this condition even if its eventual repair is valid. |
| `Scope.singleton` | A fixed repair succeeds in at most one modeled state. Existence of a successful repair for every case is supplied by the actual successful tree; unused labels need not work. |
| `Scope.query_cost` | One scalar natural-number unit per query. No cost of compilation or scope validation is included in this online measure. |
| `Scope.terminal_cost` | One unit on every nonempty support. The proof does not impose an invalid empty-support maximum identity. |
| Leaves and records | Every possible case reaches a singleton leaf, no impossible leaves are installed, unary queries stay counted. |
| `Nat.clog` | Exact natural ceiling logarithm characterized by a power inequality, including n=1. No approximate real log. |
| `profile` to `execute` | A maximizing live branch supplies an actual initial-state witness. Lower bound is not merely a loose profile overestimate. |
| Frontier closure | Validity and simultaneous attainment of both coordinates are essential. Only one coordinate or a correct tree shape is insufficient. |
| Finite scope gate | State, action and artifact types finite. The guard examines exact table fields and all finite support-dependent terminal costs, not names or old cache labels. |
| Negative scope result | Means not admitted by this restricted theorem; does not imply infeasibility or falsity of every claim about the revised model. |
| Larger horizons | The same certified tree is padded without inserting queries, so all larger finite horizons share the singleton frontier. |
| Stronger lower-bound scope | Total permissions and a repair for every state are not necessary for a lower bound on an already successful valid tree. The source assumptions are included. |

The general source proof was not weakened. Binary tree edge counting and logarithmic information bounds are established elementary mathematics, not priority claims. Same-kernel checking validates formal terms under the pinned imported environment; it does not certify model adequacy or independent origin.
