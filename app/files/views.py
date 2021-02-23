'''
/files                  GET:返回files.html页面
/file/upfile            GET:返回files.html页面                          POST:处理用户上传文件
'''

import flask
import os
from . import files
from werkzeug.utils import secure_filename
from app.tools import *



@files.route('/files', methods=['GET', 'POST'])
@check_power
def file():
    '''
        显示上传文件页面,GET请求方式返回file/files.html
        return:返回file/files.html
    '''
    return flask.render_template('file/files.html')


@files.route('/file/upfile', methods=['GET', 'POST'])
@check_power
def upfile():
    '''
        上传文件,GET请求返回file/files.html POST请求获得用户上传的文件,保存在static/upload_file/文件夹中
        如果是png或者txt后缀,显示在files.html中进行预览,否则不能进行预览
        return: 返回对应的页面
    '''
    if flask.request.method == 'POST':
        file = flask.request.files.get('file')
        filename = secure_filename(file.filename)
        res = ''
        img = ''
        if filename:
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(
                basepath, 'static/upload_file', filename)
            file.save(upload_path)
            if '.png' in filename:
                filename = 'upload_file/{}'.format(filename)
                img = flask.url_for('static', filename=filename)
            elif '.txt' in filename:
                with open(upload_path, 'r') as f:
                    res = f.read()
            else:
                res = '文件格式暂不支持在线预览'
        else:
            res = '上传文件为空'
        return flask.render_template('file/files.html', res=res, img=img)
    elif flask.request.method == 'GET':
        return flask.render_template('file/files.html')
