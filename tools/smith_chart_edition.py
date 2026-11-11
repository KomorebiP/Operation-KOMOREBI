"""Validated presentation and language changes for the retained Smith reading."""
from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath
import re


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(root, files, html_name):
    base=root/'research/smith-chart'
    figures=json.loads((base/'edition/figures.json').read_bytes())
    prose=json.loads((base/'edition/prose.json').read_bytes())
    if figures['generator_sha256']!=digest((base/'edition/generate_figures.py').read_bytes()):
        raise ValueError('Figure generator differs from its recorded revision')
    if prose['source_html_sha256']!=digest(files[html_name]):
        raise ValueError('Editorial source binding differs from the archived reading')
    if len(figures['figures'])!=42:
        raise ValueError('Unexpected vector edition inventory')
    for extra in figures.get('additional_figures',[]):
        path=PurePosixPath(extra['repository_path'])
        if path.is_absolute() or '..' in path.parts or not str(path).startswith('docs/demonstrations/figures/'):
            raise ValueError('Unsafe supplemental figure path')
        if digest((root/str(path)).read_bytes())!=extra['sha256']:
            raise ValueError('Supplemental figure checksum mismatch')
    mapping={}
    for item in figures['figures']:
        old,new,source=(item[k] for k in ('original','edition','source'))
        path=PurePosixPath(new)
        if path.is_absolute() or '..' in path.parts or not new.startswith('edition/figures/') or path.suffix!='.svg':
            raise ValueError('Unsafe vector edition path')
        if old in mapping or old not in files or source not in files:
            raise ValueError('Unexpected vector source identity')
        data=(base/new).read_bytes()
        if (digest(files[old])!=item['original_sha256'] or digest(files[source])!=item['source_sha256'] or
                digest(data)!=item['edition_sha256']):
            raise ValueError('Vector edition source or output checksum mismatch: '+old)
        if re.search(rb'<(?:script|foreignObject)\b|\son\w+\s*=',data,re.I):
            raise ValueError('Active content in a vector reading figure')
        mapping[old]={'desktop':new}
        if 'mobile_edition' in item:
            mobile=PurePosixPath(item['mobile_edition'])
            if mobile.is_absolute() or '..' in mobile.parts or not item['mobile_edition'].startswith('edition/figures/') or mobile.suffix!='.svg':
                raise ValueError('Unsafe mobile vector path')
            mobile_data=(base/item['mobile_edition']).read_bytes()
            if digest(mobile_data)!=item['mobile_sha256']:
                raise ValueError('Mobile vector checksum mismatch')
            if re.search(rb'<(?:script|foreignObject)\b|\son\w+\s*=',mobile_data,re.I):
                raise ValueError('Active content in a mobile vector')
            mapping[old]['mobile']=item['mobile_edition']
    return mapping,prose


def edit_prose(source, record):
    original_math=re.findall(r'<span class="math (?:inline|display)">.*?</span>',source,re.S)
    original_ids=re.findall(r'\bid="([^"]+)"',source)
    for change in record['edits']:
        if source.count(change['old'])!=change['expected_count']:
            raise ValueError('Editorial fragment changed: '+change['old'][:70])
        source=source.replace(change['old'],change['new'])
    if (original_math!=re.findall(r'<span class="math (?:inline|display)">.*?</span>',source,re.S) or
            original_ids!=re.findall(r'\bid="([^"]+)"',source)):
        raise ValueError('Editorial changes altered mathematics or stable identifiers')
    return source
