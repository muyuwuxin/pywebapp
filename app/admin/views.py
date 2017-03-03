#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import admin
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
from forms import LoginForm, RegistrationForm, PostArticleForm, \
    PostCategoryForm, EditArticleForm
from ..models import User, Article, Category
from .. import db
from sqlalchemy.exc import IntegrityError


@admin.route('/')
def index():
    return render_template('admin/index.html')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('admin.index'))
        flash(u'用户密码不正确')
    return render_template('admin/login.html', form=form)


@admin.route('/register', methods=['GET', 'POST'])
def register():
    register_key = "zhucema"
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.registerkey.data != register_key:
            flash(u'注册码不符，请返回重试')
            return redirect(url_for('admin.register'))
        else:
            if form.password.data != form.password2.data:
                flash(u'两次输入密码不一')
                return redirect(url_for('admin.register'))
            else:
                user = User(username=form.username.data,
                            password=form.password.data)
                db.session.add(user)
                flash(u'您已经注册成功')
                return redirect(url_for('admin.login'))
    return render_template('admin/register.html', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经登出了系统')
    return redirect(url_for('admin.index'))


@admin.route('/article', methods=['GET', 'POST'])
@login_required
def article():
    form = PostArticleForm()
    alist = Article.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data,
                          category_id=str(form.category_id.data.id),
                          user_id=current_user.id)
        # try:
        #     db.session.add(acticle)
        #     flash(u'文章添加成功')
        #     redirect(url_for('admin.index'))
        # except IntegrityError as e:
        #     db.session.rollback()
        db.session.add(article)
        flash(u'文章添加成功')
        # db.session.commit()
        # db.session.rollback()
        return redirect(url_for('admin.article'))
    return render_template('admin/article.html', form=form, list=alist,
                           username=current_user.username)


@admin.route('/article/write', methods=['GET', 'POST'])
@login_required
def article_write():
    form = PostArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data,
                          category_id=str(form.category_id.data.id),
                          user_id=current_user.id)
        db.session.add(article)
        flash(u'文章添加成功')
        return redirect(url_for('admin.article'))
    return render_template('admin/writearticle.html', form=form)


@admin.route('/article/del', methods=['GET'])
@login_required
def article_del():
    if request.args.get('id') is not None and request.args.get('a') == 'del':
        x = Article.query.filter_by(id=request.args.get('id')).first()
        if x is not None:
            db.session.delete(x)
            db.session.commit()
            flash(u'已经删除' + x.title)
            return redirect(url_for('admin.article'))
        flash(u'请检查输入')
        return redirect(url_for('admin.article'))


@admin.route('/article/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def article_edit(id):
    article = Article.query.get_or_404(id)
    form = EditArticleForm()
    # if form.validate_on_submit():
    if request.method == 'POST':
        article.body = form.body.data
        db.session.add(article)
        flash(u'成功修改文章')
        return redirect(url_for('main.read', id=id))
    if request.method == 'GET':
        form.body.data = article.body
        return render_template('admin/editarticle.html', form=form)


@admin.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    clist = Category.query.all()
    form = PostCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        # try:
        #     db.session.add(category)
        #     flash(u'分类添加成功')
        #     return redirect(url_for('admin.category'))
        # except IntegrityError as e:
        #     db.session.rollback()
        # db.session.add(category)
        db.session.merge(category)
        flash(u'分类添加成功')
        # db.session.commit()
        # db.session.rollback()
        return redirect(url_for('admin.category'))
    return render_template('admin/category.html', form=form, list=clist)


@admin.route('/category/del', methods=['GET'])
@login_required
def category_del():
    if request.args.get('id') is not None and request.args.get('a') == 'del':
        x = Category.query.filter_by(id=request.args.get('id')).first()
        if x is not None:
            db.session.delete(x)
            db.session.commit()
            flash(u'已经删除' + x.name)
            return redirect(url_for('admin.category'))
        flash(u'请检查输入')
        return redirect(url_for('admin.category'))
