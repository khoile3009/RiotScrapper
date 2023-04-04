


from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import json
def convert_python_to_sql(arg):
    if arg is None:
        return "null"
    elif isinstance(arg, str):
        return f"'{arg}'"
    elif isinstance(arg, bool):
        return f"{arg}".lower()
    else:
       return f"{arg}"
   
def insert_or_replace_to_table_query(table_name, args):
    values = [convert_python_to_sql(arg) for arg in args]
    value_string = ", ".join(values)
    
    return f""" INSERT OR REPLACE INTO {table_name} VALUES
                        ({value_string})
                      """
def insert_or_ignore_to_table_query(table_name, args):
    values = [convert_python_to_sql(arg) for arg in args]
    value_string = ", ".join(values)
    
    return f""" INSERT OR IGNORE INTO {table_name} VALUES
                        ({value_string})
                      """                  
                    
def update_row_query(table_name, where_condition, arg_names, values):
    if len(arg_names) != len(values):
        raise ValueError("args_name and values need to be the same length")
    args_update = [f"{arg_names[i]} = {values[i]}" for i in range(len(arg_names))]
    args_update_string = ", ".join(args_update)
    return f"""
        UPDATE {table_name}
        SET {args_update_string}
        WHERE {where_condition}
"""


@dataclass
class Player:
    puuid: str
    id: str = None
    account_id: str = None
    name: str = None
    last_fetched_match_history: int = 0      # Last timestamp that we update
    
    
    @classmethod
    def create_table(cls, conn):
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS player(
                                puuid VARCHAR(100) PRIMARY KEY,
                                id VARCHAR(100),
                                account_id VARCHAR(100),
                                name VARCHAR(100),
                                last_fetched_match_history TIMESTAMP
                                )
                       """)
        conn.commit()
        c.close()
      
    @classmethod
    def from_puuid(cls, puuid):
        """ Create a player object only from puuid"""
        return Player(puuid)
    
    @classmethod 
    def from_riot_response(cls, riot_response):
        """ Parse from riot response of endpoint summoners/by-name/{name}"""
        return Player(
            puuid=riot_response.get("puuid", None),
            id=riot_response.get("id", None),
            account_id=riot_response.get("accountId", None),
            name=riot_response.get("name", None),
        )
        
    def save(self, conn):
        """ Save to mock database """
        c = conn.cursor()
        # If we have information, we want to replace, if we don't we want to ignore if duplicate
        query = insert_or_ignore_to_table_query("player", [self.puuid, self.id, self.account_id, self.name, self.last_fetched_match_history])\
            if self.account_id \
            else insert_or_replace_to_table_query("player", [self.puuid, self.id, self.account_id, self.name, self.last_fetched_match_history])  
        c.execute(query)
        conn.commit()
        c.close()
        
    @classmethod
    def drop_table(cls, conn):
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS player")
        conn.commit()
        c.close()
        
@dataclass
class PlayerMatchInfo:
    """
        This class is to easily retrive player match history
    """
    puuid: str
    match_id: str 
    champion_id: int
    role: str
    team_id: str        #100/200
    win: bool

    @classmethod
    def drop_table(cls, conn):
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS playerMatch")
        conn.commit()
        c.close()

    @classmethod
    def create_table(cls, conn):
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS playerMatch(
                                puuid VARCHAR(100),
                                match_id VARCHAR(100) ,
                                champion_id INT,
                                role VARCHAR(20),
                                team_id INT,
                                win BOOLEAN,
                                PRIMARY KEY (puuid, match_id)
                                )
                       """)
        
    def save(self, conn):
        """ Save to mock database """
        c = conn.cursor()
        query = insert_or_ignore_to_table_query(
            "playerMatch",
            [self.puuid, self.match_id, self.champion_id, self.role, self.team_id, self.win]
        )
        c.execute(query)
        conn.commit()
        c.close()
        
@dataclass
class RawMatch:
    id: str
    content: str
    
    @classmethod
    def from_riot_response(cls, riot_response):
        metadata = riot_response.get("metadata")
        return RawMatch(id=metadata["matchId"], content=json.dumps(riot_response))
    
    @classmethod
    def drop_table(cls, conn):
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS rawMatch")
        conn.commit()
        c.close()
        
    @classmethod
    def create_table(cls, conn):
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS rawMatch(
                                id VARCHAR(50) PRIMARY KEY,
                                content TEXT
                                )
                       """)
        
    def save(self, conn):
        """ Save to mock database """
        c = conn.cursor()
        query = insert_or_ignore_to_table_query(
            "rawMatch",
            [self.id, self.content]
        )
        c.execute(query)
        conn.commit()
        c.close()
        
# TODO: Review this design
@dataclass
class Match:
    """
        As the use case in our app only require champion list and player list,
        we decided to skim out unimportant data like gold per mins, turret kills.
        After we got approved into production, we will re-request for these data and 
        analyze the correlation between them.
    """
    # Metadata
    id: str
    data_version: Optional[int] = None
    game_creation: Optional[int] = None  
    game_duration: Optional[int] = None 
    game_mode: Optional[str] = None             # Move this to enum
    game_type: Optional[str] = None             # Move this to enum
    game_version: Optional[str] = None 
    map_id: Optional[str] = None                # Is this encapsulated in game_mode? Only reason this change is we have major map update
    platform_id: Optional[str] = None           # This is region code 
    queue_id: Optional[str] = None              # https://static.developer.riotgames.com/docs/lol/queues.json
    # Facts           
    winning_team_id: int = None      
    participants: List[PlayerMatchInfo] = None    # Many to many table  
    bans: List[List[str]] = None                  # Json stringify
    picks: List[List[str]] = None                 # Json stringify     


    @classmethod
    def is_targeted_type(cls, match_info) -> bool:
        """ Only use classic (SR) and non custom game -> Ranked and normal
        """
        return match_info["info"]["gameMode"] == "CLASSIC" and match_info["info"]["gameType"] == "MATCHED_GAME"

    @classmethod
    def from_match_id(cls, match_id):
        return Match(id=match_id)

    @classmethod
    def from_riot_response(cls, riot_response):
        metadata = riot_response.get("metadata")
        info = riot_response.get("info")
        participants = info.get("participants")
        player_match_infos = [
            PlayerMatchInfo(
                puuid=participant["puuid"],
                match_id=metadata["matchId"],
                champion_id=participant["championId"],
                role=participant["role"],
                team_id=participant["teamId"],
                win=True
            )
            for participant in participants
        ]
        # Extract picks
        team_one_pick = [participant["championId"] for participant in participants if participant["teamId"] == 100]
        team_two_pick = [participant["championId"] for participant in participants if participant["teamId"] == 200]
        picks = [
            team_one_pick,
            team_two_pick
        ]
        
        # Extract bans
        team_one_bans = [ban_info["championId"] for ban_info in info["teams"][0]["bans"]]
        team_two_bans = [ban_info["championId"] for ban_info in info["teams"][1]["bans"]]
        bans = [
            team_one_bans,
            team_two_bans
        ]
        
        # Extract win team id
        winning_team_id = info["teams"][0]["teamId"] if info["teams"][0]["win"] else info["teams"][1]["teamId"]
        
        return Match(
            id=metadata["matchId"],
            data_version=metadata["dataVersion"],
            game_creation=info["gameCreation"],
            game_duration=info["gameDuration"],
            game_mode=info["gameMode"],
            game_type=info["gameType"],
            game_version=info["gameVersion"],
            map_id=info["mapId"],
            platform_id=info["platformId"],
            queue_id=info["queueId"],
            winning_team_id=winning_team_id,
            participants=player_match_infos,
            bans=bans,
            picks=picks
        )
        
    @classmethod
    def drop_table(cls, conn):
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS match")
        conn.commit()
        c.close()
        
    @classmethod
    def create_table(cls, conn):
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS match(
                                id VARCHAR(50) PRIMARY KEY,
                                data_version INT,
                                game_creation INT,
                                game_duration INT,
                                game_mode VARCHAR(20),
                                game_type VARCHAR(20),
                                game_version VARCHAR(20),
                                map_id VARCHAR(20),
                                platform_id VARCHAR(10),
                                queue_id VARCHAR(10),
                                winning_team_id INT,
                                bans VARCHAR(100),
                                picks VARCHAR(100)
                                )
                       """)
        
    def save(self, conn):
        """ Save to mock database """
        bans_string = json.dumps(self.bans)
        pick_string = json.dumps(self.picks)
        c = conn.cursor()
        query = insert_or_ignore_to_table_query(
            "match",
            [
                self.id, 
                self.data_version, 
                self.game_creation, 
                self.game_duration,
                self.game_mode,
                self.game_type,
                self.game_version,
                self.map_id,
                self.platform_id,
                self.queue_id,
                self.winning_team_id,
                bans_string,
                pick_string,
            ]
        )\
        if not self.data_version\
        else insert_or_replace_to_table_query(
            "match",
            [
                self.id, 
                self.data_version, 
                self.game_creation, 
                self.game_duration,
                self.game_mode,
                self.game_type,
                self.game_version,
                self.map_id,
                self.platform_id,
                self.queue_id,
                self.winning_team_id,
                bans_string,
                pick_string,
            ]
        )
        c.execute(query)
        if self.participants:
            for player_match_info in self.participants:
                player_match_info.save(conn)
        conn.commit()
        c.close()
    
    
    def get_participant_puuids(self):
        return [participant.puuid for participant in self.participants]
        
def create_all_tables(conn):
    Player.create_table(conn)
    Match.create_table(conn)
    PlayerMatchInfo.create_table(conn)
    RawMatch.create_table(conn)
    
def drop_all_tables(conn):
    Player.drop_table(conn)
    Match.drop_table(conn)
    PlayerMatchInfo.drop_table(conn)
    RawMatch.drop_table(conn)
