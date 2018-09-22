from config.settings.local import *  # noqa: F401,F403

UPDATE_DATABASE = {'NAME': 'testdb', 'HOST': 'localhost'}

try:
    from . import secure
except ImportError:
    port = 5432
else:
    port = 5431

UPDATE_DATABASE['PORT'] = port

DATABASES['default'].update(UPDATE_DATABASE)  # noqa: F405
CACHES['default'].update({'LOCATION': 'redis://localhost:6379/1'})  # noqa: F405
