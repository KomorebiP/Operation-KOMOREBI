"""Block 12 finite active-falsification primitives.

Author: Komorebi P.
"""

from .active_planner import (
    ActiveProbePlan,
    ProbeEvaluation,
    audit_plan,
    falsify_versions,
    plan_probe,
    unanimous_action,
)
from .ambient_recovery import (
    AmbientRecoveryCompilation,
    AmbientRecoveryProgram,
    compile_ambient_recovery,
)
from .axis_sequence import (
    AxisSequenceCompilation,
    AxisSequenceProgram,
    compile_axis_sequence,
)
from .compiler import compile_falsification_corpus, compile_falsification_task
from .counterfactual import (
    Probe as CounterfactualProbe,
    evaluate_record as evaluate_counterfactual_record,
    freeze_experiment as freeze_counterfactual_experiment,
    generate_probes as generate_counterfactual_probes,
    infer_contracts as infer_counterfactual_contracts,
)
from .local_transition import (
    LocalTransitionCompilation,
    SeparatorAxisProgram,
    compile_local_transition,
)
from .object_composition import (
    ObjectCompositionCompilation,
    RoleCarriedObjectProgram,
    compile_object_composition,
)
from .periodic_lattice import (
    BoundaryKeyProgram,
    PeriodicLatticeCompilation,
    compile_periodic_lattice,
)
from .shape_constructors import (
    ShapeConstructorCompilation,
    ShapeConstructorProgram,
    compile_shape_constructors,
)

__all__ = [
    "ActiveProbePlan",
    "AmbientRecoveryCompilation",
    "AmbientRecoveryProgram",
    "AxisSequenceCompilation",
    "AxisSequenceProgram",
    "BoundaryKeyProgram",
    "CounterfactualProbe",
    "LocalTransitionCompilation",
    "ObjectCompositionCompilation",
    "ProbeEvaluation",
    "PeriodicLatticeCompilation",
    "RoleCarriedObjectProgram",
    "SeparatorAxisProgram",
    "ShapeConstructorCompilation",
    "ShapeConstructorProgram",
    "audit_plan",
    "compile_ambient_recovery",
    "compile_axis_sequence",
    "compile_falsification_corpus",
    "compile_falsification_task",
    "compile_local_transition",
    "compile_object_composition",
    "compile_periodic_lattice",
    "compile_shape_constructors",
    "evaluate_counterfactual_record",
    "falsify_versions",
    "freeze_counterfactual_experiment",
    "generate_counterfactual_probes",
    "infer_counterfactual_contracts",
    "plan_probe",
    "unanimous_action",
]
