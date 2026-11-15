"""Run the unchanged archived generator with explicit UTF-8/LF text outputs."""
import argparse
import json
from pathlib import Path

import generate_candidates as generator


class OutputPath(type(Path())):
    """Retain pathlib behavior while making archive text portable on Windows."""
    def write_text(self, data, encoding=None, errors=None, newline='\n'):
        return super().write_text(data, encoding=encoding or 'utf-8', errors=errors, newline=newline)


def reproduce(output):
    records=generator.create_catalog()
    tests=generator.independent_tests(records)
    summary=generator.write_outputs(records,OutputPath(output))
    (OutputPath(output)/'verification/GENERATION_TESTS.json').write_text(json.dumps(tests,indent=2)+'\n')
    (OutputPath(output)/'verification/GENERATION_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='A separate directory for regenerated data')
    args=parser.parse_args()
    print(json.dumps(reproduce(args.output),indent=2))
