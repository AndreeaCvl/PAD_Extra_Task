import json
from flask import Flask, jsonify
import psycopg2
import http.client
from datetime import datetime, timedelta

app = Flask(__name__)

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


@app.route('/following_matches', methods=['GET'])
def get_following_matches():
    try:
        # Get the current date
        today_date = datetime.today()

        # Calculate the end date (5 days from today)
        end_date = today_date + timedelta(days=5)

        # Connect to the database
        db_params = {
            'host': 'matches-db.pad',
            'database': 'matches_db',
            'user': 'admin',
            'password': 'mysecretpassword',
            'port': '5432'
        }
        db_conn = psycopg2.connect(**db_params)
        cursor = db_conn.cursor()

        # Query upcoming matches within the specified time frame
        cursor.execute("SELECT * FROM matches WHERE match_date BETWEEN %s AND %s ORDER BY match_date",
                       (today_date, end_date))
        upcoming_matches = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()
        db_conn.close()

        # Convert the result to a list of dictionaries
        matches_info = [{'uid': match[0],
                         'date': match[1],
                         'name': match[2],
                         'venue': match[3],
                         'city': match[4],
                         'state': match[5],
                         'country': match[6]}
                        for match in upcoming_matches]

        return jsonify({'upcoming_matches': matches_info, 'status_code': 200})

    except Exception as e:
        return jsonify({'error_message': str(e), 'status_code': 500})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
