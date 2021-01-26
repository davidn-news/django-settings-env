# -*- coding: utf-8 -*-
"""
Wrapper around os.environ
"""
import re
from typing import Any, MutableMapping
from urllib.parse import urlparse, urlunparse, parse_qs, unquote_plus
from .dot_env import load_env


DJANGO_POSTGRES = 'django.db.backends.postgresql'
REDIS_DRIVER = 'django_redis.cache.RedisCache'
MYSQL_DRIVER = 'django.db.backends.mysql'

DEFAULT_DATABASE_ENV = 'DATABASE_URL'
DB_SCHEMES = {
    'postgres': DJANGO_POSTGRES,
    'postgresql': DJANGO_POSTGRES,
    'psql': DJANGO_POSTGRES,
    'pgsql': DJANGO_POSTGRES,
    'postgis': 'django.contrib.gis.db.backends.postgis',
    'mysql': MYSQL_DRIVER,
    'mysql2': MYSQL_DRIVER,
    'mysql-connector': 'mysql.connector.django',
    'mysqlgis': 'django.contrib.gis.db.backends.mysql',
    'mssql': 'sql_server.pyodbc',
    'oracle': 'django.db.backends.oracle',
    'pyodbc': 'sql_server.pyodbc',
    'redshift': 'django_redshift_backend',
    'spatialite': 'django.contrib.gis.db.backends.spatialite',
    'sqlite': 'django.db.backends.sqlite3',
    'ldap': 'ldapdb.backends.ldap',
}
_DB_BASE_OPTIONS = ['CONN_MAX_AGE', 'ATOMIC_REQUESTS', 'AUTOCOMMIT', 'SSLMODE']

DEFAULT_CACHE_ENV = 'CACHE_URL'
CACHE_SCHEMES = {
    'dbcache': 'django.core.cache.backends.db.DatabaseCache',
    'dummycache': 'django.core.cache.backends.dummy.DummyCache',
    'filecache': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmemcache': 'django.core.cache.backends.locmem.LocMemCache',
    'memcache': 'django.core.cache.backends.memcached.MemcachedCache',
    'pymemcache': 'django.core.cache.backends.memcached.PyLibMCCache',
    'rediscache': REDIS_DRIVER,
    'redis': REDIS_DRIVER,
}
_CACHE_BASE_OPTIONS = ['TIMEOUT', 'KEY_PREFIX', 'VERSION', 'KEY_FUNCTION', 'BINARY']

DEFAULT_EMAIL_ENV = 'EMAIL_URL'
EMAIL_SCHEMES = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'smtp+tls': 'django.core.mail.backends.smtp.EmailBackend',
    'smtp+ssl': 'django.core.mail.backends.smtp.EmailBackend',
    'consolemail': 'django.core.mail.backends.console.EmailBackend',
    'filemail': 'django.core.mail.backends.filebased.EmailBackend',
    'memorymail': 'django.core.mail.backends.locmem.EmailBackend',
    'dummymail': 'django.core.mail.backends.dummy.EmailBackend'
}
_EMAIL_BASE_OPTIONS = ['EMAIL_USE_TLS', 'EMAIL_USE_SSL']

DEFAULT_SEARCH_ENV = 'SEARCH_URL'
SEARCH_SCHEMES = {
    "elasticsearch": "haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine",
    "elasticsearch2": "haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine",
    "solr": "haystack.backends.solr_backend.SolrEngine",
    "whoosh": "haystack.backends.whoosh_backend.WhooshEngine",
    "xapian": "haystack.backends.xapian_backend.XapianEngine",
    "simple": "haystack.backends.simple_backend.SimpleEngine",
}


class Env:
    """
    Wrapper around os.environ with .env enhancement and django support
    """
    BOOLEAN_TRUE_STRINGS = ('T', 't', '1', 'on', 'ok', 'Y', 'y', 'en')
    _EXCEPTION_CLS = KeyError

    @staticmethod
    def os_env():
        import os
        return os.environ

    def __init__(self, *args, environ: MutableMapping[str, str] = None, exception=None, readenv=False, **kwargs):
        self._env = environ or self.os_env()
        self._env.update(args)
        if readenv:
            self.read_env(**kwargs)
        else:
            self._env.update(kwargs)
        self.exception = exception or self._EXCEPTION_CLS

    def read_env(self, **kwargs):
        kwargs.setdefault('environ', self._env)
        self._env = load_env(**kwargs)

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, exc):
        if not issubclass(exc, Exception):
            raise ValueError(f'arg {exc} is not an exception class')
        self._exception = exc

    @property
    def env(self):
        return self._env

    def get(self, var, default=None):
        return self.env.get(var, default)

    def set(self, var, value=None):
        self.env[var] = str(value) if value is not None else value

    def unset(self, var):
        if var in self.env:
            del self._env[var]

    def is_all_set(self, *vars):
        return all(v in self for v in vars)

    def is_any_set(self, *vars):
        return any(v in self for v in vars)

    def int(self, var, default=None) -> int:
        val = self.get(var, default)
        return self._int(val)

    def float(self, var, default=None) -> float:
        val = self.get(var, default)
        return self._float(val)

    def bool(self, var, default=None) -> bool:
        val = self.get(var, default)
        return val if isinstance(val, (bool, int)) else self._is_true(val)

    def list(self, var, default=None) -> list:
        val= self.get(var, default)
        return val if isinstance(val, (list, tuple)) else self._list(val)

    @classmethod
    def _is_true(cls, val):
        return val if isinstance(val, bool) else \
            True if val and any([val.startswith(v) for v in cls.BOOLEAN_TRUE_STRINGS]) else False

    @classmethod
    def _int(cls, val):
        return val if isinstance(val, int) else int(val) if val and str.isdigit(val) else 0

    @classmethod
    def _float(cls, val):
        return val if isinstance(val, float) else float(val) if val else 0

    @classmethod
    def _list(cls, val):
        return [] if val is None else re.split(r'\s*,\s*', str(val))

    def __contains__(self, var):
        return str(var) in self.env

    def __setitem__(self, var: str, value: Any):
        self.set(var, value)

    def __getitem__(self, var):
        if var not in self:
            raise self.exception(f"Key '{var}' not found")
        return self.get(var)

    def __delitem__(self, var):
        self.unset(var)

    def _check_var(self, var, default):
        url = self.get(var, default=default) if var else default
        if not url:
            raise self.exception(f'Expected {var} is not set in environment')
        return url

    # Django-specific addons

    def database_url(self, var=DEFAULT_DATABASE_ENV, default=None, engine=None, options=None):
        """
        Parse a url, mostly based on dj-database-url
        :param var:
        :param default:
        :param engine:
        :param conn_max_age:
        :param ssl_require:
        :return:
        """
        url = self._check_var(var, default=default)
        # shortcut to avoid urlparse
        if url == 'sqlite://:memory':
            return {
                'ENGINE': DB_SCHEMES['sqlite'],
                'NAME': ':memory:'
            }

        # otherwise parse the url as normal
        config = {}
        url = urlparse(url)

        path = url.path[1:]
        path = unquote_plus(path.split('?', 2)[0])

        if url.scheme == 'sqlite' and path == '':
            path = ':memory:'
        elif url.scheme == 'ldap':
            path = f'{url.scheme}://{url.hostname}'
            if url.port:
                path += f':{url.port}'

        # Handle postgres percent-encoded paths.
        hostname = url.hostname or ''
        if '%2f' in hostname.lower():
            # Switch to url.netloc to avoid lower cased paths
            hostname = url.netloc
            if "@" in hostname:
                hostname = hostname.rsplit("@", 1)[1]
            if ":" in hostname:
                hostname = hostname.split(":", 1)[0]
            hostname = hostname.replace('%2f', '/').replace('%2F', '/')

        engine = DB_SCHEMES[url.scheme] if engine is None else engine
        port = (str(url.port) if url.port and engine == DB_SCHEMES['oracle'] else url.port)

        # Update with configuration.
        config.update({
            'NAME': path or '',
            'USER': url.username or '',
            'PASSWORD': url.password or '',
            'HOST': hostname,
            'PORT': port or ''
        })

        if url.scheme == 'postgres' and path.startswith('/'):
            config['HOST'], config['NAME'] = path.rsplit('/', 1)

        elif url.scheme == 'oracle':
            if path == '':
                config['NAME'], config['HOST'] = config['HOST'], ''
            if not config['PORT']:  # Django oracle/base.py strips port and fails on non-string value
                del(config['PORT'])
            else:
                config['PORT'] = str(config['PORT'])

        db_options = {}
        # Pass the query string into OPTIONS.
        if url.query:
            for key, values in parse_qs(url.query).items():
                if key.upper() in _DB_BASE_OPTIONS:
                    config.update({key.upper(): values[0]})
                else:
                    db_options.update({key: self._int(values[0])})

            # Support for Postgres Schema URLs
            if 'currentSchema' in db_options and engine in (
                'django.contrib.gis.db.backends.postgis',
                'django.db.backends.postgresql_psycopg2',
                'django_redshift_backend',
            ):
                db_options['options'] = '-c search_path={0}'.format(db_options.pop('currentSchema'))

        if options:
            db_options.update(options)
        if db_options:
            config['OPTIONS'] = db_options
        if engine:
            config['ENGINE'] = engine
        return config

    def cache_url(self, var=DEFAULT_CACHE_ENV, default=None, backend=None, options=None):
        """ based on dj-cache-url

        :param url:
        :param backend:
        :return:
        """
        url = urlparse(self._check_var(var, default=default))

        location = url.netloc.split(',')
        if len(location) == 1:
            location = location[0]

        config = {
            'BACKEND': backend if backend else CACHE_SCHEMES[url.scheme],
            'LOCATION': location,
        }

        # Add the drive to LOCATION
        if url.scheme == 'filecache':
            config.update({
                'LOCATION': url.netloc + url.path,
            })

        if url.path and url.scheme in ['memcache', 'pymemcache']:
            config.update({
                'LOCATION': 'unix:' + url.path,
            })
        elif url.scheme.startswith('redis'):
            scheme = url.scheme.replace('cache', '') if url.hostname else 'unix'
            locations = [scheme + '://' + loc + url.path for loc in url.netloc.split(',')]
            config['LOCATION'] = locations[0] if len(locations) == 1 else locations

        cache_options = {}
        if url.query:
            for key, values in parse_qs(url.query).items():
                opt = {key.upper(): values[0]}
                if key.upper() in _CACHE_BASE_OPTIONS:
                    config.update(opt)
                else:
                    cache_options.update(opt)

        if options:
            cache_options.update(options)
        config['OPTIONS'] = cache_options
        return config

    def email_url(self, var=DEFAULT_EMAIL_ENV, default=None, backend=None, options=None):
        """ parse an email URL, based on django-environ """
        url = urlparse(self._check_var(var, default=default))

        path = url.path[1:]
        path = unquote_plus(path.split('?', 2)[0])

        # Update with environment configuration
        config = {
            'EMAIL_FILE_PATH': path,
            'EMAIL_HOST_USER': url.username,
            'EMAIL_HOST_PASSWORD': url.password,
            'EMAIL_HOST': url.hostname,
            'EMAIL_PORT': self._int(url.port),
        }

        if backend:
            config['EMAIL_BACKEND'] = backend
        elif url.scheme in EMAIL_SCHEMES:
            config['EMAIL_BACKEND'] = EMAIL_SCHEMES[url.scheme]
        else:
            raise self.exception('Invalid email schema %s' % url.scheme)

        if url.scheme in ('smtps', 'smtp+tls'):
            config['EMAIL_USE_TLS'] = True
        elif url.scheme == 'smtp+ssl':
            config['EMAIL_USE_SSL'] = True

        email_options = {}
        if url.query:
            for key, values in parse_qs(url.query).items():
                opt = {key.upper(): self._int(values[0])}
                if key.upper() in _EMAIL_BASE_OPTIONS:
                    config.update(opt)
                else:
                    email_options.update(opt)

        if options:
            email_options.update(options)
        if email_options:
            config['OPTIONS'] = email_options

        return config

    def search_url(self, var=DEFAULT_SEARCH_ENV, default=None, engine=None):
        """ parse a search URL, based on django-environ """
        url = urlparse(self._check_var(var, default=default))

        path = url.path[1:]
        path = unquote_plus(path.split('?', 2)[0])

        if url.scheme not in SEARCH_SCHEMES:
            raise self.exception('Invalid search schema %s' % url.scheme)

        config = {
            "ENGINE": engine if engine else SEARCH_SCHEMES[url.scheme]
        }

        # check common params
        params = {}
        if url.query:
            params = parse_qs(url.query)
            if 'EXCLUDED_INDEXES' in params.keys():
                config['EXCLUDED_INDEXES'] = params['EXCLUDED_INDEXES'][0].split(',')
            if 'INCLUDE_SPELLING' in params.keys():
                config['INCLUDE_SPELLING'] = self._is_true(params['INCLUDE_SPELLING'][0])
            if 'BATCH_SIZE' in params.keys():
                config['BATCH_SIZE'] = self._int(params['BATCH_SIZE'][0])

        if url.scheme == 'simple':
            return config
        elif url.scheme in ['solr', 'elasticsearch', 'elasticsearch2']:
            if 'KWARGS' in params.keys():
                config['KWARGS'] = params['KWARGS'][0]

        # remove trailing slash
        if path.endswith("/"):
            path = path[:-1]

        if url.scheme == 'solr':
            config['URL'] = urlunparse(('http',) + url[1:2] + (path,) + ('', '', ''))
            if 'TIMEOUT' in params.keys():
                config['TIMEOUT'] = self._int(params['TIMEOUT'][0])
            return config

        if url.scheme.startswith('elasticsearch'):
            split = path.rsplit("/", 1)

            if len(split) > 1:
                path = "/".join(split[:-1])
                index = split[-1]
            else:
                path = ""
                index = split[0]

            config['URL'] = urlunparse(('http',) + url[1:2] + (path,) + ('', '', ''))
            if 'TIMEOUT' in params.keys():
                config['TIMEOUT'] = self._int(params['TIMEOUT'][0])
            config['INDEX_NAME'] = index
            return config

        config['PATH'] = '/' + path

        if url.scheme == 'whoosh':
            if 'STORAGE' in params.keys():
                config['STORAGE'] = params['STORAGE'][0]
            if 'POST_LIMIT' in params.keys():
                config['POST_LIMIT'] = self._int(params['POST_LIMIT'][0])
        elif url.scheme == 'xapian':
            if 'FLAGS' in params.keys():
                config['FLAGS'] = params['FLAGS'][0]
        return config
