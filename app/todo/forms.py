#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField
from wtforms.validators import DataRequired, Length


class TodoListForm(FlaskForm):
    title = StringField(u'内容', validators=[DataRequired(), Length(1, 64)])
    status = RadioField(u'是否完成', validators=[DataRequired()],  choices=[
                        ("1", u'完成'), ("0", u'待办')])
    submit = SubmitField(u'提交')
