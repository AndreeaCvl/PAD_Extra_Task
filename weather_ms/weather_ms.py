import requests
from flask import Flask

app = Flask(__name__)

url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

querystring = {"q": "London", "days": "3"}

headers = {
    "X-RapidAPI-Key": "f7afb7df79msh96f3073060722fdp1a3006jsne26bb13d9737",
    "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())


@app.route('/')
def hello_world():
    return "hello world"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
