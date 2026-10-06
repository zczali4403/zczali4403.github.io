"""Exercise CMS create/edit/delete behavior and publication boundaries."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import unquote

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_blog', SOURCE/'scripts/build_blog.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'content/posts').mkdir(parents=True)
        (self.root/'assets/blog').mkdir(parents=True)
        (self.root/'assets/blog/photo.png').write_bytes(b'photo fixture')
        (self.root/'index.html').write_text('<main><!-- WRITING START --><!-- WRITING END --></main>')
        self.out = self.root/'_site'

    def post(self, filename='test.json', **fields):
        data = dict(title='测试日记', date='2026-10-06', content='<p>正文</p><img src="/assets/blog/photo.png">')
        data.update(fields)
        path = self.root/'content/posts'/filename
        path.write_text(json.dumps(data))
        return path

    def test_new_month_image_and_chinese_filename(self):
        self.post('秋日.json')
        builder.build(self.root, self.out)
        self.assertTrue((self.out/'archives/2026/10/index.html').exists())
        self.assertTrue((self.out/'archives/2026/index.html').exists())
        self.assertIn('正文', (self.out/'diary/秋日/index.html').read_text())
        self.assertEqual((self.out/'assets/blog/photo.png').read_bytes(), b'photo fixture')
        self.assertIn('测试日记', (self.out/'index.html').read_text())
        self.assertFalse((self.out/'content').exists())
        self.assertFalse((self.out/'posts.json').exists())

    def test_edit_keeps_url_delete_removes_output(self):
        p = self.post()
        builder.build(self.root, self.out)
        self.post(title='改了标题', date='2027-02-03')
        builder.build(self.root, self.out)
        self.assertIn('改了标题', (self.out/'diary/test/index.html').read_text())
        self.assertFalse((self.out/'archives/2026/10').exists())
        p.unlink()
        builder.build(self.root, self.out)
        self.assertFalse((self.out/'diary/test/index.html').exists())
        self.assertNotIn('改了标题', (self.out/'blog/index.html').read_text())

    def test_pagination_past_twenty(self):
        for i in range(23):
            self.post(f'{i:02d}.json')
        builder.build(self.root, self.out)
        self.assertTrue((self.out/'archives/page/3/index.html').exists())
        page = (self.out/'archives/2026/10/page/3/index.html').read_text()
        self.assertEqual(page.count('<article class="writing-card">'), 3)

    def test_invalid_and_duplicate_urls_fail_without_replacing_site(self):
        p = self.post()
        builder.build(self.root, self.out)
        original = (self.out/'index.html').read_text()
        for url in ['/../../outside/', '/admin/', '//example.com/', '/diary/a/../b/', '/diary/a/?q=1']:
            self.post(url=url)
            with self.assertRaises(ValueError):builder.build(self.root,self.out)
            self.assertEqual((self.out/'index.html').read_text(),original)
        self.post(url='/diary/same/')
        self.post('other.json', url='/diary/same/')
        with self.assertRaises(ValueError):builder.build(self.root,self.out)

    def test_legacy_url_and_html_are_preserved(self):
        url = '/2023/11/23/About_memory/'
        content = '<div class="note"><p id="paragraph">保留旧正文</p></div>'
        self.post(url=url, content=content)
        builder.build(self.root,self.out)
        self.assertIn(content, (self.out/'2023/11/23/About_memory/index.html').read_text())
        self.assertIn(url, (self.out/'blog/index.html').read_text())

    def test_invalid_date_and_output_guard(self):
        self.post(date='2026-02-30')
        with self.assertRaises(ValueError):builder.build(self.root,self.out)
        self.post()
        with self.assertRaises(ValueError):builder.build(self.root,self.root)
        self.out.mkdir()
        (self.out/'user-file.txt').write_text('keep me')
        with self.assertRaises(ValueError):builder.build(self.root,self.out)
        self.assertEqual((self.out/'user-file.txt').read_text(),'keep me')

if __name__ == '__main__':unittest.main()
