"""Check the exact labels of the redesigned three-frequency Pick diagram."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sys
import zipfile

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE/'edition'))
from diagram_redesign import PAIR_MINORS, FULL_DETERMINANT


def check():
    archive = (BASE/'SmithChart_Complete.zip').read_bytes()
    assert hashlib.sha256(archive).hexdigest() == '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
    with zipfile.ZipFile(BASE/'SmithChart_Complete.zip') as package:
        source = package.read('Smith_Chart_Research_2026-11-11/reproduction/earlier_core/smith_chart_extended.py')
        assert b'(1-c[i]*c[j])/(s[i]+s[j])' in source
    frequencies = [Q(1), Q(2), Q(3)]
    couplings = [Q(1,20), Q(1,6), Q(1,20)]
    matrix = [[(1-couplings[i]*couplings[j])/(frequencies[i]+frequencies[j])
               for j in range(3)] for i in range(3)]
    assert matrix == [[Q(399,800),Q(119,360),Q(399,1600)],
                      [Q(119,360),Q(35,144),Q(119,600)],
                      [Q(399,1600),Q(119,600),Q(133,800)]]
    assert all(matrix[i][i] > 0 for i in range(3))
    pairs = []
    for i, j in [(0,1),(0,2),(1,2)]:
        determinant = matrix[i][i]*matrix[j][j]-matrix[i][j]*matrix[j][i]
        pair, numerator, denominator = next(row for row in PAIR_MINORS if row[0] == f'{i+1}–{j+1}')
        assert determinant == Q(int(numerator),int(denominator)) and determinant > 0
        pairs.append({'nodes':[i+1,j+1], 'determinant':str(determinant), 'positive':True})
    determinant = Q(0)
    for order in permutations(range(3)):
        inversions = sum(order[i] > order[j] for i in range(3) for j in range(i+1,3))
        product = Q((-1)**inversions)
        for i in range(3):
            product *= matrix[i][order[i]]
        determinant += product
    a,b,c = matrix[0]
    d,e,f = matrix[1]
    g,h,i = matrix[2]
    assert determinant == a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    numerator, denominator = FULL_DETERMINANT
    assert determinant == Q(int(numerator.replace('−','-')),int(denominator)) < 0
    return {'status':'PASS','scope':'Fixed all-positive coupling branch at s=1,2,3',
            'matrix':[[str(x) for x in row] for row in matrix], 'pairs':pairs,
            'full_determinant':str(determinant),
            'source_sha256':hashlib.sha256(source).hexdigest(),
            'non_claim':'No new interpolation theorem, circuit feasibility result or other sign-branch enumeration.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    arguments = parser.parse_args()
    record = check()
    encoded = json.dumps(record,indent=2)+'\n'
    if arguments.output:
        arguments.output.write_text(encoded,encoding='utf-8',newline='\n')
    print(encoded)
