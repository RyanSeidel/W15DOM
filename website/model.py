from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class userinfo(db.Model, UserMixin):
    __tablename__ = 'userinfo'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    platforms = db.relationship('Platform', backref='userinfo', lazy=True)
    user_games = db.relationship('UserGame', backref='user', lazy=True)
    
    def has_platform(self, platform_name):
        for platform in self.platforms:
            if platform.name == platform_name:
                return True
        return False



class Platform(db.Model):
    __tablename__ = 'platform'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    connected = db.Column(db.Boolean, default=False)
    key = db.Column(db.String(100), nullable=False)


class UserGame(db.Model):
    __tablename__ = 'user_game'

    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id', ondelete='CASCADE'), nullable=True)
    playtime = db.Column(db.Integer, nullable=True)
    owned = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'), nullable=False)
    
    game = db.relationship('Game', backref='user_games')

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    console = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    recommend = db.Column(db.Boolean, default=False)
    external_id = db.Column(db.Integer, nullable=False)
    platform = db.relationship('Platform', backref=db.backref('games', lazy=True))





