from flask import Flask
import os


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.secret_key = os.urandom(16)
    # 注册蓝图
    from app.user import user as user_blueprint
    from app.cart import cart as cart_blueprint
    from app.book import book as book_blueprint
    from app.files import files as files_blueprint
    from app.weibo import weibo as weibo_blueprint
    app.register_blueprint(user_blueprint)
    app.register_blueprint(cart_blueprint)
    app.register_blueprint(book_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(weibo_blueprint)

    return app

