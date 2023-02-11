# scrapper
Scraper for Riot API. 
## We have 2 main scripts:
- `fetch_player_history` that get a players' username/uuid and return the player info and match history of that player and store in database
- `fetch_match_info` that get match_id and return the match_history info. 

## Mock database
Right now we are using a mock database using sqlite3 to prototype the pipeline and datamodel. We will gradually moved to using grpc to remote database service that use ORM

## TODO
- [ ] Update seed 10 players each rank
- [ ] Migrate to using grpc for database service
- [ ] Add black formatter
- [ ] Implement a rotating n API keys system
- [ ] Match history pagination query by 100 at a time and from latest and go back. Write method `get_full_match_history` and `update_match_history` that get from database what is the last puuid
- [ ] Add region as variable