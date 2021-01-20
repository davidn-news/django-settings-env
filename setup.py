try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='django-env',
    version='0.3.0',
    description='12factor.net support for django',
    author='David Nugent',
    author_email='david.nugent@news.com.au',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'django_env',
    ],
)
