import json

from flask import Flask
import http.client
from datetime import datetime


app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/update')
def update_db():
    today_date = datetime.today()
    year = today_date.year
    month = today_date.month
    day = today_date.day

    conn = http.client.HTTPSConnection("nhl-api5.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "nhl-api5.p.rapidapi.com"
    }

    conn.request("GET", f"/nhlschedule?year={year}&month={month:02d}&day={day:02d}", headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    # Parse JSON data if applicable
    json_data = json.loads(data)

    games_info = []

    for game_key, game_data in json_data.items():
        for game in game_data.get('games', []):
            game_info = {
                'date': game.get('date'),
                'uid': game.get('uid'),
                'name': game.get('name'),
                'venue_full_name': game['competitions'][0]['venue']['fullName'],
                'venue_address':
                    {'city': game['competitions'][0]['venue']['address']['city'],
                     'state': game['competitions'][0]['venue']['address']['state'],
                     'country': game['competitions'][0]['venue']['address']['country']}
                ,
            }
            games_info.append(game_info)

    # Print the extracted information
    for game_info in games_info:
        print("Date:", game_info["date"])
        print("UID:", game_info["uid"])
        print("Name:", game_info["name"])
        print("Venue Full Name:", game_info["venue_full_name"])
        print("Venue Address:", game_info["venue_address"])
        print("\n")

    return games_info


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
