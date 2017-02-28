#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import main
from flask import render_template, request, redirect, flash, url_for
from ..models import Article


@main.route('/')
def index():
    articlelist = Article.query.all()
    return render_template('main/index.html', list=articlelist)


@main.route('/read', methods=['POST', 'GET'])
def read():
    the_article = Article.query.filter_by(id=request.args.get('id')).first()
    if the_article is not None:
        return render_template('main/read.html', list=the_article)
    flash(u'未找到相关文章')
    return redirect(url_for('main.index'))
