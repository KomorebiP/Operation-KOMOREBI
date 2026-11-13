"""Render only the new chemistry pages through the real common site chrome."""
import argparse
from pathlib import Path
import shutil
from computational_chemistry import publish
from test_computational_chemistry import fixture_site,ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    site=fixture_site(args.output);publish(site);site.markdown_pages()
    shutil.copytree(ROOT/'website/assets',args.output/'assets',dirs_exist_ok=True)
    print(args.output.resolve())


if __name__=='__main__':main()
