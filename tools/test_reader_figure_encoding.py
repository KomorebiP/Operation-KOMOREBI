"""Pixel-preserving publication compression and adversarial receipt checks."""
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from PIL import Image
from encode_reader_figures import GROUPS, check
from reader_figure_assets import digest, dimensions, validate_encoding, prepare, image

ROOT=Path(__file__).resolve().parents[1]


class ReaderFigureEncodingTests(unittest.TestCase):
    def test_all_selected_originals_and_browser_images_have_identical_pixels(self):
        results=check(ROOT)
        self.assertEqual([r['group'] for r in results],list(GROUPS))
        self.assertEqual(sum(r['figures'] for r in results),233)
        self.assertGreater(sum(r['saved_bytes'] for r in results),10*1024*1024)
        for name in GROUPS:
            receipt=json.loads((ROOT/'website/assets/figures'/name/'figures.json').read_bytes())
            for row in receipt['figures']:
                raw=(ROOT/'website'/row['image']).read_bytes()
                self.assertEqual(dimensions(raw,row['image']),(row['width'],row['height']))

    def fixture(self,root):
        source=Image.new('RGBA',(4,3),(22,44,66,255));source.putpixel((1,2),(11,12,13,0))
        buffer=io.BytesIO();source.save(buffer,format='PNG');png=buffer.getvalue()
        buffer=io.BytesIO();source.save(buffer,format='WEBP',lossless=True,exact=True);webp=buffer.getvalue()
        record=dict(source='book/figures/test.pdf',source_sha256=digest(b'%PDF-source'),
            image='assets/figures/example/test.webp',image_sha256=digest(webp),
            original_png='verification/reader-figure-encoding/original/example/test.png',
            original_png_sha256=digest(png),source_rgba_sha256=digest(source.tobytes()),width=4,height=3)
        original=root/record['original_png'];original.parent.mkdir(parents=True);original.write_bytes(png)
        encoded=root/'website'/record['image'];encoded.parent.mkdir(parents=True);encoded.write_bytes(webp)
        return record,png,webp

    def test_legacy_png_and_new_webp_dimensions(self):
        with tempfile.TemporaryDirectory() as temporary:
            record,png,webp=self.fixture(Path(temporary))
            self.assertEqual(dimensions(png,'test.png'),(4,3))
            self.assertEqual(dimensions(webp,'test.webp'),(4,3))
            with self.assertRaisesRegex(ValueError,'static WebP'):
                dimensions(png,'test.webp')
            with self.assertRaisesRegex(ValueError,'Unsupported'):
                dimensions(webp,'test.jpg')

    def test_changed_pixels_fail_even_with_updated_encoded_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);record,_,_=self.fixture(root)
            altered=Image.new('RGBA',(4,3),(22,44,67,255));out=io.BytesIO()
            altered.save(out,format='WEBP',lossless=True,exact=True);raw=out.getvalue()
            (root/'website'/record['image']).write_bytes(raw);record['image_sha256']=digest(raw)
            with self.assertRaisesRegex(ValueError,'pixels differ'):
                validate_encoding(root,record,'assets/figures/example')

    def test_changed_original_receipt_or_unexpected_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);record,_,_=self.fixture(root)
            for change,message in [({'original_png_sha256':'0'*64},'PNG identity'),
                ({'source_rgba_sha256':'0'*64},'pixel identity'),
                ({'width':5},'dimensions differ'),
                ({'original_png':'verification/../outside.png'},'Unexpected original PNG')]:
                with self.subTest(change=change),self.assertRaisesRegex(ValueError,message):
                    validate_encoding(root,{**record,**change},'assets/figures/example')

    def test_shared_reader_binds_pdf_and_publishes_verified_webp(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);record,_,_=self.fixture(root)
            config=dict(base='book/',figure_receipts='assets/figures/example/figures.json')
            receipt=root/'website'/config['figure_receipts'];receipt.write_text(json.dumps(dict(figures=[record])))
            output=root/'output';output.mkdir()
            site=SimpleNamespace(root=root,output=output,read_source=lambda _:b'%PDF-source',rel=lambda target,page:target)
            reader=SimpleNamespace(site=site,add=lambda path:dict(path=path),images={})
            chapters=[({},b'',SimpleNamespace(nodes=[dict(kind='figure',body=r'\includegraphics[width=\linewidth]{test.pdf}')]))]
            assets=prepare(reader,config,chapters)
            source,target,sha=image(reader,config,{},assets,'test.pdf','read/test.html')
            self.assertEqual(source,record['source']);self.assertEqual(target,record['image'])
            self.assertEqual(sha,record['source_sha256'])
            self.assertEqual((output/target).read_bytes(),(root/'website'/record['image']).read_bytes())
            record['source_sha256']='0'*64;receipt.write_text(json.dumps(dict(figures=[record])))
            with self.assertRaisesRegex(ValueError,'source differs'):
                prepare(reader,config,chapters)


if __name__=='__main__':unittest.main()
