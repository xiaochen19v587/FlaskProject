'''
/files                  GET:返回files.html页面
/file/upfile            GET:返回files.html页面                          POST:处理用户上传文件
'''

import flask
import os
from . import weibo
from app.tools import *
from app.spiders import *


@weibo.route('/weibo', methods=['GET'])
@check_power
def weibo():
    '''
        微博热搜,返回weibo/weibo.html页面,调用spiders.py中的spi_weibo函数对微博热搜榜进行爬去生成列表
        return:返回对应页面和hot_data
    '''
    hot_data = []
    url = 'https://s.weibo.com/top/summary'
    hot_list = spi_weibo(url)
    if hot_list:
        for i in range(4, len(hot_list)-11):
            hot_url = hot_list[i][0].split(' ')[0]
            hot_url = 'https://s.weibo.com'+hot_url[1:-1]
            hot_name = hot_list[i][1]
            hot_data.append((hot_url, hot_name))
        return flask.render_template('weibo/weibo.html', res='微博热搜', hot_data=hot_data)
    else:
        return flask.render_template('weibo/weibo.html', res='结果为空')
