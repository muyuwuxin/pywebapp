#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # 引入密码加密 验证方法
from flask_login import UserMixin  # 引入flask-login用户模型继承类方法


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(64), unique=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    create_time = db.Column(db.DATETIME, default=datetime.utcnow())
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='category')


class User(UserMixin, db.Model):
    # 在使用Flask-Login作为登入功能时,在user模型要继承UserMimix类.
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    real_name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='user')

    @property
    def password(self):
        raise AttributeError(u'密码属性不正确')
        pass

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        # 增加password会通过generate_password_hash方法来加密储存
        pass

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        pass


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))
