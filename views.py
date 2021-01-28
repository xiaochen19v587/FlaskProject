import flask
import mysql.connector
import re
import os
import json
import hashlib
from functools import wraps

app = flask.Flask(__name__)
app.debug = True
app.secret_key = os.urandom(16)
app.config['JSON_AS_ASCII'] = False


def _check_input_wraps(params_list):
    '''
    装饰器:检验用户输入的参数是否为空
    return: 1 检验成功 0 检验失败
    '''
    def wrapper(func):
        @wraps(func)
        def check_input(*args, **kwargs):
            res_list = []
            for params in params_list:
                if flask.request.method == 'GET':
                    params = flask.request.args.get(params)
                    if params:
                        res_list.append(params)
                    else:
                        return func(0)
                if flask.request.method == 'POST':
                    params = flask.request.form.get(params)
                    if params:
                        res_list.append(params)
                    else:
                        return func(0)
            return func(1)
        return check_input
    return wrapper


def _check_power(func):
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


@app.route('/', methods=['GET'])
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
@_check_input_wraps(['username', 'age', 'password'])
def register(wrap_res):
    '''
        注册 ,使用装饰器对用户输入信息进行检测
        根据请求方式返回对应页面
        params:method 请求方式(get,post) wrap_res _check_input_wraps装饰器返回的验证结果(1 验证成功 0 验证失败)
        get:返回register页面
        post:注册成功返回login页面 注册失败或其他错误返回tips_page页面
    '''
    if flask.request.method == 'POST':
        if wrap_res:
            username = flask.request.form.get('username', default=None)
            age = flask.request.form.get('age', default=None)
            password = flask.request.form.get('password', default=None)
            password = __encryption_string(password)
            if __check_user(username):
                if __insert_db(username, age, password):
                    resp = flask.make_response(flask.redirect('/loginsuccess'))
                    resp.set_cookie('username', username)
                    flask.session['username'] = username
                    return resp
                else:
                    return flask.render_template('register.html', res='注册失败')
            else:
                return flask.render_template('register.html', res='{}已存在'.format(username))
        else:
            return flask.render_template('register.html', res='请输入正确的信息')
    elif flask.request.method == 'GET':
        return flask.render_template('register.html')


def __check_user(username):
    '''
        检测数据库中是否存在username;
        params:username 用户输入的用户名
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


def __encryption_string(string):
    '''
        对用户输入的字符串进行加盐加密
        params:string 需要加密的字符串
        return:new_string 加盐加密之后的字符串
    '''
    hash_string = hashlib.md5(b'xiaochen19v587')
    hash_string.update(string.encode('utf-8'))
    new_string = hash_string.hexdigest()
    hash_string = hashlib.md5(b'password')
    hash_string.update(new_string.encode('utf-8'))
    new_string = hash_string.hexdigest()
    return new_string


def __insert_db(username, age, password):
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
        print(e)
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
@_check_input_wraps(['username', 'password'])
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
            password = __encryption_string(password)
            if __check_user_pass(username, password) == 1:
                resp = flask.make_response(flask.redirect('/loginsuccess'))
                resp.set_cookie('username', username)
                flask.session['username'] = username
                return resp
            elif __check_user_pass(username, password) == 2:
                return flask.render_template('login.html', res='用户已注销')
            else:
                return flask.render_template('login.html', res='用户名或密码输入错误')
        else:
            return flask.render_template('login.html', res='请输入正确的参数')
    elif flask.request.method == 'GET':
        return flask.render_template('login.html')


def __check_user_pass(username, password):
    '''
        检测用户名和密码是否匹配
        params: username 用户输入的用户名, passwrod 用户输入的密码
        return: 1 用户名和密码匹配成功 0 用户名和密码匹配失败 2 当前用户已经注销
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'select password, isalive from students where name = %s'
    try:
        cursor.execute(sql, [username])
        user_pass = cursor.fetchall()
        cursor.close()
        conn.close()
        if user_pass[0][0] == password and user_pass[0][1] == 0:
            return 1
        elif user_pass[0][1] == 1:
            return 2
        elif user_pass[0][0] != password:
            return 0
    except:
        return 0


@app.route('/loginsuccess', methods=['GET'])
@_check_power
def loginsuccess():
    '''
        登录或注册成功,验证权限成功之后跳转页面
    '''
    username = flask.session['username']
    return flask.render_template('login_success.html', res='{}登录成功'.format(username))


@app.route('/students', methods=['GET'])
@_check_power
def students():
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
    return flask.render_template('students.html', id=data[0][0], name=data[0][1], age=data[0][2], password=data[0][3])


@app.route('/logout', methods=['GET'])
@_check_power
def logout():
    '''
        用户退出,删除seesion中的username
    '''
    flask.session.pop('username', None)
    return flask.redirect('/')


@app.route('/INSERT/cartinfo', methods=['GET', 'POST'])
@_check_power
@_check_input_wraps(['cartname', 'price'])
def shoppingcart(wraps_res):
    '''
        添加用户购物车,_check_power装饰器验证用户权限,_check_input_wraps装饰器验证用户输入信息是否为空
        params:wraps_res _check_input_wraps装饰器返回值(1 验证成功输入不为空 0 验证失败输入为空)
        return:返回cartinfo页面
    '''
    if wraps_res and flask.request.method == 'POST':
        cartname = flask.request.form.get('cartname')
        price = flask.request.form.get('price')
        username = flask.session['username']
        conn = mysql.connector.connect(
            host='127.0.0.1', user='root', passwd='123123', database='test')
        cursor = conn.cursor()
        sql = 'select id from students where name = %s'
        try:
            cursor.execute(sql, [username])
            data = cursor.fetchall()[0][0]
        except Exception as e:
            print(e)
            return flask.render_template('cartinfo.html', res='用户id不存在')
        try:
            sql = 'insert into cartinfo (studentid,cartname,price) values (%s,%s,%s)'
            cursor.execute(sql, [data, cartname, price])
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return flask.render_template('carifno.html', res='添加失败')
        cursor.close()
        conn.close()
        return flask.render_template('cartinfo.html', res='购物车添加成功')
    elif flask.request.method == 'GET':
        return flask.render_template('cartinfo.html')
    else:
        return flask.render_template('cartinfo.html', res='输入信息不能为空')


@app.route('/carts', methods=['GET', 'POST'])
@_check_power
def carts():
    '''
        显示当前登录用户的购物车信息,_check_power装饰器验证用户权限
        return:返回carts页面,用于显示用户购物车信息
    '''
    username = flask.session['username']
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    try:
        sql = 'select id from students where name=%s'
        cursor.execute(sql, [username])
        user_id = cursor.fetchall()[0][0]
    except Exception as e:
        print(e)
        return flask.render_template('carts.html', res='查询用户失败')
    try:
        sql = 'select cartid,cartname,price from cartinfo where studentid = %s'
        cursor.execute(sql, [user_id])
        data = cursor.fetchall()
    except Exception as e:
        print(e)
        return flask.render_template('carts.html', res='查询信息失败')
    cursor.close()
    conn.close()
    if data:
        return flask.render_template('carts.html', res='{}用户的购物车'.format(flask.session['username']), data=data)
    else:
        return flask.render_template('carts.html', res='当前购物车信息为空')


@app.route('/logoff', methods=['GET'])
@_check_power
def logoff():
    '''
        用户注销功能,修改用户数据表中对应用户的isalive字段为1,并删除session
        return:重定向到首页(/)
    '''
    username = flask.session['username']
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'update students set isalive = 1 where name = %s'
    try:
        cursor.execute(sql, [username])
        flask.session.pop('username', None)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        return flask.render_template('login_success.html', res='注销失败')
    cursor.close()
    conn.close()
    return flask.redirect('/')


@app.route('/DELETE/carts/')
def delete_carts():
    cartid = flask.request.args.get('cartid')
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    try:
        sql = 'delete from cartinfo where cartid = %s'
        cursor.execute(sql, [cartid])
        conn.commit()
    except:
        conn.rollback()
    cursor.close()
    conn.close()
    return flask.redirect('/carts')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
