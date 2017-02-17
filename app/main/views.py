#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import main


@main.route('/')
def index():
    return 'hello world!!!!'
