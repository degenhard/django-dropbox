# Description

A Django App that contains a Django Storage which uses Dropbox.

## Version
0.0.1

# Installing

## From Python Package Index

`pip install django-dropbox`

## Add it to your Django Project

In __settings.py__:

    INSTALLED_APPS = (
        ...
        'django_dropbox',
        ...
    )

Additionally, you must set these as well:

    DROPBOX.app_key = 'xxx'
    DROPBOX.app_secret = 'xxx'
    DROPBOX.access_key = 'xxx'
    DROPBOX.access_secret = 'xxx'
    DROPBOX.access_type = 'app_folder | dropbox'
    
## If you don't have any key/secet

If you don't have `DROPBOX.app_key` or `DROPBOX.app_secret`,
you will need to create a Dropbox app at [Dropbox for Developers](https://www.dropbox.com/developers).
Place the `app_key` and `app_secret` into `DROPBOX.app_key` and `DROPBOX.app_secret`, respectively.

After that run

    $ python manage.py get_dropbox_token

and follow the screen instructions.  Set the `DROPBOX.access_token` and `DROPBOX.access_secret`.
