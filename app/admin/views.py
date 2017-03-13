#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import admin
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
from forms import LoginForm, RegistrationForm, PostArticleForm, \
    PostCategoryForm, EditProfileForm, EditProfileAdminForm
from ..models import User, Article, Category, Role
from .. import db


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
        article = Article(title=form.title.data,
                          body=form.body.data,
                          category_id=str(form.category_id.data.id),
                          user_id=current_user.id)

        db.session.add(article)
        flash(u'文章添加成功')

        return redirect(url_for('admin.article'))
    return render_template('admin/article.html', form=form, list=alist,
                           username=current_user.username)


@admin.route('/article/write', methods=['GET', 'POST'])
@login_required
def article_write():
    form = PostArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data,
                          body=form.body.data,
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
    form = PostArticleForm()
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
        db.session.merge(category)
        flash(u'分类添加成功')
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


@admin.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST':
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'资料已更新.')
        return redirect(url_for('main.user', username=current_user.username))
    if request.method == 'GET':
        form.location.data = current_user.location
        form.about_me.data = current_user.about_me
        return render_template('admin/edit_profile.html', form=form)


@admin.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    # if form.validate_on_submit():
    #     # user.email = form.email.data
    #     user.username = form.username.data
    #     # user.confirmed = form.confirmed.data
    #     user.role = Role.query.get(form.role.data)
    #     # user.name = form.name.data
    #     user.location = form.location.data
    #     user.about_me = form.about_me.data
    #     db.session.add(user)
    #     flash('The profile has been updated.')
    #     return redirect(url_for('admin.user', username=user.username))
    # # form.email.data = user.email
    # form.username.data = user.username
    # # form.confirmed.data = user.confirmed
    # form.role.data = user.role_id
    # # form.name.data = user.name
    # form.location.data = user.location
    # form.about_me.data = user.about_me
    # return render_template('admin/edit_profile.html', form=form, user=user)
    if request.method == 'POST':
        # user.email = form.email.data
        # user.username = form.username.data
        # user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        # user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'资料已被管理员修改')
        return redirect(url_for('main.user', username=user.username))
    if request.method == 'GET':
        # form.username.data = user.username
        # form.confirmed.data = user.confirmed
        form.role.data = user.role_id
        # form.name.data = user.name
        form.location.data = user.location
        form.about_me.data = user.about_me
        return render_template('admin/edit_profile_admin.html', form=form,
                               user=user)
