#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask import Blueprint


todo = Blueprint('todo', __name__)


from . import views, errors
