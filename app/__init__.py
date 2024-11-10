from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workhours.db'

    db.init_app(app)

    from .routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()
        # 檢查是否需要建立預設設定
        from .models import Settings
        if not Settings.query.first():
            default_settings = Settings()
            db.session.add(default_settings)
            db.session.commit()

    return app
