#!/usr/bin/python
# -*- coding:utf8 -*-
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

# initialization
app = Flask(__name__)
EXPIRATION = 600  # token 有效期600s
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 数据库事务自动提交会话

# extensions
DB = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(DB.Model):
    __tablename__ = 'users'
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(32), index=True)
    password_hash = DB.Column(DB.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=EXPIRATION):
        # 第一个参数是内部的私钥，这里写在共用的配置信息里了
        # 第二个参数是有效期(秒)
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})  # 接收用户id转换与编码

    @staticmethod
    def verify_auth_token(token):
        # 参数为私有秘钥，跟上面方法的秘钥保持一致
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/new_user', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(401)  # existing user
    user = User(username=username)
    user.hash_password(password)
    DB.session.add(user)
    DB.session.commit()
    return (jsonify({'username': user.username}), 201, {
        'Location': url_for('get_user', id=user.id, _external=True)
    })


@app.route('/get_user/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/get_token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(EXPIRATION)
    return jsonify({'token': token.decode('utf8'), 'duration': EXPIRATION})
