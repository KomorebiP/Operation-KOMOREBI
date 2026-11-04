"""Publish the MathJax entry point used by the reader and all lazy modules."""
import hashlib
import json
from pathlib import Path
import shutil

from fetch_reader_runtime import URL, INTEGRITY


# These are complete alternative entry bundles, not extension/output modules.
# The reader loads tex-svg-full.js; switching output in its menu uses output/.
ALTERNATIVE_BUNDLES = frozenset({
    'tex-chtml.js', 'tex-chtml-full.js', 'tex-chtml-full-speech.js',
    'tex-mml-chtml.js', 'mml-chtml.js', 'tex-svg.js', 'tex-mml-svg.js', 'mml-svg.js',
})


def publish_mathjax(source, target):
    if source is None:
        raise ValueError('The complete pinned MathJax runtime is required')
    source = Path(source).resolve()
    required = ('tex-svg-full.js', 'a11y/assistive-mml.js',
                'a11y/semantic-enrich.js', 'a11y/explorer.js', 'ui/menu.js',
                'SOURCE.json', 'LICENSE')
    if not all((source/name).is_file() for name in required):
        raise ValueError('The complete pinned MathJax runtime is required')
    source_bytes = (source/'SOURCE.json').read_bytes()
    record = json.loads(source_bytes)
    files = [p for p in source.rglob('*') if p.is_file()]
    if (record.get('url') != URL or record.get('sha512_base64') != INTEGRITY or
            record.get('files') != len(files)-1):
        raise ValueError('MathJax source record differs from the pinned runtime')
    omitted = sorted(name for name in ALTERNATIVE_BUNDLES if (source/name).is_file())

    def ignore(directory, names):
        return ALTERNATIVE_BUNDLES.intersection(names) if Path(directory) == source else ()

    shutil.copytree(source, target, ignore=ignore)
    publication = dict(
        profile='tex-svg-full with all extension, output, font and accessibility modules',
        entry='tex-svg-full.js', source_record='SOURCE.json',
        source_record_sha256=hashlib.sha256(source_bytes).hexdigest(),
        source_files=len(files), published_source_files=len(files)-len(omitted),
        omitted_root_bundles=omitted,
        omitted_bytes=sum((source/name).stat().st_size for name in omitted),
        scope='Retained runtime files are copied unchanged from the verified package.',
    )
    (Path(target)/'PUBLISHED.json').write_text(json.dumps(publication, indent=2)+'\n',
                                             encoding='utf-8', newline='\n')
    return publication
