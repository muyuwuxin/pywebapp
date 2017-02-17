#! /usr/bin/env python2
# -*-coding:utf-8-*-


from logging.handlers import RotatingFileHandler
from flask import logging


class Config:
    SECRET_KEY = 'A KEY HHH'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        _handler = RotatingFileHandler(
            'app.log', maxBytes=10000, backupCount=1)
        _handler.setLevel(level=30)  # 奇怪的地方，按照原文章不能运行，去看ＡＰＩ改成了这个样子
        app.logger.addHandler(_handler)
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask_dev'


config = {
    'default': DevelopmentConfig
}
