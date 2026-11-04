"""Exercise whole-site coverage and capability boundaries for reading guides."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from build_reader_site import Site
from check_reader_site import Page
from reader_documents import page_path
from reading_paths import guide_model, guide_url, guide_enabled, eligible_books, EXISTING_GUIDES, publish, render_guide, verify, INDEX, REPORT

ROOT=Path(__file__).resolve().parents[1]


def fixture(output):
    load=lambda name:json.loads((ROOT/'manifests'/name).read_bytes())
    registry=load('browse-resources.json');status=load('project-status.json')
    site=SimpleNamespace(root=ROOT,output=output,revision='reading-paths-test',registry=registry,guided_reading=True,
        status=status,assessments={r['id']:r for r in status['components']},
        components={r['id']:r for r in load('source-components.json')['components']},
        claims=load('claim-navigation.json'),search=[],editorial_editions={},cache=None)
    site.documents={('collection',r['reader_guide']):'' for r in status['components'] if r.get('reader_guide')}
    for name in ('rel','write','page'):
        setattr(site,name,lambda *args,_name=name,**kwargs:getattr(Site,_name)(site,*args,**kwargs))
    reader=SimpleNamespace(site=site,learning=load('reader-experience.json'),records={},lean_works={},
        paper_introductions=load('paper-introductions.json')['papers'],readable_books={})
    for component in registry['components']:
        paths=[r['path'] for r in component['resources']]
        work=component['id'];base=component['destination']+'/'
        intro=reader.paper_introductions.get(work)
        if intro:
            paths.append(intro['setup']['path'].removeprefix(base))
            claim=next(c for c in site.claims['records'] if c['id']==intro['claim'])
            paths.append(claim['statement_path'].removeprefix(base))
        receipt=load('source-imports/'+work+'.json')
        owned={f['path']:f for f in receipt['files']}
        for path in paths:
            if path not in owned:continue  # Directory shortcuts use the work's file list.
            full=base+path;reader.records[full]=dict(work=work,url=page_path(work,full))
    # A prepared-book stand-in lets guide tests move source anchors without
    # coupling them to current manuscript line numbers.
    from kcos_routes import REQUIRED_LABELS
    work='monographs-cos-method'
    reader.readable_books[work]=dict(chapters=[
        (dict(source='monographs/cos-method/book/fixture.tex',url='read/'+work+'/fixture-chapter.html'),
         b'',SimpleNamespace(nodes=[dict(id='fixture-'+str(i),kind='subsection',labels=[label])
                                   for i,label in enumerate(REQUIRED_LABELS)]))])
    return reader


class ReadingPathsTests(unittest.TestCase):
    def test_kcos_worked_enclosure_uses_the_prepared_manuscript_label(self):
        with tempfile.TemporaryDirectory() as folder:
            reader=fixture(Path(folder));work='monographs-cos-method'
            component=next(c for c in reader.site.registry['components'] if c['id']==work)
            spec,_,chapter=reader.readable_books[work]['chapters'][0]
            enclosure=next(n for n in chapter.nodes if 'sec:worked-enclosure' in n['labels'])
            enclosure['id']='enclosure-after-source-move'
            spec['url']='read/'+work+'/moved-enclosure.html'
            model=guide_model(reader,component)
            step=next(s for s in model['paths'][0]['steps'] if s['title']=='A worked probability enclosure')
            self.assertEqual(step['url'],spec['url']+'#enclosure-after-source-move')
            render_guide(reader.site,model)
            page=Page((reader.site.output/model['url']).read_text())
            self.assertIn('moved-enclosure.html#enclosure-after-source-move',page.links)
            self.assertNotIn('09-intervals.html',page.links)
            enclosure['labels']=[]
            with self.assertRaisesRegex(ValueError,'Missing K-COS reading-path labels'):
                guide_model(reader,component)
            del reader.readable_books[work]
            with self.assertRaisesRegex(ValueError,'requires its prepared manuscript'):
                guide_model(reader,component)

    def test_only_complete_html_manuscripts_with_html_visual_guides_get_paths(self):
        reader=fixture(Path('unused'))
        models=[guide_model(reader,c) for c in reader.site.registry['components'] if c['id'] in eligible_books()]
        self.assertEqual(len(models),15)
        self.assertEqual(set(eligible_books()),set(reader.paper_introductions)|{
            'monographs-quantum-and-circuits','monographs-large-signal-model','monographs-cos-method'})
        self.assertEqual(len({m['url'] for m in models}),15)
        for model in models:
            self.assertEqual(len(model['paths']),3)
            self.assertEqual(model['scope'],reader.site.assessments[model['work']]['scope'])
            self.assertTrue(all(p['steps'] for p in model['paths']))
            self.assertTrue(all(len({s['url'] for s in p['steps']})==len(p['steps']) for p in model['paths']))

    def test_pdf_only_experimental_and_manuscript_only_works_stay_out(self):
        reader=fixture(Path('unused'))
        for component in reader.site.registry['components']:
            if component['id'] not in eligible_books():
                self.assertEqual(guide_enabled(reader.site,component['id']),component['id'] in EXISTING_GUIDES)
                with self.assertRaisesRegex(ValueError,'complete HTML manuscript and HTML visual guide'):
                    guide_model(reader,component)
        import readable_chapters as reading
        configs={
            'pdf-only':dict(chapters=[],atlas_index='read/visual.html'),
            'manuscript-only':dict(chapters=[dict(url='read/one.html')]),
            'partial':dict(chapters=[dict(url='read/one.html')],partial=True,atlas_index='read/visual.html'),
            'complete':dict(chapters=[dict(url='read/one.html')],visual_guide_index='read/visual.html')}
        with patch.object(reading,'BOOKS',configs):self.assertEqual(set(eligible_books()),{'complete'})

    def test_core_questions_setup_statements_and_proofs_remain_work_specific(self):
        reader=fixture(Path('unused'))
        for component in reader.site.registry['components'][:12]:
            model=guide_model(reader,component);work=component['id']
            intro=reader.paper_introductions[work]
            self.assertEqual(model['question'],intro['question'])
            self.assertEqual(model['limits'],intro['limits'])
            self.assertIn('#L'+str(intro['setup']['line']),model['paths'][2]['steps'][0]['url'])
            self.assertIn('written proof',model['paths'][2]['steps'][2]['title'])
        reader.paper_introductions['paper-i']['example']='refinement'
        with self.assertRaisesRegex(ValueError,'another work'):guide_model(reader,reader.site.registry['components'][0])

    def test_missing_pdf_and_cross_work_resources_fail_closed(self):
        reader=fixture(Path('unused'));component=reader.site.registry['components'][0]
        pdf=next(r for r in component['resources'] if r['kind']=='pdf')
        path=component['destination']+'/'+pdf['path']
        reader.records[path]['work']='paper-ii'
        with self.assertRaisesRegex(ValueError,'Cross-work'):guide_model(reader,component)
        del reader.records[path]
        with self.assertRaisesRegex(ValueError,'Missing published'):guide_model(reader,component)

    def test_publish_preserves_curated_guides_and_checks_selected_routes(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder);reader=fixture(output)
            from quantum_start import publish as publish_quantum
            publish_quantum(reader,None)
            quantum=(output/guide_url('monographs-quantum-and-circuits')).read_bytes()
            lsm=guide_url('monographs-large-signal-model')
            reader.site.page(lsm,'Retained LSM guide','<h1>Retained guide</h1><h2 id="introduction">First reading</h2><h2 id="study">Study</h2><h2 id="evidence">Evidence</h2>')
            lsm_bytes=(output/lsm).read_bytes()
            rows=publish(reader)
            self.assertEqual((output/guide_url('monographs-quantum-and-circuits')).read_bytes(),quantum)
            self.assertEqual((output/lsm).read_bytes(),lsm_bytes)
            self.assertEqual({r['work'] for r in rows},set(eligible_books()))
            pages={p.relative_to(output).as_posix():Page(p.read_text(encoding='utf-8')) for p in output.rglob('*.html')}
            # Stand-in destination pages retain their actual source-linked anchors.
            for row in rows:
                for target in row['targets']:
                    path,_,anchor=target.partition('#')
                    if path not in pages:pages[path]=Page('<h1>Target</h1>')
                    if anchor and anchor not in pages[path].ids:pages[path].ids.append(anchor)
                overview='collection/works/'+row['work']+'.html'
                pages.setdefault(overview,Page('<h1>Work overview</h1>'))
                pages[overview].links.append(reader.site.rel(row['url'],overview))
            documents={'source_revision':reader.site.revision}
            self.assertEqual(verify(output,documents,pages),{'works':15,'paths':45})
            self.assertEqual(len([s for s in reader.site.search if s['url']!=INDEX]),14)
            record=json.loads((output/REPORT).read_bytes());record['guides'].pop()
            (output/REPORT).write_text(json.dumps(record),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'every eligible'):verify(output,documents,pages)
            (output/REPORT).write_text(json.dumps(dict(source_revision=reader.site.revision,guides=rows)),encoding='utf-8')
            pages[rows[0]['url']].links.remove(reader.site.rel(rows[0]['targets'][0],rows[0]['url']))
            with self.assertRaises(AssertionError):verify(output,documents,pages)

    def test_editorial_metadata_is_escaped_in_the_generated_guide(self):
        with tempfile.TemporaryDirectory() as folder:
            reader=fixture(Path(folder));model=guide_model(reader,reader.site.registry['components'][0])
            model['summary']='<script>unsafe</script>'
            render_guide(reader.site,model)
            text=(reader.site.output/model['url']).read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;',text)
            self.assertNotIn('<script>unsafe</script>',text)

    def test_only_eligible_work_toolbars_gain_a_guide(self):
        from reader_documents import ReadingDocuments
        reader=fixture(Path('unused'));reader.primary_pdf=lambda work:None
        reader.manuscript_roots={}
        reader.work_route_targets=lambda work:ReadingDocuments.work_route_targets(reader,work)
        for component in reader.site.registry['components']:
            work=component['id'];page='collection/works/'+work+'.html'
            body=ReadingDocuments.work_intro(reader,work,page)
            primary=body.split('<details class="work-more">')[0]
            if work not in eligible_books():
                self.assertNotIn(reader.site.rel(guide_url(work),page),Page(body).links)
                continue
            self.assertIn('<a class="button" href="'+reader.site.rel(guide_url(work),page)+'">Start here</a>',primary)
            self.assertEqual(Page(body).links.count(reader.site.rel(guide_url(work),page)),1)

    def test_standalone_reading_library_omits_unpublished_site_guides(self):
        import readable_chapters as reading
        with tempfile.TemporaryDirectory() as folder:
            reader=fixture(Path(folder));reader.primary_pdf=lambda work:None
            work='komorebi-methodology'
            config=dict(work=work,label='Standalone',title='A retained book',
                        index='read/'+work+'/index.html',reading_guide=guide_url(work),
                        atlas_index='read/'+work+'/atlas/index.html',
                        chapters=[dict(url='read/'+work+'/one.html',title='Opening chapter')])
            reader.site.guided_reading=False
            with patch.object(reading,'BOOKS',{work:config}):reading.render_reading_index(reader)
            page=Page((reader.site.output/'read/index.html').read_text(encoding='utf-8'))
            self.assertNotIn('start.html',page.links)
            self.assertNotIn(work+'/start.html',page.links)
            self.assertIn(work+'/one.html',page.links)
            reader.site.guided_reading=True
            with patch.object(reading,'BOOKS',{work:config}):reading.render_reading_index(reader)
            page=Page((reader.site.output/'read/index.html').read_text(encoding='utf-8'))
            self.assertIn('start.html',page.links)
            self.assertIn(work+'/start.html',page.links)


if __name__=='__main__':unittest.main()
