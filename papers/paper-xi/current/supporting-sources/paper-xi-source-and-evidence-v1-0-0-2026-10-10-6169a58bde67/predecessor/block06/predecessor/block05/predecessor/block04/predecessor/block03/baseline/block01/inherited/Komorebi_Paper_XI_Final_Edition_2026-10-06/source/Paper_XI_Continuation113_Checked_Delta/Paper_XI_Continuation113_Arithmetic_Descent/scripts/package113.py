#!/usr/bin/env python3
"""Package continuation113 with exact member hashes and an extraction check."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import tempfile
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    assert not output.exists(), 'Use a new archive path; never overwrite a release.'
    assert not output.is_relative_to(root), 'Archive must be outside its source tree.'
    status = json.loads((root / 'STATUS113.json').read_text())
    assert status['original_claim']['count'] == '65/66'
    assert status['original_claim']['status'] == 'open'
    for name, expected in status['evidence_sha256'].items():
        assert digest((root / name).read_bytes()) == expected, name
    result = json.loads((root / 'evidence/final_replay_corrected/replay/RESULT.json').read_text())
    assert result['status'] == 'PASS' and result['exports_audited'] == 76
    assert Counter(d['kind'] for m in result['modules'] for d in m['declarations']) == {
        'theorem': 61, 'def': 14, 'structure': 1
    }
    retained_objects = {}
    for module in result['modules']:
        assert digest((root / ('formalization/' + module['module'].replace('.', '/') + '.lean')).read_bytes()) == module['source_sha256']
        for suffix, expected in module['objects'].items():
            name = 'evidence/final_replay_corrected/replay/objects/' + module['module'].replace('.', '/') + suffix
            assert digest((root / name).read_bytes()) == expected
            retained_objects[name] = expected
    assert len(retained_objects) == 8
    included = {}
    omitted = Counter()
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        name = relative.as_posix()
        if name == 'PACKAGE_MANIFEST113.json':
            continue
        if '__pycache__' in relative.parts or path.suffix == '.pyc':
            omitted['temporary_python_cache'] += 1
            continue
        if path.suffix in {'.png', '.pdf'}:
            omitted['source_page_render_or_document'] += 1
            continue
        if 'objects' in relative.parts and name not in retained_objects:
            omitted['inherited_or_duplicate_objects'] += 1
            continue
        if path.is_symlink():
            omitted['symbolic_link'] += 1
            continue
        data = path.read_bytes()
        included[name] = {'bytes': len(data), 'sha256': digest(data)}
    assert set(retained_objects) <= set(included)
    manifest = {
        'schema': 'PaperXI.continuation113.package.v1',
        'original_count': '65/66',
        'scope': 'This continuation only; pinned baseline archives, runtime and primary sources are external dependencies.',
        'manifest_self_excluded': True,
        'included_file_count_excluding_manifest': len(included),
        'included_bytes_excluding_manifest': sum(item['bytes'] for item in included.values()),
        'retained_final_new_module_objects': retained_objects,
        'excluded_counts': dict(sorted(omitted.items())),
        'exclusion_policy': ['Exclude inherited and duplicate proof objects; retain only final113 objects.',
                             'Exclude temporary Python caches and rendered source pages.',
                             'Exclude symbolic links; dependencies are identified by their original receipts.'],
        'files': included,
    }
    (root / 'PACKAGE_MANIFEST113.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    names = sorted(list(included) + ['PACKAGE_MANIFEST113.json'])
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            data = (root / name).read_bytes()
            if name in included:
                assert digest(data) == included[name]['sha256'], 'Source changed during packaging: ' + name
            info = zipfile.ZipInfo(root.name + '/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {root.name + '/' + name for name in names}
        with tempfile.TemporaryDirectory(prefix='paperxi113_extract_') as directory:
            archive.extractall(directory)
            extracted = Path(directory) / root.name
            assert (extracted / 'PACKAGE_MANIFEST113.json').read_bytes() == (root / 'PACKAGE_MANIFEST113.json').read_bytes()
            for name, expected in included.items():
                data = (extracted / name).read_bytes()
                assert len(data) == expected['bytes'] and digest(data) == expected['sha256'], name
    receipt = {'status': 'PASS', 'archive': str(output), 'bytes': output.stat().st_size,
               'sha256': digest(output.read_bytes()), 'zip_crc': 'PASS',
               'extracted_member_hashes': 'PASS', 'member_count': len(names),
               'included_final_objects': len(retained_objects),
               'package_manifest_sha256': digest((root / 'PACKAGE_MANIFEST113.json').read_bytes())}
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
