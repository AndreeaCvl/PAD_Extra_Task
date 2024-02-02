import requests
import json
from flask import Flask, jsonify, request
import psycopg2
import json
import http.client
from datetime import datetime, timezone
from prometheus_client import Counter, Gauge, generate_latest


app = Flask(__name__)

# Define Prometheus counters for total requests
weather_counter = Counter('weather_forecast_requests_total', 'Total number of weather forecast requests', ['endpoint'])


def generate_unique_id():
    # You can use a more robust method to generate unique IDs (e.g., UUID)
    return str(datetime.now())


def get_weather_forecast(location, date):
    date_str = date.replace(',', '')  # Remove the comma
    date_str = date_str.replace('GMT', '+0000')  # Convert GMT to +0000
    date_iso = datetime.strptime(date_str, '%d.%m.%Y').isoformat()

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

    conn.request("GET", f"/forecast.json?q={location}&days=1&dt={date_str}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    weather_data = json.loads(data.decode('utf-8'))

    # Extract relevant information
    forecast = weather_data.get('forecast', {}).get('forecastday', [])

    # Initialize hourly weather dictionary
    hourly_weather = {}

    for hour_data in forecast[0].get('hour', []):
        hour = hour_data.get('time').split()[1]  # Extracting only the hour part
        hourly_weather[hour] = {
            'temp_c': hour_data.get('temp_c'),
            'condition': hour_data.get('condition', {}).get('text'),
            'wind_mph': hour_data.get('wind_mph'),
            'cloud': hour_data.get('cloud'),
            'chance_of_rain': hour_data.get('chance_of_rain', 0)
        }

    # Create the weather_info dictionary
    weather_info = {
        'location': location,
        'forecast_date': date_str,
        'hourly_weather': hourly_weather
    }

    return weather_info


def get_current_weather(city):
    import http.client

    conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "weatherapi-com.p.rapidapi.com"
    }

    conn.request("GET", f"/current.json?q={city}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the JSON response
    weather_data = json.loads(data.decode("utf-8"))

    # Extract relevant information
    current_weather = weather_data.get('current', {})
    location_data = weather_data.get('location', {})

    # Extracting date and time
    date_time_str = location_data.get('localtime', '')
    date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    date = date_time.strftime('%Y-%m-%d')
    hour = date_time.strftime('%H:%M')

    # Creating the result dictionary
    result_dict = {
        'date': date,
        'city_name': location_data.get('name'),
        'hour': hour,
        'temp_c': current_weather.get('temp_c'),
        'condition': current_weather.get('condition', {}).get('text'),
        'wind_mph': current_weather.get('wind_mph'),
        'cloud': current_weather.get('cloud')
    }

    return result_dict


def get_weather_history_by_location_date(location, date):
    conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "weatherapi-com.p.rapidapi.com"
    }

    # Parse the input date in the format "day.month.year"
    day, month, year = map(int, date.split('.'))
    date_iso = datetime(year, month, day).isoformat()
    date_str = date_iso.split('T')[0]  # Extracting only the date part

    conn.request("GET", f"/history.json?q={location}&dt={date_str}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Parse the JSON response
    weather_data = json.loads(data.decode("utf-8"))

    # Extract relevant information
    location_data = weather_data.get('location', {})
    forecast = weather_data.get('forecast', {})

    # Extracting hourly weather information
    hourly_weather = {}
    for hour_data in forecast.get('forecastday', [{}])[0].get('hour', []):
        hour = hour_data.get('time').split()[1]  # Extracting only the hour part
        hourly_weather[hour] = {
            'temp_c': hour_data.get('temp_c'),
            'condition': hour_data.get('condition', {}).get('text'),
            'wind_mph': hour_data.get('wind_mph'),
            'cloud': hour_data.get('cloud'),
            'chance_of_rain': hour_data.get('chance_of_rain', 0)
        }

    # Create the result dictionary
    result_dict = {
        'date': date_str,
        'city_name': location_data.get('name'),
        'hourly_weather': hourly_weather
    }

    return result_dict


def get_astro(city, date):
    conn = http.client.HTTPSConnection("weatherapi-com.p.rapidapi.com")

    # Parse the input date in the format "day.month.year"
    day, month, year = map(int, date.split('.'))
    date_iso = datetime(year, month, day).isoformat()
    date_str = date_iso.split('T')[0]  # Extracting only the date part

    headers = {
        'X-RapidAPI-Key': "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
        'X-RapidAPI-Host': "weatherapi-com.p.rapidapi.com"
    }

    conn.request("GET", f"/astronomy.json?q={city}&dt={date}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    astronomy_data = json.loads(data.decode("utf-8"))

    # Extract relevant information
    location_data = astronomy_data.get('location', {})
    astronomy = astronomy_data.get('astronomy', {}).get('astro', {})

    # Create the result dictionary
    result_dict = {
        'city_name': location_data.get('name'),
        'date': date,
        'sunrise': astronomy.get('sunrise'),
        'sunset': astronomy.get('sunset'),
        'moonrise': astronomy.get('moonrise'),
        'moonset': astronomy.get('moonset'),
    }

    return result_dict


def record_exists(location, forecast_date, cursor):
    cursor.execute("SELECT COUNT(*) FROM weather WHERE location = %s AND match_date = %s", (location, forecast_date))
    return cursor.fetchone()[0] > 0


def insert_into_database(weather_info):
    # Generate a unique ID for the data
    unique_id = generate_unique_id()
    try:
        # Database connection parameters
        db_params = {
            'host': 'weather-db.pad',
            'database': 'weather_db',
            'user': 'admin',
            'password': 'mysecretpassword',
            'port': '5432'
        }

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Extract relevant information
        location = weather_info['location']
        forecast_date = datetime.strptime(weather_info['forecast_date'], '%Y-%m-%d').date()
        hourly_weather = weather_info['hourly_weather']

        # Convert the hourly_weather dictionary to JSON format
        hourly_weather_json = json.dumps(hourly_weather)

        # Check if the record already exists
        if not record_exists(location, forecast_date, cursor):
            # Insert data into the PostgreSQL table
            cursor.execute(
                "INSERT INTO weather (id, match_date, location, hourly_weather) VALUES (%s, %s, %s, %s)",
                (location + forecast_date.isoformat(), forecast_date, location, hourly_weather_json)
            )
            connection.commit()
        else:
            print("Record already exists in the database.")

        cursor.close()
        connection.close()

    except Exception as e:
        print("Error inserting into database:", e)


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


@app.route('/get_all_records', methods=['GET'])
def get_all_records():
    try:
        # Database connection parameters
        db_params = {
            'host': 'weather-db.pad',
            'database': 'weather_db',
            'user': 'admin',
            'password': 'mysecretpassword',
            'port': '5432'
        }

        # Establish the database connection
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Fetch all records from the 'weather' table
        cursor.execute("SELECT * FROM weather")
        records = cursor.fetchall()

        # Convert the records to a list of dictionaries
        records_list = []
        for record in records:
            record_dict = {
                'id': record[0],
                'forecast_date': record[1].isoformat(),
                'location': record[2],
                'hourly_weather': record[3]
            }
            records_list.append(record_dict)

        # Close cursor and connection
        cursor.close()
        connection.close()

        return jsonify(records_list)

    except Exception as e:
        return jsonify({'error': f'Error fetching records from the database: {e}'})



# Define the Flask endpoint for the weather forecast
@app.route('/weather_forecast', methods=['GET'])
def weather_forecast():
    weather_counter.labels(endpoint='weather_forecast').inc()

    # Get parameters from the query string
    location = request.args.get('location')
    date = request.args.get('date')

    # Validate parameters
    if not location or not date:
        return jsonify({'error': 'Location and date are required parameters'}), 400

    try:

        # Call the get_weather_forecast function
        weather_info = get_weather_forecast(location, date)

        # Call the get_weather_forecast function
        weather_info = get_weather_forecast(location, date)

        # Insert the data into the PostgreSQL database
        insert_into_database(weather_info)

        return jsonify(weather_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Define the Flask endpoint for current weather
@app.route('/current_weather', methods=['GET'])
def current_weather():
    weather_counter.labels(endpoint='current_weather').inc()

    # Get the 'city' parameter from the query string
    city = request.args.get('city')

    # Validate parameters
    if not city:
        return jsonify({'error': 'City is a required parameter'}), 400

    try:
        # Call the get_current_weather function
        weather_info = get_current_weather(city)
        return jsonify(weather_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/weather_history', methods=['GET'])
def weather_history():

    weather_counter.labels(endpoint='weather_history').inc()

    # Get parameters from the query string
    location = request.args.get('location')
    date = request.args.get('date')

    # Validate parameters
    if not location or not date:
        return jsonify({'error': 'Location and date are required parameters'}), 400

    try:
        # Call the get_weather_history_by_location_date function
        weather_info = get_weather_history_by_location_date(location, date)
        return jsonify(weather_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/astro', methods=['GET'])
def astro():

    weather_counter.labels(endpoint='astro').inc()

    # Get parameters from the query string
    city = request.args.get('city')
    date = request.args.get('date')

    # Validate parameters
    if not city or not date:
        return jsonify({'error': 'City and date are required parameters'}), 400

    try:
        # Call the get_astro function
        astro_info = get_astro(city, date)
        return jsonify(astro_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'OK'})


# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
