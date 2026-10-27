#!/usr/bin/env python3
"""Build the bookmarked complete reader from the manuscript and preserved releases."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from datetime import datetime, timezone
import hashlib
import json
from pypdf import PdfReader, PdfWriter, __version__ as PYPDF_VERSION
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

ROOT = Path(__file__).resolve().parent
ROMANS = ('I','II','III','IV','V','VI','VII','VIII')
MANUSCRIPT = ROOT / 'Komorebi_Special_Functions_Consolidated_Manuscript_v0.1.pdf'
OUTPUT = ROOT / 'Komorebi_Special_Functions_Complete_Reader_v0.1.pdf'

def namespace_destinations(reader, prefix):
    """Disambiguate hyperref names without touching page content or geometry.

    PdfWriter.append imports named destinations, but repeated names in later
    inputs can be skipped. Renaming the destination tree and its local references
    before append keeps each paper's TOC and cross-references inside that paper.
    Only the in-memory PdfReader is edited; preserved input files are unchanged.
    """
    named = reader.named_destinations
    renamed = {str(name): prefix + str(name) for name in named}
    counts = {'named_destinations': len(named), 'destination_references': 0}

    def rename(value):
        if isinstance(value, str):
            if str(value) not in renamed:
                raise RuntimeError(f'Unresolved internal destination {value!r} in {prefix}')
            counts['destination_references'] += 1
            return TextStringObject(renamed[str(value)])
        return value

    seen_actions = set()
    def action(value):
        value = value.get_object()
        if isinstance(value, ArrayObject):
            for item in value:
                action(item)
            return
        if not isinstance(value, DictionaryObject) or id(value) in seen_actions:
            return
        seen_actions.add(id(value))
        if value.get('/S') == '/GoTo' and '/D' in value:
            value[NameObject('/D')] = rename(value['/D'])
        if '/Next' in value:
            action(value['/Next'])

    def entry(value):
        value = value.get_object()
        if '/Dest' in value:
            value[NameObject('/Dest')] = rename(value['/Dest'])
        if '/A' in value:
            action(value['/A'])
        if '/AA' in value:
            for item in value['/AA'].get_object().values():
                action(item)

    for page in reader.pages:
        entry(page)
        for annotation in page.get('/Annots', []):
            entry(annotation)
    catalog = reader.root_object
    entry(catalog)
    if '/OpenAction' in catalog:
        value = catalog['/OpenAction']
        if isinstance(value, str):
            catalog[NameObject('/OpenAction')] = rename(value)
        elif isinstance(value, DictionaryObject):
            action(value)

    seen_outlines = set()
    def outline(value):
        value = value.get_object()
        if id(value) in seen_outlines:
            return
        seen_outlines.add(id(value))
        entry(value)
        for key in ('/First', '/Next'):
            if key in value:
                outline(value[key])
    if '/Outlines' in catalog:
        outline(catalog['/Outlines'])

    # A single sorted leaf is a valid PDF name tree. Preserve other name trees.
    entries = ArrayObject()
    for name in sorted(named, key=lambda item: renamed[str(item)]):
        entries.extend([TextStringObject(renamed[str(name)]), named[name].dest_array])
    names = catalog.get('/Names', DictionaryObject()).get_object()
    names[NameObject('/Dests')] = DictionaryObject({NameObject('/Names'): entries})
    catalog[NameObject('/Names')] = names
    catalog.pop(NameObject('/Dests'), None)
    return counts

def internal_links(reader, page, named=None):
    """Return local annotation targets and view arguments in annotation order."""
    links = []
    if named is None:
        named = reader.named_destinations
    for annotation in page.get('/Annots', []):
        annotation = annotation.get_object()
        destination = annotation.get('/Dest')
        action = annotation.get('/A')
        if action is not None:
            action = action.get_object()
            if action.get('/S') == '/GoTo':
                destination = action.get('/D')
        if destination is None:
            continue
        if isinstance(destination, str):
            if str(destination) not in named:
                raise RuntimeError(f'Missing merged destination {destination!r}')
            destination = named[str(destination)].dest_array
        destination = destination.get_object()
        target = destination[0]
        page_number = reader.get_page_number(target.get_object())
        if page_number is None or page_number < 0:
            raise RuntimeError(f'Invalid local page target {target!r}')
        links.append((page_number, tuple(str(value) for value in destination[1:])))
    return links

def page_signature(page):
    contents = page.get_contents()
    return {
        'decoded_content_sha256': hashlib.sha256(contents.get_data() if contents is not None else b'').hexdigest(),
        'media_box': list(page.mediabox), 'crop_box': list(page.cropbox),
        'rotation': page.get('/Rotate', 0),
    }

def outline_signature(reader, items=None, depth=0, offset=0):
    signature = []
    for item in reader.outline if items is None else items:
        if isinstance(item, list):
            signature.extend(outline_signature(reader, item, depth + 1, offset))
        else:
            target = reader.get_destination_page_number(item)
            signature.append((str(item.title), None if target is None else offset + target,
                              tuple(map(str, item.dest_array[1:])), depth))
    return signature

def main():
    writer = PdfWriter()
    streams = []
    index = []
    inputs = []
    input_hashes = {MANUSCRIPT: hashlib.sha256(MANUSCRIPT.read_bytes()).hexdigest()}
    manuscript_reader = PdfReader(MANUSCRIPT)
    manuscript_named = manuscript_reader.named_destinations
    inputs.append((manuscript_reader, 0, 'consolidated::',
                   [page_signature(page) for page in manuscript_reader.pages],
                   [internal_links(manuscript_reader, page, manuscript_named) for page in manuscript_reader.pages]))
    manuscript_navigation = namespace_destinations(manuscript_reader, 'consolidated::')
    writer.append(manuscript_reader, outline_item='Consolidated manuscript: mathematics, visuals, corrections, evidence')
    index.append({'part':'Consolidated manuscript','physical_start_page':1,'pages':len(manuscript_reader.pages),
                  'destination_namespace':'consolidated::','navigation':manuscript_navigation})
    for roman in ROMANS:
        name = f'Projector_Generated_Special_Functions_{roman}'
        archive = ROOT / 'original_releases' / f'{name}_Release.zip'
        input_hashes[archive] = hashlib.sha256(archive.read_bytes()).hexdigest()
        with ZipFile(archive) as z:
            candidates = [n for n in z.namelist() if Path(n).name == name + '.pdf']
            if not candidates:
                raise RuntimeError(f'Missing source PDF for {roman}')
            selected = min(candidates, key=lambda n:(len(n),n))
            stream = BytesIO(z.read(selected))
        streams.append(stream)
        reader = PdfReader(stream)
        start = len(writer.pages) + 1
        prefix = f'paper_{roman}::'
        original_named = reader.named_destinations
        inputs.append((reader, start - 1, prefix,
                       [page_signature(page) for page in reader.pages],
                       [internal_links(reader, page, original_named) for page in reader.pages]))
        navigation = namespace_destinations(reader, prefix)
        writer.append(reader, outline_item=f'Source Paper {roman}')
        index.append({'part':f'Source Paper {roman}','archive':archive.name,'pdf_member':selected,
                      'physical_start_page':start,'physical_end_page':len(writer.pages),'pages':len(reader.pages),
                      'destination_namespace':prefix,'navigation':navigation})
    writer.add_metadata({'/Title':'Komorebi Special Functions: Complete Reader v0.1',
                         '/Author':'Komorebi P.','/Subject':'Unified manuscript plus the eight preserved source papers'})
    with OUTPUT.open('wb') as f:
        writer.write(f)
    (ROOT / 'evidence' / 'reader_index.json').write_text(json.dumps(index, indent=2)+'\n')
    merged = PdfReader(OUTPUT)
    assert len(merged.pages) == sum(item['pages'] for item in index)
    validation = {'generated_utc':datetime.now(timezone.utc).isoformat(),'pypdf_version':PYPDF_VERSION,
                  'page_content_and_geometry_checked': 0, 'internal_annotation_links_checked': 0,
                  'named_destinations_checked': 0, 'parts': [], 'all_passed': True}
    merged_named = merged.named_destinations
    for reader, offset, prefix, signatures, links in inputs:
        part = {'namespace':prefix,'pages':len(reader.pages),'internal_links':0,'named_destinations':0}
        for local_number, signature in enumerate(signatures):
            merged_page = merged.pages[offset + local_number]
            if page_signature(merged_page) != signature:
                raise RuntimeError(f'Page content or geometry changed in {prefix}, page {local_number + 1}')
            expected = [(offset + target, view) for target, view in links[local_number]]
            if internal_links(merged, merged_page, merged_named) != expected:
                raise RuntimeError(f'Internal hyperlink changed target in {prefix}, page {local_number + 1}')
            validation['page_content_and_geometry_checked'] += 1
            validation['internal_annotation_links_checked'] += len(expected)
            part['internal_links'] += len(expected)
        for name, destination in reader.named_destinations.items():
            expected_page = offset + reader.get_destination_page_number(destination)
            actual = merged_named.get(name)
            if actual is None or merged.get_destination_page_number(actual) != expected_page:
                raise RuntimeError(f'Named destination changed target: {name}')
            if tuple(map(str, actual.dest_array[1:])) != tuple(map(str, destination.dest_array[1:])):
                raise RuntimeError(f'Named destination changed view: {name}')
            validation['named_destinations_checked'] += 1
            part['named_destinations'] += 1
        validation['parts'].append(part)
    expected_outline = []
    for number, (reader, offset, prefix, _, _) in enumerate(inputs):
        title = ('Consolidated manuscript: mathematics, visuals, corrections, evidence'
                 if number == 0 else f'Source Paper {ROMANS[number - 1]}')
        expected_outline.append((title, offset, ('/Fit',), 0))
        expected_outline.extend(outline_signature(reader, depth=1, offset=offset))
    if outline_signature(merged) != expected_outline:
        raise RuntimeError('Imported bookmark title, target, view or hierarchy changed')
    validation['imported_outline_items_checked'] = len(expected_outline) - len(inputs)
    validation['part_bookmarks_checked'] = len(inputs)
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != digest for path, digest in input_hashes.items()):
        raise RuntimeError('An input PDF or original source archive changed during the build')
    validation['input_files_unchanged'] = True
    validation['input_sha256'] = {str(path.relative_to(ROOT)):digest for path,digest in input_hashes.items()}
    validation['output_sha256'] = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    validation['note'] = 'All source page decoded-content hashes, media/crop boxes and rotations match. Local hyperlink destinations and view arguments match the original papers with their physical page offsets. Input archives were not edited.'
    (ROOT / 'evidence' / 'reader_navigation_validation.json').write_text(json.dumps(validation, indent=2)+'\n')
    lines = ['# Complete reader navigation and preservation QA', '',
             f"Generated: {validation['generated_utc']}. pypdf: {PYPDF_VERSION}.", '',
             'The complete reader contains the 38-page consolidated manuscript and all eight preserved source papers, for 469 physical pages.', '',
             'The source PDFs reuse hyperref destination names, including `chapter.1` and `Doc-Start`. Before merging, the script assigns a separate namespace to every input and updates its local actions and outline references. This prevents a later paper’s contents link from resolving to an earlier paper.', '',
             '| Input | Pages checked | Local annotation links checked | Named destinations checked |',
             '|---|---:|---:|---:|']
    for part in validation['parts']:
        lines.append(f"| {part['namespace'].rstrip(':')} | {part['pages']} | {part['internal_links']} | {part['named_destinations']} |")
    lines.extend(['', f"All {validation['page_content_and_geometry_checked']} page decoded-content hashes, media boxes, crop boxes and rotations match their inputs. All {validation['internal_annotation_links_checked']} internal annotation links preserve their target page and view arguments. All {validation['named_destinations_checked']} names preserve their target page and view arguments.", '',
                  f"All {validation['imported_outline_items_checked']} imported outline entries preserve their title, target page, view arguments and hierarchy. The {validation['part_bookmarks_checked']} added part bookmarks point to the correct starts.", '',
                  'Input manuscript and archive SHA256 values are unchanged before and after the build. No source files were modified. Only imported navigation names and references were changed in memory.', '',
                  'This is structural and navigation QA. The consolidated manuscript’s visual QA is reported separately. Full hashes and exact counts appear in `reader_navigation_validation.json`.'])
    (ROOT / 'evidence' / 'reader_navigation_validation.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'pages':len(writer.pages),'output':str(OUTPUT),'parts':len(index),'navigation_validation':validation}))

if __name__ == '__main__':
    main()
