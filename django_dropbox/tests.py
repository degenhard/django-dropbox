import tempfile
from django.core.files.base import ContentFile
from django.test import TestCase
from django_dropbox.storage import DropboxStorage

class DropboxStorageTest(TestCase):
  def setUp(self):
    self.location = '/Public/testing'
    self.storage = DropboxStorage(location=self.location)
    self.tmpfile = tempfile.NamedTemporaryFile()

  def tearDown(self):
    self.tmpfile.close()

  def test_file_access(self):
    """
    Standard file access options are available, and work as expected.
    """
    self.assertFalse(self.storage.exists('storage_test'))
    
    with self.storage.open('storage_test', 'w') as f:
      f.write('storage contents')
    self.assertTrue(self.storage.exists('storage_test'))

    with self.storage.open('storage_test', 'r') as f:
      self.assertEqual(f.read(), 'storage contents')

    self.storage.delete('storage_test')
    self.assertFalse(self.storage.exists('storage_test'))

  def test_exists_folder(self):
    self.assertFalse(self.storage.exists('storage_test_exists'))
    self.storage.client.file_create_folder(self.location + '/storage_test_exists')
    self.assertTrue(self.storage.exists('storage_test_exists'))
    self.storage.delete('storage_test_exists')
    self.assertFalse(self.storage.exists('storage_test_exists'))

  def test_listdir(self):
    """
    File storage returns a tuple containing directories and files.
    """
    self.assertFalse(self.storage.exists('storage_test_1'))
    self.assertFalse(self.storage.exists('storage_test_2'))
    self.assertFalse(self.storage.exists('storage_dir_1'))

    f = self.storage.save('storage_test_1', ContentFile('custom content'))
    f = self.storage.save('storage_test_2', ContentFile('custom content'))
    self.storage.client.file_create_folder(self.location + '/storage_dir_1')

    dirs, files = self.storage.listdir(self.location)
    self.assertEqual(set(dirs), set([u'storage_dir_1']))
    self.assertEqual(set(files),
                     set([u'storage_test_1', u'storage_test_2']))

    self.storage.delete('storage_test_1')
    self.storage.delete('storage_test_2')
    self.storage.delete('storage_dir_1')
    
  def test_file_url(self):
    """
    File storage returns a url to access a given file from the Web.
    """
    # url = self.share(path)
    # self.assertRaises(ValueError, self.storage.url, 'test.file')
    pass

  def test_file_size(self):
    """
    File storage returns a url to access a given file from the Web.
    """
    self.assertFalse(self.storage.exists('storage_test_size'))

    contents = "here are some file contents."
    with self.storage.open('storage_test_size', 'w') as f:
      f.write(contents)
    self.assertTrue(self.storage.exists('storage_test_size'))

    with self.storage.open('storage_test_size', 'r') as f:
      self.assertEqual(f.size, len(contents))

    self.storage.delete('storage_test_size')
    self.assertFalse(self.storage.exists('storage_test_size'))
