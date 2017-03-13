#! /usr/bin/env python2
# -*-coding:utf-8-*-


from . import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash \
    # 引入密码加密 验证方法
from flask_login import UserMixin, AnonymousUserMixin  # 引入flask-login用户模型继承类方法
import time


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    # title = db.Column(db.String(64))
    body = db.Column(db.Text)
    create_time = db.Column(db.String(50), default=time.strftime(
        "%Y-%m-%d %A %X %Z", time.localtime()))
    # create_time = db.Column(db.DATETIME, default=datetime.utcnow())
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='article', lazy='dynamic')


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    # id = db.Column(db.Integer)
    # name = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    articles = db.relationship('Article', backref='category', lazy='dynamic')


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    # 在使用Flask-Login作为登入功能时,在user模型要继承UserMimix类.
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    articles = db.relationship('Article', backref='user', lazy='dynamic')
    todolists = db.relationship('TodoList', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    albums = db.relationship('Album', backref='author', lazy='dynamic')
    photos = db.relationship('Photo', backref='author', lazy='dynamic')

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username == "testuser1":
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.followed.append(Follow(followed=self))

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.String(50), default=time.strftime(
        "%Y-%m-%d %A %X %Z", time.localtime()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.String(50), default=time.strftime(
        "%Y-%m-%d %A %X %Z", time.localtime()))
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64))
    url_s = db.Column(db.String(64))
    url_t = db.Column(db.String(64))
    about = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    order = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'))
    comments = db.relationship('Comment', backref='photo', lazy='dynamic')


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    about = db.Column(db.Text)
    cover = db.Column(db.String(64))
    type = db.Column(db.Integer, default=0)
    tag = db.Column(db.String(64))
    no_public = db.Column(db.Boolean, default=True)
    no_comment = db.Column(db.Boolean, default=True)
    asc_order = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photos = db.relationship('Photo', backref='album', lazy='dynamic')
