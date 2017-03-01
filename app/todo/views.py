#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import todo
from .. import db, login_manager
from ..models import TodoList, User
from flask_login import login_required, login_user, logout_user, current_user
# from .forms import TodoListForm, LoginForm, RegisterForm
from .forms import TodoListForm
from flask import render_template, redirect, request, url_for, flash


@todo.route('/', methods=['GET', 'POST'])
@login_required
def show_todo_list():
    form = TodoListForm()
    if request.method == 'GET':
        todolists = TodoList.query.filter_by(
            user_id=current_user.id).all()
        return render_template('todo/index.html', todolists=todolists, form=form, username=current_user.username)
    else:
        if form.validate_on_submit():
            todolist = TodoList(
                user_id=current_user.id, title=form.title.data, status=form.status.data)
            try:
                db.session.add(todolist)
                db.session.commit()
                flash(u'You have added a todo sucessfully')
            except:
                db.session.rollback()
                raise
        else:
            flash(u'Please log in first')
        return redirect(url_for('todo.show_todo_list'))


@todo.route('/delete/<int:id>')
@login_required
def delete_todo_list(id):
    todolist = TodoList.query.filter_by(id=id).first_or_404()
    try:
        db.session.delete(todolist)
        db.session.commit()
        flash(u'You delete a todo sucessfully')
        return redirect(url_for('todo.show_todo_list'))
    except:
        db.session.rollback()
        raise


@todo.route('/change/<int:id>', methods=['GET', 'POST'])
@login_required
def change_todo_list(id):
    if request.method == 'GET':
        todolist = TodoList.query.filter_by(id=id).first_or_404()
        form = TodoListForm()
        form.title.data = todolist.title
        form.status.data = str(todolist.status)
        return render_template('todo/modify.html', form=form)
    else:
        form = TodoListForm()
        if form.validate_on_submit():
            todolist = TodoList.query.filter_by(id=id).first_or_404()
            todolist.title = form.title.data
            todolist.status = form.status.data
            try:
                db.session.commit()
                flash(u'You modify a todo sucessfully')
            except:
                db.session.rollback()
        else:
            flash(form.errors)
        return redirect(url_for('todo.show_todo_list'))


# @todo.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if request.method == 'GET':
#         return render_template('register.html', form=form)
#     if form.validate_on_submit:
#         if User.query.filter_by(username=form.username.data).first():
#             flash("The username has existed")
#             return redirect(url_for('todo.register'))
#         else:
#             if form.password.data != form.password2.data:
#                 flash(u'The two password is different')
#                 return redirect(url_for('todo.register'))
#             else:
#                 user = User(username=form.username.data,
#                             password=form.password.data)
#                 try:
#                     db.session.add(user)
#                     flash(u'You have signed up a account sucessfully')
#                     return redirect(url_for('todo.login'))
#                 except:
#                     db.session.rollback()
#                     raise


# @todo.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         user = User.query.filter_by(
#             username=request.form['username'], password=request.form['password']).first()
#         if user:
#             login_user(user)
#             flash('You have logged in!')
#             return redirect(url_for('todo.show_todo_list'))
#         else:
#             flash(u'Invalid name or password')
#     form = LoginForm()
#     return render_template('login.html', form=form)


# @todo.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash(u'You have signed out sucessfully')
#     return redirect(url_for('todo.login'))


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.filter_by(id=int(user_id)).first()
