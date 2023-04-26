from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from website.model import Game, UserGame, Platform, userinfo, db
from .forms import SearchForm
from website.steam import get_owned_games
from sqlalchemy import func, desc, case
from sqlalchemy.orm import joinedload, contains_eager, load_only
import difflib
import ast


# Creating a Blueprint for views
views = Blueprint('views', __name__)

# Route for the index page
@views.route('/')
def index():
    return render_template('index.html')

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = SearchForm()
    filter_choices = [(field, field.capitalize()) for field in Game.__table__.columns.keys()]
    form.search_filter.choices = filter_choices

    # Querying for user's games ordered by playtime in descending order
    all_games = Game.query \
    .outerjoin(UserGame, (Game.id == UserGame.game_id) & (UserGame.user_id == current_user.id)) \
    .filter((UserGame.user_id == current_user.id) | (Game.user_id == current_user.id)) \
    .with_entities(Game, UserGame.playtime, UserGame.last_played, UserGame.completion_achievements, Game.total_achievements) \
    .order_by(UserGame.playtime.desc().nullslast(), Game.name) \
    .all()

    games = all_games
    search_string = ''  # Initialize the search_string variable

    # Check if the form is submitted
    if request.method == 'POST':
        if form.submit.data:
            # Extracting the search filter and the search string from the form
            search_filter = form.search_filter.data.lower() if form.search_filter.data else None
            search_string = form.search.data.lower()

            # Filtering the games based on the search filter and the search string
            if search_filter and search_string:
                games = [(game, playtime) for game, playtime in all_games if search_string in str(getattr(game, search_filter)).lower()]
            elif search_string:
                games = [(game, playtime) for game, playtime in all_games if search_string in game.name.lower()]
            else:
                games = all_games


        # Check if the 'show all' button is clicked
        elif 'show-all-btn' in request.form:
            form.search.data = ''
            games = all_games
            session['show_games'] = True
        elif 'toggle-games-btn' in request.form:
            session['show_games'] = not session.get('show_games', True)

    # Set the session variable to True by default
    session.setdefault('show_games', True)

    # Render the home template with the appropriate data
    return render_template('home.html', form=form, username=current_user.name, games=games, search_string=search_string)


@views.route('/get_games')
@login_required
def get_games():
    # Fetch the games belonging to the current user from the database
    games = Game.query.filter_by(user_id=current_user.id).all()

    # Convert the games to a list of dictionaries
    game_list = []
    for game in games:
        game_dict = {
            'id': game.id,
            'name': game.name,
            'genre': game.genre,
            'console': game.console,
            'completed': game.completed,
            'recommend': game.recommend,
            'completed': game.completed
        }
        game_list.append(game_dict)

    # Return the games as JSON
    return jsonify({'games': game_list})


@views.route('/delete_game/<int:game_id>', methods=['DELETE'])
@login_required
def delete_game(game_id):
    # Fetch the game from the database
    game = Game.query.get_or_404(game_id)

    # Delete user-game association rows
    UserGame.query.filter_by(game_id=game_id).delete()

    # Delete the game
    db.session.delete(game)
    db.session.commit()

    # Return a JSON response indicating success
    return jsonify({'success': True}), 200


@views.route('/get_game/<int:game_id>', methods=['GET'])
@login_required
def get_game(game_id):
    # Fetch the game from the database
    game = Game.query.get_or_404(game_id)

    # Check if the game belongs to the current user
    if game.user_id != current_user.id:
        return jsonify({'error': 'You are not authorized to view this game.'}), 403

    # Return the game as a JSON object
    return jsonify({'game': game.to_dict()})


@views.route('/update_game/<int:game_id>', methods=['POST'])
@login_required
def update_game(game_id):
    # Fetch the game from the database
    game = Game.query.get_or_404(game_id)

    # Check if the game belongs to the current user
    if game.user_id != current_user.id:
        flash('You do not have permission to update this game', category='error')
        return redirect(url_for('views.archive'))

    # Update the game with the new data
    game.completed = request.form.get('completed') == 'true'
    game.recommend = request.form.get('recommend') == 'true'

    print('game.completed: ', game.completed)
    print('game.recommend: ', game.recommend)

    # Save the changes to the database
    db.session.commit()

    # Return a JSON response indicating success
    return jsonify({'success': True}), 200


# Route for the games page
@views.route('/games')
@login_required
def games():
    return render_template("games.html")

# Route for the settings page
@views.route('/settings')
@login_required
def settings():
    return render_template("settings.html")

# Route for the archive page
@views.route('/archive', methods=['GET', 'POST'])
@login_required
def archive():
    recommend = None  # Define the variable before it's used

    if request.method == 'POST':
        name = request.form.get('name')
        genre = request.form.get('genre')
        console = request.form.get('console')
        completed = 'completed' in request.form
        recommend = 'recommend' in request.form

        new_game = Game(user_id=current_user.get_id(), name=name, genre=genre,
                        console=console, completed=completed, recommend=recommend)
        db.session.add(new_game)
        db.session.commit()

        flash('Game added successfully', category='success')

    games = Game.query.filter_by(user_id=current_user.id).all()
    return render_template("vgarchive.html", games=games, recommend=recommend)


@views.route('/add_game', methods=['POST'])
@login_required
def add_game():
    data = request.get_json()
    name = data.get('name')
    genre = data.get('genre')
    console = data.get('console')
    completed = data.get('completed')
    recommend = data.get('recommend')

    # check if a game with the same name already exists for this user
    existing_game = Game.query.filter_by(user_id=current_user.get_id(), name=name).first()
    if existing_game:
        # game with same name already exists for this user
        return jsonify({'success': False, 'error': 'You have already added a game with this name'})

    # create a new game and add to the database
    platform_name = data.get('platform')
    if platform_name:
        platform = Platform.query.filter_by(user_id=current_user.get_id(), name=platform_name).first()
        if not platform:
            return jsonify({'success': False, 'error': 'Platform not found'})
        new_game = Game(user_id=current_user.get_id(), name=name, genre=genre,
                        console=console, completed=completed, recommend=recommend, platform=platform)
    else:
        new_game = Game(user_id=current_user.get_id(), name=name, genre=genre,
                        console=console, completed=completed, recommend=recommend)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({'success': True})

# Route for the help page
@views.route('/help')
@login_required
def help():
    return render_template('help.html')

# Route for the leaderboard page
@views.route('/leaderboard')
@login_required
def leaderboard():
    games = (db.session.query(Game.name, Game.image_url, func.sum(UserGame.playtime).label('total_playtime'),
                          func.sum(case((Game.recommend == True, 1), else_=0)).label('total_likes'),
                          func.sum(case((Game.recommend == False, 1), else_=0)).label('total_dislikes'))
             .join(Game.user_games)
             .filter(UserGame.playtime != None)
             .group_by(Game.id)
             .order_by(desc('total_playtime'))
             .limit(5)
             .all())


    return render_template('leaderboard.html', games=games)


@views.route('/import_games', methods=['POST'])
@login_required
def import_games():
    platform = db.session.query(Platform).options(load_only(Platform.key)).filter_by(user_id=current_user.id, name='Steam').first()
    if platform:
        get_owned_games(platform.key)
        return redirect(url_for('views.account'))
    else:
        flash('Steam platform not found for current user', 'warning')
        return redirect(url_for('views.account'))












