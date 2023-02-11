from pathlib import Path

RIOT_API_BASE_V4 = "https://na1.api.riotgames.com/lol"
RIOT_API_BASE_V5 = "https://americas.api.riotgames.com/lol"
MATCH_API = RIOT_API_BASE_V5 + "/match/v5/matches"
MATCH_INFO_API = MATCH_API + "/{match_id}"
MATCH_HISTORY_API = MATCH_API + "/by-puuid/{puuid}/ids"
PLAYER_API = RIOT_API_BASE_V4 + "/summoner/v4/summoners"
PLAYER_NAME_API = PLAYER_API + "/by-name/{name}"
PLAYER_PUUID_API = PLAYER_API + "/by-puuid/{encryptedPUUID}"