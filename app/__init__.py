from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workhours.db'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

    db.init_app(app)

    @app.route('/static/<path:filename>')
    def static_files(filename):
        response = send_from_directory(app.static_folder, filename)
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
        response.headers['Vary'] = 'Accept-Encoding'
        return response

    from .routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()
        from .models import Settings
        if not Settings.query.first():
            default_settings = Settings()
            db.session.add(default_settings)
            db.session.commit()

    return app
