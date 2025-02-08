import requests

API_KEY = "ed3c39530f5ed4ba489da8b95524187d"
SEASONS = "season-df-1:season-df-2:season-df-3:season-df-4:season-tww-1"
CURRENT_SEASON = "season-tww-1"
RAIDS = "uldir:battle-of-dazaralor:crucible-of-storms:eternal-palace:nyalotha-the-waking-city:castle-nathria:sanctum-of-domination:sepulcher-of-the-first-ones:vault-of-the-incarnates:aberrus-the-shadowed-crucible:amirdrassil-the-dreams-hope:nerubar-palace"
FIELDS_STATS = f"guild,mythic_plus_scores_by_season:{SEASONS},mythic_plus_best_runs:all,mythic_plus_weekly_highest_level_runs,mythic_plus_previous_weekly_highest_level_runs,mythic_plus_recent_runs,raid_achievement_curve:{RAIDS}"

def ask_api_rio_stats(character_name, realm):
    url = f'https://raider.io/api/v1/characters/profile?region=eu&realm={realm}&name={character_name}&fields={FIELDS_STATS}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur", f"Erreur API: {response.status_code}")
        return None