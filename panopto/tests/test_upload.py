import unittest

from panopto.upload import PanoptoUploadTarget, PanoptoUpload


class TestPanoptoUploadTarget(unittest.TestCase):

    def test_initialization(self):
        upload_id = '39fe1efd-1f0e-46d4-b497-2643443aae8a'
        target = 'https://test.hosted.panopto.com/Panopto/' \
            'Upload/ac6bef38-19a8-46ce-996a-e863012b0747'

        self.obj = PanoptoUploadTarget(upload_id, target)

        self.assertEqual(self.obj.host(),
                         'https://test.hosted.panopto.com')

        self.assertEqual(self.obj.bucket_name, 'Panopto')

        self.assertEqual(self.obj.file_key('foo.mp4'),
                         'Upload/ac6bef38-19a8-46ce-996a-e863012b0747/foo.mp4')

    def test_pypanopto_manifest(self):
        uploader = PanoptoUpload()
        manifest = uploader._panopto_manifest('/tmp', u'foo', u'foo bar')
        self.assertTrue(b'<Title>foo</Title>' in manifest)
        self.assertTrue(b'<Filename>/tmp</Filename>' in manifest)
        self.assertTrue(b'<Description>foo bar</Description>' in manifest)
