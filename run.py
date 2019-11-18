#!/usr/bin/python
# -*- coding:utf8 -*-
# project_dir should be set as PYTHONPATH before run this file
from dept.dept import dept
from user.user import user
from auth import app, DB
import os

# 路由分发
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(dept, url_prefix='/dept')

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        DB.create_all()
    app.run(debug=True, host='0.0.0.0')
