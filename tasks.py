# coding: utf8
from __future__ import print_function
import logging

from celery import Celery

from lib import qiniu_util, utils


celery = Celery("tasks", broker="amqp://guest:guest@localhost:5672")
celery.conf.CELERY_RESULT_BACKEND = "amqp"


@celery.task
def upload_pictures(files, user):
    """task of uploading pictures to qiniu"""
    pics = []
    for file in files:
        content_type = file.get('content_type')
        filename = file.get('filename')
        body = file.get('body')
        key = utils.random_str(30)
        ret, err = qiniu_util.upload_binary_stream(key, body, content_type)
        if err:
            logging.log(logging.ERROR, err)
            print(err)
            continue
        pic = {
            'creator_id': int(user['uid']) if user else None,
            'service': 'qiniu',
            'store_key': key,
            'size': len(body),
        }
        pics.append(pic)
    return pics