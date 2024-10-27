
import requests

account_name = "JWEA8"
account_tag = "2767"
api_key = "RGAPI-a0382dc3-305b-4779-8121-3d46e7cdfc84"
api_url_puuid = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
api_url_puuid =  api_url_puuid + account_name + "/" + account_tag + "?api_key=" + api_key
resp = requests.get(api_url_puuid)

puuid = resp.json()
puuid = puuid['puuid']

api_get_summoner_info_url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/"
api_get_summoner_info_url = api_get_summoner_info_url + puuid + "?api_key=" + api_key
summoner_stats = requests.get(api_get_summoner_info_url)
player_info = summoner_stats.json()
print(player_info)
player_account_id = player_info['accountId']
player_level = player_info['summonerLevel']

#matches_api_url = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
#matches_api_url = matches_api_url + puuid + "/ids?start=0&count=20&api_key=" + api_key
#matches_stats = requests.get(matches_api_url)
#matches = matches_stats.json()
#print(matches)
#match = matches[0]

# ind_match_data_url = "https://americas.api.riotgames.com/lol/match/v5/matches/"
# ind_match_data_url = ind_match_data_url + match + "?api_key=" + api_key
# match_data_resp = requests.get(ind_match_data_url)
# match_data = match_data_resp.json()
def get_matches(matches_wanted, puuid, region, api_key):
    matches_api_url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid +
        "/ids?start=0&count=" + 
        str(matches_wanted) + 
        "&api_key=" +
        api_key
    )
    resp = requests.get(matches_api_url)
    data = resp.json()
    return data

def get_matches_ranked(matches_wanted, puuid, region, api_key):
    matches_api_url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid +
        "/ids?type=ranked&start=0&count=" + 
        str(matches_wanted) + 
        "?api_key=" +
        api_key
    )
    resp = requests.get(matches_api_url)
    data = resp.json()
    return data

def get_match_data(region, match_id, api_key):
    api_url_match = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id +
        "?api_key=" +
        api_key
    )
    resp = requests.get(api_url_match)
    data = resp.json()
    return data

def player_game_stats(puuid, match_data):
    player_index = match_data['metadata']['participants'].index(puuid)
    player_ingame = match_data['info']['participants'][player_index]
    return player_ingame

def win_or_lose(puuid, match_data):
    player_index = match_data['metadata']['participants'].index(puuid)
    return match_data['info']['participants'][player_index]['win']

region = "americas"

matches_wanted = 4
matches = get_matches(matches_wanted, puuid, region, api_key)
#print(matches)
match = matches[0]
match_data = get_match_data(region, match, api_key)
#print(match_data)

player_game_stats(puuid, match_data)

for match in matches:
    #print(match)
    match_data = get_match_data(region, match, api_key)
    #print(match_data)
    player_ingame = player_game_stats(puuid, match_data)
    print(win_or_lose(puuid, match_data))
