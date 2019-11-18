#!/usr/bin/python
# -*- coding:utf8 -*-
from flask import jsonify
from flask import Blueprint
from auth import auth
import json

dept = Blueprint(
    'dept',
    __name__,
)
dept_data = [{'name': '部门1', 'id': 12345}, {'name': '部门2', 'id': 12346}]


@dept.route('/<int:id>', methods=[
    'GET',
])
@auth.login_required
def get(id):
    for dept in dept_data:
        if int(dept['id']) == id:
            return jsonify(status='success', dept=dept)

    return jsonify(status='failed', msg='dept not found')


@dept.route('/depts', methods=[
    'GET',
])
@auth.login_required
def get_depts():
    data = {'status': 'success', 'depts': dept_data}
    return json.dumps(data, ensure_ascii=False, indent=1)
