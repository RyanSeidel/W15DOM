from flask import Flask, render_template
from website.views import views
from website.auth import auth
from flask_login import LoginManager
from website.model import Game, UserGame, Platform, userinfo, RatingEnum, db
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import steam.webapi

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:4dUPuSxKvWdh3FiCycIg@containers-us-west-202.railway.app:6607/railway'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['STEAM_API_KEY'] = '0969A678DCBE10BE0AA4B40204BFAAB2'

    app.steam_api = steam.webapi.WebAPI(app.config['STEAM_API_KEY'])

    db.init_app(app)

    app.register_blueprint(views)
    app.register_blueprint(auth)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    migrate = Migrate(app, db)

    return app



def init_db(app):
    with app.app_context():
        db.create_all()
        inspector = db.engine.dialect.inspector(db.engine)
        tables = inspector.get_table_names()
        print(tables)

@login_manager.user_loader
def load_user(user_id):
    return userinfo.query.get(int(user_id))
