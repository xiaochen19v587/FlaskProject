#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
check_input_wraps       装饰器,用于验证用户输入的参数是否为空
check_power             装饰器,用于验证用户权限
check_user              函数,用于验证数据库中是否存在username
encryption_string       函数,用于对用户输入的字符串进行加盐加密
insert_db               函数,用于向数据库中插入数据
check_user_pass         函数,用于验证用户名和密码是否和数据库中匹配
check_update_passwd     函数,用于验证用户输入的新旧密码是否符合条件
update_cart             函数,修改商品信息
select_book             函数,查找用户书籍
update_book_info        函数,修改用户书籍信息
add_book_info           函数,添加书籍信息
'''
from functools import wraps
import flask
import mysql.connector
import hashlib


def select_mysql(sql, params_list):
    '''
        查询数据库信息
        params: sql 执行的sql语句; parmas_list sql语句中的参数列表
        return: data 如果执行sql语句没有报错,返回查询到的数据列表;否则返回加密过的encryption_string('select_data_err')
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='info')
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params_list)
        data = cursor.fetchall()
    except Exception as e:
        print(e)
        data = encryption_string('select_data_err')
    cursor.close()
    conn.close
    return data


def update_mysql(sql, params_list):
    '''
        更新数据库信息
        params:sql 执行的sql语句; params_list sql语句中的参数列表
        return:err sql语句执行成功返回None;执行失败返回Exception信息
    '''
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='info')
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params_list)
        conn.commit()
        err = None
    except Exception as e:
        print(e)
        err = e
        conn.rollback()
    cursor.close()
    conn.close()
    return err


def check_input_wraps(params_list):
    '''
        装饰器:检验用户输入的参数是否为空
        return: 1 检验成功 0 检验失败
    '''
    def wrapper(func):
        @wraps(func)
        def check_input(*args, **kwargs):
            sign_list = ["|", "_", "~", "^", "*",
                         "&", "%", "@", "$", " ", "\\"]
            for params in params_list:
                if flask.request.method == 'GET':
                    method_func_res = flask.request.args.get(params)
                elif flask.request.method == 'POST':
                    method_func_res = flask.request.form.get(params)
                if not method_func_res:
                    return func(0)
                for sign in sign_list:
                    if sign in method_func_res:
                        return func(0)
            return func(1)
        return check_input
    return wrapper


def check_power(func):
    '''
        装饰器:验证用户权限,判断'username'是否存在于session中
        验证成功执行被装饰函数,验证失败重定向到/user/login
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if flask.request.cookies.get('username'):
            if 'username' in flask.session and 'id' in flask.session:
                return func(*args, **kwargs)
            else:
                return flask.redirect('/')
        else:
            return flask.redirect('/')
    return wrapper


def check_user(username):
    '''
        检测数据库中是否存在username;
        params:username 用户输入的用户名
        return:0 已存在 1 不存在
    '''
    sql = "select id from users where name = %s"
    params_list = [username]
    data = select_mysql(sql, params_list)
    if data == encryption_string('select_data_err'):
        return 0
    elif data:
        return 0
    else:
        return 1


def encryption_string(string):
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


def insert_db(name, age, password):
    '''
        向数据库中插入数据;
        params: name 用户输入的usernmae,age 用户输入的age, password 用户输入的password
        return: 0 插入数据失败 1 插入数据成功
    '''
    sql = 'insert into users (name,age,password) values (%s,%s,%s)'
    params_list = [name, age, password]
    err = update_mysql(sql, params_list)
    if not err:
        sql = 'select id from users where name = %s'
        params_list = [name]
        data = select_mysql(sql, params_list)
        if data == encryption_string('select_data_err'):
            return (0, None)
        elif data:
            return (1, data[0][0])
    else:
        return (0, None)


def check_user_pass(username, password):
    '''
        检测用户名和密码是否匹配
        params: username 用户输入的用户名, passwrod 用户输入的密码
        return: 1 用户名和密码匹配成功 0 用户名和密码匹配失败 2 当前用户已经注销
    '''
    sql = 'select password, isalive, id from users where name = %s'
    params_list = [username]
    data = select_mysql(sql, params_list)
    if data == encryption_string('select_data_err'):
        return (0, None)
    elif data:
        if data[0][0] == password and data[0][1] == 0:
            return (1, data[0][2])
        elif data[0][1] == 1:
            return (2, None)
        elif data[0][0] != password:
            return (0, None)
    else:
        return (0, None)


def check_update_passwd(old_password, new_password1, new_password2):
    '''
        检测用户输入的新旧密码是否符合条件
        return: 1 修改成功 2 查询用户失败 3 旧密码输入不正确 4 两次新密码输入不一致 5 修改密码失败 6 新密码和旧密码相同
    '''
    if new_password1 != new_password2:
        # 两次新密码不一致
        res = '输入的新密码不一致'
    else:
        old_password = encryption_string(old_password)
        if encryption_string(new_password1) == old_password:
            # 新旧密码相同
            res = '新密码不能和旧密码相同'
        else:
            sql = 'select password from users where name = %s'
            params_list = [flask.session['username']]
            data = select_mysql(sql, params_list)
            if not data:
                res = '查询用户失败'
            elif data == encryption_string('select_data_err'):
                res = 'UnKnow err'
            else:
                password = data[0][0]
                if password == old_password:
                    # 修改密码
                    sql = 'update users set password = %s where name = %s'
                    params_list = [encryption_string(
                        new_password1), flask.session['username']]
                    err = update_mysql(sql, params_list)
                    if err:
                        res = '修改密码失败'
                    else:
                        res = 1
                else:
                    # 密码不匹配
                    res = '旧密码输入不正确'
    return res


def update_cart(cartid, cartname, price):
    '''
        修改商品信息,根据前端返回的cartid修改数据库中对应的数据
        params:cartid cartid, cartname 用户输入的cartname, price 用户输入的price
        return:1修改成功 0 修改失败
    '''
    sql = 'select cartname,price from carts where cartid=%s'
    params_list = [cartid]
    data = select_mysql(sql, params_list)
    if not data:
        return 0
    elif data == encryption_string('select_data_err'):
        return 0
    sql = 'update carts set cartname=%s,price=%s where cartid=%s'
    params_list = [cartname, price, cartid]
    err = update_mysql(sql, params_list)
    return err


def select_book(userid):
    '''
        查找对应用户的书籍信息,根据用户的id查找到数据库中所有的书籍信息
        return:书籍信息
    '''
    sql = 'select id,name,author from books where userid=%s'
    params_list = [userid]
    data = select_mysql(sql, params_list)
    if data == encryption_string('select_data_err'):
        pass
    elif data:
        return data


def update_book_info(id, name, author):
    '''
        接收三个参数,进行数据修改
        params:id 书籍id;name 书籍名;author 作者
        return:1 修改成功 0 修改失败
    '''
    sql = 'update books set name=%s,author=%s where id=%s'
    params_list = [name, author, id]
    err = update_mysql(sql, params_list)
    return err


def add_book_info(userid, name, author):
    '''
        接收数据,将数据添加到数据库中
        params:userid 当前登录用户id;name 书籍名;author 书籍作者
        return:1 添加成功 0 添加失败
    '''
    sql = 'insert into books (userid,name,author) values (%s,%s,%s)'
    params_list = [userid, name, author]
    err = update_mysql(sql, params_list)
    return err
