


from dataclasses import dataclass
from typing import Dict, List, Optional
import time

@dataclass
class Player:
    id: Optional[str]
    riot_id: str
    account_id: str
    puuid: str
    name: str
    last_match_history_fetched: int         # Last timestamp that we update
    
    @classmethod
    def create_table(cls, conn):
        c = conn.cursor()
        c.execute(""" CREATE TABLE player(
                                id INTERGER PRIMARY KEY,
                                riot_id VARCHAR(100),
                                account_id VARCHAR(100),
                                puuid VARCHAR(100),
                                name VARCHAR(100),
                                last_match_history_fetched TIMESTAMP
                                )
                       """)
    
    @classmethod 
    def from_riot_response(cls, riot_response):
        """ Parse from riot response of endpoint summoners/by-name/{name}"""
        return Player(
            id=None,
            riot_id=riot_response.get("id", None),
            account_id=riot_response.get("accountId", None),
            puuid=riot_response.get("puuid", None),
            name=riot_response.get("name", None),
            last_match_history_fetched=int(time.time())
        )
        
    def save(self, conn):
        """ Save to mock database """
        c = conn.cursor()
        if self.id:
            raise ValueError("Only save if player does not have id yet")
        c.execute(f""" INSERT INTO player VALUES
                        ({self.riot_id}, {self.account_id}, {self.puuid}, {self.name}, {self.last_match_history_fetched})
                      """)

# TODO(khoi): implement this
# @dataclass
# class PlayerMatch:
#     """
#         This class is to easily retrive player match history
#     """
#     player_id: int 
#     match_id: int 
#     champion_id: int
#     result: int

    
@dataclass
class Match:
    id: int
    data_version: int
    match_id: str
    participants: List[str]
    info: Dict                 
    

        