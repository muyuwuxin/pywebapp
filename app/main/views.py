#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_login import login_required, current_user
from flask import render_template, request, redirect, flash, url_for
from ..models import Article, Comment
from .forms import CommentForm
from . import main
from .. import db


@main.route('/')
def index():
    articlelist = Article.query.all()
    return render_template('main/indextest.html', list=articlelist)


@main.route('/read/<int:id>', methods=['POST', 'GET'])
def read(id):
    # the_article = Article.query.filter_by(id=request.args.get('id')).first()
    the_article = Article.query.get_or_404(id)
    if the_article is not None:
        return render_template('main/read.html', list=the_article)
    flash(u'未找到相关文章')
    return redirect(url_for('main.index'))


@main.route('/listarticle')
def listarticle():
    the_article = Article.query.filter_by(user_id=request.args.get('id')).all()
    if the_article is not None:
        return render_template('main/article.html', list=the_article)
    flash(u'未找到该作者相关文章')
    return redirect(url_for('main.index'))


@main.route('/comment/<int:id>', methods=['POST', 'GET'])
@login_required
def comment(id):
    the_article = Article.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          article=the_article,
                          user=current_user._get_current_object()
                          )
        # comment = Comment(body=form.body.data)
        db.session.add(comment)
        db.session.commit()
        flash(u'你已成功添加评论')
        return redirect(url_for('main.read', id=id))
    return render_template('main/comment.html', form=form)
