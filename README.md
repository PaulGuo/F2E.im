## ABOUT F2E.im

F2E is a community for front-end-developer.

## How to contribute

Fork and send pull request.

## Danger

* now every logined user can upload pictures as many as they want, without any limit
* many SQL-injection danger

## How to run f2e.im on your own machine

1. install all required modules:

    ```
    shell> pip install -r requirements.txt
    ```

2. create database and then execute sql file in dbstructure/

    ```
    shell> mysql -u YOURUSERNAME -p

    mysql> create database f2e;
    mysql> exit

    shell> mysql -u YOURUSERNAME -p --database=f2e < dbstructure/f2e.sql
    ```

3. set your mysql user/password and smtp server config in `application.py` and `lib/sendmail.py`.

4. cp settings.py.bak settings.py and modify settings.py as you like

5. install rabbitmq-server and run it

6. run ```celery -A tasks worker --loglevel=info```

7. check above, using ``python application.py`` to start server.

    ```
    shell> python application.py
    ```

## How to set up a production enironment

You need to know a little of supervisor and nginx, all config files are available in conf/
