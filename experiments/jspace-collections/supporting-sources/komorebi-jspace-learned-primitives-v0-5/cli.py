"""Edit workspaces whose new operations are learned kernels. Komorebi P."""
import argparse
import json
from pathlib import Path
import numpy as np
from workspace import Workspace
from geometry import BehaviorGeometry
from primitive_model import Kernels, Catalog
from executor import Executor
from primitive_workspace import PrimitiveWorkspace

ROOT = Path(__file__).resolve().parent


def context(seed=0, results=None):
    folder = Path(results) if results is not None else ROOT / 'results'
    kernels = Kernels.load(folder / f'models/trained_square_{seed}.npz')
    receipt = json.loads((folder / f'catalog_square_{seed}.json').read_text())
    if receipt['receipt']['kernel_identity'] != kernels.identity():
        raise ValueError('Catalog and primitive checkpoint do not match.')
    executor = Executor(Catalog(kernels, receipt['accepted'], receipt['receipt']))
    model = Workspace.load(ROOT / 'baseline/model_0.npz')
    geometry = BehaviorGeometry.from_dict(json.loads((ROOT / 'baseline/geometry_0.json').read_text()))
    return model, geometry, executor


def load_bank(path, seed=0, results=None):
    return PrimitiveWorkspace.load(path, *context(seed, results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, default=Path('my_workspaces.json'))
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Create an editable copy of the supplied seed-0 bank.')
    sub.add_parser('list')
    p = sub.add_parser('primitive'); p.add_argument('channel'); p.add_argument('a', type=float); p.add_argument('b', type=float)
    p = sub.add_parser('read'); p.add_argument('name'); p.add_argument('x', type=float); p.add_argument('z', type=float)
    p.add_argument('--other', type=float, nargs=2, default=[0., 0.], metavar=('X', 'Z'))
    p = sub.add_parser('fork'); p.add_argument('source'); p.add_argument('name')
    p = sub.add_parser('edit-amplitude'); p.add_argument('name'); p.add_argument('delta', type=float)
    p = sub.add_parser('undo'); p.add_argument('name')
    args = parser.parse_args()
    try:
        if args.command == 'primitive':
            if not np.all(np.isfinite([args.a, args.b])): raise ValueError('Operands must be finite.')
            executor = context()[2]
            result = {'channel': args.channel, 'operands': [args.a, args.b],
                      'value': float(executor.catalog.call(args.channel, args.a, args.b))}
        elif args.command == 'init':
            if args.bank.exists(): raise ValueError('Destination already exists; choose a new bank path.')
            bank = load_bank(ROOT / 'results/workspaces_0.json'); bank.save(args.bank)
            result = {'status': 'created', 'bank': str(args.bank), 'workspaces': len(bank.slots)}
        else:
            bank = load_bank(args.bank)
            if args.command == 'list':
                result = [{'name': name, 'revision': slot['current'],
                           'amplitude': bank.state(name)['amplitude']}
                          for name, slot in bank.slots.items()]
            elif args.command == 'read':
                if not np.all(np.isfinite([args.x, args.z, *args.other])): raise ValueError('Coordinates must be finite.')
                result = dict(zip(['value', 'difference', 'sum'],
                                  bank.read(args.name, [[args.x, args.z]], [args.other])[:, 0].tolist()))
            elif args.command == 'fork':
                bank.fork(args.source, args.name); bank.save(args.bank)
                result = {'status': 'created', 'workspace': args.name}
            elif args.command == 'edit-amplitude':
                result = bank.edit_amplitude(args.name, args.delta); bank.save(args.bank)
            else:
                result = {'undone': bank.undo(args.name)}; bank.save(args.bank)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, FileNotFoundError) as exc:
        parser.exit(2, 'Error: ' + str(exc) + '\n')


if __name__ == '__main__': main()
