from __future__ import annotations

import json
import math
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

import abc_offline_exhaustive as engine


def check_singular_lifting() -> None:
    roots = engine.all_roots_prime_power(1, 1, 2, 2, 3)
    assert roots == [1, 3, 5, 7]


def check_semiconvergents() -> None:
    values = engine.convergents_and_semiconvergents(engine.mpm.sqrt(2), 20, 20)
    pairs = {(p, q) for p, q, _ in values}
    assert (1, 1) in pairs
    assert (3, 2) in pairs
    assert (7, 5) in pairs


def check_record_neighbor() -> None:
    config = json.loads(json.dumps(engine.PROFILES['quick']))
    config['q_min'] = 1.60
    config['min_c'] = 1
    config['cf']['enabled'] = False
    config['plateau']['enabled'] = False
    config['neighbor'] = {
        'enabled': True,
        'value_max': 10**8,
        'prime_max': 127,
        'support': 2,
        'exp_max': 20,
        'max_difference': 1000,
    }
    config['workers'] = 2
    with tempfile.TemporaryDirectory() as directory:
        summary = engine.run_search(config, Path(directory), None, None)
        assert abs(summary['best_quality'] - float(engine.TARGET_RECORD)) < 1e-14
        frame = pd.read_csv(Path(directory) / 'results' / 'verified_triples.csv', dtype=str)
        record = frame[(frame.a == '2') & (frame.b == '6436341') & (frame.c == '6436343')]
        assert len(record) == 1


def check_resume_and_identities() -> None:
    config = json.loads(json.dumps(engine.PROFILES['quick']))
    config['workers'] = 2
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        engine.run_search(config, path, None, 50)
        connection = sqlite3.connect(path / 'search.sqlite')
        before = connection.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        expected_cf = len(engine.generate_cf_tasks(config))
        assert connection.execute("SELECT COUNT(*) FROM tasks WHERE engine='cf' AND status='done'").fetchone()[0] == expected_cf
        connection.close()
        engine.run_search(config, path, None, 50)
        connection = sqlite3.connect(path / 'search.sqlite')
        after = connection.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        rows = connection.execute('SELECT a,b,c,radical,quality,complete FROM triples').fetchall()
        connection.close()
        assert before == after
        for a_text, b_text, c_text, radical_text, q, complete in rows:
            a, b, c = int(a_text), int(b_text), int(c_text)
            assert a + b == c
            assert math.gcd(a, b) == 1
            if complete:
                radical = int(radical_text)
                assert abs(float(engine.mpm.log(c) / engine.mpm.log(radical)) - q) < 1e-12


def main() -> None:
    checks = [
        check_singular_lifting,
        check_semiconvergents,
        check_record_neighbor,
        check_resume_and_identities,
    ]
    for check in checks:
        check()
        print(f'PASS {check.__name__}')
    print(f'{len(checks)} verification groups passed')


if __name__ == '__main__':
    main()
