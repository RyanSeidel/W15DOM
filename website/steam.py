from website.model import Platform, UserGame, Game, db
import steam.webapi
from flask import flash

api_key = "0969A678DCBE10BE0AA4B40204BFAAB2"
steam_api = steam.webapi.WebAPI(api_key)

def get_owned_games(platform_key):
    platform = Platform.query.filter_by(key=platform_key).first()
    if not platform:
        print(f"Platform not found for key: {platform_key}")
        return

    user_games = UserGame.query.filter_by(platform_id=platform.id).all()
    user_game_dict = {user_game.game_id: user_game for user_game in user_games}

    try:
        steam_id = platform.key
        response = steam_api.call('IPlayerService.GetOwnedGames', steamid=steam_id, include_appinfo=1, include_played_free_games=1, include_free_sub=1, appids_filter=[], language='english', include_extended_appinfo=1)
        games = response['response']['games']

        exclude_keywords = ['dedicated server', 'win32', 'pc gamer', 'AMD drivers', 'AMD Driver Updater', 'Vista and 7', '32 bit', 'Dedicated Server - Win32', 'Dedicated Server - Linux']

        def is_game(name):
            for keyword in exclude_keywords:
                if keyword.lower() in name.lower():
                    return False
            return True

        for game in games:
            game_id = game['appid']
            name = game['name']

            if not is_game(name):
                continue

            playtime = game.get('playtime_forever', 0)

            # check if game with same external_id already exists
            existing_game = Game.query.filter_by(external_id=game_id).first()

            if existing_game:
                # update attributes of existing game
                existing_game.genre = game.get('genre', '')
                existing_game.console = 'PC'
                existing_game.image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{existing_game.external_id}/header.jpg"

                # check for duplicate user_game
                existing_user_game = user_game_dict.get(existing_game.id)
                if existing_user_game:
                    # update existing user_game
                    existing_user_game.playtime = playtime
                else:
                    # create new user_game
                    new_user_game = UserGame(platform_id=platform.id, game_id=existing_game.id, playtime=playtime, owned=True, user_id=platform.user_id)
                    db.session.add(new_user_game)
            else:
                # create new game
                new_game = Game(user_id=platform.user_id, name=name, platform_id=platform.id, genre=game.get('genre', ''), console='PC', completed=False, recommend=False, external_id=game_id)
                new_game.image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{new_game.external_id}/header.jpg"
                db.session.add(new_game)
                db.session.flush()

                # check for duplicate user_game
                existing_user_game = user_game_dict.get(new_game.id)
                if existing_user_game:
                    # update existing user_game
                    existing_user_game.playtime = playtime
                else:
                    # create new user_game
                    new_user_game = UserGame(platform_id=platform.id, game_id=new_game.id, playtime=playtime, owned=True, user_id=platform.user_id)
                    db.session.add(new_user_game)

        db.session.commit()
        flash(f"Successfully retrieved {len(games)} owned games for platform {platform.key}", 'success')
        print(f"Retrieved games: {len(games)}")

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to retrieve owned games for platform {platform.key}: {str(e)}", 'danger')




