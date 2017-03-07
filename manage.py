#! /usr/bin/env python2
# -*-coding:utf-8-*-


from app import create_app, db
from flask_script import Manager, Shell
from app.models import Article, Category, User, Role, Permission, Comment
from flask_migrate import Migrate, MigrateCommand  # 载入migrate扩展


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)  # 注册migrate到flask


def make_shell_context():
    return dict(app=app, db=db, User=User,  Role=Role, Category=Category,
                Permission=Permission, Article=Article, Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  # 在终端环境下添加一个db命令


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

    # create self-follows for all users
    # User.add_self_follows()


if __name__ == '__main__':
    manager.run()
