# How the Komorebi works fit together

[Project overview](START_HERE.md) · [Three demonstrations](DEMONSTRATIONS.md) · [Browse every work](BROWSE.md) · [Current work queue](FINALIZATION_QUEUE.md)

Use this map to choose a route through the collection. It covers the twelve
core papers and selected connecting books. The [complete catalogue](BROWSE.md)
also includes research continuations, software and experiments.

**Read the relationships carefully.** The cards show subject groups and a
suggested learning order. The table under [documented connections](#documented-connections)
identifies specific uses named in retained source text. Neither is a complete
graph of theorem dependencies or a new review of those dependencies.

<a id="foundations"></a>

## Begin with the finite foundations

For a first mathematical reading, the suggested order is **Paper I → Paper II → Paper III**.
Vectors, matrices, linear maps, kernels and images provide a useful starting
background. Individual chapters state additional algebraic and analytic assumptions.

<div class="project-map" role="group" aria-label="Suggested foundation reading order">
<div class="map-card"><h3>1. Describe the parts</h3><p><a href="works/paper-i.md">Paper I: Typed systems and exact packet coordinates</a></p><p>Seeds, operator actions, packet families and reconstruction.</p><p><a href="demonstrations/PACKETS.md">Try operator reconstruction</a></p></div>
<div class="map-card"><h3>2. Compare resolutions</h3><p><a href="works/paper-ii.md">Paper II: Refinement, transfer and integral separation</a></p><p>Coarse and fine coordinates, weighted paths and lattice constraints.</p><p><a href="demonstrations/REFINEMENT.md">Try residue refinement</a></p></div>
<div class="map-card"><h3>3. Track compatibility</h3><p><a href="works/paper-iii.md">Paper III: Typed transfer and obstructions</a></p><p>Composable operations, chosen connections, nonlinear coordinates and defects.</p><p><a href="demonstrations/RECOVERY.md">Begin with a recovery obstruction</a></p></div>
</div>

[Realization Calculus](works/realization-calculus-book.md) collects the core
development. [Komorebi Space](works/komorebi-space.md) develops the broader
setting for comparing realizations. Their pages identify the relevant editions
and evidence.

## Choose an application or extension

The groups below organize subjects. They do not assert that every paper in one
group is a formal prerequisite of the next group.

<div class="project-map" role="group" aria-label="Core paper subject map">
<div class="map-card"><h3>Functions, signals and evolution</h3><p><a href="works/paper-iv.md">IV: Cyclic analytic functions and reciprocal families</a></p><p><a href="works/paper-v.md">V: Polyphase signal calculus</a></p><p><a href="works/paper-vi.md">VI: Transfer semigroups and their realizations</a></p><p>Begin with series, signal indexing or linear evolution as appropriate. Analytic convergence and probability assumptions belong to the selected result.</p></div>
<div class="map-card"><h3>Quantum and computation</h3><p><a href="works/paper-vii.md">VII: Quantum seed calculus</a></p><p><a href="works/paper-viii.md">VIII: Packet algorithms and exact compilation</a></p><p>Packet algebra connects to finite quantum examples and algorithms. Physical interpretation, performance and hardware behavior need their own evidence.</p></div>
<div class="map-card"><h3>Arithmetic and comparison</h3><p><a href="works/paper-ix.md">IX: Arithmetic packets and local deformation</a></p><p><a href="works/paper-x.md">X: Residual seeds and conditional completion</a></p><p><a href="works/paper-xi.md">XI: Arithmetic realization and conditional comparison</a></p><p><a href="works/paper-xii.md">XII: Patching support and conditional automorphic completion</a></p><p>Use each work's algebraic and arithmetic hypotheses. A finite construction does not discharge an open arithmetic premise.</p></div>
</div>

For an example before a paper, use the [core-paper example index](LEARNING_MAP.md#start-from-a-core-paper).
Paper XI's [Conjecture 66 obligations](works/paper-xi.md#before-you-start) remain
open. Paper XII retains its [original and amended claim distinction](works/paper-xii.md#before-you-start)
and explicit arithmetic inputs.

<a id="limits-and-repair"></a>

## Connect the books by the question you are asking

| Question | Starting works | Concrete introduction |
|---|---|---|
| What can a representation retain or recover? | [Realization Boundaries](works/realization-boundaries.md), [Information Realization](works/information-realization.md), [Sufficient Resolution](works/sufficient-resolution.md) | [Recovery demonstration](demonstrations/RECOVERY.md), then [kernels](examples/10_KERNELS.md). |
| How can an obstruction be repaired? | [Constructive Repair](works/constructive-repair.md), [Grounded Abstraction](works/monographs-grounded-abstraction.md) | [Repair directions](examples/25_REPAIR_MENUS.md) and [reusable calibration](examples/23_CALIBRATED_CONTINUATION.md). |
| How should a proof or inference retain its evidence? | [Proof Path Theory](works/proof-path-theory.md), [Komorebi Methodology](works/komorebi-methodology.md), [Certified Inference](works/certified-inference.md) | [Proof certificates](examples/21_PROOF_CERTIFICATES.md) and [a Gaussian update](examples/26_GAUSSIAN_UPDATE.md). |
| How do finite constructions enter models? | [Special Functions](works/monographs-special-functions.md), [Large Signal Model](works/monographs-large-signal-model.md), [Quantum and Circuits](works/monographs-quantum-and-circuits.md), [Physics](works/monographs-physics.md) | Start with the relevant [paper example](LEARNING_MAP.md#start-from-a-core-paper), then inspect the model's assumptions. |
| What changes with hidden state or interacting systems? | [Machine Societies](works/monographs-machine-societies.md), [Machine Native Reasoning](works/monographs-machine-native-reasoning.md) | [Hidden memory](examples/22_HIDDEN_MEMORY.md), followed by each work's recorded review scope. |

These are subject connections. A shared term such as “residual” or “packet” is
not sufficient to transfer a theorem between different settings.

## Documented connections

The following source passages support narrower statements than the broad
reading map. Read the linked statement and its hypotheses before using a result.

| Earlier work → later use | What the source actually records | Source |
|---|---|---|
| Paper I → Paper III's starting framework | The introduction credits Paper I with typed seeds, operator grammars, exact projector packets, generated hulls and reconstruction. This is a statement of background use. | [Paper III, purpose and formal status](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/finite-coordinates.html#L8). |
| Paper II → Paper III's coordinate transport | The canonical triangle holonomy result names the inherited `refineCoordinates_comp` and `refineCoordinates_self` declarations. This is an explicit inherited formal dependency recorded by the manuscript. | [Result and inherited names](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/finite-coordinates.html#L534), then the [refinement boundary](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/finite-coordinates.html#L543). |
| Earlier finite contracts → Paper III's release scope | The manuscript distinguishes its thirty original result environments from definitions and interfaces, and separates Paper III declarations from inherited results. | [Finite contract and its denominator](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-iii/finite-coordinates.html#L39). |

The coordinate-transport boundary matters: two complete coordinate presentations
are being compared. Discarding data or learning a coarse model introduces extra
structure. The inherited result does not automatically cover those operations.

This map records what the source says. It does not certify the source's proof
or rerun the inherited Lean projects. For exact formal declarations and replay
evidence, use the work's **Lean** and **Evidence** sections.

## Software routes

[Komorebi Math](https://github.com/KomorebiP/komorebi-math/blob/main/docs/README.md)
contains Python implementations of selected finite constructions.
[Polyphase Float](https://github.com/KomorebiP/polyphase-float/blob/main/docs/README.md)
provides C arithmetic with explicit precision and rounding on its supported
platform. The [three standalone demonstrations](DEMONSTRATIONS.md) need neither
library. [First runs](FIRST_RUN.md) provides their separate installation routes.

## Keep the current records together

Use the [finalization queue](FINALIZATION_QUEUE.md) for remaining work and
completion criteria, the [status catalogue](STATUS_CATALOG.md) for each
component's evidence, and the [records guide](RECORDS.md) for dated reviews and
their source bindings. These remain the maintained status records. This map
does not introduce a competing completion score.

[Project overview](START_HERE.md) · [Three demonstrations](DEMONSTRATIONS.md) · [Choose a reading route](READING_ROUTES.md)
