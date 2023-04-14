from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website.model import Game, UserGame, Platform, db
from .forms import SearchForm
import difflib

# Creating a Blueprint for views
views = Blueprint('views', __name__)

# Route for the index page
@views.route('/')
def index():
    return render_template('index.html')

# Route for the home page, handling both GET and POST requests
import difflib
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from website.model import Game, UserGame, Platform, db
from .forms import SearchForm

# Creating a Blueprint for views
views = Blueprint('views', __name__)

# Route for the home page, handling both GET and POST requests
@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = SearchForm()
    filter_choices = [(field, field.capitalize()) for field in Game.__table__.columns.keys()]
    form.search_filter.choices = filter_choices

    # Querying for user's games ordered by playtime in descending order
    all_games = Game.query\
    .join(UserGame, Game.id == UserGame.game_id)\
    .filter(UserGame.user_id == current_user.id)\
    .with_entities(Game, UserGame.playtime)\
    .order_by(UserGame.playtime.desc().nullslast(), Game.name)\
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
def get_games():
    # Fetch the games from the database
    games = Game.query.all()

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
    game = Game.query.get_or_404(game_id)
    return jsonify({'game': game.to_dict()})


@views.route('/update_game/<int:game_id>', methods=['POST'])
@login_required
def update_game(game_id):
    # Fetch the game from the database
    game = Game.query.get_or_404(game_id)

    # Update the game with the new data
    game.completed = 'completed' in request.form
    game.recommend = 'recommend' in request.form

    # Save the updated game to the database
    db.session.commit()

    # Redirect to the archive page
    flash('Game updated successfully', category='success')
    return redirect(url_for('views.archive'))


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

    games = Game.query.filter_by(user_id=current_user.get_id()).all()
    return render_template("vgarchive.html", games=games)

@views.route('/add_game', methods=['POST'])
@login_required
def add_game():
    data = request.get_json()
    name = data.get('name')
    genre = data.get('genre')
    console = data.get('console')
    completed = data.get('completed')
    recommend = data.get('recommend')

    # check if a game with the same name already exists
    existing_game = Game.query.filter_by(name=name).first()
    if existing_game:
        # game with same name already exists
        return jsonify({'success': False, 'error': 'Game with same name already exists'})

    # create a new game and add to the database
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

# Route for the message page
@views.route('/message')
@login_required
def message():
    return render_template("message.html")

@views.route('/account')
@login_required
def account():
    return render_template('account.html')
