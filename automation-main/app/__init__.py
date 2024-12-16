from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='../static', 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))
    app.config.from_object(Config)

    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    setup_logging(app)

    from app.routes import bp
    app.register_blueprint(bp)

    return app

def setup_logging(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/flask.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask startup')
