from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']=os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:python@127.0.0.1:3306/blog?charset=utf8"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.init_app(app)

    from app.admin import admin as admin_blueprint
    from app.home import home as home_blueprint

    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(home_blueprint)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("home/404.html"), 404

    return app
