"""Regenerate the two analytical figures; neither is agent-experiment data.

Requires matplotlib. Underlying survival values use exact rational arithmetic;
conversion to floating point occurs only for rendering. Run from any directory.
"""
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
PDF_METADATA = {'CreationDate': None, 'ModDate': None}


def survival_curve(repair: Fraction, horizon: int = 150) -> list[float]:
    if horizon < 0 or not Fraction(0) <= repair <= Fraction(9, 10):
        raise ValueError('Invalid horizon or repair probability.')
    healthy, degraded = Fraction(1), Fraction(0)
    failure = degradation = Fraction(1, 10)
    values = []
    for _ in range(horizon + 1):
        values.append(float(healthy + degraded))
        healthy, degraded = (
            healthy * (1 - degradation) + degraded * repair,
            healthy * degradation + degraded * (1 - repair - failure),
        )
    return values


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams['pdf.fonttype'] = 42
    fig, ax = plt.subplots(figsize=(7.2, 3.8), layout='constrained')
    ax.plot(range(4), [k - 2 for k in range(4)], 'o-',
            label="Outsider's entry gain")
    ax.plot(range(1, 5), [k - 3 for k in range(1, 5)], 's--',
            label="Incumbent's payoff")
    ax.axhline(0, linewidth=0.8, linestyle=':')
    ax.set(xlabel='Number of existing adopters',
           ylabel='Payoff relative to nonadoption',
           xticks=range(5), yticks=range(-2, 3))
    ax.legend(loc='upper left')
    ax.grid(axis='y', alpha=0.25)
    fig.savefig(OUT / 'formation_barrier.pdf', bbox_inches='tight', metadata=PDF_METADATA)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.8), layout='constrained')
    ax.plot(range(151), survival_curve(Fraction(0)),
            label='No repair: expected lifetime 20 epochs')
    ax.plot(range(151), survival_curve(Fraction(2, 5)),
            label='Repair probability 0.4: expected lifetime 60 epochs')
    ax.set(xlabel='Epoch', ylabel='Probability of remaining operational',
           xlim=(0, 150), ylim=(0, 1.02))
    ax.legend(loc='upper right')
    ax.grid(alpha=0.25)
    fig.savefig(OUT / 'institutional_survival.pdf', bbox_inches='tight', metadata=PDF_METADATA)
    plt.close(fig)
    print('Regenerated both analytical figures.')


if __name__ == '__main__':
    main()
