#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import todo
from .. import db
from ..models import TodoList
from flask_login import login_required, current_user
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
        return render_template('todo/index.html', todolists=todolists,
                               form=form, username=current_user.username)
    else:
        if form.validate_on_submit():
            todolist = TodoList(
                user_id=current_user.id, title=form.title.data,
                status=form.status.data)
            try:
                db.session.add(todolist)
                db.session.commit()
                flash(u'你成功增加了待办事项')
            except:
                db.session.rollback()
                raise
        else:
            flash(u'请先登录')
        return redirect(url_for('todo.show_todo_list'))


@todo.route('/delete/<int:id>')
@login_required
def delete_todo_list(id):
    todolist = TodoList.query.filter_by(id=id).first_or_404()
    try:
        db.session.delete(todolist)
        db.session.commit()
        flash(u'你成功的删除了待办事项')
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
                flash(u'你成功修改了待办事项')
            except:
                db.session.rollback()
        else:
            flash(form.errors)
        return redirect(url_for('todo.show_todo_list'))
