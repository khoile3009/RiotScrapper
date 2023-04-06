from database.mongo_database import MongoDBClient
from riot_api import RiotAPI
from database.mock_database import MockDatabase
from database.mock_data_model import Match, Player


def add_players_to_database_from_name(name, mongodb_client: MongoDBClient):
    response = RiotAPI().get_player_info_from_name(name)
    mongodb_client.insert_player(response)


def get_all_players_with_history_not_updated(connection):
    """Get all players from database where the last time we fetched match history is more than 30 days/patches"""
    cursor = connection.cursor()
    cursor.execute(
        """
                select 
                    puuid,
                    last_fetched_match_history,
                    JULIANDAY('now') - JULIANDAY(last_fetched_match_history) as days_since_last_fetch
                from player
                where days_since_last_fetch > 30
                order by days_since_last_fetch DESC
               """
    )
    player_response = cursor.fetchall()
    players = [
        {"puuid": player[0], "last_fetched": player[1]} for player in player_response
    ]
    cursor.close()
    return players


def add_match_id_to_database(match_id, connection):
    match = Match.from_match_id(match_id)
    match.save(connection)


def add_puuid_to_database(puuid, connection):
    player = Player.from_puuid(puuid)
    player.save(connection)


def add_player_history(player, client: MongoDBClient):
    """
    Add a list of player's matches
    TODO: Pagination
    """
    match_history = RiotAPI().get_match_history_from_puuid(
        player["_id"], player["last_updated"]
    )
    client.insert_match_ids(match_history)
    client.update_player_last_update(player["_id"])


def update_all_match_history(client: MongoDBClient):
    players = client.get_not_updated_players()
    for player in players:
        add_player_history(player, client)


def get_null_matches(connection):
    """TODO: Remove limit
    Get list of ids of matches that we doesnt update info yet
    """
    cursor = connection.cursor()
    cursor.execute(
        """
               select id 
               from match
               where game_version is null
               limit 10
               """
    )
    result = cursor.fetchall()
    return [match[0] for match in result]


def get_participant_from_match(match):
    return match["metadata"]["participants"]


def add_match_information(match_id, client: MongoDBClient):
    response = RiotAPI().get_match_info_from_match_id(match_id)
    client.update_match(response)
    puuids = response["metadata"]["participants"]
    client.insert_player_puuids(puuids)


def update_all_null_matches(client: MongoDBClient):
    match_ids = client.get_match_ids_with_no_data()
    for match_id in match_ids:
        add_match_information(match_id, client)


def add_player_information(puuid, client: MongoDBClient):
    response = RiotAPI().get_player_info_from_puuid(puuid)
    client.update_player(response)


def update_info_for_player_with_no_info(client: MongoDBClient):
    puuids = client.get_puuids_with_no_data()
    for puuid in puuids:
        add_player_information(puuid, client)
