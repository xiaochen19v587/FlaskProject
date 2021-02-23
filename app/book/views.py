'''
/books                  GET:返回books.html页面
/book/DELETE            GET:删除用户书籍信息
/book/UPDATE            GET:返回book_update.html页面                    POST:处理用户输入信息,对书籍数据进行修改
/book/ADD               GET:返回book_info.html页面                      POST:处理用户输入信息,将书籍信息添加进数据库中
'''
import flask
import re
from . import book
from app.tools import *


@book.route('/books', methods=['GET'])
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
            res = '{}用户的书籍信息:'.format(flask.session['username'])
        else:
            books = ''
            res = '当前书籍信息为空'
        return flask.render_template('book/books.html', books=books, res=res)


@book.route('/book/DELETE', methods=['GET'])
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


@book.route('/book/UPDATE', methods=['GET', 'POST'])
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
            input_res = 'UnKnow Err'
        else:
            id = re.findall("'(.*?)'", flask.request.form.get('data'))[0]
            name = flask.request.form.get('name')
            author = flask.request.form.get('author')
            if wraps_res:
                if not update_book_info(id, name, author):
                    input_res = '修改成功'
                    data = (id, name, author)
                else:
                    input_res = '修改失败'
                    data = flask.request.form.get('data')
            else:
                input_res = '输入信息不能为空'
                data = flask.request.form.get('data')
        return flask.render_template('book/book_update.html', res='{}用户的书籍信息'.format(flask.session['username']), data=data, input=input_res)


@book.route('/book/ADD', methods=['GET', 'POST'])
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
