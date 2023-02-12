
from pprint import pprint
from database.mock_database import MockDatabase
from database.mock_data_model import create_all_tables, drop_all_tables
from helpers.helpers import update_all_match_history, update_all_null_matches
from helpers.seed_players import add_seed_players

def initialize_database():
    database = MockDatabase()
    
    drop_all_tables(database.conn)
    create_all_tables(database.conn)
    
    # Add the initial seed players
    add_seed_players(database.conn)
    
    # Load the match history of seed players 
    update_all_match_history(database.conn)
    
    # Fill in the match information and extract more players from these match
    update_all_null_matches(database.conn)
    
if __name__ == '__main__':
    initialize_database()
    