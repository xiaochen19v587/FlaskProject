from app import create_app
import flask

app = create_app()

@app.route('/', methods=['GET'])
def index():
    '''
        请求路由为/,返回register页面
    '''
    if flask.request.cookies.get('username'):
        if 'username' in flask.session and 'id' in flask.session:
            res = 'You are login'
            name = '{},'.format(flask.session['username'])
        else:
            res = 'You are not logged in'
            name = ''
    else:
        if 'username' in flask.session and 'id' in flask.session:
            res = "The login has expired"
            name = ''
        else:
            res = 'You are not logged in'
            name = ''
    return flask.render_template('index.html', name=name, res=res)


@app.errorhandler(404)
def page_not_found(e):
    '''
        404错误页面
    '''
    return flask.render_template('error/404.html'), 404


@app.errorhandler(500)
def server_internal_error(e):
    '''
        505错误页面
    '''
    return flask.render_template('error/500.html'), 500


@app.errorhandler(405)
def method_not_found(e):
    '''
        405错误页面
    '''
    return flask.render_template('error/405.html'), 405


if __name__ == '__main__':
    app.run()
