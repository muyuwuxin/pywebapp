#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_login import login_required, current_user
from flask import render_template, request, redirect, flash, url_for,\
    current_app
from ..models import Article, Comment, User
from .forms import CommentForm
from . import main
from .. import db


@main.route('/')
def index():
    # articlelist = Article.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('main/index.html',  list=articles,
                           pagination=pagination)

    # return render_template('main/indextest.html', list=articles)


@main.route('/read/<int:id>', methods=['POST', 'GET'])
def read(id):
    # the_article = Article.query.filter_by(id=request.args.get('id')).first()
    the_article = Article.query.get_or_404(id)
    if the_article is not None:
        return render_template('main/read.html', list=the_article)
    flash(u'未找到相关文章')
    return redirect(url_for('main.index'))


@main.route('/listarticle/<int:id>')
def listarticle(id):
    # the_article = Article.query.filter_by(user_id=request.args.get('id')).all()
    # user = User.query.get(request.args.get('id'))
    # if the_article is not None:
    #     # return render_template('main/article.html', list=the_article)
    #     return render_template('main/articletest.html', username=user.username, list=the_article)
    # flash(u'未找到该作者相关文章')
    # return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter_by(user_id=id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    # pagination = Article.query.filter_by(user_id=request.args.get('id')).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    articles = pagination.items
    return render_template('main/articletest.html', list=articles, id=id,
                           pagination=pagination) \
        # 此处耗费了我好多好多脑细胞，要把id传进去，不然每次的翻页请求id不能正常传进去
    # 而且分页模板那个地方，也要传进去id（因为改变成了路由带有参数）


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
