#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_wtf import FlaskForm
from ..models import Category, User, Article  # 解决重复的用户名,分类名和标题名而加上
# 解决重复注册用户名加上的错误类型
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, length, Regexp, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class LoginForm(FlaskForm):
    username = StringField(u'账号', validators=[DataRequired(), length(4, 64)])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submmit = SubmitField(u'登入')


class RegistrationForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(), length(
        6, 18), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只允许字母数字以及下划线,用户名不允许特殊符号')])  # 这里本来有问题，说是多了参数,我把最后两个合在了一起
    password = PasswordField(
        u'密码', validators=[DataRequired(), EqualTo('password2', message=u'密码错误提示1')])
    password2 = PasswordField(u'重复密码', validators=[DataRequired()])
    registerkey = StringField(u'注册码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_username(self, field):  # 解决重复的用户名而加上
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')
        pass


class PostArticleForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(), length(6, 64)])
    body = TextAreaField(u'内容')
    category_id = QuerySelectField(u'分类', query_factory=lambda: Category.query.all(
    ), get_pk=lambda a: str(a.id), get_label=lambda a: a.name)
    submit = SubmitField(u'发布')

    def validate_title(self, field):  # 解决重复的文章标题名而加上
        if Article.query.filter_by(title=field.data).first():
            raise ValidationError(u'该标题已使用')
        pass


class PostCategoryForm(FlaskForm):
    name = StringField(u'分类名', validators=[DataRequired(), length(6, 64)])
    submit = SubmitField(u'发布')

    def validate_name(self, field):  # 解决重复的分类名而加上,必须为对应的字段名字
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError(u'该分类已使用')
        pass
