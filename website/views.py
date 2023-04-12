from flask import Blueprint, render_template, request, session
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
    all_games = Game.query.outerjoin(UserGame, (UserGame.user_id == current_user.id) & (UserGame.game_id == Game.id))\
                       .with_entities(Game, UserGame.playtime)\
                       .order_by(UserGame.playtime.desc().nullslast(), Game.name).all()


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
@views.route('/archive')
@login_required
def archive():
    return render_template("vgarchive.html")

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
