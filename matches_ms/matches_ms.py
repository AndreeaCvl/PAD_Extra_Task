import json
from flask import Flask, jsonify, request
import psycopg2
import http.client
from datetime import datetime, timedelta
import time
from prometheus_client import Counter, Gauge, generate_latest

app = Flask(__name__)
app.config['TIMEOUT'] = 5

# Define Prometheus counters for total requests
matches_counter = Counter('matches_requests', 'Total number of requests per endpoint', ['endpoint'])


def get_upcoming_matches():
    try:
        today_date = datetime.today()
        year, month, day = today_date.year, today_date.month, today_date.day

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
                    'city': game['competitions'][0]['venue']['address']['city'],
                    'state': game['competitions'][0]['venue']['address']['state'],
                    'country': game['competitions'][0]['venue']['address']['country']
                }
                games_info.append(game_info)

        return games_info

    except Exception as e:
        return {'error_message': str(e), 'status_code': 500}


def get_today_matches():
    today_date = datetime.today().strftime('%Y-%m-%d')

    conn = http.client.HTTPSConnection("nhl-api5.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "nhl-api5.p.rapidapi.com"
    }

    conn.request("GET", f"/nhlschedule", headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    matches_data = json.loads(data)

    # Extract relevant information from today's matches
    today_matches_info = []

    for date_str, date_info in matches_data.items():
        match_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')

        if match_date == today_date:
            for game_info in date_info.get('games', []):
                venue_info = game_info.get('competitions', [{}])[0].get('venue', {})
                teams_info = game_info.get('competitors', [])

                match_info = {
                    'date': game_info.get('date', ''),
                    'uid': game_info.get('uid', ''),
                    'name': game_info.get('name', ''),
                    'venue_full_name': venue_info.get('fullName', ''),
                    'city': venue_info.get('address', {}).get('city', ''),
                    'country': venue_info.get('address', {}).get('country', ''),
                    'state': venue_info.get('address', {}).get('state', ''),
                }

                today_matches_info.append(match_info)

    return today_matches_info


def get_past_matches_on_date(target_date):
    target_date_obj = datetime.strptime(target_date, "%d.%m.%Y")

    # Construct the API request parameters
    year = target_date_obj.year
    month = target_date_obj.month
    day = target_date_obj.day

    conn = http.client.HTTPSConnection("nhl-api5.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "nhl-api5.p.rapidapi.com"
    }

    # conn.request("GET", f"/nhlschedule?year={year}&month={month:02d}&day={day:02d}", headers=headers)
    conn.request("GET", f"/nhlscoreboard?year={year}&month={month:02d}&day={day:02d}", headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    response_dict = json.loads(data)

    # Extract relevant information from the response
    events = response_dict.get('events', [])

    events_data = []

    for event in events:
        event_data = {
            'date': event['date'],
            'uid': event['uid'],
            'name': event['name'],
            'venue_full_name': event['competitions'][0]['venue']['fullName'],
            'city': event['competitions'][0]['venue']['address']['city'],
            'state': event['competitions'][0]['venue']['address']['state'],
            'country': event['competitions'][0]['venue']['address']['country']
        }
        events_data.append(event_data)

    return events_data


def team_info_by_game_id(game_id):
    conn = http.client.HTTPSConnection("nhl-api5.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "nhl-api5.p.rapidapi.com"
    }

    conn.request("GET", f"/nhlpicks?id={game_id}", headers=headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    # Parse the JSON data
    json_data = json.loads(data)

    # Extract relevant information about the teams
    leaders = json_data.get('leaders', [])
    if leaders:
        team1_info = leaders[0].get('team', {})
        team2_info = leaders[1].get('team', {})

        team1 = {
            'team_id': team1_info.get('id', ''),
            'name': team1_info.get('displayName', ''),
            'abbreviation': team1_info.get('abbreviation', ''),
            'logo': team1_info.get('logo', ''),
            'record': team1_info.get('record', [])
        }

        team2 = {
            'team_id': team2_info.get('id', ''),
            'name': team2_info.get('displayName', ''),
            'abbreviation': team2_info.get('abbreviation', ''),
            'logo': team2_info.get('logo', ''),
        }

        return team1, team2
    else:
        return None, None


@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/pingdb')
def ping_db():
    db_params = {
        'host': 'matches-db.pad',
        'database': 'matches_db',
        'user': 'admin',
        'password': 'mysecretpassword',
        'port': '5432'
    }

    # Establish a connection to the PostgreSQL database
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Execute a query to get the current timestamp from the database
        cursor.execute("SELECT current_timestamp;")

        # Fetch the result
        current_time = cursor.fetchone()[0]

        # Print the current time
        print(f"Current time from the database: {current_time}")

        # Close the cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed.")

        return jsonify(current_time), 200

    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return str(e), 500


@app.route('/update')
def update_db():
    matches_counter.labels(endpoint='update').inc()

    try:
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
                    'city': game['competitions'][0]['venue']['address']['city'],
                    'state': game['competitions'][0]['venue']['address']['state'],
                    'country': game['competitions'][0]['venue']['address']['country']
                    ,
                }
                games_info.append(game_info)

        db_params = {
            'host': 'matches-db.pad',
            'database': 'matches_db',
            'user': 'admin',
            'password': 'mysecretpassword',
            'port': '5432'
        }

        #dsn = f"host={db_params['host']} dbname={db_params['database']} user={db_params['user']} password={db_params['password']} port={db_params['port']}"
        db_conn = psycopg2.connect(**db_params)
        cursor = db_conn.cursor()

        # Print the extracted information
        for game_info in games_info:
            print("Date:", game_info["date"])
            print("UID:", game_info["uid"])

            cursor.execute(("SELECT uid FROM matches WHERE uid = %s"), (game_info['uid'],))
            existing_id = cursor.fetchone()

            if existing_id:
                # ID already exists, skip insertion
                print(f"Record with ID {game_info['uid']} already exists. Skipping insertion.")
            else:
                # ID doesn't exist, insert the new record
                cursor.execute(
                ("INSERT INTO matches (uid, match_date, match_name, venue, city, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s)"),
                    (
                        game_info['uid'],
                        game_info['date'],
                        game_info['name'],
                        game_info['venue_full_name'],
                        game_info['city'],
                        game_info['state'],
                        game_info['country'],
                    )
                )
                print(f"Record with ID {game_info['uid']} inserted successfully.")

        # Commit the changes and close the connection
        db_conn.commit()
        cursor.close()
        db_conn.close()

        print("\n")
        return jsonify({'message': 'Data updated successfully', 'status_code': 200})

    except Exception as e:
        return jsonify({'error_message': str(e), 'status_code': 500})


@app.route('/upcoming_matches', methods=['GET'])
def upcoming_matches():
    matches_counter.labels(endpoint='upcoming_matches').inc()
    try:
        # Call the get_upcoming_matches function
        matches_info = get_upcoming_matches()
        return jsonify(matches_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/today_matches', methods=['GET'])
def today_matches():
    matches_counter.labels(endpoint='today_matches').inc()

    try:
        # Call the get_today_matches function
        matches_info = get_today_matches()
        return jsonify(matches_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/past_matches', methods=['GET'])
def past_matches():
    matches_counter.labels(endpoint='past_matches').inc()
    try:
        # Get the 'target_date' parameter from the query string
        target_date = request.args.get('target_date')

        # Validate parameters
        if not target_date:
            return jsonify({'error': 'Target date is a required parameter'}), 400

        # Call the get_past_matches_on_date function
        matches_info = get_past_matches_on_date(target_date)
        return jsonify(matches_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/team_info', methods=['GET'])
def team_info():
    matches_counter.labels(endpoint='team_info').inc()

    try:
        # Get the 'game_id' parameter from the query string
        game_id = request.args.get('game_id')

        # Validate parameters
        if not game_id:
            return jsonify({'error': 'Game ID is a required parameter'}), 400

        # Call the team_info_by_game_id function
        team1_info, team2_info = team_info_by_game_id(game_id)

        # Return the team information as JSON
        return jsonify({'team1': team1_info, 'team2': team2_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
