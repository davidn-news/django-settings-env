import contextlib
import io
import django_env
import pytest


TEST_ENV = [
    '# This is an example .env file',
    'DATABASE_URL=postgresql://username:password@localhost/database_name',
    'CACHE_URL=memcache://localhost:11211',
    'REDIS_URL=redis://localhost:6379/5',
    'INTVALUE=225',
    'FLOATVALUE=54.92',
    'BOOLVALUETRUE=True',
    'BOOLVALUEFALSE=off',
]


@contextlib.contextmanager
def dotenv(ignored):
    _ = ignored
    yield io.StringIO("\n".join(TEST_ENV))


def test_env_wrapper():
    env = django_env.Env()
    assert 'HOME' in env
    assert 'USER' in env


def test_env_int(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env(readenv=True)
    assert env.int('INTVALUE', default=99) == 225
    assert env.int('DEFAULTINTVALUE', default=981) == 981


def test_env_float(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env(readenv=True)
    assert env.float('FLOATVALUE', default=99.9999) == 54.92
    assert env.float('DEFAULTFLOATVALUE', default=83.6) == 83.6


def test_env_bool(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env(readenv=True)
    assert env.bool('BOOLVALUETRUE', default=False)
    assert env.bool('DEFAULTBOOLVALUETRUE', default=True)
    assert not env.bool('BOOLVALUEFALSE', default=True)
    assert not env.bool('DEFAULTBOOLVALUEFALSE', default=False)


def test_env_inject(monkeypatch, capsys):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env()
    # must be explicitly read in
    env.read_env()
    assert 'DATABASE_URL' in env
    print(env['DATABASE_URL'])
    assert 'CACHE_URL' in env
    print(env['CACHE_URL'])
    assert 'REDIS_URL' in env
    print(env['REDIS_URL'])
    captured = capsys.readouterr()
    assert captured.out == "postgresql://username:password@localhost/database_name\n" \
                           "memcache://localhost:11211\n" \
                           "redis://localhost:6379/5\n"


def test_env_db(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env()
    env.read_env()
    database = env.database_url()
    assert database['NAME'] == 'database_name'
    assert database['USER'] == 'username'
    assert database['PASSWORD'] == 'password'
    assert database['HOST'] == 'localhost'
    assert database['ENGINE'] == 'django.db.backends.postgresql'


def test_env_memcached(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env()
    env.read_env()
    cache = env.cache_url()
    assert cache['LOCATION'] == 'localhost:11211'
    assert cache['BACKEND'] == 'django.core.cache.backends.memcached.MemcachedCache'


def test_env_redis(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.Env()
    env.read_env()
    cache = env.cache_url('REDIS_URL')
    assert cache['LOCATION'] == 'redis://localhost:6379/5'
    assert cache['BACKEND'] == 'django_redis.cache.RedisCache'


def test_env_email(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    with pytest.raises(KeyError):
        env = django_env.Env()
        env.read_env()
        env.email_url()
    env['EMAIL_URL'] = 'smtps://user@example.com:secret@smtp.example.com:587'
    email = env.email_url()
    assert email['EMAIL_HOST_USER'] == 'user@example.com'
    assert email['EMAIL_HOST_PASSWORD'] == 'secret'
    assert email['EMAIL_HOST'] == 'smtp.example.com'
    assert email['EMAIL_PORT'] == 587
    env['EMAIL_URL'] = 'smtps://user@example.com:secret@smtp.example.com:587'


def test_env_search(monkeypatch):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    with pytest.raises(KeyError):
        env = django_env.Env()
        env.read_env()
        env.search_url()
    env['SEARCH_URL'] = 'elasticsearch2://127.0.0.1:9200/index'
    search = env.search_url()

