from functools import wraps
import flask
import mysql.connector
import hashlib


def check_input_wraps(params_list):
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


def check_power(func):
    '''
        装饰器:验证用户权限,判断'username'是否存在于session中
        验证成功执行被装饰函数,验证失败重定向到/user/login
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in flask.session:
            return func(*args, **kwargs)
        else:
            return flask.redirect('/user/login')
    return wrapper


def check_user(username):
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
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'insert into students (name,age,password) values (%s,%s,%s)'
    try:
        cursor.execute(sql, [name, age, password])
        conn.commit()
        err = None
    except Exception as e:
        print(e)
        conn.rollback()
        err = e
    cursor.close()
    conn.close()
    if err:
        return 0
    else:
        return 1


def check_user_pass(username, password):
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


def check_update_passwd(old_password, new_password1, new_password2):
    '''
        检测用户输入的新旧密码是否符合条件
        return: 1 修改成功 2 查询用户失败 3 旧密码输入不正确 4 两次新密码输入不一致 5 修改密码失败 6 新密码和旧密码相同
    '''
    if new_password1 != new_password2:
        # 两次新密码不一致
        return 4
    old_password = encryption_string(old_password)
    if encryption_string(new_password1) == old_password:
        # 新旧密码相同
        return 6
    conn = mysql.connector.connect(
        host='127.0.0.1', user='root', passwd='123123', database='test')
    cursor = conn.cursor()
    sql = 'select password from students where name = %s'
    try:
        cursor.execute(sql, [flask.session['username']])
        password = cursor.fetchall()[0][0]
        if password == old_password:
            # 修改密码
            sql = 'update students set password = %s where name = %s'
            try:
                cursor.execute(sql, [encryption_string(
                    new_password1), flask.session['username']])
                conn.commit()
            except Exception as e:
                print(e)
                # 修改密码失败
                return 5
            cursor.close()
            conn.close()
            return 1
        else:
            # 密码不匹配
            return 3
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        # 查询用户失败
        return 2