from pprint import pprint
from database.mock_database import MockDatabase
from database.mock_data_model import create_all_tables, drop_all_tables
from helpers.helpers import (
    update_all_match_history,
    update_all_null_matches,
    update_info_for_player_with_no_info,
)
from helpers.seed_players import add_seed_players
from database.mongo_database import MongoDBClient

"""
    TODO: Move everything to mongodb
"""


def initialize_database():
    # database = MockDatabase()
    client = MongoDBClient()
    # drop_all_tables(database.conn)
    # create_all_tables(database.conn)

    # Add the initial seed players
    add_seed_players(client)

    # Load the match history of seed players
    update_all_match_history(client)

    # Fill in the match information and extract more players from these match
    update_all_null_matches(client)


if __name__ == "__main__":
    # initialize_database()
    client = MongoDBClient()
    client.drop_all_collections()
    add_seed_players(client)
    client.summarize_collections()
    update_all_match_history(client)
    client.summarize_collections()
    update_all_null_matches(client)
    client.summarize_collections()
    update_info_for_player_with_no_info(client)
    client.summarize_collections()
