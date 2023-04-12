from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from website.model import db, userinfo, Game, UserGame, Platform
from website.steam import steam_api, api_key, get_owned_games
import requests


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = userinfo.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect email or password', category='error')

    return render_template('login.html')


@auth.route('/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        if not email or not name or not password:
            flash('Please fill in all the fields', category='error')
            return redirect(url_for('auth.signup'))

        user = userinfo.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        else:
            new_user = userinfo(email=email, name=name, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
            return redirect(url_for('auth.login'))

    return render_template('index.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')


@auth.route('/vgarchive', methods=['GET', 'POST'])
@login_required
def vgarchive():
    if request.method == 'POST':
        name = request.form.get('name')
        genre = request.form.get('genre')
        console = request.form.get('console')
        completed = 'completed' in request.form
        recommend = 'recommend' in request.form

        new_game = Game(user_id=current_user.get_id(), name=name, genre=genre, console=console, completed=completed, recommend=recommend)
        db.session.add(new_game)
        db.session.commit()

        flash('Game added successfully', category='success')
        return redirect(url_for('auth.vgarchive'))

    games = Game.query.filter_by(user_id=current_user.get_id()).all()
    return render_template('vgarchive.html', games=games)

@auth.route('/add_game', methods=['POST'])
@login_required
def add_game():
    data = request.get_json()
    name = data['name']
    genre = data['genre']
    console = data['console']
    completed = data['completed']
    recommend = data['recommend']
    
    game = Game(user_id=current_user.id, name=name, genre=genre, console=console, completed=completed, recommend=recommend)
    db.session.add(game)
    db.session.commit()
    return jsonify({"success": True})

@auth.route('/get_game/<int:game_id>', methods=['GET'])
@login_required
def get_game(game_id):
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()
    if game:
        game_data = {
            'id': game.id,
            'name': game.name,
            'genre': game.genre,
            'console': game.console,
            'completed': game.completed,
            'recommend': game.recommend
        }
        return jsonify({"game": game_data, "success": True})
    else:
        return jsonify({"success": False})

@auth.route('/update_game/<int:game_id>', methods=['PUT'])
@login_required
def update_game(game_id):
    data = request.get_json()
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()
    if game:
        game.name = data['name']
        game.genre = data['genre']
        game.console = data['console']
        game.completed = data['completed']
        game.recommend = data['recommend']
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@auth.route('/delete_game/<int:game_id>', methods=['DELETE'])
@login_required
def delete_game(game_id):
    game = Game.query.filter_by(id=game_id, user_id=current_user.id).first()
    if game:
        db.session.delete(game)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
@auth.route('/get_games', methods=['GET'])
@login_required
def get_games():
    steam_id = session.get('steam_user', {}).get('steamid')
    if steam_id:
        get_owned_games(steam_id)
        db.session.commit() # wait for get_owned_games to complete
        games = Game.query.join(Platform).filter_by(key=steam_id).all()
        games = [{'id': game.id, 'name': game.name, 'genre': game.genre, 'console': game.console, 'completed': game.completed, 'recommend': game.recommend} for game in games]
    else:
        games = Game.query.filter_by(user_id=current_user.get_id()).all()
        games = [{'id': game.id, 'name': game.name, 'genre': game.genre, 'console': game.console, 'completed': game.completed, 'recommend': game.recommend} for game in games]
    return jsonify(games)


@auth.route('/add_user_game', methods=['POST'])
@login_required
def add_user_game():
    data = request.get_json()

    game_id = data['game_id']
    platform_id = data['platform_id']
    user_id = current_user.get_id()

    existing_user_game = UserGame.query.filter_by(game_id=game_id, platform_id=platform_id, user_id=user_id).first()

    if existing_user_game is None:
        new_user_game = UserGame(game_id=game_id, platform_id=platform_id, user_id=user_id)
        db.session.add(new_user_game)

        db.session.commit()

        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@auth.route('/remove_user_game', methods=['DELETE'])
@login_required
def remove_user_game():
    data = request.get_json()
    game_id = data['game_id']
    platform_id = data['platform_id']
    user_game = UserGame.query.filter_by(user_id=current_user.id, game_id=game_id, platform_id=platform_id).first()
    if user_game:
        db.session.delete(user_game)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "User game does not exist"})

@auth.route('/get_user_games', methods=['GET'])
@login_required
def get_user_games():
    user_games = UserGame.query.filter_by(user_id=current_user.id).all()
    games = []
    for user_game in user_games:
        game = user_game.game
        platform = user_game.platform
        games.append({
            'id': user_game.id,
            'name': game.name,
            'genre': game.genre,
            'console': game.console,
            'completed': user_game.completed,
            'recommend': user_game.recommend,
            'platform': platform.name,
            'platform_id': platform.key
        })
    return jsonify(games)


@auth.route('/delete_user_game/<int:user_game_id>', methods=['DELETE'])
@login_required
def delete_user_game(user_game_id):
    user_game = UserGame.query.filter_by(id=user_game_id, user_id=current_user.id).first()
    if user_game:
        db.session.delete(user_game)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@auth.route("/steam_login")
def steam_login():
    return redirect(f"https://steamcommunity.com/openid/login?openid.ns=http://specs.openid.net/auth/2.0&openid.mode=checkid_setup&openid.return_to={url_for('auth.authorized', _external=True)}&openid.realm={request.host_url}&openid.ns.sreg=http://openid.net/extensions/sreg/1.1&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.identity=http://specs.openid.net/auth/2.0/identifier_select")

@auth.route("/authorized")
@login_required
def authorized():
    steam_id = request.args.get("openid.identity").split("/")[-1]
    session["steam_user"] = {"steamid": steam_id}

    # Get the current user from the database
    user = current_user

    # Check if a platform with the given steam_id already exists for the user
    existing_platform = Platform.query.filter_by(user_id=user.id, name='Steam').first()

    if existing_platform is None:
        # Create a new platform object and add it to the user's list of connected platforms
        platform = Platform(name='Steam', user_id=user.id, connected=True, key=steam_id)
        user.platforms.append(platform)
    else:
        # Update the existing platform with the new values
        existing_platform.connected = True
        existing_platform.key = steam_id
        
        # Set a session variable to remember that the user has connected their Steam account
        session["steam_connected"] = existing_platform.connected

    db.session.commit()

    # Call the function to retrieve user's owned games from Steam API
    if existing_platform.connected:
        get_owned_games(platform_key=existing_platform.key)

    return redirect(url_for("views.account"))


@auth.route('/steam_disconnect', methods=['POST'])
@login_required
def steam_disconnect():
    session.pop('steam_user', None)
    flash('You have successfully disconnected your Steam account.', category='success')
    return redirect(url_for('views.account'))






















