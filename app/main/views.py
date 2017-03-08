#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_login import login_required, current_user
from flask import render_template, request, redirect, flash, url_for,\
    current_app
from ..decorators import admin_required, permission_required
from ..models import Article, Comment, User, Permission
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
    #     return render_template('main/article.html', username=user.username, list=the_article)
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
    return render_template('main/article.html', list=articles, id=id,
                           pagination=pagination) \
        # 此处耗费了我好多好多脑细胞，要把id传进去，不然每次的翻页请求id不能正常传进去
    # 而且分页模板那个地方，也要传进去id（因为改变成了路由带有参数）


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.articles.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('admin/user.html', user=user, list=articles,
                           pagination=pagination)


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


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('admin.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)
