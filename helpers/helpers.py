from riot_api import RiotAPI
from database.mock_database import MockDatabase
from database.mock_data_model import Match, Player

def add_players_to_database_from_name(name, connection):
    response = RiotAPI().get_player_info_from_name(name)
    player = Player.from_riot_response(response)
    player.save(connection)
    
def get_all_players_with_history_not_updated(connection):
    """ Get all players from database where the last time we fetched match history is more than 30 days/patches"""
    cursor = connection.cursor()
    cursor.execute("""
                select 
                    puuid,
                    last_fetched_match_history,
                    JULIANDAY('now') - JULIANDAY(last_fetched_match_history) as days_since_last_fetch
                from player
                where days_since_last_fetch > 30
                order by days_since_last_fetch DESC
               """)
    player_response = cursor.fetchall()
    players = [{"puuid": player[0], "last_fetched": player[1]} for player in player_response]
    cursor.close()
    return players

def add_match_id_to_database(match_id, connection):
    match = Match.from_match_id(match_id)
    match.save(connection)

def add_puuid_to_database(puuid, connection):
    player = Player.from_puuid(puuid)
    player.save(connection)
    
def add_player_history(player, connection):
    """Add a list of players"""
    match_history = RiotAPI().get_match_history_from_puuid(player["puuid"], player["last_fetched"])
    for match_id in match_history:
        add_match_id_to_database(match_id, connection)

def update_all_match_history(connection):
    players = get_all_players_with_history_not_updated(connection)
    for player in players:
        add_player_history(player, connection)

def get_null_matches(connection):
    """ TODO: Remove limit
        Get list of ids of matches that we doesnt update info yet
    """
    cursor = connection.cursor()
    cursor.execute("""
               select id 
               from match
               where game_version is null
               limit 10
               """
               )
    result = cursor.fetchall()
    return [match[0] for match in result]

def add_match_information(match_id, connection):
    response = RiotAPI().get_match_info_from_match_id(match_id)
    match = Match.from_riot_response(response)
    match.save(connection)
    puuids = match.get_participant_puuids()
    for puuid in puuids:
        add_puuid_to_database(puuid, connection)
    
def update_all_null_matches(connection):
    match_ids = get_null_matches(connection)
    for match_id in match_ids:
        add_match_information(match_id, connection)
    
def update_info_for_player_with_no_info(name, connection):
    pass