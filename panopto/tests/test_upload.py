import unittest

from panopto.upload import PanoptoUploadTarget


class TestPanoptoUploadTarget(unittest.TestCase):

    def test_initialization(self):
        upload_id = '39fe1efd-1f0e-46d4-b497-2643443aae8a'
        target = 'https://test.hosted.panopto.com/Panopto/' \
            'Upload/ac6bef38-19a8-46ce-996a-e863012b0747'

        self.obj = PanoptoUploadTarget(upload_id, target)

        self.assertEquals(self.obj.host(),
                          'test.hosted.panopto.com')

        self.assertEquals(self.obj.bucket_name, 'Panopto/Upload')

        self.assertEquals(self.obj.file_key('foo.mp4'),
                          'ac6bef38-19a8-46ce-996a-e863012b0747/foo.mp4')
