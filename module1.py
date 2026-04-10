import requests
import time
import os
import json

# -----------------------------
# CONFIG
# -----------------------------
CLIENT_ID = "f82b44d9e2fa42d48912ae123722155c"
CLIENT_SECRET = "OulFWH7YJIYP8JVVS58sjCwTwuMjB1em"
REGION = "us"  # "us", "eu", "kr", "tw"
LOCALE = "en_US"
NAMESPACE_DYNAMIC = f"dynamic-{REGION}"

# Standard brackets
BRACKETS = ["2v2", "3v3", "battlegrounds"]  # "rbg" was renamed to "battlegrounds"

# Solo Shuffle brackets (must use full class-spec slugs)
SHUFFLE_BRACKETS = [
    "shuffle-deathknight-blood",
    "shuffle-deathknight-frost",
    "shuffle-deathknight-unholy",
    "shuffle-demonhunter-havoc",
    "shuffle-demonhunter-vengeance",
    "shuffle-druid-balance",
    "shuffle-druid-feral",
    "shuffle-druid-guardian",
    "shuffle-druid-restoration",
    "shuffle-evoker-augmentation",
    "shuffle-evoker-devastation",
    "shuffle-evoker-preservation",
    "shuffle-hunter-beastmastery",
    "shuffle-hunter-marksmanship",
    "shuffle-hunter-survival",
    "shuffle-mage-arcane",
    "shuffle-mage-fire",
    "shuffle-mage-frost",
    "shuffle-monk-brewmaster",
    "shuffle-monk-mistweaver",
    "shuffle-monk-windwalker",
    "shuffle-paladin-holy",
    "shuffle-paladin-protection",
    "shuffle-paladin-retribution",
    "shuffle-priest-discipline",
    "shuffle-priest-holy",
    "shuffle-priest-shadow",
    "shuffle-rogue-assassination",
    "shuffle-rogue-outlaw",
    "shuffle-rogue-subtlety",
    "shuffle-shaman-elemental",
    "shuffle-shaman-enhancement",
    "shuffle-shaman-restoration",
    "shuffle-warlock-affliction",
    "shuffle-warlock-demonology",
    "shuffle-warlock-destruction",
    "shuffle-warrior-arms",
    "shuffle-warrior-fury",
    "shuffle-warrior-protection",
]

ALL_BRACKETS = BRACKETS + SHUFFLE_BRACKETS
OUTPUT_DIR = "wow_pvp_arena_data"

# -----------------------------
# AUTH: Get OAuth token
# -----------------------------
def get_access_token():
    url = f"https://{REGION}.battle.net/oauth/token"
    data = {"grant_type": "client_credentials"}
    resp = requests.post(url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    resp.raise_for_status()
    return resp.json()["access_token"]

# -----------------------------
# API helper
# FIX: namespace must be sent as a header, not a query param
# -----------------------------
def get(url, token, params=None):
    if params is None:
        params = {}
    params.setdefault("locale", LOCALE)
    params.setdefault("access_token", token)

    headers = {
    "Authorization": f"Bearer {token}",       # was ?access_token=... in URL
    "Battlenet-Namespace": NAMESPACE_DYNAMIC,  # was ?namespace=... in URL
}

    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()

# -----------------------------
# Fetch CURRENT PvP season
# -----------------------------
def get_current_season(token):
    url = f"https://{REGION}.api.blizzard.com/data/wow/pvp-season/index"
    data = get(url, token)
    current = data.get("current_season")
    if not current:
        raise Exception("No current PvP season in response.")
    return current["id"]

# -----------------------------
# Fetch leaderboard for one season + bracket
# -----------------------------
def get_leaderboard(token, season_id, bracket):
    url = f"https://{REGION}.api.blizzard.com/data/wow/pvp-season/{season_id}/pvp-leaderboard/{bracket}"
    return get(url, token)

# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Getting access token...")
    token = get_access_token()
    print("Token acquired.")

    print("Fetching current PvP season...")
    season_id = get_current_season(token)
    print(f"Current season ID: {season_id}")

    for bracket in ALL_BRACKETS:
        print(f"\nFetching bracket: {bracket}...")
        try:
            data = get_leaderboard(token, season_id, bracket)
        except requests.HTTPError as e:
            print(f"  Skipping {bracket}: {e}")
            continue

        filename = f"season_{season_id}_{bracket}.json"
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Saved {filename} ({len(data.get('entries', []))} entries).")
        time.sleep(0.2)

if __name__ == "__main__":
    main()