import os
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL environment variable is not set.")

EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

with open("previous_games.txt", "r") as f:
    previous_games = set(line.strip() for line in f.readlines())

response = requests.get(EPIC_API_URL)
if response.status_code != 200:
    raise Exception(f"Failed to fetch Epic Games API. Status code: {response.status_code}")

data = response.json()

free_games = []

elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
for game in elements:
    promotions = game.get("promotions", {})
    if promotions is None:
        continue
    promo_offers = promotions.get("promotionalOffers", [])

    if promo_offers and len(promo_offers) > 0:
        if promo_offers[0].get("promotionalOffers", []):
            title = game.get("title")
            if title in previous_games:
                continue
            slug = game.get("productSlug")
            url = f"https://www.epicgames.com/store/en-US/p/{slug}" if slug else "No URL"
            free_games.append((title, url))

if free_games:
    message_content = "**New Epic Games Free Today!**\n"
    for title, url in free_games:
        message_content += f"- {title}: {url}\n"

    payload = {
        "content": message_content
    }

    with open("previous_games.txt", "w") as f:
        for title, _ in free_games:
            f.write(f"{title}\n")

    discord_response = requests.post(WEBHOOK_URL, json=payload)
    if discord_response.status_code not in (200, 204):
        raise Exception(f"Failed to send Discord message. Status code: {discord_response.status_code}")
else:
    discord_response = requests.post(WEBHOOK_URL, json={"content": "No new free games today."})
    if discord_response.status_code not in (200, 204):
        raise Exception(f"Failed to send Discord message. Status code: {discord_response.status_code}")