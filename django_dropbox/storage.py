import errno
import os.path
import re
import itertools
try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO
from dropbox.session import DropboxSession
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.encoding import filepath_to_uri

from .settings import DROPBOX

class DropboxFile(File):
  def __init__(self, name, storage, mode):
    self._storage = storage
    self._mode = mode
    self._is_dirty = False
    self.file = StringIO()
    self.start_range = 0
    self._name = name

  @property
  def size(self):
    return self._storage.size(self._name)

  def read(self, num_bytes=None):
    return self._storage.client.get_file(self._name).read()

  def write(self, content):
    if 'w' not in self._mode:
      raise AttributeError("File was opened for read-only access.")
    self.file = StringIO(content)
    self._is_dirty = True

  def flush(self):
    """
    Push the contents of our data to Dropbox.
    """
    if self._is_dirty:
      self._storage.client.put_file(self._name, self.file.getvalue())
    
  def close(self):
    self.flush()
    self.file.close()

def abs_path(base_dir_attr):
  """
  Assuming the second parameter of the callable is a path, let's prepend
  a base directory to it.
  """
  def wrapper(callable):
    def wrapped(self, *args, **kwargs):
      args[0] = os.path.join(getattr(self, base_dir_attr), args[0])
      return callable(self, *args, **kwargs)
    return wrapped
  return wrapper

class DropboxStorage(Storage):
   """
   A storage class providing access to resources in a Dropbox Public folder.
   """
   def __init__(self, location=None):
     session = DropboxSession(DROPBOX.app_key, DROPBOX.app_secret, DROPBOX.access_type, locale=None)
     session.set_token(DROPBOX.access_key, DROPBOX.access_secret)
     self.client = DropboxClient(session)
     self.overwrite_mode = DROPBOX.overwrite_mode
     self._location = location

   @prepend_path_with_attr("_location")
   def delete(self, name):
     self.client.file_delete(name)

   @prepend_path_with_attr("_location")
   def exists(self, name):
     try:
       metadata = self.client.metadata(name, list=False)
       return not metadata.get('is_deleted')
     except ErrorResponse as e:
       if 404 == e.status: # not found
         return False
       raise e 
     return True

   @prepend_path_with_attr("_location")
   def listdir(self, name, query_filter=None):
     if query_filter is None or len(query_filter) < 3:
       metadata = self.client.metadata(name)
     else:
       metadata = self.client.search(name, query_filter, file_limit=25000)
     directories = []
     files = []
     for entry in metadata.get('contents', []):
       if entry['is_dir']:
         directories.append(os.path.basename(entry['path']))
       else:
         files.append(os.path.basename(entry['path']))
     return directories, files

   @prepend_path_with_attr("_location")
   def open(self, name, mode='rb'):
     return DropboxFile(name, self, mode)

   @prepend_path_with_attr("_location")
   def save(self, name, content):
     metadata = self.client.put_file(name, content)
     return metadata['path']

   @prepend_path_with_attr("_location")
   def size(self, name):
     return self.client.metadata(name, list=False)['bytes']

   @prepend_path_with_attr("_location")
   def url(self, name):
     try:
       return self.client.share(name)['url']
     except ErrorResponse as e:
       if 404 == e.status: # not found
         return None
       raise e

   @prepend_path_with_attr("_location")
   def get_available_name(self, name):
     """
     Returns a filename that's free on the target storage system, and
     available for new content to be written to.
     """
     if self.overwrite_mode:
       return name

     if self.exists(name):
       dir_name, file_name = os.path.split(name)
       file_root, file_ext = os.path.splitext(file_name)
       
       # If the filename already exists, add an underscore and a number (before
       # the file extension, if one exists) to the filename until the generated
       # filename doesn't exist.
       dir_contents = self.listdir(dir_name, file_root)
       count = itertools.count(1)
       while True:
         # file_ext includes the dot.
         name = "%s_%s%s" % (file_root, count.next(), file_ext)
         if name not in dir_contents:
           return os.path.join(dir_name, name)
     else:
       return name

   @prepend_path_with_attr("_location")
   def get_valid_name(self, name):
     return name
