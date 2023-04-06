# import requests
from dotenv import load_dotenv
import os
import requests
from pprint import pprint
from constants import (
    MATCH_HISTORY_API,
    MATCH_INFO_API,
    PLAYER_NAME_API,
    PLAYER_PUUID_API,
)

load_dotenv()


class RiotAPI:
    """
    Class to make request to riot api
    """

    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY")

    def _request(self, api_url, params={}):
        args = {"api_key": self.api_key, **params}
        response = requests.get(api_url, params=args)
        return response.json()

    def get_player_info_from_name(self, name):
        url = PLAYER_NAME_API.format(name=name)
        return self._request(url)

    def get_player_info_from_puuid(self, puuid):
        url = PLAYER_PUUID_API.format(encryptedPUUID=puuid)
        return self._request(url)

    def get_match_history_from_puuid(self, puuid, start_time=None):
        # TODO(khoi): Fetch all with pagination
        url = MATCH_HISTORY_API.format(puuid=puuid)
        # TODO: Change this to 100
        params = {"count": 5}
        if start_time:
            params["startTime"] = start_time
        return self._request(url, params)

    def get_match_info_from_match_id(self, match_id):
        url = MATCH_INFO_API.format(match_id=match_id)
        return self._request(url)


if __name__ == "__main__":
    api = RiotAPI()
    pprint(api.get_player_info_from_name("scarria"))
    pprint(
        api.get_match_history_from_puuid(
            "pRHSBIZo91C5n1L2uqjxKx9DDLCOLAefMmKET9t6w3n5ba7HazwQ9d3bzKt0wfNESDezCyEUjXZrpg"
        )
    )
    match_info = api.get_match_info_from_match_id("NA1_4573472375")
    for k, v in match_info["metadata"].items():
        print(k, v)
    for k, v in match_info["info"]["teams"][0].items():
        print(k)
    print(type(match_info["info"]["teams"][1]["teamId"]))
