from django.conf import settings
from dictobj import MutableDictionaryObject

DROPBOX_DEFAULT = {
  """
  A dictionary containing all the applicable dropbox settings, along with their defaults.
  Users may override any setting in their own settings.DROPBOX.
  """
  
  'app_key':None,
  'app_secret':None,
  'access_key':None,
  'access_secret':None,
  
  # access_type should be 'dropbox' or 'app_folder' as configured for your app
  'access_type':'dropbox',

  # The following functionality is disabled by default.
  #
  # If the filename already exists, add an underscore and a number (before
  # the file extension, if one exists) to the filename until the generated
  # filename doesn't exist.
  'overwrite_mode':False,
}

# Update the default settings with our user's custom updates.
DROPBOX_DEFAULT.update(getattr(settings.DROPBOX, 'DROPBOX', {}))

# Wrap the dropbox settings into a comfortable MutableDictionaryObject.
DROPBOX = MutableDictionaryObject(DROPBOX_DEFAULT)
