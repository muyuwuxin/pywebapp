#! /usr/bin/env python2
# -*-coding:utf-8-*-


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  TextAreaField,\
    SelectField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from .. import photos


class CommentForm(FlaskForm):
    # body = StringField('', validators=[DataRequired()])
    # 必须是TextAreaField这种才能使用富文本编辑器，这个问题找死我了
    body = TextAreaField(u'内容', validators=[DataRequired()])
    submit = SubmitField(u'提交评论')


class NewAlbumForm(FlaskForm):
    title = StringField(u'标题')
    about = TextAreaField(u'介绍', render_kw={'rows': 8})
    photo = FileField(u'图片(请勿上传全中文名的图片)', validators=[
        FileRequired(u'你还没有选择图片！'),
        FileAllowed(photos, u'只能上传图片！')
    ])
    asc_order = SelectField(u'显示顺序',
                            choices=[('True', u'按上传时间倒序排列'), ('False', u'按上传时间倒序排列')])
    no_public = BooleanField(u'私密相册（勾选后相册仅自己可见）')
    no_comment = BooleanField(u'禁止评论')
    submit = SubmitField(u'提交')


class AddPhotoForm(FlaskForm):
    photo = FileField(u'图片', validators=[
        FileRequired(),
        FileAllowed(photos, u'只能上传图片！')
    ])
    submit = SubmitField(u'提交')


class EditAlbumForm(FlaskForm):
    title = StringField(u'标题')
    about = TextAreaField(u'介绍', render_kw={'rows': 8})
    asc_order = SelectField(u'显示顺序',
                            choices=[("1", u'按上传时间倒序排列'), ("0", u'按上传时间倒序排列')])
    no_public = BooleanField(u'私密相册（右侧滑出信息提示：勾选后相册仅自己可见）')
    no_comment = BooleanField(u'允许评论')
    submit = SubmitField(u'提交')
