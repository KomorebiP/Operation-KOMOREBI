"""Learn a finite typed operator from data, then evaluate untouched test records.

The data generator is controlled and in-grammar. This demonstrates parameter
learning and candidate selection, not discovery of a new operator language.
"""
import json
import numpy as np
from komorebi_pr_lasm import LASMProgram, ProjectorResolvedLargeSignalModel
from komorebi_arc3_offline.lasm_synthetic import generate_program_identification_scenario


def main() -> None:
    scenario = generate_program_identification_scenario('quadratic-spatial', steps=100, seed=4)
    shared = dict(resolution='macro', state_rank=12, atlas_rank=24, interaction_rank=6)
    programs = (
        LASMProgram('linear-spatial', 'linear', atlas='spatial', **shared),
        LASMProgram('quadratic-spatial', 'quadratic', atlas='spatial', **shared),
        LASMProgram('linear-fourier', 'linear', atlas='fourier', **shared),
        LASMProgram('delay-portfolio', 'delay', atlas='portfolio', **shared),
    )
    model = ProjectorResolvedLargeSignalModel(programs=programs, complexity_penalty=.0012,
                                             mechanism_penalty=.35, resolution_penalty={'macro':0.0})
    model.fit(scenario.transitions[:75])
    predicted, truth = [], []
    for record in scenario.transitions[75:]:
        estimates = [item.regression.predict(item.program.design_transition(record))[0][0]
                     for item in model.fitted]
        weights = np.asarray([item.posterior_probability for item in model.fitted])
        predicted.append(weights @ np.vstack(estimates))
        truth.append(programs[0].targets(record))
    error = float(np.sqrt(np.mean((np.vstack(predicted)[:, :12]-np.vstack(truth)[:, :12])**2)))
    assert model.posterior_summary()['best_program'] == 'quadratic-spatial'
    print(json.dumps({"training_records":75,"unseen_test_records":25,
                      "heldout_state_rmse":error,"posterior":model.posterior_summary()},indent=2))


if __name__ == '__main__':
    main()
