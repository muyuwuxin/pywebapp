#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    # body = StringField('', validators=[DataRequired()])
    # 必须是TextAreaField这种才能使用富文本编辑器，这个问题找死我了
    body = TextAreaField(u'内容', validators=[DataRequired()])
    submit = SubmitField(u'提交评论')
