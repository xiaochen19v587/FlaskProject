#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
/users                  GET:返回user/login_sunccess.html页面
/user/info              GET:返回user/userinfo.html页面
/user/register          GET:返回user/register.html页面                  POST:处理用户输入信息进行注册
/user/login             GET:返回user/login.html页面                     POST:处理用户输入信息进行登录
/user/logout            GET:重定向到/,删除session
/user/logoff            GET:重定向到/,修改用户isalive字段为注销状态1 删除session
/user/UPDATE/userinfo   GET:返回update_info.html页面                    POST:处理用户输入信息,对用户数据进行修改
/user/UPDATE/password   GET:返回update_passwd.html页面                  POST:处理用户输入信息,对用户数据进行修改
/carts                  GET:返回carts.html页面,显示用户购物车中的信息
/cart/ADD               GET:返回cart/cart_info.html                      POST:处理用户输入信息将信息插入到数据库中
/cart/DELETE            GET:重定向到/carts,删除对应id的购物车信息
'''
import flask
import mysql.connector
import re
import os
import json
from tools import *

app = flask.Flask(__name__)
app.debug = True
app.secret_key = os.urandom(16)
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
def index():
    '''
        请求路由为/,返回register页面
    '''
    if 'username' in flask.session:
        return flask.render_template('index.html', name='', res='You are login')
    return flask.render_template('index.html', name='', res='You are not logged in')


@app.errorhandler(404)
def page_not_found(e):
    '''
        错误页面
    '''
    return flask.render_template('error/404.html'), 404


@app.errorhandler(500)
def Server_internal_error(e):
    '''
        错误页面
    '''
    return flask.render_template('error/500.html'), 500


@app.route('/user/register', methods=['GET', 'POST'])
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
                if insert_db(username, age, password):
                    resp = flask.make_response(flask.redirect('/users'))
                    resp.set_cookie('username', username)
                    flask.session['username'] = username
                    return resp
                else:
                    return flask.render_template('user/register.html', res='注册失败')
            else:
                return flask.render_template('user/register.html', res='{}已存在'.format(username))
        else:
            return flask.render_template('user/register.html', res='请输入正确的信息')
    elif flask.request.method == 'GET':
        return flask.render_template('user/register.html')


@app.route('/user/login', methods=['GET', 'POST'])
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
            if check_user_pass(username, password) == 1:
                resp = flask.make_response(flask.redirect('/users'))
                resp.set_cookie('username', username)
                flask.session['username'] = username
                return resp
            elif check_user_pass(username, password) == 2:
                return flask.render_template('user/login.html', res='用户已注销')
            else:
                return flask.render_template('user/login.html', res='用户名或密码输入错误')
        else:
            return flask.render_template('user/login.html', res='请输入正确的参数')
    elif flask.request.method == 'GET':
        return flask.render_template('user/login.html')


@app.route('/users', methods=['GET', 'POST'])
@check_power
def users():
    '''
        登录或注册成功,验证权限成功之后跳转页面
    '''
    username = flask.session['username']
    return flask.render_template('user/login_success.html', res='{}登录成功'.format(username))


@app.route('/user/info', methods=['GET', 'POST'])
@check_power
def userinfo():
    '''
        验证权限之后跳转到用户页面,显示用户id,name,age,passwd
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'select * from students where name = %s'
    try:
        cursor.execute(sql, [flask.session['username']])
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return flask.render_template('user/userinfo.html', id=data[0][0], name=data[0][1], age=data[0][2], password=data[0][3])
    except:
        return flask.redirect('/user/login')


@app.route('/user/logout', methods=['GET'])
@check_power
def logout():
    '''
        用户退出,删除seesion中的username
    '''
    flask.session.pop('username', None)
    return flask.redirect('/')


@app.route('/cart/ADD', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['cartname', 'price'])
def shoppingcart(wraps_res):
    '''
        添加用户购物车,check_power装饰器验证用户权限,check_input_wraps装饰器验证用户输入信息是否为空
        params:wraps_res check_input_wraps装饰器返回值(1 验证成功输入不为空 0 验证失败输入为空)
        return:返回cart_info页面
    '''
    if wraps_res and flask.request.method == 'POST':
        cartname = flask.request.form.get('cartname', default=None)
        price = flask.request.form.get('price', default=None)
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
            return flask.render_template('cart/cart_info.html', res='用户id不存在')
        try:
            sql = 'insert into cartinfo (studentid,cartname,price) values (%s,%s,%s)'
            cursor.execute(sql, [data, cartname, price])
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return flask.render_template('cart/cart_info.html', res='添加失败')
        cursor.close()
        conn.close()
        return flask.render_template('cart/cart_info.html', res='购物车添加成功')
    elif flask.request.method == 'GET':
        return flask.render_template('cart/cart_info.html')
    else:
        return flask.render_template('cart/cart_info.html', res='输入信息不能为空')


@app.route('/carts', methods=['GET', 'POST'])
@check_power
def carts():
    '''
        显示当前登录用户的购物车信息,check_power装饰器验证用户权限
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
        return flask.render_template('cart/carts.html', res='查询用户失败')
    try:
        sql = 'select cartid,cartname,price from cartinfo where studentid = %s'
        cursor.execute(sql, [user_id])
        data = cursor.fetchall()
    except Exception as e:
        print(e)
        return flask.render_template('cart/carts.html', res='查询信息失败')
    cursor.close()
    conn.close()
    if data:
        return flask.render_template('cart/carts.html', res='{}用户的购物车'.format(flask.session['username']), data=data)
    else:
        return flask.render_template('cart/carts.html', res='当前购物车信息为空')


@app.route('/user/logoff', methods=['GET'])
@check_power
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
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        return flask.render_template('user/login_success.html', res='注销失败')
    cursor.close()
    conn.close()
    return flask.redirect('/user/logout')


@app.route('/cart/DELETE', methods=['GET'])
@check_power
def delete_carts():
    '''
        删除对应id的购物车信息,验证当前用户权限,获取url参数cartid,删除对应cartid数据
        return: 重定向到/carts
    '''
    cartid = flask.request.args.get('cartid', default=None)
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    try:
        sql = 'delete from cartinfo where cartid = %s'
        cursor.execute(sql, [cartid])
        conn.commit()
    except:
        conn.rollback()
        return flask.render_template('cart/carts.html', res='删除失败')
    cursor.close()
    conn.close()
    return flask.redirect('/carts')


@app.route('/user/UPDATE/userinfo', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['username', 'age'])
def update_userinfo(wraps_res):
    '''
        修改用户信息,验证用户输入信息,get请求返回update_info.html,post请求修改用户信息
        return: 重定向到students
    '''
    if flask.request.method == 'GET':
        return flask.render_template('user/update_info.html')
    elif flask.request.method == 'POST':
        if not wraps_res:
            return flask.render_template('user/update_info.html', res='输入信息不能为空')
        username = flask.request.form.get('username', default=None)
        if not check_user(username):
            return flask.render_template('user/update_info.html', res='用户名已存在')
        age = flask.request.form.get('age', default=None)
        conn = mysql.connector.connect(
            host='127.0.0.1', user='root', passwd='123123', database='test')
        cursor = conn.cursor()
        sql = 'select id from students where name = %s'
        try:
            cursor.execute(sql, [flask.session['username']])
            id = cursor.fetchall()[0][0]
        except Exception as e:
            print(e)
        sql = 'update students set name = %s, age = %s where id =%s'
        try:
            cursor.execute(sql, [username, age, id])
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            return flask.render_template('user/update_info.html', res='请输入正确的信息')
        cursor.close()
        conn.close()
        flask.session['username'] = username
        print(flask.session['username'])
        return flask.redirect('/user/info')


@app.route('/user/UPDATE/password', methods=['GET', 'POST'])
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
            if check_update_res == 1:
                flask.session.pop('username', None)
                return flask.redirect('/user/login')
            elif check_update_res == 2:
                res = '查询用户失败'
            elif check_update_res == 3:
                res = '输入的原密码不正确'
            elif check_update_res == 4:
                res = '两次输入的新密码不正确'
            elif check_update_res == 5:
                res = '修改密码失败'
            elif check_update_res == 6:
                res = '新密码和旧密码相同'
            return flask.render_template('user/update_passwd.html', res=res)
        else:
            return flask.render_template('user/update_passwd.html', res='输入信息不能为空')


@app.route('/cart/UPDATE', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['cartname', 'price'])
def cart_update(wraps_res):
    '''
        修改用户的购物信息,GET请求返回cart/cart_update页面,POST请求获取前端返回数据,将数据在数据库中同步修改
        return:返回对应页面
    '''
    if flask.request.method == 'GET':
        cartid = flask.request.args.get('cartid', default=None)
        cartname = flask.request.args.get('cartname', default=None)
        price = flask.request.args.get('price', default=None)
        return flask.render_template('cart/cart_update.html', cartinfo='当前商品信息:{}, {}, {}'.format(cartid, cartname, price))
    if flask.request.method == 'POST' and wraps_res:
        cartinfo = flask.request.form.get('cartinfo', default=None)
        cartname = flask.request.form.get('cartname', default=None)
        price = flask.request.form.get('price', default=None)
        cartid = re.findall(':(.*?),', cartinfo)[0]
        if update_cart(cartid, cartname, price):
            return flask.render_template('cart/cart_update.html', cartinfo='当前商品信息:{}, {}, {}'.format(cartid, cartname, price), res='修改成功')
        else:
            return flask.render_template('cart/cart_update.html', cartinfo=cartinfo, res='修改失败')
    elif flask.request.method == 'POST' and not wraps_res:
        cartinfo = flask.request.form.get('cartinfo')
        return flask.render_template('cart/cart_update.html', cartinfo=cartinfo, res='当前输入信息为空')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
