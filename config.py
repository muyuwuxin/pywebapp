#! /usr/bin/env python2
# -*-coding:utf-8-*-

import os
# import psycopg2
from logging.handlers import RotatingFileHandler
from flask import logging


class Config:
    SECRET_KEY = 'A KEY HHH'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_POSTS_PER_PAGE = 5
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FANXIANGCE_ALBUMS_PER_PAGE = 12
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/app/static/img/'
    FANXIANGCE_PHOTOS_PER_PAGE = 20
    FANXIANGCE_ALBUM_LIKES_PER_PAGE = 12
    FANXIANGCE_PHOTO_LIKES_PER_PAGE = 20
    FANXIANGCE_FOLLOWERS_PER_PAGE = 10
    BOOTSTRAP_SERVE_LOCAL = True
    FANXIANGCE_COMMENTS_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        _handler = RotatingFileHandler(
            'app.log', maxBytes=10000, backupCount=1)
        _handler.setLevel(level=30)  # 奇怪的地方，按照原文章不能运行，去看ＡＰＩ改成了这个样子
        app.logger.addHandler(_handler)
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask_dev'
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


config = {
    'default': DevelopmentConfig
}
