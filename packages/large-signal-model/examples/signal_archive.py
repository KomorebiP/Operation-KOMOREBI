"""Save and load source signal coordinates, not a trained model checkpoint."""
import argparse
import json
from pathlib import Path
import numpy as np
from komorebi_pr_lasm import analyze_signal, save_signal_archive, load_signal_archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('results/example_signal.npz'))
    output = parser.parse_args().output
    original = analyze_signal(np.linspace(-2, 3, 60), modulus=7, maximum_depth=6)
    path = save_signal_archive(original, output)
    loaded = load_signal_archive(path)
    assert np.array_equal(loaded.spatial, original.spatial)
    print(json.dumps({"archive": str(output), "length": loaded.length,
                      "effective_depth": loaded.effective_depth,
                      "source_bitwise_equal": True,
                      "scope": "source coordinates only; model and agent state are not serialized"}, indent=2))


if __name__ == '__main__':
    main()
