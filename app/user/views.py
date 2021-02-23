'''
/users                  GET:返回user/login_sunccess.html页面
/user/info              GET:返回user/userinfo.html页面
/user/register          GET:返回user/register.html页面                  POST:处理用户输入信息进行注册
/user/login             GET:返回user/login.html页面                     POST:处理用户输入信息进行登录
/user/logout            GET:重定向到/,删除session
/user/logoff            GET:重定向到/,修改用户isalive字段为注销状态1 删除session
/user/UPDATE/userinfo   GET:返回update_info.html页面                    POST:处理用户输入信息,对用户数据进行修改
/user/UPDATE/password   GET:返回update_passwd.html页面                  POST:处理用户输入信息,对用户数据进行修改
'''

import flask
from . import user
from app.tools import *


@user.route('/user/register', methods=['GET', 'POST'])
@check_input_wraps(['username', 'age', 'password'])
def register(wrap_res):
    '''
        注册 ,使用装饰器对用户输入信息进行检测
        根据请求方式返回对应页面
        params:method 请求方式(get,post) wrap_res check_input_wraps装饰器返回的验证结果(1 验证成功 0 验证失败)
        get:返回register页面
        post:注册成功返回login页面 注册失败或其他错误返回tips_page页面
    '''
    if flask.request.method == 'POST':
        if wrap_res:
            username = flask.request.form.get('username', default=None)
            age = flask.request.form.get('age', default=None)
            password = flask.request.form.get('password', default=None)
            password = encryption_string(password)
            if check_user(username):
                insert_db_res = insert_db(username, age, password)
                if insert_db_res[0] == 1:
                    resp = flask.make_response(flask.redirect('/users'))
                    resp.set_cookie('username', username, max_age=3600)
                    flask.session['username'] = username
                    flask.session['id'] = insert_db_res[1]
                    return resp
                elif insert_db_res[0] == 0:
                    res = '注册失败'
            else:
                res = '{}已存在'.format(username)
        else:
            res = '请输入正确的信息'
        return flask.render_template('user/register.html', res=res)
    elif flask.request.method == 'GET':
        return flask.render_template('user/register.html')


@user.route('/user/login', methods=['GET', 'POST'])
@check_input_wraps(['username', 'password'])
def login(wrap_res):
    '''
        登录 ,使用装饰器对用户输入的信息进行检测;
        params: method 当前请求方式,wrap_res 装饰器检测结果 1 通过检测 0 有空值
        return: get请求放回login页面 post请求返回tips_page页面
    '''
    if flask.request.method == 'POST':
        if wrap_res:
            username = flask.request.form.get('username', default=None)
            password = flask.request.form.get('password', default=None)
            password = encryption_string(password)
            check_user_pass_res = check_user_pass(username, password)
            res = check_user_pass_res[0]
            if res == 1:
                id = check_user_pass_res[1]
                resp = flask.make_response(flask.redirect('/users'))
                resp.set_cookie('username', username, max_age=3600)
                flask.session['username'] = username
                flask.session['id'] = id
                return resp
            elif res == 2:
                res = '用户已注销'
            else:
                res = '用户名或密码输入错误'
        else:
            res = '请输入正确的参数'
        return flask.render_template('user/login.html', res=res)
    elif flask.request.method == 'GET':
        return flask.render_template('user/login.html')


@user.route('/users', methods=['GET', 'POST'])
@check_power
def users():
    '''
        登录或注册成功,验证权限成功之后跳转页面
    '''
    username = flask.session['username']
    return flask.render_template('user/login_success.html', res='{}登录成功'.format(username))


@user.route('/user/info', methods=['GET', 'POST'])
@check_power
def userinfo():
    '''
        验证权限之后跳转到用户页面,显示用户id,name,age,passwd
    '''
    sql = 'select * from users where name = %s'
    params_list = [flask.session['username']]
    data = select_mysql(sql, params_list)
    if data:
        return flask.render_template('user/userinfo.html', id=data[0][0], name=data[0][1], age=data[0][2], password=data[0][3])
    else:
        return flask.redirect('/user/login')


@user.route('/user/logout', methods=['GET'])
@check_power
def logout():
    '''
        用户退出,删除seesion中的username
    '''
    flask.session.pop('username', None)
    flask.session.pop('id', None)
    resp = flask.make_response(flask.redirect('/'))
    resp.delete_cookie('username')
    return resp


@user.route('/user/logoff', methods=['GET'])
@check_power
def logoff():
    '''
        用户注销功能,修改用户数据表中对应用户的isalive字段为1,并删除session
        return:重定向到首页(/)
    '''
    username = flask.session['username']
    sql = 'update users set isalive = 1 where name = %s'
    params_list = [username]
    err = update_mysql(sql, params_list)
    if err:
        return flask.render_template('user/login_success.html', res='注销失败')
    flask.session.pop('username', None)
    flask.session.pop('id', None)
    return flask.redirect('/')


@user.route('/user/UPDATE/userinfo', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['username', 'age'])
def update_userinfo(wraps_res):
    '''
        修改用户信息,验证用户输入信息,get请求返回update_info.html,post请求修改用户信息
        return: 重定向到/user/info
    '''
    if flask.request.method == 'GET':
        return flask.render_template('user/update_info.html')
    elif flask.request.method == 'POST':
        if wraps_res:
            username = flask.request.form.get('username', default=None)
            if check_user(username):
                age = flask.request.form.get('age', default=None)
                sql = 'update users set name = %s, age = %s where id =%s'
                params_list = [username, age, flask.session['id']]
                err = update_mysql(sql, params_list)
                if not err:
                    flask.session['username'] = username
                    return flask.redirect('/user/info')
                else:
                    res = '修改失败'
            else:
                res = '用户名已存在'
        else:
            res = '输入信息不能为空'
        return flask.render_template('user/update_info.html', res=res)


@user.route('/user/UPDATE/password', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['old_password', 'new_password1', 'new_password2'])
def update_passwd(wraps_res):
    '''
        修改用户登录密码,get请求返回update_passwd.html页面,post请求修改密码
        return: 返回对应的页面
    '''
    if flask.request.method == 'GET':
        return flask.render_template('user/update_passwd.html')
    elif flask.request.method == 'POST':
        if wraps_res:
            old_password = flask.request.form.get('old_password', default=None)
            new_password1 = flask.request.form.get(
                'new_password1', default=None)
            new_password2 = flask.request.form.get(
                'new_password2', default=None)
            check_update_res = check_update_passwd(
                old_password, new_password1, new_password2)
            res = check_update_res
        else:
            res = '输入信息不能为空'
        if res == 1:
            return flask.redirect('/user/login')
        else:
            return flask.render_template('user/update_passwd.html', res=res)
