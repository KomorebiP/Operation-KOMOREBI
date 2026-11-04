"""Search recall, source retention, and static catalogue integrity."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from search_catalog import publish, verify, metadata_rows, normalized, decode_ids, encode_ids


def fixture_rows():
    return [
        dict(title='Euler seed', group='Collection', kind='Guides', work_ids=['paper-i'],
             url='collection/euler.html', text='Seed generation with a deep nilpotent control', preview='An authored introduction.'),
        dict(title='Résumé α and Γ', group='Collection', kind='Written proofs', work_ids=['paper-iv'],
             url='read/proof.html#statement', text='Café βeta, ρ and gamma; coefficient refinement.',
             preview='A mathematical preview.', preview_parts=[dict(type='text', text='<img src=x> '),dict(type='math', text=r'\alpha+\rho')], math_preview=r'E_8=1385'),
        dict(title='Operator implementation', group='Komorebi Math', kind='Code', work_ids=['paper-i','paper-v'],
             url='math/operator.html', text='start '*300+'thedeepneedleoperator at the very end'),
        dict(title='Haar visual guide', group='Collection', kind='Guides', work_ids=['paper-v'],
             url='read/atlas.html', text='Wavelet phase reconstruction and seed weights', visual_guide=True),
        dict(title='Empty body', group='Polyphase Float', kind='Code', work_ids=[], url='polyphase/empty.html', text=''),
    ]


def build_fixture(root, rows=None):
    root=Path(root)
    root.mkdir(parents=True,exist_ok=True)
    site=SimpleNamespace(output=root,revision='fixture',search=rows or fixture_rows(),
                         write=lambda p,s:(root/p).write_text(s,encoding='utf8'))
    result=publish(site)
    return result


def matches(root, words):
    manifest=json.loads((root/'search-index.json').read_bytes())
    terms=json.loads((root/manifest['lexicon']).read_bytes())
    found=[]
    for word in words:
        ids=set()
        for i,term in enumerate(terms):
            if word in term:
                part=json.loads((root/(manifest['postings']+str(i//manifest['terms_per_part'])+'.json')).read_bytes())
                ids.update(decode_ids(part[term],manifest['entries']))
        found.append(ids)
    return set.intersection(*found) if found else set(range(manifest['entries']))


class SearchCatalogueTests(unittest.TestCase):
    def test_search_page_loads_the_versioned_engine_before_the_interface(self):
        from build_reader_site import Site
        with tempfile.TemporaryDirectory() as folder:
            site=object.__new__(Site)
            site.root=Path(__file__).resolve().parent.parent
            site.output=Path(folder)
            site.revision='fixture'
            site.page('search.html','Search','<h1>Search</h1>')
            page=(site.output/'search.html').read_text(encoding='utf8')
            self.assertIn('assets/search-engine.js?v=',page)
            self.assertLess(page.index('assets/search-engine.js'),page.index('assets/reader.js'))
            site.page('404.html','Page unavailable','<h1>Page unavailable</h1>')
            self.assertNotIn('search-engine.js',(site.output/'404.html').read_text(encoding='utf8'))

    def test_substrings_unicode_and_deep_body_matches_keep_complete_recall(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);rows=fixture_rows();build_fixture(root,rows)
            for query in ['eed','Euler nilpotent','deepneedle','cafe','α','rho','gamma','Γ','refine','empty','missing', 'phase seed']:
                words=normalized(query).split()
                expected={i for i,row in enumerate(rows) if all(w in normalized(row['title']+' '+row['text']) for w in words)}
                with self.subTest(query=query):self.assertEqual(matches(root,words),expected)
            manifest=json.loads((root/'search-index.json').read_bytes())
            detail=json.loads((root/(manifest['details']+'0.json')).read_bytes())
            self.assertNotIn('text',detail,'The authored preview avoids downloading its hidden search-only text')
            self.assertEqual(matches(root,['nilpotent']),{0},'Omitted preview text stays fully searchable')

    def test_complete_metadata_previews_and_revision_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);summary=build_fixture(root)
            self.assertEqual(verify(root,'fixture'),summary)
            for actual,original in zip(metadata_rows(root),fixture_rows()):
                for key in ['title','group','kind','url','work_ids']:
                    self.assertEqual(actual[key],original[key])
                self.assertEqual(bool(actual.get('visual_guide')),bool(original.get('visual_guide')))
            manifest=json.loads((root/'search-index.json').read_bytes())
            self.assertLess((root/'search-index.json').stat().st_size,2048)
            math=json.loads((root/(manifest['details']+'1.json')).read_bytes())
            self.assertEqual(math['preview_parts'],fixture_rows()[1]['preview_parts'])
            self.assertEqual(math['math_preview'],fixture_rows()[1]['math_preview'])
            with self.assertRaises(AssertionError):verify(root,'another-revision')

    def test_tampered_posting_preview_or_metadata_cannot_pass_integrity(self):
        for target in ['postings/0.json','entries/0.json','metadata.json']:
            with self.subTest(target=target),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);build_fixture(root)
                path=root/'search/fixture'/target;data=json.loads(path.read_bytes())
                if target.startswith('postings'):data.pop(next(iter(data)))
                elif target.startswith('entries'):data['preview']='changed'
                else:data['rows'][0][0]='changed title'
                path.write_text(json.dumps(data),encoding='utf8')
                with self.assertRaises(AssertionError):verify(root,'fixture')

    def test_delta_encoding_zero_and_large_ids_and_invalid_order(self):
        ids=[0,1,35,36,127,20008]
        self.assertEqual(decode_ids(encode_ids(ids),20009),ids)
        for encoded in ['', '-1','0.0','1.-1','z.z.z','!','0..1']:
            with self.subTest(encoded=encoded),self.assertRaises(ValueError):decode_ids(encoded,40)

    def test_read_only_legacy_fixtures_and_safe_output_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);rows=fixture_rows()
            (root/'search-index.json').write_text(json.dumps(rows),encoding='utf8')
            self.assertEqual(metadata_rows(root),rows)
            site=SimpleNamespace(revision='../escape',output=root,search=rows)
            with self.assertRaises(ValueError):publish(site)


if __name__=='__main__':unittest.main()
