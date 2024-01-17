import requests
import json
from flask import Flask, jsonify
import psycopg2
import http.client
from datetime import datetime

app = Flask(__name__)

url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

querystring = {"q": "London", "days": "3"}

headers = {
    "X-RapidAPI-Key": "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
    "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())



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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
