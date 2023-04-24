from website.model import Game, UserGame, Platform, userinfo, db
import steam.webapi
from flask import flash
from datetime import datetime
import requests
import json

# rest of the code


api_key = "4A26AAF6AC8E26A257000E3F51E3AF2B"
steam_api = steam.webapi.WebAPI(api_key)

def get_player_achievements_count(steam_id, app_id, api_key):
    try:
        response = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={api_key}&steamid={steam_id}&format=json")
        response_data = response.json()

        if response_data.get('playerstats', {}).get('success', False):
            achievements = response_data['playerstats']['achievements']
            completed_achievements = [achievement for achievement in achievements if achievement['achieved'] == 1]
            completed_count = len(completed_achievements)
            total_count = len(achievements)
            percentage = round((completed_count / total_count) * 100, 2) if total_count else 0
            return completed_count, total_count, percentage
        else:
            return None, None, 0
    except Exception as e:
        print(f"Error fetching achievements: {str(e)}")
        return None, None, 0
    
def get_genre(app_id, api_key):
    try:
        response = requests.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}&key={api_key}&cc=us&l=en")
        response_data = response.json()

        if response_data.get(str(app_id), {}).get('success', False):
            app_data = response_data[str(app_id)]['data']
            genre = app_data.get('genres', [])
            genre_str = ', '.join([g['description'] for g in genre])
            return genre_str
        else:
            return ''
    except Exception as e:
        print(f"Error fetching genre: {str(e)}")
        return ''
      

def get_owned_games(platform_key):
    print("You made it here!")
    print(f"get_owned_games called with platform_key: {platform_key}")
    platform = Platform.query.filter_by(key=platform_key).first()
    if not platform:
        print(f"Platform not found for key: {platform_key}")
        return

    user_games = UserGame.query.filter_by(platform_id=platform.id).all()
    user_game_dict = {user_game.game_id: user_game for user_game in user_games}

    try:
        steam_id = platform.key
        print(f"Steam ID: {steam_id}")

        response = steam_api.call('IPlayerService.GetOwnedGames', steamid=steam_id, include_appinfo=1, include_played_free_games=1, include_free_sub=1, appids_filter=[], language='english', include_extended_appinfo=1)
        games = response['response']['games']

        exclude_keywords = ['dedicated server', 'win32', 'pc gamer', 'AMD drivers', 'AMD Driver Updater', 'Vista and 7', '32 bit', 'Dedicated Server - Win32', 'Dedicated Server - Linux']

        def is_game(name):
            for keyword in exclude_keywords:
                if keyword.lower() in name.lower():
                    print(f"Skipping game (keyword found): {name}")
                    return False
            return True

        for game in games:
            print(f"Processing game: {game['name']}")
            game_id = game['appid']
            name = game['name']

            if not is_game(game['name']):
                print(f"Skipping game (excluded keyword found): {game['name']}")
                continue

            playtime = game.get('playtime_forever', 0)

            # get last played time for game
            rtime_last_played = game.get('rtime_last_played', None)
            last_played = None
            if rtime_last_played:
                last_played = datetime.fromtimestamp(rtime_last_played)
                print(f"Last played for {name}: {last_played}")
                

            # Get the number of completed achievements for the game
            completed_achievements_count, total_achievements_count, completion_percentage = get_player_achievements_count(steam_id, game_id, api_key)
            

            # check if game with same external_id already exists
            existing_game = Game.query.filter_by(external_id=str(game_id)).first()

            if existing_game:
                # update attributes of existing game
                print(f"Updating existing game: {existing_game.name}")
                existing_game.genre = get_genre(game_id, api_key)
                existing_game.console = 'PC'
                existing_game.image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{existing_game.external_id}/header.jpg"
                existing_game.total_achievements = total_achievements_count  # Add this line
              
                # check for duplicate user_game
                existing_user_game = user_game_dict.get(existing_game.id)
                if existing_user_game:
                    # update existing user_game
                    existing_user_game.playtime = playtime
                    existing_user_game.last_played = last_played
                    existing_user_game.completion_percentage = completed_achievements_count
                else:
                    # create new user_game
                    print(f"Adding new game: {name}")
                    new_user_game = UserGame(platform_id=platform.id, game_id=existing_game.id, playtime=playtime, owned=True, user_id=platform.user_id, last_played=last_played, completion_percentage=completed_achievements_count)
                    db.session.add(new_user_game)

        # persist changes to the database
        db.session.commit()


        flash(f"Successfully retrieved {len(games)} owned games for platform {platform.key}", 'success')
        print(f"Retrieved games: {len(games)}")

    except Exception as e:
        db.session.rollback()
        flash(f"Failed to retrieve owned games for platform {platform.key}: {str(e)}", 'danger')
        
        






