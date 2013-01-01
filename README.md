## ABOUT F2E.im

F2E is a community for front-end-developer.

## How to contribute

Fork and send pull request.

## How to run f2e.im on your own machine

1. install all required modules:

    * tornado
    * jinja2
    * markdown
    * pygments
    * python-memcached
    * PIL(need libjpeg-devel)

2. create database and then execute sql file in dbstructure/
3. set your mysql user/password and smtp server config in `application.py` and `lib/sendmail.py`.
3. check above, using ``python application.py`` to start server.

## How to set up a production enironment

You need to know a little of supervisor and nginx, all config files are available in conf/
