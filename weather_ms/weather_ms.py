import requests
import json
from flask import Flask, jsonify, request
import psycopg2
import json
import http.client
from datetime import datetime, timezone

app = Flask(__name__)


def generate_unique_id():
    # You can use a more robust method to generate unique IDs (e.g., UUID)
    return str(datetime.now())


def match_weather_to_db(date, location, weather_data, match_name):
    # Generate a unique ID for the data
    unique_id = generate_unique_id()

    # Database connection parameters
    db_params = {
        'host': 'weather-db.pad',
        'database': 'weather_db',
        'user': 'admin',
        'password': 'mysecretpassword',
        'port': '5432'
    }

    # Connect to the database
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Check if a record with the same date and location already exists
        cursor.execute("""
                SELECT id FROM weather
                WHERE match_date = %s AND location = %s AND match_name = %s
            """, (date, location, match_name))

        existing_record = cursor.fetchone()

        if existing_record:
            # If the record exists, update it
            cursor.execute("""
                    UPDATE weather
                    SET hourly_weather = %s
                    WHERE id = %s
                """, (json.dumps(weather_data, indent=2), existing_record[0]))
            action = "updated"
        else:
            # If the record doesn't exist, insert a new one
            unique_id = generate_unique_id()
            cursor.execute("""
                INSERT INTO weather (id, match_date, location, match_name, hourly_weather)
                VALUES (%s, %s, %s, %s, %s)
            """, (unique_id, date, location, match_name, json.dumps(weather_data, indent=2)))
            action = "added"

        # Commit the changes
        connection.commit()

        print(f"Weather data {action} to the database successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        if connection:
            connection.close()


def extract_weather_data(json_data, city, match_name):
    # Extract relevant information from the json_data
    forecast_data = json_data.get('forecast', {}).get('forecastday', [])
    result = []

    for forecast in forecast_data:
        # Extract hourly data for the given date
        hourly_data = forecast.get('hour', [])

        for hour_data in hourly_data:
            time_epoch = hour_data.get('time_epoch', 0)

            # Convert time_epoch to datetime
            forecast_time = datetime.utcfromtimestamp(time_epoch)

            temp_c = hour_data.get('temp_c', None)
            condition_text = hour_data.get('condition', {}).get('text', None)
            wind_mph = hour_data.get('wind_mph', None)
            cloud = hour_data.get('cloud', None)
            chance_of_rain = hour_data.get('chance_of_rain', None)

            # Append the extracted information to the result list
            result.append({
                'time': forecast_time.strftime('%Y-%m-%d %H:%M'),
                'temp_c': temp_c,
                'condition': condition_text,
                'wind_mph': wind_mph,
                'cloud': cloud,
                'chance_of_rain': chance_of_rain
            })

    return result

@app.route('/pingdb')
def ping_db():
    db_params = {
        'host': 'weather-db.pad',
        'database': 'weather_db',
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


@app.route('/')
def hello_world():
    return "hello world"

@app.route('/get_weather_by_location', methods=['POST'])
def get_weather_by_location():
    try:
        # Get the JSON data from the request
        match_info_list = request.get_json()

        if not isinstance(match_info_list, list):
            return jsonify({'error': 'Request data must be a list of matches'}), 400

        all_weather_data = []

        for match_info in match_info_list:
            if 'city' not in match_info:
                return jsonify({'error': 'Missing "city" key in one of the matches'}), 400

            city = match_info['city']
            match_name = match_info.get('name')
            date_str = match_info.get('date')

            if not date_str:
                return jsonify({'error': 'Missing "date" key in one of the matches'}), 400

            # Manually parse the date string to a valid ISO 8601 format
            date_str = date_str.replace(',', '')  # Remove the comma
            date_str = date_str.replace('GMT', '+0000')  # Convert GMT to +0000
            date_iso = datetime.strptime(date_str, '%a %d %b %Y %H:%M:%S %z').isoformat()

            # Parse the ISO 8601 formatted date string into a datetime object
            date = datetime.fromisoformat(date_iso).astimezone(timezone.utc)

            day = date.day
            month = date.month
            year = date.year

            date_str = f"{year}-{month:02d}-{day:02d}"

            conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")

            headers = {
                'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
                'X-RapidAPI-Host': "weatherapi-com.p.rapidapi.com"
            }

            conn.request("GET", f"/forecast.json?q={city}&days=1&dt={date_str}", headers=headers)

            res = conn.getresponse()
            data = res.read()

            # Parse JSON data if applicable
            json_data = json.loads(data)

            # Extract relevant weather data
            hourly_weather_data = extract_weather_data(json_data, city, match_name)

            # Append additional information to the weather data
            match_info_data = {
                'match_id': match_info['uid'],
                'location': city,
                'match_date': date_str,
                'match_name': match_name,
            }

            all_weather_data.append({
                'match_info': match_info_data,
                'hourly_weather': hourly_weather_data
            })

            # Call the function to add data to the database
            match_weather_to_db(date, city, match_name, hourly_weather_data)

        return jsonify({'success': True, 'data': all_weather_data}), 200

    except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/get_latest_records', methods=['GET'])
def get_latest_records():
    try:
        # Database connection parameters
        db_params = {
            'host': 'weather-db.pad',
            'database': 'weather_db',
            'user': 'admin',
            'password': 'mysecretpassword',
            'port': '5432'
        }

        # Connect to the database
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Retrieve the last 5 records from the 'weather' table
        cursor.execute("""
            SELECT *
            FROM weather
            ORDER BY id DESC
            LIMIT 5;
        """)

        # Fetch the result
        records = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Format the result as a list of dictionaries
        result = []
        for record in records:
            result.append({
                'id': record[0],
                'match_date': record[1],
                'location': record[2],
                'match_name': record[3],
                'hourly_weather': record[4]
            })

        return jsonify({'success': True, 'data': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
