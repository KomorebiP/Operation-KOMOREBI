"""Build the reconstructed visual guide in isolation; never run model checkers."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tectonic', help='Path to Tectonic; otherwise use XeLaTeX')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'Paper_IV_Visual_Guide_Reconstructed.pdf')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    engine = args.tectonic or shutil.which('xelatex')
    if not engine:
        parser.error('Use an existing XeLaTeX installation or pass --tectonic PATH.')
    with tempfile.TemporaryDirectory(prefix='paper-iv-visual-reconstruction-') as temporary:
        stage = Path(temporary)
        for name in ('main.tex', 'pages.tex', 'komorebi-monograph.sty', 'komorebi-publication.sty'):
            shutil.copyfile(root/name, stage/name)
        for name in ('fonts', 'graphics'):
            shutil.copytree(root/name, stage/name)
        command = ([engine, '-X', 'compile', '--untrusted', '--keep-logs', 'main.tex'] if args.tectonic else
                   [engine, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'])
        for _ in range(1 if args.tectonic else 2):
            subprocess.run(command, cwd=stage, check=True)
        log = (stage/'main.log').read_text(encoding='utf-8', errors='replace')
        for error in ('Missing character:', 'Undefined control sequence', 'undefined references', 'Overfull \\vbox'):
            if error in log:
                raise ValueError('Review compiler diagnostic: '+error)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(stage/'main.pdf', args.output)
    print(args.output.resolve())


if __name__ == '__main__':
    main()
