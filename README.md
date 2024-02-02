# PAD EXTRA TASK
App that includes weather forecasts for match locations.
### HOW TO RUN
First obtain the images from https://hub.docker.com/repository/docker/andreeacvl/pad_extra_task/general
Clone this repository by doing git clone <repo>
Run the command docker-compose up

Use the postman collection of requests provided here to test the app. 
You can find below a short description of how it works.

### API-s used:
NHL API - https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/nhl-api5
WeatherAPI.com - https://rapidapi.com/weatherapi/api/weatherapi-com

### Matches Microservice:
Is built in flask and used for:
- obtaining upcoming NHL matches;
- obtaining NHL matches happening today (sometimes there might be an empty return if no matches);
- obtaining NHL matches which happened in the past, by providing a date;
- obtaining info about teams by providing the Game ID..

There are 3 replicas of this microservice, which you can see in the docker-compose file, or they would appear as separate containers.
It has its own database build with postgres, with the following schema:
```sql
CREATE TABLE matches (
  uid VARCHAR (50) PRIMARY KEY,
  match_date DATE NOT NULL,
  match_name VARCHAR (200) NOT NULL,
  venue VARCHAR (100) NOT NULL,
  city VARCHAR (100) NOT NULL,
  state VARCHAR (50) NOT NULL,
  country VARCHAR (100) NOT NULL
);
```
In the database are added the upcoming matches.
This microservice features a '/status' endpoint.


### Weeather Microservice:
Is built in flask and used for:
- obtaining the weather forecast for a given location and date in the future;
- obtaining the weather now for a specific location;
- btaining the weather in the past for a specific location and time;
- obtaining info about teams by providing the Game ID.

There are 3 replicas of this microservice, which you can see in the docker-compose file, or they would appear as separate containers.
It has its own database build with postgres, with the following schema:
```sql
CREATE TABLE weather (
  id VARCHAR(50) PRIMARY KEY,
  match_date DATE NOT NULL,
  location VARCHAR(100) NOT NULL,
  hourly_weather JSONB
);
```
In the database I add the weather forecast.
This microservice also features a '/status' endpoint.

### Gateway
Build in Golang. Features a Load Blancer and implements redis cache for all endpoints. Has 8 endpoints for each service endpoint and 3 aggregation endpoints:
- get meteo for future matches;
- get weather for today matches;
- get weather for past matches.

It also contains a status endpoint which checks if all replicas of the microservices and the gateway itself are alive, and returns the status (OK/Unhealthy).

##### Load Balancer:
It is defined in the gateway. I all the addresses of the replicas in 2 lists -  weatherHostnames and matchesHostnames. And 2 functions which must give the next weather/matches endpoint.
```go
var (
	weatherHostnames = []string{"http://weather-hostname.pad:5001", "http://weather-hostname-2.pad:5001",
		"http://weather-hostname-3.pad:5001"}
	currentIndex = 0
	mu           sync.Mutex
)

// RoundRobinBalancer returns the next available weather microservice endpoint
func RoundRobinBalancer() string {
	mu.Lock()
	defer mu.Unlock()

	endpoint := weatherHostnames[currentIndex]
	currentIndex = (currentIndex + 1) % len(weatherHostnames)
	return endpoint
}
```
Then, when making a request, the endpoint address if found in this way:
```	go
url := RoundRobinBalancer() + "/endpoint_name"
```
##### Concurrent task limit and Task Timeout
Those are set with the Hystrix - a fault tolerance library developed by netflix.
I needed to set the configuration for the request using the following parameters:
```go 
hystrix.ConfigureCommand("getAstroInfo", hystrix.CommandConfig{
    Timeout:               1000, // Timeout in milliseconds
	MaxConcurrentRequests: 10,  // Maximum number of concurrent requests
	ErrorPercentThreshold: 25,   // Error percentage threshold for circuit breaker
})
```
Then did the request using the configuration. I usually set big values for timeout, to give the services time to return the answer, since there is lots of data to be parsed which may happen pretty slow.

##### Redis Cache
Every time before making a request, the program checks if there is any data saved in the redis cache db. The cache key is created by taking into account the parameters a request receives. If the request doesn't receive any parameters but relies on the today's date - it is also taken into account.
```
	cacheKey := "past_matches_" + targetDate
	// Check if the result is already in the cache
	cachedResult, err := redisClient.Get(context.Background(), cacheKey).Result()
	if err == nil {
		// If cached result is found, return it
		w.Write([]byte(cachedResult))
		return
	}
```

### Prometheus + Grafana
Prometheus is connected to both microservices and Grafana is ocnnected to Prometheus for metrics and statistics.
To check the metrics, you can go on the page http://localhost:3000/login, log in using admin as a username and a password, then go to the explore tab from the left menue. Here you can create a new query as in the image below and you must see the statistics.

### Postman Collenction
It can be found as a json file in the repo.
