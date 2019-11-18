#!/usr/bin/python
# -*- coding:utf8 -*-

from flask import jsonify
from flask import Blueprint
import json

user = Blueprint(
    'user',
    __name__,
)

user_data = [{
    'id': 1,
    'name': '张三',
    'age': 23
}, {
    'id': 2,
    'name': '李四',
    'age': 24
}]


@user.route('/<int:id>', methods=[
    'GET',
])
def get(id):
    for user in user_data:
        if user['id'] == id:
            return jsonify(status='success', user=user)


@user.route('/users', methods=[
    'GET',
])
def users():
    data = {'status': 'success', 'users': user_data}
    return json.dumps(data, ensure_ascii=False, indent=1)
