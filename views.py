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
/cart/ADD               GET:返回cart/cart_info.html                     POST:处理用户输入信息将信息插入到数据库中
/cart/DELETE            GET:重定向到/carts,删除对应id的购物车信息
/files                  GET:返回files.html页面
/file/upfile            GET:返回files.html页面                          POST:处理用户上传文件
/books                  GET:返回books.html页面
/book/DELETE            GET:删除用户书籍信息
/book/UPDATE            GET:返回book_update.html页面                    POST:处理用户输入信息,对书籍数据进行修改
/book/ADD               GET:返回book_info.html页面                      POST:处理用户输入信息,将书籍信息添加进数据库中
'''
import flask
import re
import os
from tools import *
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)
app.debug = True
app.secret_key = os.urandom(16)
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
def index():
    '''
        请求路由为/,返回register页面
    '''
    if 'username' in flask.session and 'id' in flask.session:
        res = 'You are login'
        name = '{},'.format(flask.session['username'])
    else:
        res = 'You are not logged in'
        name = ''
    return flask.render_template('index.html', name=name, res=res)


@app.errorhandler(404)
def page_not_found(e):
    '''
        错误页面
    '''
    return flask.render_template('error/404.html'), 404


@app.errorhandler(500)
def server_internal_error(e):
    '''
        错误页面
    '''
    return flask.render_template('error/500.html'), 500


@app.errorhandler(405)
def method_not_found(e):
    '''
        错误页面
    '''
    return flask.render_template('error/405.html'), 405


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
                insert_db_res = insert_db(username, age, password)
                if insert_db_res[0] == 1:
                    resp = flask.make_response(flask.redirect('/users'))
                    resp.set_cookie('username', username)
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
            check_user_pass_res = check_user_pass(username, password)
            res = check_user_pass_res[0]
            if res == 1:
                id = check_user_pass_res[1]
                resp = flask.make_response(flask.redirect('/users'))
                resp.set_cookie('username', username)
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
    sql = 'select * from users where name = %s'
    params_list = [flask.session['username']]
    data = select_mysql(sql, params_list)
    if data:
        return flask.render_template('user/userinfo.html', id=data[0][0], name=data[0][1], age=data[0][2], password=data[0][3])
    else:
        return flask.redirect('/user/login')


@app.route('/user/logout', methods=['GET'])
@check_power
def logout():
    '''
        用户退出,删除seesion中的username
    '''
    flask.session.pop('username', None)
    flask.session.pop('id', None)
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
        if wraps_res:
            cartname = flask.request.form.get('cartname', default=None)
            price = flask.request.form.get('price', default=None)
            sql = 'insert into carts (userid,cartname,price) values (%s,%s,%s)'
            params_list = [flask.session['id'], cartname, price]
            err = update_mysql(sql, params_list)
            if err:
                return flask.render_template('cart/cart_info.html', res='添加失败')
            res = '购物车添加成功'
        else:
            res = '输入信息不能为空'
        return flask.render_template('cart/cart_info.html', res=res)
    elif flask.request.method == 'GET':
        return flask.render_template('cart/cart_info.html')


@app.route('/carts', methods=['GET', 'POST'])
@check_power
def carts():
    '''
        显示当前登录用户的购物车信息,check_power装饰器验证用户权限
        return:返回carts页面,用于显示用户购物车信息
    '''
    user_id = flask.session['id']
    sql = 'select cartid,cartname,price from carts where userid = %s'
    params_list = [user_id]
    data = select_mysql(sql, params_list)
    if data == encryption_string('select_data_err'):
        res = '查询信息失败'
        data = ''
    elif data:
        res = '{}用户的购物车'.format(flask.session['username'])
        data = data
    else:
        res = '当前购物车信息为空'
        data = ''
    return flask.render_template('cart/carts.html', res=res, data=data)


@app.route('/user/logoff', methods=['GET'])
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


@app.route('/cart/DELETE', methods=['GET'])
@check_power
def delete_carts():
    '''
        删除对应id的购物车信息,验证当前用户权限,获取url参数cartid,删除对应cartid数据
        return: 重定向到/carts
    '''
    cartid = flask.request.args.get('cartid', default=None)
    sql = 'delete from carts where cartid = %s'
    params_list = [cartid]
    err = update_mysql(sql, params_list)
    if err:
        return flask.render_template('cart/carts.html', res='删除失败')
    return flask.redirect('/carts')


@app.route('/user/UPDATE/userinfo', methods=['GET', 'POST'])
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
            res = check_update_res
        else:
            res = '输入信息不能为空'
        if res == 1:
            return flask.redirect('/user/login')
        else:
            return flask.render_template('user/update_passwd.html', res=res)


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
        return flask.render_template('cart/cart_update.html', carts='当前商品信息:{}, {}, {}'.format(cartid, cartname, price))
    if flask.request.method == 'POST':
        if wraps_res:
            carts = flask.request.form.get('carts', default=None)
            cartname = flask.request.form.get('cartname', default=None)
            price = flask.request.form.get('price', default=None)
            cartid = re.findall(':(.*?),', carts)[0]
            if not update_cart(cartid, cartname, price):
                carts = '当前商品信息:{}, {}, {}'.format(cartid, cartname, price)
                res = '修改成功'
            else:
                carts = carts
                res = '修改失败'
        else:
            carts = flask.request.form.get('carts')
            res = '当前输入信息为空'
        return flask.render_template('cart/cart_update.html', carts=carts, res=res)


@app.route('/files', methods=['GET', 'POST'])
@check_power
def file():
    '''
        显示上传文件页面,GET请求方式返回file/files.html
        return:返回file/files.html
    '''
    return flask.render_template('file/files.html')


@app.route('/file/upfile', methods=['GET', 'POST'])
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


@app.route('/books', methods=['GET'])
@check_power
def books():
    '''
        书籍信息,GET请求返回当前用户的书籍信息
    '''
    if flask.request.method == 'GET':
        userid = flask.session['id']
        book_data = select_book(userid)
        if book_data:
            books = book_data
            res = ''
        else:
            books = ''
            res = '当前书籍信息为空'
        return flask.render_template('book/books.html', books=books, res='当前书籍信息为空')


@app.route('/book/DELETE', methods=['GET'])
@check_power
def delete_book():
    '''
        删除书籍,根据选中书籍id删除数据库中的书籍信息
    '''
    sql = 'delete from books where id = %s'
    params_list = [flask.request.args.get('id')]
    err = update_mysql(sql, params_list)
    if err:
        return flask.render_template('book/books.html', res='删除失败')
    return flask.redirect('/books')


@app.route('/book/UPDATE', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['name', 'author'])
def update_book(wraps_res):
    '''
        修改用户书籍信息,GET请求返回book_update.html页面,传入data;POST请求修改数据,将用户输入的信息进行检测后传递给update_book_info函数,进行数据修改
        return:返回对应页面和信息
    '''
    if flask.request.method == 'GET':
        id = flask.request.args.get('id')
        name = flask.request.args.get('name')
        author = flask.request.args.get('author')
        return flask.render_template('book/book_update.html', res='{}用户的书籍信息'.format(flask.session['username']), data=(id, name, author))
    elif flask.request.method == 'POST':
        if not re.findall("'(.*?)'", flask.request.form.get('data')):
            data = flask.request.form.get('data')
            input = 'UnKnow Err'
        else:
            id = re.findall("'(.*?)'", flask.request.form.get('data'))[0]
            name = flask.request.form.get('name')
            author = flask.request.form.get('author')
            if wraps_res:
                if not update_book_info(id, name, author):
                    input = '修改成功'
                    data = (id, name, author)
                else:
                    input = '修改失败'
                    data = flask.request.form.get('data')
            else:
                input = '输入信息不能为空'
                data = flask.request.form.get('data')
        return flask.render_template('book/book_update.html', res='{}用户的书籍信息'.format(flask.session['username']), data=data, input=input)


@app.route('/book/ADD', methods=['GET', 'POST'])
@check_power
@check_input_wraps(['name', 'author'])
def add_book(wraps_res):
    '''
        添加书籍,GET请求返回book_info.html页面;POST请求获取用户输入的信息,调用add_book_info函数对数据进行处理
        params:wraps_res 1 用户输入信息验证通过 0 用户输入信息为空
        return:返回对应页面和对应信息
    '''
    if flask.request.method == 'GET':
        return flask.render_template('book/book_info.html', info='{}用户书籍信息'.format(flask.session['username']))
    elif flask.request.method == 'POST':
        if wraps_res:
            name = flask.request.form.get('name')
            author = flask.request.form.get('author')
            if not add_book_info(flask.session['id'], name, author):
                res = '添加成功'
            else:
                res = '添加失败'
        else:
            res = '输入信息不能为空'
        return flask.render_template('book/book_info.html', info='{}用户书籍信息'.format(flask.session['username']), res=res)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
