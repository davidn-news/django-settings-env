# django-env
## customise environment handler

This module provides a convenient interface for handling the environment,
and therefore application configuration using 12factor.net principals.

This module provides some features not supported by other dotenv handlers (python-dotenv,
django-environ etc.) including expansion of template variables which is very useful for DRY,
and in addition adds similar functionalty to that found in django-environ
dropping python2 support completely.


Some django specific factors included in this module are URL parsers for:

- DATABASE_URL
- CACHE_URL
- EMAIL_URL
- SEARCH_URL
- STORAGE_URL

each of which can be injected into django settings.

