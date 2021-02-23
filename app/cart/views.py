'''
/carts                  GET:返回carts.html页面,显示用户购物车中的信息
/cart/ADD               GET:返回cart/cart_info.html                     POST:处理用户输入信息将信息插入到数据库中
/cart/DELETE            GET:重定向到/carts,删除对应id的购物车信息
/cart/UPDATE            GET:
'''

import flask
import re
from . import cart
from app.tools import *


@cart.route('/cart/ADD', methods=['GET', 'POST'])
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


@cart.route('/carts', methods=['GET', 'POST'])
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


@cart.route('/cart/DELETE', methods=['GET'])
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


@cart.route('/cart/UPDATE', methods=['GET', 'POST'])
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
