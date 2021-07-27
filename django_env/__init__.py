# -*- coding: utf-8 -*-
from smart_env import dot_env
from smart_env.dot_env import load_env, load_dotenv
from .env_django import DjangoEnv as Env


__all__ = (
    'dot_env',
    'load_env',
    'load_dotenv',
    'Env',
)
