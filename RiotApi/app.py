from flask import Flask, render_template, jsonify, request
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
import os


app = Flask(__name__)

api_key = "Your API Code Here"

# Function to get PUUID
def get_puuid(region, account_name, account_tag):
    api_url_puuid = (
        "https://" + region +
        ".api.riotgames.com/riot/account/v1/accounts/by-riot-id/" +
        account_name + "/" + account_tag + "?api_key=" + api_key
    )
    #print(f"Requesting PUUID from: {api_url_puuid}")
    resp = requests.get(api_url_puuid)
    #print(f"Response status code: {resp.status_code}, Response: {resp.text}")
    if resp.status_code != 200:
        return None
    return resp.json().get('puuid')

# Function to get matches
def get_matches(puuid, matches_wanted, region):
    matches_api_url = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" +
        puuid +
        "/ids?start=0&count=" + 
        str(matches_wanted) + 
        "&api_key=" + api_key
    )
    resp = requests.get(matches_api_url)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_ranked_matches(puuid, matches_wanted, region):
    api_url_matchs = (
        "https://" +
        region + 
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + 
        puuid +
        "/ids?type=ranked&start=0&count=" + 
        str(matches_wanted) +
        "&api_key=" + api_key
    )
    resp = requests.get(api_url_matchs)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_normal_matches(puuid, matches_wanted, region):
    api_url_matchs = (
        "https://" +
        region + 
        ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + 
        puuid +
        "/ids?type=normal&start=0&count=" + 
        str(matches_wanted) +
        "&api_key=" + api_key
    )
    resp = requests.get(api_url_matchs)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_match_data(region, match_id, api_key):
    api_url_match = (
        "https://" +
        region +
        ".api.riotgames.com/lol/match/v5/matches/" +
        match_id +
        "?api_key=" + api_key
    )
    resp = requests.get(api_url_match)
    #print(f"Fetching match data for {match_id}: Status Code: {resp.status_code}")
    return resp.json()

def win_or_lose(puuid, match_data):
    player_index = match_data['metadata']['participants'].index(puuid)
    return match_data['info']['participants'][player_index]['win']

def get_win_loss_stats(puuid, matches, region):
    wins = 0
    losses = 0

    for match_id in matches:
        match_data = get_match_data(region, match_id, api_key)
        if match_data is None:  # Handle rate limit error gracefully
            break  # Stop fetching more match data if we hit the limit
        if win_or_lose(puuid, match_data):
            wins += 1
        else:
            losses += 1

    total_games = wins + losses
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0

    return {
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate
    }

# Graph Functions

def create_graph(preference, x, y):
    plt.bar(x, y)

    plt.xlabel('Match ID')
    plt.ylabel(preference.upper())

    plt.title(preference.upper())

    plt.gca().invert_xaxis()
    
    graph_path = os.path.join('static', 'graph.png')
    plt.savefig(graph_path)
    plt.close()

# Table functions 

def get_champion(puuid, match_data):
    player_index = match_data['metadata']['participants'].index(puuid)
    champion_name = match_data['info']['participants'][player_index]['championName']
    return champion_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    data = request.get_json()
    preference = data.get('preference')
    matches = data.get('matches')  # This should be the matches data passed from the front end

    if not matches or not preference:
        return jsonify({'error': 'Invalid data'}), 400

    stats_data = []

    for match in matches:
        if preference == 'kda':
            kda_values = match['KDA'].split('/')  # Expecting format "kills/deaths/assists"
            kda_ratio = (int(kda_values[0]) + int(kda_values[2])) / (int(kda_values[1]) + 1)  # KDA Ratio
            stats_data.append((match['match_id'], kda_ratio))
        
        elif preference == 'dmgDone':
            stats_data.append((match['match_id'], int(match['dmgDone'])))
        elif preference == 'dmgTaken':
            stats_data.append((match['match_id'], int(match['dmgTaken'])))
        elif preference == 'gold':
            stats_data.append((match['match_id'], int(match['gold'])))
        elif preference == 'goldMinute':
            stats_data.append((match['match_id'], int(match['goldMinute'])))
        elif preference == 'questions':
            stats_data.append((match['match_id'], int(match['questions'])))

    # Sort the stats_data based on the second element (the value to plot)
    sorted_stats = sorted(stats_data, key=lambda x: x[1])  # Sort by the value

    # Unzip the sorted data into x and y
    x = [match[0] for match in sorted_stats]  # Get match IDs from the sorted stats
    y = [match[1] for match in sorted_stats]  # Get corresponding values from the sorted stats

    create_graph(preference, x, y)
    return jsonify({'success': True})  

@app.route('/get_matches_stats/<account_name>/<account_tag>/<int:matches_wanted>', methods=['POST'])
def fetch_matches_stats(account_name, account_tag, matches_wanted):
    region = "americas"
    puuid = get_puuid(region, account_name, account_tag)
    if not puuid:
        return jsonify({'error': 'Unable to fetch PUUID'}), 400
    
    preferences = request.get_json().get('preferences', [])
    
    if "ranked" in preferences:
        matches = get_ranked_matches(puuid, matches_wanted, region)
    elif "normal" in preferences:
        matches = get_normal_matches(puuid, matches_wanted, region)
    else:
        matches = get_matches(puuid, matches_wanted, region)

    if not matches:
        return jsonify({'error': 'Unable to fetch matches'}), 400

    match_data_cache = {}
    match_details = []

    for match_id in matches:
        if match_id not in match_data_cache:
            match_data = get_match_data(region, match_id, api_key)
            if match_data is None:  # Handle rate limit error gracefully
                break  # Stop fetching more match data if we hit the limit
            match_data_cache[match_id] = match_data  # Cache match data
        else:
            match_data = match_data_cache[match_id]  # Retrieve from cache
        
        result = win_or_lose(puuid, match_data)
        match_info = {
            'match_id': match_id,
            'KDA': 0,
            'dmgDone': 0,
            'dmgTaken': 0,
            'gold': 0,
            'goldMinute': 0,
            'questions': 0,
            'result': 'Win' if result else 'Lose'
        }
        
        for pref in preferences:
            player_index = match_data['metadata']['participants'].index(puuid)
            if pref == "champion":
                match_info['champion'] = match_data['info']['participants'][player_index]['championName']
            # Handle other preferences as needed
            if pref == "kda":
                kills = 0;
                deaths = 0;
                assists = 0;
                kills = match_data['info']['participants'][player_index]['kills']
                deaths = match_data['info']['participants'][player_index]['deaths']
                assists = match_data['info']['participants'][player_index]['assists']
                kda = str(kills) + '/' + str(deaths) + '/' + str(assists)
                match_info['KDA'] = kda
            if pref == "dmgDone":
                match_info['dmgDone'] = match_data['info']['participants'][player_index]['totalDamageDealtToChampions']
            if pref == "dmgTaken":
                match_info['dmgTaken'] = match_data['info']['participants'][player_index]['totalDamageTaken']
            if pref == "gold":
                match_info['gold'] = match_data['info']['participants'][player_index]['goldEarned']
            if pref == "goldMinute":
                match_info['goldMinute'] = match_data['info']['participants'][player_index]['challenges']['goldPerMinute']
            if pref == "questions":
                match_info['questions'] = match_data['info']['participants'][player_index]['enemyMissingPings']
             
        match_details.append(match_info)

    # Now get win/loss statistics just once based on match IDs
    stats = get_win_loss_stats(puuid, matches, region)

    return jsonify({
        'matches': match_details,
        'stats': stats
    })

if __name__ == "__main__":
    app.run(debug=True)
