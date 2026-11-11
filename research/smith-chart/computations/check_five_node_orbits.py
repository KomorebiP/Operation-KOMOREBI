"""Independently recount the archive's restricted five-node reactive placements.

This is a finite graph check, not an electrical necessity or feasibility proof.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import platform
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'SmithChart_Complete.zip'
ARCHIVE_SHA256 = '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
CATALOG = 'Smith_Chart_Research_2026-11-11/reproduction/six_state/q6_5node_canonical_topologies.json'
CATALOG_SHA256 = 'ff8a03ca0b91ea0c21e57866b5bfa3318930cf510490d125da7ec0729d657866'
EDGES = tuple(itertools.combinations(range(5), 2))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def connected(edges, start, end):
    adjacency = {n: set() for n in range(5)}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen = {start}
    queue = deque([start])
    while queue:
        for neighbor in adjacency[queue.popleft()] - seen:
            seen.add(neighbor)
            queue.append(neighbor)
    return end in seen


def acyclic(edges):
    # A simple undirected graph has a cycle iff an edge has an alternate path.
    return all(not connected(edges[:i] + edges[i + 1:], *edge) for i, edge in enumerate(edges))


def survives(inductors, capacitors):
    if connected(inductors, 0, 1) or connected(capacitors, 0, 1):
        return False
    if not acyclic(inductors) or not acyclic(capacitors):
        return False
    if all(connected(inductors, *edge) for edge in capacitors):
        return False
    if all(connected(capacitors, *edge) for edge in inductors):
        return False
    return True


def orbit(placement, *, exchange_terminals=True):
    results = set()
    for swap in ((False, True) if exchange_terminals else (False,)):
        for inner in itertools.permutations((2, 3, 4)):
            mapping = ((1, 0) if swap else (0, 1)) + inner
            transformed = tuple(tuple(sorted(tuple(sorted((mapping[u], mapping[v]))) for u, v in group))
                                for group in placement)
            results.add(transformed)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='Optional new JSON receipt; never overwritten')
    args = parser.parse_args()
    script = Path(__file__).read_bytes()
    archive = ARCHIVE.read_bytes()
    if sha(archive) != ARCHIVE_SHA256:
        raise RuntimeError('Research archive checksum mismatch')
    with zipfile.ZipFile(ARCHIVE) as z:
        raw_catalog = z.read(CATALOG)
    if sha(raw_catalog) != CATALOG_SHA256:
        raise RuntimeError('Archived topology catalogue checksum mismatch')
    catalog = json.loads(raw_catalog)

    choices = tuple(itertools.combinations(EDGES, 3))
    representatives = {}
    survivor_count = 0
    for inductors in choices:
        for capacitors in choices:
            if not survives(inductors, capacitors):
                continue
            survivor_count += 1
            placement = (inductors, capacitors)
            representative = min(orbit(placement))
            representatives.setdefault(representative, set()).add(placement)
    if len(choices) ** 2 != 14400 or survivor_count != 1934 or len(representatives) != 168:
        raise AssertionError('Recount differs from the stated finite census')
    if any(len(members) != len(orbit(rep)) for rep, members in representatives.items()):
        raise AssertionError('A survivor orbit is incomplete')
    # Dropping terminal exchange must change the quotient, not silently give
    # the same count under a different equivalence relation.
    internal_only = {min(orbit(placement, exchange_terminals=False))
                     for members in representatives.values() for placement in members}
    if len(internal_only) != 336:
        raise AssertionError('Unexpected count without terminal exchange')

    archived = {}
    for row in catalog:
        placement = tuple(tuple(EDGES[index] for index in row[key]) for key in ('L_edges', 'C_edges'))
        if not survives(*placement):
            raise AssertionError('An archived representative fails the filters')
        key = min(orbit(placement))
        if key in archived or row['orbit_size'] != len(orbit(placement)):
            raise AssertionError('Archived class or orbit size is inconsistent')
        archived[key] = row['orbit_size']
    if set(archived) != set(representatives) or sum(archived.values()) != survivor_count:
        raise AssertionError('Archived representatives do not cover the survivor orbits')
    if Path(__file__).read_bytes() != script or sha(ARCHIVE.read_bytes()) != ARCHIVE_SHA256:
        raise RuntimeError('An input changed during the recount')
    receipt = {'status': 'PASS', 'python': platform.python_version(), 'script_sha256': sha(script),
               'archive_sha256': ARCHIVE_SHA256, 'catalog_path_in_archive': CATALOG,
               'catalog_sha256': CATALOG_SHA256, 'nodes': 5, 'terminals': [0, 1],
               'total_labelled_placements': len(choices) ** 2, 'filter_survivors': survivor_count,
               'orbit_classes': len(representatives),
               'classes_without_terminal_exchange': len(internal_only),
               'orbit_size_histogram': dict(sorted(Counter(archived.values()).items())),
               'symmetry': 'Exchange terminals and permute the three internal vertices; keep L and C distinct.',
               'scope': 'Checks the finite graph filters and catalogue only; it does not prove the filters necessary for circuits or decide resistor feasibility.'}
    text = json.dumps(receipt, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as out:
            out.write(text)
    print(text, end='')


if __name__ == '__main__':
    main()
