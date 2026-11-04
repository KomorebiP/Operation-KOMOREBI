"""Check crawler-visible metadata and exact sitemap coverage."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from build_reader_site import Site
from check_reader_site import Page
from site_metadata import (BASE_URL, DESCRIPTIONS, MAX_DESCRIPTION, canonical_url,
                           description, head_metadata, publish, verify, verify_card)


class MetadataTests(unittest.TestCase):
    def test_canonical_urls_keep_the_project_prefix_and_encode_real_paths(self):
        for path, expected in [('index.html',''), ('read/paper-v/index.html','read/paper-v/'),
                               ('read/α & beta.html','read/%CE%B1%20%26%20beta.html')]:
            self.assertEqual(canonical_url(path),BASE_URL+expected)
        for path in ['', '/index.html', '//outside.test/a.html', '../a.html', 'read/../a.html',
                     'read/./a.html', 'read//a.html', 'a.html?q=x', 'a.html#x', 'a\\b.html', 'a.json']:
            with self.subTest(path=path), self.assertRaises(ValueError):canonical_url(path)

    def test_descriptions_use_chapter_prose_instead_of_navigation_or_source_code(self):
        prose='This chapter describes a finite reconstruction calculation and the assumptions needed to interpret its exact output.'
        body='<p>A long but irrelevant introductory toolbar paragraph outside the actual chapter, which must not be selected.</p>'
        body+='<article id="chapter-text"><nav><p>'+('Navigation words '*12)+'</p></nav>'
        body+='<p><a href="x">'+('Only links '*12)+'</a></p><pre><p>'+('Source code '*12)+'</p></pre>'
        body+='<p>This long mathematical paragraph needs its full equation to remain meaningful and should never become a fragmentary summary: <span class="arithmatex">equation</span>.</p>'
        body+='<p><span class="arithmatex">'+('formula '*20)+'</span></p><p>'+prose+'</p></article>'
        self.assertEqual(description('read/paper-v/intro.html','A chapter',body),prose)
        self.assertLessEqual(len(description('read/long.html','A very long title '*30,'')),MAX_DESCRIPTION)
        self.assertTrue(all(0<len(value)<=MAX_DESCRIPTION for value in DESCRIPTIONS.values()))

    def test_metadata_escapes_titles_and_prose_without_inventing_markup(self):
        title='α < β & "quoted"'
        text='A reader can inspect "quoted" assumptions & comparisons in this deliberately literal description of the current page.'
        page=Page('<head><title>α &lt; β &amp; "quoted" · Komorebi</title>'+head_metadata('read/a.html',title,'<p>'+text.replace('&','&amp;')+'</p>')+'</head>')
        meta=dict(page.metadata)
        self.assertEqual(meta['og:title'],title+' · Komorebi')
        self.assertEqual(meta['description'],text)
        self.assertEqual(meta['og:description'],text)
        self.assertEqual(meta['og:url'],BASE_URL+'read/a.html')
        self.assertEqual(page.canonicals,[BASE_URL+'read/a.html'])
        self.assertEqual(len(meta),len(page.metadata))

    def fixture(self,root):
        site=object.__new__(Site)
        site.root=Path(__file__).resolve().parents[1]
        site.output=root
        site.revision='fixture'
        shutil.copytree(site.root/'website/assets/brand',root/'assets/brand')
        paths=['index.html','read/paper-v/index.html','read/paper-v/chapter.html',
               'search.html','side-by-side.html','reading-list.html','lean/run.html','404.html']
        for path in paths:site.page(path,'Page '+path,'<h1>Example</h1><p>A complete mathematical reading page with its source links and recorded assumptions available for inspection.</p>')
        (root/'assets/viewer.html').write_text('<html>Unchanged third-party asset</html>',encoding='utf8')
        report=publish(site)
        pages={p:Page((root/p).read_text(encoding='utf8')) for p in paths}
        return site,pages,report

    def test_sitemap_matches_indexable_generated_pages_and_all_preview_fields_verify(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);site,pages,report=self.fixture(root)
            self.assertEqual(verify(root,pages),report)
            self.assertEqual(report['pages'],8)
            self.assertEqual(report['sitemap_urls'],3)
            xml=(root/'sitemap.xml').read_text(encoding='utf8')
            for excluded in ['search.html','reading-list.html','404.html','viewer.html','lastmod','changefreq','priority']:
                self.assertNotIn(excluded,xml)
            self.assertIn('Sitemap',(root/'index.html').read_text(encoding='utf8'))

    def test_stale_or_corrupt_sharing_art_cannot_pass(self):
        for key in ['image','source']:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);self.fixture(root)
                record=json.loads((root/'assets/brand/sharing-card.json').read_bytes())
                path=root/record[key];path.write_bytes(path.read_bytes()+b'changed')
                with self.assertRaises(AssertionError):verify_card(root)

    def test_duplicate_metadata_wrong_canonical_or_missing_sitemap_url_cannot_pass(self):
        for change in ['duplicate','canonical','sitemap']:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);site,pages,_=self.fixture(root)
                if change=='duplicate':pages['index.html'].metadata.append(('og:title','Duplicate'))
                elif change=='canonical':pages['index.html'].canonicals=[BASE_URL+'wrong.html']
                else:(root/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>',encoding='utf8')
                with self.assertRaises(AssertionError):verify(root,pages)


if __name__=='__main__':unittest.main()
