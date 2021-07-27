----------
django-env
----------
Customised environment handler for Django

smart-env
---------

The functionality outlined in this section is derived from the dependent package
`smart-env`, the docs for which are repeated below.
Skip to the Django Support section for functionality added by this extension.

This module provides a convenient interface for handling the environment,
and therefore application configuration using 12factor.net principals.

This module provides some features not supported by other dotenv handlers
(python-dotenv, django-environ etc.) including expansion of template variables 
which is very useful for DRY, and in addition adds similar functionalty to 
that found in django-environ and dropping the now defunct python2 support 
completely.

An `Env` instance delivers a lot of functionality by providing a type-smart
front-end to `os.environ`, with support for most - if not all - `os.environ`
functionality.
::
    from django_env import Env

    env = Env()         # by default, sources (and updates) os.environ
    assert env['HOME'] ==  '/Users/davidn'
    env['TESTING'] = 'This is a test'
    assert env['TESTING'] == 'This is a test'

    import os
    assert os.environ['TESTING'] == 'This is a test'

    assert env.get('UNSET_VAR') is None
    env.set('UNSET_VAR', 'this is now set')
    assert env.get('UNSET_VAR') is not None
    env.setdefault('UNSET_VAR', 'and this is a default value but only if not set')
    assert env.get('UNSET_VAR') == 'this is now set'
    del env['UNSET_VAR']
    assert env.get('UNSET_VAR') is None

An Env instance can also read a `.env` (default name) file and update the
environment accordingly.
It can read this either from the constructor or via the method `read_env()`.

Some type-smart functions act as an alternative to `Env.get` and having to
parse the result::
    from django_env import Env

    env = Env()         # by default, sources (and updates) os.environ

    env['AN_INTEGER_VALUE'] = 2875083
    assert env.get('AN_INTEGER_VALUE') == '2875083'
    assert env.int('AN_INTEGER_VALUE') == 2875083

    env['A_TRUE_VALUE'] = True
    assert env.get('A_TRUE_VALUE') == 'True'
    assert env.bool('A_TRUE_VALUE') is True

    env['A_FALSE_VALUE'] = 0
    assert env.get('A_FALSE_VALUE') == '0'
    assert env.int('A_FALSE_VALUE') == 0
    assert env.bool('A_FALSE_VALUE') is False

    env['A_FLOAT_VALUE'] = 287.5083
    assert env.get('A_FLOAT_VALUE') == '287.5083'
    assert env.float('A_FLOAT_VALUE') == 287.5083

    env['A_LIST_VALUE'] = '1,"two",3,"four"'
    assert env.get('A_LIST_VALUE') == '1,"two",3,"four"'
    assert env.list('A_LIST_VALUE') == ['1', 'two', '3', 'four']

Note that environment variables are always stored as strings. This is
enforced by the underlying os.environ, but also also true of any provided
environment, using the `MutableMapping[str, str]` contract.

Django Support
--------------

Some django specific methods included in this module are URL parsers for:

| Default Var    | Parser
|----------------|----------------------- 
| DATABASE_URL   | `env.database_url()`
| CACHE_URL      | `env.cache_url()`
| EMAIL_URL      | `env.email_url()`
| SEARCH_URL     | `env.search_url()`
| QUEUE_URL      | `env.queue_url()`

each of which can be injected into django settings via the environment, typically
from a .env file. The name of the file and paths search is fully customisable.

The url specified includes a schema that determines the "backend" class or module
that handles the corresponding functionality as documented below.

## `database_url`
Evaluates a URL in the form 
```
schema://[username:[password]@]host_or_path[:port]/name
```
Schemas:

| Scheme          | Database
|-----------------|----------------------
| postgres        | Postgres (psycopg2)
| postgresql      | Postgres (psycopg2)
| psql            | Postgres (psycopg2)
| pgsql           | Postgres (psycopg2)
| postgis         | Postgres (psycopg2) using PostGIS extensions
| mysql           | MySql (mysqlclient) 
| mysql2          | MySql (mysqlclient)
| mysql-connector | MySql (mysql-connector)
| mysqlgis        | MySql (mysqlclient) using GIS extensions
| mssql           | SqlServer (sql_server.pyodbc)
| oracle          | Oracle (cx_Oracle)
| pyodbc          | ODBC (pyodbc)
| redshift        | Amazon Redshift
| spatialite      | Sqlite with spatial extensions (spatialite)
| sqlite          | Sqlite
| ldap            | django-ldap

## `cache_url`
Evaluates a URL in the form
```
schema://[username:[password]@]host_or_path[:port]/[name]
```
Schemas:

| Scheme          | Cache
|-----------------|----------------------
| dbcache         | cache in database
| dummycache      | dummy cache - "no cache" 
| filecache       | cache data in files
| locmemcache     | cache in memory
| memcache        | memcached (python-memcached)
| pymemcache      | memcached (pymemcache)
| rediscache      | redis (django-redis)
| redis           | redis (django-redis)

## `email_url`
Evaluates a URL in the form
```
schema://[username[@domain]:[password]@]host_or_path[:port]/
```
Schemas:

| Scheme          | Service
|-----------------|----------------------
| smtp            | smtp, no SSL
| smtps           | smtp over SSL
| smtp+tls        | smtp over SSL
| smtp+ssl        | smtp over SSL
| consolemail     | publish mail to console (dev)
| filemail        | append email to file (dev)
| memorymail      | store emails in memory
| dummymail       | do-nothing email backend
| amazonses       | Amazon Wimple Email Service
| amazon-ses      | Amazon Wimple Email Service

## `search_url`
Evaluates a URL in the form
```
schema://[username:[password]@]host_or_path[:port]/[index]
```
Schemas:

| Scheme          | Engine
|-----------------|----------------------
| elasticsearch   | elasticsearch (django-haystack)
| elasticsearch2  | elasticsearch2 (django-haystack)
| solr            | Apache solr (django-haystack)
| whoosh          | Whoosh search engine (pure python, haystack)
| xapian          | Xapian search engine (haystack)
| simple          | Simple search engine (haystack)

## `queue_url`
Evaluates a URL in the form
```
schema://[username:[password]@]host_or_path[:port]/[queue]
```
Schemas:

| Scheme          | Engine
|-----------------|----------------------
| rabbitmq        | RabbitMQ
| redis           | Redis
| amazonsqs       | Amazon SQS
| amazon-sqs      | alias for Amazon SQS
