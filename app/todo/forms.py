#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo
from ..models import User


class TodoListForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired(), Length(1, 64)])
    status = RadioField(u'Finished or not', validators=[DataRequired()],  choices=[
                        ("1", u'Finished'), ("0", u'Unfinished')])
    submit = SubmitField(u'Submit')


# class LoginForm(FlaskForm):
#     username = StringField(u'Username', validators=[
#                            DataRequired(), Length(1, 24)])
#     password = PasswordField(
#         u'Password', validators=[DataRequired(), Length(1, 24)])
#     submit = SubmitField(u'Sign in')


# class RegisterForm(FlaskForm):
#     username = StringField(u'Username', validators=[
#                            DataRequired(), Length(1, 24)])
#     password = PasswordField(
#         u'Password', validators=[DataRequired(), EqualTo('password2', message=u'password wrong1')])
#     password2 = PasswordField(u'Repeat the password',
#                               validators=[DataRequired()])
#     submit = SubmitField(u'Sign up')
#
#     def validate_username(self, field):  # 解决重复的用户名而加上
#         if User.query.filter_by(username=field.data).first():
#             raise ValidationError(u'The username has existed!')
#         pass
