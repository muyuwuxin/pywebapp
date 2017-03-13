#! /usr/bin/env python2
# -*-coding:utf-8-*-


import os
import time
import PIL
import hashlib
from PIL import Image
from flask_login import login_required, current_user
from flask import render_template, request, redirect, flash, url_for,\
    current_app, send_from_directory, abort
from ..decorators import admin_required, permission_required
from ..models import Article, Comment, User, Permission, Album, Photo, Category
from .forms import CommentForm, NewAlbumForm, EditAlbumForm, AddPhotoForm
from . import main
from .. import db, photos


@main.route('/')
def index():
    categorys = Category.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('main/index.html',
                           list=articles,
                           categorys=categorys,
                           pagination=pagination)


@main.route('/read/<int:id>', methods=['POST', 'GET'])
def read(id):
    # the_article = Article.query.filter_by(id=request.args.get('id')).first()
    the_article = Article.query.get_or_404(id)
    if the_article is not None:
        return render_template('main/read.html', list=the_article)
    flash(u'未找到相关文章')
    return redirect(url_for('main.index'))


@main.route('/listarticle/<int:id>')
def listarticle(id):
    # the_article = Article.query.filter_by(user_id=request.args.get('id')).all()
    # user = User.query.get(request.args.get('id'))
    # if the_article is not None:
    #     # return render_template('main/article.html', list=the_article)
    #     return render_template('main/article.html', username=user.username, list=the_article)
    # flash(u'未找到该作者相关文章')
    # return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter_by(user_id=id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    # pagination = Article.query.filter_by(user_id=request.args.get('id')).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    articles = pagination.items
    return render_template('main/article.html', list=articles, id=id,
                           pagination=pagination) \
        # 此处耗费了我好多好多脑细胞，要把id传进去，不然每次的翻页请求id不能正常传进去
    # 而且分页模板那个地方，也要传进去id（因为改变成了路由带有参数）


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.articles.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('admin/user.html', user=user, list=articles,
                           pagination=pagination)


@main.route('/comment/<int:id>', methods=['POST', 'GET'])
@login_required
def comment(id):
    the_article = Article.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          article=the_article,
                          user=current_user._get_current_object()
                          )
        # comment = Comment(body=form.body.data)
        db.session.add(comment)
        db.session.commit()
        flash(u'你已成功添加评论')
        return redirect(url_for('main.read', id=id))
    return render_template('main/comment.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash(u'你已经关注此用户')
        return redirect(url_for('admin.user', username=username))
    current_user.follow(user)
    flash(u'你正在关注 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash(u'你没有关注此用户')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash(u'你没有关注 %s anymore.' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


def save_image(files):
    photo_amount = len(files)
    if photo_amount > 50:
        flash(u'抱歉每次上传不超过50张！', 'warning')
        return redirect(url_for('main.new_album'))
    images = []
    for img in files:
        filename = hashlib.md5(current_user.username +
                               str(time.time())).hexdigest()[:10]
        image = photos.save(img, name=filename + '.')
        file_url = photos.url(image)
        url_s = image_resize(image, 800)
        url_t = image_resize(image, 300)
        images.append((file_url, url_s, url_t))
    return images


img_suffix = {
    300: '_t',  # thumbnail
    800: '_s'  # show
}


def image_resize(image, base_width):
    #: create thumbnail
    filename, ext = os.path.splitext(image)
    img = Image.open(photos.path(image))
    if img.size[0] <= base_width:
        return photos.url(image)
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(current_app.config[
             'UPLOADED_PHOTOS_DEST'], filename + img_suffix[base_width] + ext))
    return url_for('.uploaded_file', filename=filename + img_suffix[base_width] + ext)


@main.route('/<username>', methods=['GET', 'POST'])
@login_required
def albums(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    page = request.args.get('page', 1, type=int)
    pagination = user.albums.order_by(Album.timestamp.desc()).paginate(
        page, per_page=current_app.config['FANXIANGCE_ALBUMS_PER_PAGE'], error_out=False)
    albums = pagination.items

    photo_count = sum([len(album.photos.all()) for album in albums])
    album_count = len(albums)

    # allowed_tags = ['br']
    # if user.about_me:
    #     about_me = bleach.linkify(bleach.clean(
    #         user.about_me.replace('\r', '<br>'), tags=allowed_tags, strip=True))
    # else:
    #     about_me = None
    # form = CommentForm()
    # if form.validate_on_submit() and current_user.is_authenticated:
    #     comment = Message(body=form.body.data,
    #                       user=user,
    #                       author=current_user._get_current_object())
    #     db.session.add(comment)
    #     flash(u'你的评论已经发表。', 'success')
    #     return redirect(url_for('.albums', username=username))

    # comments = user.messages.order_by(Message.timestamp.asc()).all()
    return render_template('main/albums.html',
                           user=user, albums=albums, album_count=album_count,
                           photo_count=photo_count, pagination=pagination)


@main.route('/new-album', methods=['GET', 'POST'])
@login_required
def new_album():
    form = NewAlbumForm()
    if form.validate_on_submit():  # current_user.can(Permission.CREATE_ALBUMS)
        if request.method == 'POST' and 'photo' in request.files:
            images = save_image(request.files.getlist('photo'))

        title = form.title.data
        about = form.about.data
        author = current_user._get_current_object()
        no_public = form.no_public.data
        no_comment = form.no_comment.data
        album = Album(title=title, about=about,
                      cover=images[0][2], author=author,
                      no_public=no_public, no_comment=no_comment)
        db.session.add(album)

        for url in images:
            photo = Photo(url=url[0], url_s=url[1], url_t=url[2],
                          album=album, author=current_user._get_current_object())
            db.session.add(photo)
        db.session.commit()
        flash(u'相册创建成功！', 'success')
        return redirect(url_for('.edit_photo', id=album.id))
    return render_template('main/new_album.html', form=form)


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'],
                               filename)


@main.route('/edit-photo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_photo(id):
    album = Album.query.get_or_404(id)
    photos = album.photos.order_by(Photo.order.asc())
    if request.method == 'POST':
        for photo in photos:
            photo.about = request.form[str(photo.id)]
            photo.order = request.form["order-" + str(photo.id)]
            db.session.add(photo)
        album.cover = request.form['cover']
        db.session.add(album)
        db.session.commit()
        flash(u'更改已保存。', 'success')
        return redirect(url_for('.album', id=id))
    enu_photos = []
    for index, photo in enumerate(photos):
        enu_photos.append((index, photo))

    return render_template('main/edit_photo.html', album=album, photos=photos, enu_photos=enu_photos)


@main.route('/album/<int:id>')
def album(id):
    album = Album.query.get_or_404(id)
    # display default cover when an album is empty
    placeholder = 'http://p1.bpimg.com/567591/15110c0119201359.png'
    photo_amount = len(list(album.photos))
    if photo_amount == 0:
        album.cover = placeholder
    elif photo_amount != 0 and album.cover == placeholder:
        album.cover = album.photos[0].path

    if current_user != album.author and album.no_public == True:
        abort(404)
    page = request.args.get('page', 1, type=int)
    if album.asc_order:
        pagination = album.photos.order_by(Photo.order.asc()).paginate(
            page, per_page=current_app.config['FANXIANGCE_PHOTOS_PER_PAGE'],
            error_out=False)
    else:
        pagination = album.photos.order_by(Photo.order.asc()).paginate(
            page, per_page=current_app.config['FANXIANGCE_PHOTOS_PER_PAGE'],
            error_out=False)
    photos = pagination.items
    if len(photos) == 0:
        no_pic = True
    else:
        no_pic = False

    return render_template('main/album.html', album=album, photos=photos, pagination=pagination,
                           no_pic=no_pic)


@main.route('/photo/<int:id>', methods=['GET', 'POST'])
def photo(id):
    photo = Photo.query.get_or_404(id)
    album = photo.album
    if current_user != album.author and album.no_public == True:
        abort(404)

    photo_sum = len(list(album.photos))
    form = CommentForm()
    photo_index = [p.id for p in album.photos.order_by(
        Photo.order.asc())].index(photo.id) + 1

    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(body=form.body.data,
                              photo=photo,
                              author=current_user._get_current_object())
            db.session.add(comment)
            flash(u'你的评论已经发表。', 'success')
            return redirect(url_for('.photo', id=photo.id))
        else:
            flash(u'请先登录。', 'info')
    page = request.args.get('page', 1, type=int)
    pagination = photo.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FANXIANGCE_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    amount = len(comments)
    return render_template('main/photo.html', form=form, album=album, amount=amount,
                           photo=photo, pagination=pagination,
                           photo_index=photo_index, photo_sum=photo_sum)


@main.route('/edit-album/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_album(id):
    album = Album.query.get_or_404(id)
    form = EditAlbumForm()
    if form.validate_on_submit():
        album.title = form.title.data
        album.about = form.about.data
        album.asc_order = form.asc_order.data
        album.no_public = form.no_public.data
        album.no_comment = form.no_comment.data
        album.author = current_user._get_current_object()
        flash(u'更改已保存。', 'success')
        return redirect(url_for('.album', id=id))
    form.title.data = album.title
    form.about.data = album.about
    form.asc_order.data = album.asc_order
    form.no_comment.data = album.no_comment
    form.no_public.data = album.no_public
    return render_template('main/edit_album.html', form=form, album=album)


@main.route('/add-photo/<int:id>', methods=['GET', 'POST'])
@login_required
def add_photo(id):
    album = Album.query.get_or_404(id)
    form = AddPhotoForm()
    if form.validate_on_submit():  # current_user.can(Permission.CREATE_ALBUMS)
        if request.method == 'POST' and 'photo' in request.files:
            images = save_image(request.files.getlist('photo'))

            for url in images:
                photo = Photo(url=url[0], url_s=url[1], url_t=url[2],
                              album=album, author=current_user._get_current_object())
                db.session.add(photo)
            db.session.commit()
        flash(u'图片添加成功！', 'success')
        return redirect(url_for('.album', id=album.id))
    return render_template('main/add_photo.html', form=form, album=album)


@main.route('/save-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def save_edit(id):
    album = Album.query.get_or_404(id)
    photos = album.photos
    for photo in photos:
        photo.about = request.form[str(photo.id)]
        photo.order = request.form["order-" + str(photo.id)]
        db.session.add(photo)
    default_value = album.cover
    album.cover = request.form.get('cover', default_value)
    db.session.add(album)
    db.session.commit()
    flash(u'更改已保存。', 'success')
    return redirect(url_for('.album', id=id))


@main.route('/save-photo-edit/<int:id>', methods=['GET', 'POST'])
@login_required
def save_photo_edit(id):
    photo = Photo.query.get_or_404(id)
    album = photo.album
    photo.about = request.form.get('about', '')
    # set default_value to avoid 400 error.
    default_value = album.cover
    print default_value
    album.cover = request.form.get('cover', default_value)
    db.session.add(photo)
    db.session.add(album)
    db.session.commit()
    flash(u'更改已保存。', 'success')
    return redirect(url_for('.photo', id=id))


@main.route('/photo/n/<int:id>')
def photo_next(id):
    "redirect to next imgae"
    photo_now = Photo.query.get_or_404(id)
    album = photo_now.album
    photos = album.photos.order_by(Photo.order.asc())
    position = list(photos).index(photo_now) + 1
    if position == len(list(photos)):
        flash(u'已经是最后一张了。', 'info')
        return redirect(url_for('main.photo', id=id))
    photo = photos[position]
    return redirect(url_for('main.photo', id=photo.id))


@main.route('/photo/p/<int:id>')
def photo_previous(id):
    "redirect to previous imgae"
    photo_now = Photo.query.get_or_404(id)
    album = photo_now.album
    photos = album.photos.order_by(Photo.order.asc())
    position = list(photos).index(photo_now) - 1
    if position == -1:
        flash(u'已经是第一张了。', 'info')
        return redirect(url_for('.photo', id=id))
    photo = photos[position]
    return redirect(url_for('.photo', id=photo.id))


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    return render_template('upload.html')


@main.route('/upload-add', methods=['GET', 'POST'])
@login_required
def upload_add():
    id = request.form.get('album')
    return redirect(url_for('.add_photo', id=id))


@main.route('/delete/photo/<id>')
@login_required
def delete_photo(id):
    photo = Photo.query.filter_by(id=id).first()
    album = photo.album
    if photo is None:
        flash(u'无效的操作。', 'warning')
        return redirect(url_for('.index', username=current_user.username))
    if current_user.username != photo.author.username:
        abort(403)
    db.session.delete(photo)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('.album', id=album.id))


@main.route('/delete/edit-photo/<id>')
@login_required
def delete_edit_photo(id):
    photo = Photo.query.filter_by(id=id).first()
    album = photo.album
    if photo is None:
        flash(u'无效的操作。', 'warning')
        return redirect(url_for('.index', username=current_user.username))
    if current_user.username != photo.author.username:
        abort(403)
    db.session.delete(photo)
    db.session.commit()
    return (''), 204


@main.route('/delete/album/<id>')
@login_required
def delete_album(id):
    album = Album.query.filter_by(id=id).first()
    if album is None:
        flash(u'无效的操作。', 'warning')
        return redirect(url_for('.index', username=current_user.username))
    if current_user.username != album.author.username:
        abort(403)
    db.session.delete(album)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('.albums', username=album.author.username))


@main.route('/category/<int:id>', methods=['POST', 'GET'])
def category(id):
    category = Category.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = category.articles.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('main/category_articles.html',
                           list=articles,
                           category=category,
                           pagination=pagination)
