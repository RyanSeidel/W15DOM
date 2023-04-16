from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, make_response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from website.model import db, userinfo, Game, UserGame, Platform
from website.steam import steam_api, api_key, get_owned_games
import requests
from sqlalchemy import exists, and_


auth = Blueprint('auth', __name__)


#  Login Feature 
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

# Registration Feature
@auth.route('/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')

        if not email or not name or not password:
            flash('Please fill in all the fields', category='error')
            return redirect(url_for('auth.signup'))

        user_email = userinfo.query.filter_by(email=email).first()
        if user_email:
            flash('Email already exists', category='error')
            return jsonify({'message': 'error',
                            'value': 'Email already in use'})

        user_name = userinfo.query.filter_by(name=name).first()
        if user_name:
            flash('Username already exists', category='error')
            return jsonify({'message': 'error',
                            'value': 'Username already in use'})

        new_user = userinfo(email=email, name=name, password=generate_password_hash(
            password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created', category='success')
        # return redirect(url_for('auth.login'))
        return jsonify({'message': 'success',
                        'value': 'login'})

    return render_template('index.html')

# Logout Feature
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

# Get all games
@auth.route('/get_all_games', methods=['GET'])
@login_required
def get_all_games():
    games = Game.query.filter_by(user_id=current_user.get_id()).all()
    games = [{'id': game.id, 'name': game.name, 'genre': game.genre, 'console': game.console,
              'completed': game.completed, 'recommend': game.recommend} for game in games]
    return jsonify(games)


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
    existing_platform = Platform.query.filter_by(
        user_id=user.id, name='Steam').first()

    if existing_platform is None:
        # Create a new platform object and add it to the user's list of connected platforms
        platform = Platform(name='Steam', user_id=user.id,
                            connected=True, key=steam_id)
        db.session.add(platform)
        user.platforms.append(platform)
    else:
        # Update the existing platform with the new values
        existing_platform.connected = True
        existing_platform.key = steam_id

        # Set a session variable to remember that the user has connected their Steam account
        session["steam_connected"] = existing_platform.connected

    # Call the function to retrieve user's owned games from Steam API
    get_owned_games(platform_key=steam_id)

    # Commit the changes to the database
    db.session.commit()

    return redirect(url_for("views.account"))

@auth.route('/steam_disconnect', methods=['POST'])
@login_required
def steam_disconnect():
    # Get the current user from the database
    user = current_user

    # Get the platform to disconnect
    platform = Platform.query.filter_by(user_id=user.id, name='Steam').first()

    if platform:
        # Delete all games associated with the platform
        for game in platform.games:
            UserGame.query.filter_by(game_id=game.id).delete()
            db.session.delete(game)

        # Delete the platform
        db.session.delete(platform)
        db.session.commit()

        flash(f"You have successfully disconnected from the {platform.name} platform.", category='success')
    else:
        flash('You are not currently connected to the Steam platform.', category='danger')

    return redirect(url_for('views.account'))
