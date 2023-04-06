import pymongo
from datetime import datetime, timedelta
from pymongo.errors import BulkWriteError, DuplicateKeyError

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["riotdb"]
matches = db.get_collection("matches")


class MongoDBClient:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client.get_database("riotdb")
        self.matches = self.db.get_collection("matches")
        self.players = self.db.get_collection("players")

    # POST
    def insert_player_puuids(self, puuids):
        document = [
            {"_id": puuid, "last_updated": None, "data": None} for puuid in puuids
        ]
        try:
            self.players.insert_many(document, ordered=False)
        except BulkWriteError:
            pass

    def insert_player(self, riot_response):
        document = {
            "_id": riot_response.get("puuid"),
            "last_updated": None,
            "data": riot_response,
        }
        try:
            self.players.insert_one(document)
        except DuplicateKeyError:
            pass

    def update_player(self, response):
        return self.players.update_one(
            {"_id": response["puuid"]}, {"$set": {"data": response}}, upsert=True
        )

    def update_player_last_update(self, puuid):
        return self.players.update_one(
            {"_id": puuid}, {"$set": {"last_updated": datetime.utcnow()}}
        )

    def insert_match(self, riot_response):
        document = {
            "_id": riot_response.get("metadata").get("matchId"),
            "data": riot_response,
        }
        return self.matches.insert_one(document)

    def update_match(self, riot_response):
        return self.matches.update_one(
            {"_id": riot_response.get("metadata").get("matchId")},
            {"$set": {"data": riot_response}},
            upsert=True,
        )

    def insert_match_ids(self, match_ids):
        documents = [{"_id": match_id, "data": None} for match_id in match_ids]
        try:
            self.matches.insert_many(documents, ordered=False)
        except BulkWriteError:
            print("Duplicate value")

    # GET
    def get_match_ids_with_no_data(self, n=10):
        return [match["_id"] for match in self.matches.find({"data": None}).limit(n)]

    def get_puuids_with_no_data(self, n=10):
        return [player["_id"] for player in self.players.find({"data": None}).limit(n)]

    def get_not_updated_players(self, n=10):
        return [
            player
            for player in self.players.find(
                {
                    "$or": [
                        {"last_updated": None},
                        {
                            "last_updated": {
                                "$lte": datetime.utcnow() - timedelta(days=14)
                            }
                        },
                    ]
                }
            ).limit(n)
        ]

    # SUMMARY
    def summarize_collections(self):
        num_matches = self.matches.count_documents({})
        num_matches_with_detail = self.matches.count_documents({"data": {"$ne": None}})
        num_players = self.players.count_documents({})
        num_players_not_updated = self.players.count_documents(
            {
                "$or": [
                    {"last_updated": None},
                    {"last_updated": {"$lte": datetime.utcnow() - timedelta(days=14)}},
                ]
            }
        )
        print("-------------- Dataset report --------------")
        print(f"Total number of matches: {num_matches}")
        print(
            f"Number of matches with detail: {num_matches_with_detail}. That is {num_matches_with_detail / num_matches * 100 if num_matches != 0 else 0}% of matches\n"
        )
        print(f"Total number of players: {num_players}")
        print(
            f"Number of players with history not updated: {num_players_not_updated}. That is {num_players_not_updated / num_players * 100 if num_players != 0 else 0}% of players\n"
        )

    # DELETE
    def drop_all_collections(self):
        self.matches.drop()
        self.players.drop()


if __name__ == "__main__":
    mongodb = MongoDBClient()
    print(mongodb.get_number_matches())
