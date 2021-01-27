import flask
import mysql.connector
import re
import os
import json
from functools import wraps

app = flask.Flask(__name__)
app.debug = True
app.secret_key = os.urandom(16)
app.config['JSON_AS_ASCII'] = False


def check_input_mraps(params_list):
    '''
    装饰器:检验用户输入的参数是否为空
    return: 1 检验成功 0 检验失败
    return: 当前请求方式 GET 或者 POST
    '''
    def wrapper(func):
        @wraps(func)
        def check_input(*args, **kwargs):
            if flask.request.method == 'GET':
                return func('GET', 1)
            elif flask.request.method == 'POST':
                res_list = []
                for params in params_list:
                    params = flask.request.form.get(params)
                    if params:
                        res_list.append(params)
                    else:
                        return func('POST', 0)
            return func('POST', 1)
        return check_input
    return wrapper


def check_power(func):
    '''
        装饰器:验证用户权限,判断'username'是否存在于session中
        验证成功执行被装饰函数,验证失败重定向到/login
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in flask.session:
            return func(*args, **kwargs)
        else:
            return flask.redirect('/login')
    return wrapper


@app.route('/')
def hello_world():
    '''
        请求路由为/,返回register页面
    '''
    if 'username' in flask.session:
        return flask.render_template('tips_page.html', name='', res='You are login')
    return flask.render_template('tips_page.html', name='', res='You are not logged in')


@app.errorhandler(404)
def page_not_found(e):
    '''
        错误页面
    '''
    return flask.render_template('error/404.html'), 404


@app.route('/register', methods=['GET', 'POST'])
@check_input_mraps(['username', 'age', 'password'])
def register_user(method, wrap_res):
    '''
        注册 ,使用装饰器对用户输入信息进行检测
        根据请求方式返回对应页面
        get:返回register页面
        post:注册成功返回login页面 注册失败或其他错误返回tips_page页面
    '''
    if method == 'GET':
        return flask.render_template('register.html')
    elif method == 'POST':
        if wrap_res:
            username = flask.request.form.get('username', default=None)
            age = flask.request.form.get('age', default=None)
            password = flask.request.form.get('password', default=None)
            if check_user(username):
                if insert_db(username, age, password):
                    resp = flask.make_response(flask.redirect('/loginsuccess'))
                    resp.set_cookie('username', username)
                    flask.session['username'] = username
                    return resp
                else:
                    return flask.render_template('tips_page.html', name=username, res='注册失败')
            else:
                return flask.render_template('tips_page.html', name=username, res='已存在')
        else:
            return flask.render_template('tips_page.html', name='请输入正确的', res='参数')


def check_user(username):
    '''
        检测数据库中是否存在username;
        return:0 已存在 1 不存在
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = "select id from students where name = %s"
    cursor.execute(sql, [username])
    user_counts = cursor.fetchall()
    cursor.close()
    conn.close()
    if user_counts:
        return 0
    else:
        return 1


def insert_db(username, age, password):
    '''
        向数据库中插入数据;
        params: username 用户输入的usernmae,age 用户输入的age, password 用户输入的password
        return: 0 插入数据失败 1 插入数据成功
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'insert into students (name,age,password) values (%s,%s,%s)'
    try:
        cursor.execute(sql, [username, age, password])
    except Exception as e:
        conn.rollback()
        err = e
    else:
        conn.commit()
        err = None
    cursor.close()
    conn.close()
    if err:
        return 0
    else:
        return 1


@app.route('/login', methods=['GET', 'POST'])
@check_input_mraps(['username', 'password'])
def login(method, wrap_res):
    '''
        登录 ,使用装饰器对用户输入的信息进行检测;
        params: method 当前请求方式,wrap_res 装饰器检测结果 1 通过检测 0 有空值
        return: get请求放回login页面 post请求返回tips_page页面
    '''
    if method == 'GET':
        return flask.render_template('login.html')
    elif method == 'POST':
        if wrap_res:
            username = flask.request.form.get('username', default=None)
            password = flask.request.form.get('password', default=None)
            if check_user_pass(username, password):
                resp = flask.make_response(flask.redirect('/loginsuccess'))
                resp.set_cookie('username', username)
                flask.session['username'] = username
                return resp
            else:
                return flask.render_template('tips_page.html', name='用户名或密码', res='输入错误')
        else:
            return flask.render_template('tips_page.html', name='请输入正确的', res='参数')


def check_user_pass(username, password):
    '''
        检测用户名和密码是否匹配
        params: username 用户输入的用户名, passwrod 用户输入的密码
        return: 1 用户名和密码匹配成功 0 用户名和密码匹配失败
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'select password from students where name = %s'
    try:
        cursor.execute(sql, [username])
        user_pass = cursor.fetchall()
        cursor.close()
        conn.close()
        if user_pass[0][0] == password:
            return 1
        else:
            return 0
    except:
        return 0


@app.route('/loginsuccess')
@check_power
def loginsuccess():
    '''
        登录或注册成功,验证权限成功之后跳转页面
    '''
    return flask.render_template('login_success.html')


@app.route('/userinfo', methods=['GET'])
@check_power
def userinfo():
    '''
        验证权限之后跳转到用户页面,显示用户id,name,age,passwd
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'select * from students where name = %s'
    cursor.execute(sql, [flask.session['username']])
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return flask.render_template('user_info.html', id=data[0][0], name=data[0][1], age=data[0][2], password=data[0][3])


@app.route('/carinfo', methods=['GET'])
@check_power
def carinfo():
    '''
        验证权限之后跳转到购物车页面
    '''
    return flask.render_template('car_info.html')


@app.route('/logout', methods=['GET'])
def logout():
    '''
        用户退出,删除seesion中的username
    '''
    flask.session.pop('username', None)
    return flask.redirect('/')


@app.route('/senddate')
def senddate():
    return flask.jsonify({'status': '0', 'errmsg': '登录成功！'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
