from pprint import pprint
from database.mock_database import MockDatabase
from helpers.helpers import add_player_history, get_all_players_with_history_not_updated, update_all_match_history


database = MockDatabase()
cursor = database.conn.cursor()
update_all_match_history()
cursor.execute("select * from player")
pprint(cursor.fetchall())
cursor.execute("select * from match")
pprint(cursor.fetchall()[:5])
cursor.execute("select * from playerMatch")
pprint(cursor.fetchall())
cursor.execute("""
               select id 
               from match
               where game_version is null
               limit 2 
               """
               )
pprint(cursor.fetchall())