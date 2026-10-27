"""Learn a declared two-delay recurrence using only four observed values.

Run: python examples/output_only_example.py
Requires SymPy. No hidden matrices are passed to the learner.
"""
from __future__ import annotations
from pathlib import Path
import sys
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from observable_reference import learn_delay, forecast_scalar


def main() -> None:
    outputs=[sp.Integer(1),sp.Rational(1,2),sp.Rational(1,2),sp.Rational(11,24)]
    model=learn_delay(outputs,h=2)
    print('Observed values:',outputs)
    print('Exact fitted transition in delay coordinates:')
    print(model.ambient_transition)
    print('Next six outputs:',forecast_scalar(model,outputs[-2:],6))
    print('Verified from samples: kernel consistency and closure of the observed span.')
    print('Not verified from samples alone: coverage and closure of the true physical predictive space.')


if __name__=='__main__':
    main()
