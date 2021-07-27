try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='django-env',
    version=open('version').read().strip(),
    description='12factor.net/smart-env support for Django',
    author='David Nugent',
    author_email='david.nugent@news.com.au',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'django_env',
    ],
)
