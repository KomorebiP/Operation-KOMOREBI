"""Structural checks for scientifically meaningful diagram redraws."""
from collections import Counter
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT/'research/smith-chart/edition'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class DiagramTest(unittest.TestCase):
    def test_three_pair_edges_are_distinct_and_nodes_are_not_collinear(self):
        for suffix in ('.svg','.mobile.svg'):
            svg = ET.fromstring((EDITION/'figures'/('08_frequency_obstruction'+suffix)).read_bytes())
            nodes = {int(el.attrib['data-node']):(float(el.attrib['data-x']),float(el.attrib['data-y']))
                     for el in svg.iter() if 'data-node' in el.attrib}
            self.assertEqual(set(nodes),{1,2,3})
            (ax,ay),(bx,by),(cx,cy) = (nodes[i] for i in (1,2,3))
            self.assertGreater(abs((bx-ax)*(cy-ay)-(by-ay)*(cx-ax)),10000)
            pairs = [el.attrib['data-pair'] for el in svg.iter() if 'data-pair' in el.attrib]
            self.assertCountEqual(pairs,['1,2','1,3','2,3'])

    def test_wide_and_narrow_schematics_preserve_components_and_connections(self):
        expected = {'11':{'R':4,'L':2,'C':1}, '18':{'R':2,'L':2,'C':2},
                    '26':{'L':6,'C':6}, '27':{'R':3,'L':1,'C':1},
                    '30':{'R':3,'L':1,'C':1}, '37':{'R':4,'L':2,'C':1}}
        for number, counts in expected.items():
            wide = next((EDITION/'figures').glob(number+'_*.svg'))
            if wide.name.endswith('.mobile.svg'):
                wide = wide.with_name(wide.name.replace('.mobile.svg','.svg'))
            narrow = wide.with_name(wide.stem+'.mobile.svg')
            def components(path):
                return Counter((el.attrib['data-component'],el.attrib['data-kind'],el.attrib['data-endpoints'])
                               for el in ET.fromstring(path.read_bytes()).iter() if 'data-component' in el.attrib)
            wide_parts,narrow_parts = components(wide),components(narrow)
            self.assertEqual(wide_parts,narrow_parts,number)
            self.assertEqual(Counter(kind for (_,kind,_),count in wide_parts.items() for _ in range(count)),counts,number)

    def test_exact_frequency_labels_match_the_retained_kernel_example(self):
        checker = module(ROOT/'research/smith-chart/computations/check_diagram_labels.py','diagram_label_check')
        self.assertEqual(checker.check()['status'],'PASS')


if __name__ == '__main__':
    unittest.main()
