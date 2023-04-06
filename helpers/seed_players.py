from database.mongo_database import MongoDBClient
from helpers.helpers import add_players_to_database_from_name
from riot_api import RiotAPI

# TODO(khoi): Move this to a file, puuid instead of name since name can be changed
SEED_PLAYERS = ["scarria", "3K3K", "MediumSteak", "aaanh"]

def add_seed_players(client: MongoDBClient):
    for seed_player_name in SEED_PLAYERS:
        add_players_to_database_from_name(seed_player_name, client)