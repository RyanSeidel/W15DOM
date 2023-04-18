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
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userinfo.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    genre = db.Column(db.String(100))
    console = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    recommend = db.Column(db.Boolean, default=None, nullable = True)
    external_id = db.Column(db.String(100))
    image_url = db.Column(db.String(200))


    platform = db.relationship('Platform', backref=db.backref('games', lazy=True))

    def __repr__(self):
        return f"Game('{self.name}', '{self.platform.name if self.platform else None}', '{self.console}', '{self.completed}', '{self.recommend}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'platform': self.platform.name if self.platform else None,
            'genre': self.genre,
            'console': self.console,
            'completed': self.completed,
            'recommend': self.recommend,
            'external_id': self.external_id,
            'image_url': self.image_url  # add to_dict support for new column
        }

    
    @staticmethod
    def add_game(user_id, name, platform_id, genre, console, completed, recommend, external_id):
        existing_game = Game.query.filter_by(user_id=user_id, name=name).first()
        if existing_game:
            # game with same name already exists for this user
            return False

        new_game = Game(user_id=user_id, name=name, platform_id=platform_id, genre=genre,
                        console=console, completed=completed, recommend=recommend, external_id=external_id)
        db.session.add(new_game)
       
