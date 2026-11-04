"""Check reading order, boundaries and uncluttered access to secondary routes."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from reading_navigation import entries, neighbours, navigation, outline, resources, work_links, Navigation, publish_record, verify, chapter_layout, sequence_groups, contents_list, atlas_config, visual_title, visual_backlink, visual_position, visual_contents


class ReadingNavigationTests(unittest.TestCase):
    def config(self, partial=False):
        return dict(work='test',label='Paper test',index='read/test/index.html',
                    chapters=[dict(url='read/test/one.html',title='I. First part'),
                              dict(url='read/test/two.html',title='II. Second part')],
                    bib_page='read/test/references.html',partial=partial)

    def test_sequence_includes_bibliography_and_reciprocal_neighbours(self):
        config=self.config();sequence=entries(config)
        self.assertEqual([e['url'] for e in sequence],['read/test/one.html','read/test/two.html','read/test/references.html'])
        for i,entry in enumerate(sequence):
            _,position,previous,following=neighbours(config,entry['url'])
            self.assertEqual(position,i)
            if i:self.assertEqual(previous,sequence[i-1])
            if i+1<len(sequence):self.assertEqual(following,sequence[i+1])
        self.assertEqual(neighbours(config,sequence[0]['url'])[2]['url'],config['index'])
        self.assertEqual(neighbours(config,sequence[-1]['url'])[3]['url'],config['index'])

    def test_custom_reader_does_not_duplicate_references(self):
        config=self.config();config['chapters'].append(dict(url=config['bib_page'],title='References'))
        self.assertEqual(len(entries(config)),3)
        self.assertEqual(entries(config)[-1]['title'],'References')

    def test_partial_edition_continues_in_sources(self):
        config=self.config(True)
        self.assertEqual(neighbours(config,config['bib_page'])[3]['url'],'read/test/index.html#source-continuations')
        self.assertIn('Continue reading',navigation(config,config['bib_page']))
        self.assertNotIn('Finished',navigation(config,config['bib_page']))

    def test_current_part_is_marked_and_native_menu_works_without_script(self):
        config=self.config();markup=navigation(config,'read/test/two.html')
        parsed=Navigation(markup).controls[0]
        current=[a for a in parsed['links'] if a.get('aria-current')=='page']
        self.assertEqual(len(current),1);self.assertEqual(current[0]['href'],'two.html')
        self.assertIn('<summary>Chapters</summary>',markup)
        self.assertIn('II. Second part',markup)
        self.assertIn('rel="prev" href="one.html"',markup)
        self.assertIn('rel="next" href="references.html"',markup)
        self.assertNotIn(' hidden',markup);self.assertNotIn('<script',markup)
        self.assertNotIn(' open',outline('<nav>Sections</nav>'))
        self.assertNotIn(' open',resources('Sources'))

    def test_book_footer_keeps_neighbors_and_contents_without_a_second_full_menu(self):
        config=self.config();config['footer_index_only']=True
        top=Navigation(navigation(config,'read/test/two.html')).controls[0]
        footer=navigation(config,'read/test/two.html','bottom');bottom=Navigation(footer).controls[0]
        self.assertEqual(len([a for a in top['links'] if 'data-reading-entry' in a]),3)
        self.assertFalse(any('data-reading-entry' in a for a in bottom['links']))
        self.assertEqual([a['href'] for a in bottom['links'] if 'reading-menu-link' in a.get('class','')],['index.html'])
        self.assertIn('rel="prev" href="one.html"',footer)
        self.assertIn('rel="next" href="references.html"',footer)
        self.assertNotIn('<script',footer);self.assertNotIn(' hidden',footer)
        # Adding hundreds of topics must not multiply every footer's markup.
        config['chapters'] += [dict(url='read/test/topic-'+str(i)+'.html',title='Topic '+str(i)) for i in range(1000)]
        self.assertLess(len(navigation(config,'read/test/two.html','bottom').encode()),2000)

    def test_secondary_routes_are_grouped_without_losing_unique_destinations(self):
        targets=[('Read chapters','read/test/index.html'),('Read PDF','read/test/pdf.html'),
                 ('Lean','work.html#lean'),('Evidence','work.html#evidence'),
                 ('Search this work','search.html?work=test'),('Other <route>','more.html')]
        reader=SimpleNamespace(work_route_targets=lambda work:targets,site=SimpleNamespace(rel=lambda url,page:url))
        markup=work_links(reader,'test','read/test/one.html')
        self.assertNotIn('read/test/index.html',markup)
        for label,url in targets[1:]:self.assertEqual(markup.count('href="'+url+'"'),1)
        self.assertIn('Read and explore',markup);self.assertIn('Proofs and implementation',markup)
        self.assertIn('Other &lt;route&gt;',markup)

    def test_unknown_and_duplicate_pages_are_rejected(self):
        config=self.config()
        with self.assertRaisesRegex(ValueError,'outside'):navigation(config,'read/other/one.html')
        config['chapters'].append(config['chapters'][0])
        with self.assertRaisesRegex(ValueError,'unique'):entries(config)

    def test_grouped_contents_preserve_order_and_open_only_the_current_part(self):
        config=self.config()
        config['contents_groups']=[dict(start='read/test/one.html',title='Part I'),
                                   dict(start='read/test/two.html',title='Part II')]
        groups=sequence_groups(config)
        self.assertEqual([title for title,_ in groups],['Part I','Part II','References'])
        self.assertEqual([entry for _,group in groups for entry in group],entries(config))
        markup=contents_list(config,'read/test/two.html',1)
        self.assertEqual(markup.count(' open'),1)
        self.assertIn('<details class="reading-contents-group" open><summary>Part II',markup)
        self.assertEqual(markup.count('aria-current="page"'),1)
        self.assertNotIn(' open',contents_list(config,config['index']))
        config['contents_groups'].reverse()
        with self.assertRaisesRegex(ValueError,'in order'):sequence_groups(config)

    def test_atlas_controls_use_the_full_sequence_and_preserve_boundaries(self):
        plates=[dict(number=i,url='read/test/atlas/v'+str(i)+'.html',title='Plate '+str(i)) for i in range(1,4)]
        config=atlas_config('test','Paper test','read/test/atlas/index.html',plates)
        self.assertIn('<summary>Visuals</summary>',navigation(config,plates[1]['url']))
        self.assertIn('All 3 visuals',navigation(config,plates[1]['url']))
        for plate in plates:
            for placement in ('top','bottom'):
                control=Navigation(navigation(config,plate['url'],placement)).controls[0]
                self.assertEqual(len([a for a in control['links'] if 'data-reading-entry' in a]),3 if placement=='top' else 0)
                self.assertEqual(control['attrs']['data-reading-placement'],placement)
                self.assertIn('../../../collection/works/test.html',[a['href'] for a in control['links']])
        self.assertEqual(neighbours(config,plates[0]['url'])[2]['url'],config['index'])
        self.assertEqual(neighbours(config,plates[-1]['url'])[3]['url'],config['index'])

    def test_visual_labels_use_the_subject_and_keep_position_separate(self):
        from reading_navigation import visual_search_terms
        entry=dict(number=3,title=r'Residues in $\mathbb{F}_5$',url='read/test/atlas/v03.html')
        config=atlas_config('test','Paper test','read/test/atlas/index.html',[entry])
        self.assertEqual(entries(config)[0]['title'],'Residues in F_5')
        self.assertEqual(visual_title('Paper test',entry),'Paper test visual guide / Residues in F_5')
        self.assertEqual(visual_backlink(entry),'Visual guide: Residues in F_5')
        self.assertEqual(visual_position('Paper test',3,24),'Paper test visual guide · Visual 3 of 24')
        self.assertEqual(visual_search_terms(entry),'Visual 3 V3')
        self.assertEqual(visual_search_terms(dict(entry,url='read/test/atlas/s03.html')),'Visual 3 Section 3')
        self.assertEqual(visual_search_terms(dict(entry,url='read/test/atlas/l03.html')),'Visual 3 Lesson 3')

    def test_visual_search_preview_uses_the_drawing_description_and_preserves_math(self):
        from reading_navigation import visual_search_preview
        from readable_chapters import Chapter
        chapter=Chapter('',{})
        chapter.math=[r'Q=I']
        chapter.nodes=[dict(kind='figure',body='drawing')]
        figures={'drawing':dict(description=dict(description=r'The grid retains $P_\alpha=Q_\alpha$.'))}
        preview=visual_search_preview(chapter,figures)
        self.assertEqual(preview['preview_parts'],[dict(type='text',text='The grid retains '),
            dict(type='math',text=r'P_\alpha=Q_\alpha'),dict(type='text',text='.')])
        self.assertEqual(chapter.math,[r'Q=I'])
        figures['drawing']['description']='A source-bound diagram description.'
        self.assertEqual(visual_search_preview(chapter,figures)['preview_parts'],
                         [dict(type='text',text='A source-bound diagram description.')])
        chapter.nodes=[]
        self.assertEqual(visual_search_preview(chapter,figures),{})

    def test_visual_contents_link_titles_directly_and_keep_pdf_context_and_anchors(self):
        import posixpath
        entry=dict(number=3,title='Packets & coordinates',url='read/test/atlas/v03.html')
        relative=lambda target,page:posixpath.relpath(target,posixpath.dirname(page))
        body=visual_contents([entry],'read/test/atlas/index.html',relative,lambda p:'pdf.html#page=5')
        self.assertIn('id="v03"',body)
        self.assertIn('<a href="v03.html">Packets &amp; coordinates</a>',body)
        self.assertIn('href="pdf.html#page=5" aria-label="Original PDF: Packets &amp; coordinates"',body)
        self.assertNotIn('Read V3',body)

    def test_section_and_lesson_guides_share_visual_controls_and_group_boundaries(self):
        from paper_ix_atlas import reading_config as ix
        from paper_xi_atlas import reading_config as xi
        for builder,total,starts in [(ix,23,[1,16]),(xi,47,[1,12,24,40,46])]:
            from inspect import getmodule
            module=getmodule(builder)
            selected=[dict(number=n,title='Subject '+str(n),url=module.section_url(n)) for n in range(1,total+1)]
            config=builder(selected)
            self.assertEqual(config['menu_title'],'Visuals')
            self.assertTrue(config['footer_index_only'])
            self.assertEqual([e['title'] for e in entries(config)],[r['title'] for r in selected])
            self.assertEqual([g['start'] for g in config['contents_groups']],[module.section_url(n) for n in starts])

    def test_paper_vi_groups_cover_every_page_once(self):
        from paper_vi_reading import BOOK
        groups=sequence_groups(BOOK)
        self.assertEqual([len(group) for _,group in groups],[21,20,8,1,1])
        self.assertEqual([entry for _,group in groups for entry in group],entries(BOOK))

    def test_sidebar_preserves_nested_contents_and_exact_article_bytes(self):
        contents=outline('<nav class="chapter-contents"><h2 id="contents">Contents</h2>'
                         '<a href="#L4">Section</a><details><summary>Statements</summary>'
                         '<a href="#L5">Theorem</a></details></nav>')
        article='<article id="chapter-text"><h2 id="L4">A &amp; B</h2><section id="L5">\\(x&lt;y\\)</section></article>'
        source='<h1>Title</h1>'+contents+resources('<details><summary>Sources</summary>TeX</details>')+article+'<nav>Next chapter</nav>'
        result=chapter_layout(source)
        self.assertEqual(result.count(article),1)
        self.assertEqual(result.count('href="#L5"'),1)
        self.assertIn('<details><summary>Statements</summary><a href="#L5">Theorem</a></details>',result)
        self.assertIn('<details><summary>Sources</summary>TeX</details>',result)
        self.assertIn('id="contents"',result)
        self.assertTrue(result.endswith('<nav>Next chapter</nav>'))
        self.assertLess(result.index('class="chapter-toolbar"'),result.index('class="chapter-layout"'))
        self.assertNotIn(' open',result)

    def test_pages_without_a_chapter_outline_keep_their_structure(self):
        for source in ('<h1>Guide</h1>', '<article id="chapter-text">References</article>',
                       outline('<nav>Contents</nav>')+'<article>Other page</article>'):
            self.assertEqual(chapter_layout(source),source)

    def test_sidebar_return_links_keep_the_work_and_contents_with_exact_article(self):
        config=self.config();config['label']='Paper <test> & reader'
        article='<article id="chapter-text"><h2 id="L4">Kept</h2><p>\\(x+y\\)</p></article>'
        body=navigation(config,'read/test/two.html')+outline('<nav class="chapter-contents"><a href="#L4">Kept</a></nav>')+article+navigation(config,'read/test/two.html','bottom')
        result=chapter_layout(body)
        parsed=Navigation(result)
        self.assertEqual(result.count(article),1)
        self.assertEqual(len(parsed.controls),2)
        self.assertEqual([a['href'] for a in parsed.returns[0]['links']],['one.html','../../collection/works/test.html','index.html','references.html'])
        self.assertIn('aria-label="Paper &lt;test&gt; &amp; reader overview"',result)
        self.assertLess(result.index('class="reading-return"'),result.index('</aside>'))
        self.assertNotIn(' hidden',result)

    def test_nested_atlas_return_links_keep_their_own_index(self):
        config=atlas_config('test','Paper test','read/test/atlas/index.html',[dict(number=1,url='read/test/atlas/v1.html',title='A plate')])
        body=navigation(config,'read/test/atlas/v1.html')+outline('<nav>Sections</nav>')+'<article id="chapter-text">A plate</article>'
        links=Navigation(chapter_layout(body)).returns[0]['links']
        self.assertEqual([a['href'] for a in links],['index.html','../../../collection/works/test.html','index.html','index.html'])

    def test_partial_reader_return_row_keeps_the_source_continuation(self):
        config=self.config(True);page=config['bib_page']
        body=navigation(config,page)+outline('<nav>Sections</nav>')+'<article id="chapter-text">Text</article>'
        result=chapter_layout(body)
        self.assertEqual(Navigation(result).returns[0]['links'][-1]['href'],'index.html#source-continuations')
        self.assertIn('>Continue →</a>',result)

    def test_verifier_rejects_wrong_next_menu_and_missing_footer(self):
        import readable_chapters
        config=self.config();config['footer_index_only']=True
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            def write(path,text):
                dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
            publish_record(SimpleNamespace(write=write),{'test':config})
            for entry in entries(config):
                write(entry['url'],navigation(config,entry['url'])+'<article>Text</article>'+navigation(config,entry['url'],'bottom'))
            first='read/test/one.html'
            write(first,chapter_layout(navigation(config,first)+outline('<nav>Sections</nav>')+'<article id="chapter-text">Text</article>'+navigation(config,first,'bottom')))
            pages={entry['url']:None for entry in entries(config)}
            with patch.dict(readable_chapters.BOOKS,{'test':config},clear=True):
                self.assertEqual(verify(root,pages,dict(files=[])),dict(editions=1,reading_pages=3,navigation_controls=6))
                page=root/'read/test/one.html';original=page.read_text(encoding='utf-8')
                for bad in [original.replace('rel="next" href="two.html"','rel="next" href="references.html"',1),
                            original.replace('data-reading-entry="2" href="two.html"','data-reading-entry="2" href="one.html"',1),
                            original.replace('class="reading-work-overview" href="../../collection/works/test.html"','class="reading-work-overview" href="../../collection/works/other.html"'),
                            original.replace('class="reading-full-contents" href="index.html"','class="reading-full-contents" href="two.html"'),
                            original.replace('class="reading-return"','class="other-return"'),
                            original.replace('class="reading-menu-link button" rel="contents" href="index.html"','class="reading-menu-link button" rel="contents" href="two.html"'),
                            navigation(config,'read/test/one.html')]:
                    page.write_text(bad,encoding='utf-8')
                    with self.assertRaises(AssertionError):verify(root,pages,dict(files=[]))
                page.write_text(original,encoding='utf-8')


if __name__=='__main__':unittest.main()
