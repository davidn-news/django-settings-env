# -*- coding: utf-8 -*-
import contextlib

import django_env
import io
import pytest


@pytest.fixture
def envmap():
    return {
        'FIRST': 'first-value',
        'SECOND': 'second-value',
        'THIRD': 'third-value',
        'FORTH': 'forth-value',
    }


@contextlib.contextmanager
def dotenv(ignored):
    _ = ignored
    yield io.StringIO("""
# This is an example .env file
SECOND=a-second-value
THIRD=altnernative-third
FIFTH=fifth-value
COMBINED=${FIRST}:${THIRD}:${FIFTH}
""")


def test_load_env(monkeypatch, envmap):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.load_env(search_path=__file__, environ=envmap)
    for var in envmap.keys():
        assert var in env
    assert 'FIFTH' in env
    assert env['COMBINED'] == 'first-value:third-value:fifth-value'


def test_load_env_overwrite(monkeypatch, envmap):
    monkeypatch.setattr(django_env.dot_env, 'open_env', dotenv)
    env = django_env.load_env(search_path=__file__, environ=envmap, overwrite=True)
    for var in envmap.keys():
        assert var in env
    assert 'FIFTH' in env
    assert env['COMBINED'] == 'first-value:altnernative-third:fifth-value'
