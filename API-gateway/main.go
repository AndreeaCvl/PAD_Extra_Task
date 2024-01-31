package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
)

var (
	weatherHostnames = []string{"http://weather-hostname.pad:5001", "http://weather-hostname-2.pad:5001"}
	currentIndex     = 0
	mu               sync.Mutex
)

var (
	matchesHostnames    = []string{"http://matches-hostname.pad:5000", "http://matches-hostname-2.pad:5000"}
	matchesCurrentIndex = 0
	matchesMu           sync.Mutex
)

// RoundRobinBalancer returns the next available weather microservice endpoint
func RoundRobinBalancer() string {
	mu.Lock()
	defer mu.Unlock()

	endpoint := weatherHostnames[currentIndex]
	currentIndex = (currentIndex + 1) % len(weatherHostnames)
	return endpoint
}

// returns the next available matches microservice endpoint
func MatchesBalancer() string {
	matchesMu.Lock()
	defer matchesMu.Unlock()

	endpointMatches := matchesHostnames[matchesCurrentIndex]
	matchesCurrentIndex = (matchesCurrentIndex + 1) % len(matchesHostnames)
	return endpointMatches
}

// ForwardRequest forwards the incoming request to the Flask microservice
func getWeatherRequest(w http.ResponseWriter, r *http.Request) {
	// Set the URL of the Flask microservice endpoint
	//url := "http://weather-hostname.pad:5001/weather_forecast"
	url := RoundRobinBalancer() + "/weather_forecast"

	// Get query parameters from the incoming request
	location := r.URL.Query().Get("location")
	date := r.URL.Query().Get("date")

	// Validate parameters
	if location == "" || date == "" {
		http.Error(w, "Location and date are required parameters", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request", http.StatusInternalServerError)
		return
	}

	// Set query parameters
	q := req.URL.Query()
	q.Add("location", location)
	q.Add("date", date)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client
	w.WriteHeader(resp.StatusCode)
	w.Write(body)

}

// GetCurrentWeather connects to the Flask microservice's /current_weather endpoint
func getCurrentWeather(w http.ResponseWriter, r *http.Request) {
	// Set the URL of the Flask microservice endpoint for current weather
	//url := "http://weather-hostname.pad:5001/current_weather"
	url := RoundRobinBalancer() + "/current_weather"

	// Get query parameters from the incoming request
	city := r.URL.Query().Get("city")

	// Validate parameters
	if city == "" {
		http.Error(w, "City is a required parameter", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice for current weather
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request for current weather", http.StatusInternalServerError)
		return
	}

	// Set query parameters for current weather
	q := req.URL.Query()
	q.Add("city", city)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice for current weather
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice for current weather", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice for current weather
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice for current weather", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client for current weather
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

// GetWeatherHistory connects to the Flask microservice's /weather_history endpoint
func getWeatherHistory(w http.ResponseWriter, r *http.Request) {
	// Set the URL of the Flask microservice endpoint for weather history
	//url := "http://weather-hostname.pad:5001/weather_history"
	url := RoundRobinBalancer() + "/weather_history"

	// Get query parameters from the incoming request
	location := r.URL.Query().Get("location")
	date := r.URL.Query().Get("date")

	// Validate parameters
	if location == "" || date == "" {
		http.Error(w, "Location and date are required parameters", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice for weather history
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request for weather history", http.StatusInternalServerError)
		return
	}

	// Set query parameters for weather history
	q := req.URL.Query()
	q.Add("location", location)
	q.Add("date", date)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice for weather history
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice for weather history", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice for weather history
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice for weather history", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client for weather history
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

// GetAstroInfo connects to the Flask microservice's /astro endpoint
func getAstroInfo(w http.ResponseWriter, r *http.Request) {
	// Set the URL of the Flask microservice endpoint for astro information
	//url := "http://weather-hostname.pad:5001/astro"
	url := RoundRobinBalancer() + "/astro"

	// Get query parameters from the incoming request
	city := r.URL.Query().Get("city")
	date := r.URL.Query().Get("date")

	// Validate parameters
	if city == "" || date == "" {
		http.Error(w, "City and date are required parameters", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice for astro information
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request for astro information", http.StatusInternalServerError)
		return
	}

	// Set query parameters for astro information
	q := req.URL.Query()
	q.Add("city", city)
	q.Add("date", date)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice for astro information
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice for astro information", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice for astro information
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice for astro information", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client for astro information
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

// Function to fetch upcoming matches from matches_ms
func getUpcomingMatches(w http.ResponseWriter, r *http.Request) {
	url := MatchesBalancer() + "/upcoming_matches"

	client := http.Client{}
	resp, err := client.Get(url)
	if err != nil {
		http.Error(w, "Error making request to matches_ms for upcoming matches", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the matches_ms
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from matches_ms for upcoming matches", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

func getTodayMatches(w http.ResponseWriter, r *http.Request) {
	url := MatchesBalancer() + "/today_matches"

	client := http.Client{}
	resp, err := client.Get(url)
	if err != nil {
		http.Error(w, "Error making request to matches_ms for today's matches", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from matches_ms
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from matches_ms for today's matches", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

// GetPastMatches connects to the Flask microservice's /past_matches endpoint
func getPastMatches(w http.ResponseWriter, r *http.Request) {
	url := MatchesBalancer() + "/past_matches"

	// Get query parameters from the incoming request
	targetDate := r.URL.Query().Get("target_date")

	// Validate parameters
	if targetDate == "" {
		http.Error(w, "Target date is a required parameter", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice for past matches
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request for past matches", http.StatusInternalServerError)
		return
	}

	// Set query parameters for past matches
	q := req.URL.Query()
	q.Add("target_date", targetDate)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice for past matches
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice for past matches", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice for past matches
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice for past matches", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client for past matches
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

func getTeamInfo(w http.ResponseWriter, r *http.Request) {
	url := MatchesBalancer() + "/team_info"

	// Get query parameters from the incoming request
	gameID := r.URL.Query().Get("game_id")

	// Validate parameters
	if gameID == "" {
		http.Error(w, "Game ID is a required parameter", http.StatusBadRequest)
		return
	}

	// Create a new request to the Flask microservice for team info
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		http.Error(w, "Error creating request for team info", http.StatusInternalServerError)
		return
	}

	// Set query parameters for team info
	q := req.URL.Query()
	q.Add("game_id", gameID)
	req.URL.RawQuery = q.Encode()

	// Make the request to the Flask microservice for team info
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error making request to Flask microservice for team info", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read the response from the Flask microservice for team info
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response from Flask microservice for team info", http.StatusInternalServerError)
		return
	}

	// Forward the response to the client for team info
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

type WeatherForecastResponse struct {
	ForecastDate  string                   `json:"forecast_date"`
	HourlyWeather map[string]HourlyWeather `json:"hourly_weather"`
}

type HourlyWeather struct {
	ChanceOfRain int     `json:"chance_of_rain"`
	Cloud        int     `json:"cloud"`
	Condition    string  `json:"condition"`
	TempC        float64 `json:"temp_c"`
	WindMPH      float64 `json:"wind_mph"`
}

type Match struct {
	City          string `json:"city"`
	Country       string `json:"country"`
	Date          string `json:"date"`
	Name          string `json:"name"`
	State         string `json:"state"`
	UID           string `json:"uid"`
	VenueFullName string `json:"venue_full_name"`
}

type WeatherForecastResponseWithInfo struct {
	City     string                  `json:"city"`
	UID      string                  `json:"uid"`
	Forecast WeatherForecastResponse `json:"forecast"`
}

func getMatchesWeatherForecast(w http.ResponseWriter, r *http.Request) {
	// Step 1: Get upcoming matches
	matchesURL := MatchesBalancer() + "/upcoming_matches"
	matchesResp, err := http.Get(matchesURL)
	if err != nil {
		http.Error(w, "Error making request to matches_ms for upcoming matches", http.StatusInternalServerError)
		return
	}
	defer matchesResp.Body.Close()

	matchesBody, err := io.ReadAll(matchesResp.Body)
	if err != nil {
		http.Error(w, "Error reading response from matches_ms for upcoming matches", http.StatusInternalServerError)
		return
	}

	// Parse the matches response
	var matches []Match // Replace Match with the actual struct type for your matches
	if err := json.Unmarshal(matchesBody, &matches); err != nil {
		http.Error(w, "Error parsing upcoming matches response", http.StatusInternalServerError)
		return
	}

	// Step 2: Get weather forecast for each location
	var forecasts []WeatherForecastResponseWithInfo
	for _, match := range matches {
		// Skip if city is empty
		if match.City == "" {
			continue
		}

		// Replace spaces with "&" for multi-word cities
		cityQuery := strings.ReplaceAll(match.City, " ", "&")

		weatherURL := RoundRobinBalancer() + "/weather_forecast?location=" + cityQuery + "&date=" + match.Date
		weatherResp, err := http.Get(weatherURL)
		if err != nil {
			http.Error(w, "Error making request to weather microservice", http.StatusInternalServerError)
			return
		}
		defer weatherResp.Body.Close()

		weatherBody, err := io.ReadAll(weatherResp.Body)
		if err != nil {
			http.Error(w, "Error reading response from weather microservice", http.StatusInternalServerError)
			return
		}

		// Parse the weather response
		var forecast WeatherForecastResponse
		if err := json.Unmarshal(weatherBody, &forecast); err != nil {
			fmt.Printf("Error parsing weather forecast response: %v\n", err)
			fmt.Printf("Response body: %s\n", string(weatherBody))
			http.Error(w, "Error parsing weather forecast response", http.StatusInternalServerError)
			return
		}

		forecasts = append(forecasts, WeatherForecastResponseWithInfo{
			City:     match.City,
			UID:      match.UID,
			Forecast: forecast,
		})
	}

	// Step 3: Return the combined forecast to the user
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(forecasts)
}

type CurrentWeatherResponse struct {
	CityName  string  `json:"city_name"`
	Cloud     int     `json:"cloud"`
	Condition string  `json:"condition"`
	Date      string  `json:"date"`
	Hour      string  `json:"hour"`
	TempC     float64 `json:"temp_c"`
	WindMPH   float64 `json:"wind_mph"`
}

type CombinedPastMatchResponse struct {
	City          string                   `json:"city"`
	UID           string                   `json:"uid"`
	CityName      string                   `json:"city_name"`
	Date          string                   `json:"date"`
	HourlyWeather map[string]HourlyWeather `json:"hourly_weather"`
}

// GetTodayMatchesAndWeather fetches today's matches and current weather for each city
func getTodayMatchesAndWeather(w http.ResponseWriter, r *http.Request) {
	// Step 1: Get today's matches
	matchesURL := MatchesBalancer() + "/today_matches"
	matchesResp, err := http.Get(matchesURL)
	if err != nil {
		http.Error(w, "Error making request to matches_ms for today's matches", http.StatusInternalServerError)
		return
	}
	defer matchesResp.Body.Close()

	matchesBody, err := io.ReadAll(matchesResp.Body)
	if err != nil {
		http.Error(w, "Error reading response from matches_ms for today's matches", http.StatusInternalServerError)
		return
	}

	// Parse the matches response
	var matches []Match // Replace Match with the actual struct type for your matches
	if err := json.Unmarshal(matchesBody, &matches); err != nil {
		http.Error(w, "Error parsing today's matches response", http.StatusInternalServerError)
		return
	}

	// Step 2: Find unique cities where matches are held
	citiesMap := make(map[string]bool)
	for _, match := range matches {
		citiesMap[match.City] = true
	}

	// Step 3: Get current weather for each city
	var weatherResponses []struct {
		City    string                 `json:"city"`
		Weather CurrentWeatherResponse `json:"weather"`
	}

	for city := range citiesMap {
		// Replace spaces with "&" for multi-word cities
		cityQuery := strings.ReplaceAll(city, " ", "&")

		weatherURL := RoundRobinBalancer() + "/current_weather?city=" + cityQuery
		weatherResp, err := http.Get(weatherURL)
		if err != nil {
			http.Error(w, "Error making request to weather microservice for current weather", http.StatusInternalServerError)
			return
		}
		defer weatherResp.Body.Close()

		weatherBody, err := io.ReadAll(weatherResp.Body)
		if err != nil {
			http.Error(w, "Error reading response from weather microservice for current weather", http.StatusInternalServerError)
			return
		}

		// Parse the weather response
		var currentWeather CurrentWeatherResponse
		if err := json.Unmarshal(weatherBody, &currentWeather); err != nil {
			http.Error(w, "Error parsing current weather response", http.StatusInternalServerError)
			return
		}

		weatherResponses = append(weatherResponses, struct {
			City    string                 `json:"city"`
			Weather CurrentWeatherResponse `json:"weather"`
		}{
			City:    city,
			Weather: currentWeather,
		})
	}

	// Step 4: Combine the responses and return to the user
	response := struct {
		Weather []struct {
			City    string                 `json:"city"`
			Weather CurrentWeatherResponse `json:"weather"`
		} `json:"weather"`
	}{
		Weather: weatherResponses,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

type PastMatch struct {
	City          string `json:"city"`
	Country       string `json:"country"`
	Date          string `json:"date"`
	Name          string `json:"name"`
	State         string `json:"state"`
	UID           string `json:"uid"`
	VenueFullName string `json:"venue_full_name"`
}

type WeatherHistoryResponse struct {
	CityName      string                   `json:"city_name"`
	Date          string                   `json:"date"`
	HourlyWeather map[string]HourlyWeather `json:"hourly_weather"`
}

// GetPastMatchesMeteo combines past matches and weather history for a specific date
func getPastMatchesMeteo(w http.ResponseWriter, r *http.Request) {
	// Get query parameter from the incoming request
	targetDate := r.URL.Query().Get("date")

	// Validate parameters
	if targetDate == "" {
		http.Error(w, "Date is a required parameter", http.StatusBadRequest)
		return
	}

	// Step 1: Get past matches
	matchesURL := MatchesBalancer() + "/past_matches?target_date=" + targetDate
	matchesResp, err := http.Get(matchesURL)
	if err != nil {
		http.Error(w, "Error making request to matches_ms for past matches", http.StatusInternalServerError)
		return
	}
	defer matchesResp.Body.Close()

	matchesBody, err := io.ReadAll(matchesResp.Body)
	if err != nil {
		http.Error(w, "Error reading response from matches_ms for past matches", http.StatusInternalServerError)
		return
	}

	// Parse the matches response
	var matches []PastMatch
	if err := json.Unmarshal(matchesBody, &matches); err != nil {
		http.Error(w, "Error parsing past matches response", http.StatusInternalServerError)
		return
	}

	// Step 2: Get weather history for each city
	var combinedResponses []CombinedPastMatchResponse

	for _, match := range matches {
		cityName := url.QueryEscape(match.City)
		cityName = strings.ReplaceAll(cityName, "+", "&")

		weatherURL := RoundRobinBalancer() + "/weather_history?location=" + cityName + "&date=" + match.Date
		weatherResp, err := http.Get(weatherURL)
		if err != nil {
			http.Error(w, "Error making request to weather microservice for weather history", http.StatusInternalServerError)
			return
		}
		defer weatherResp.Body.Close()

		weatherBody, err := io.ReadAll(weatherResp.Body)
		if err != nil {
			http.Error(w, "Error reading response from weather microservice for weather history", http.StatusInternalServerError)
			return
		}

		// Parse the weather response
		var weatherHistory WeatherHistoryResponse
		if err := json.Unmarshal(weatherBody, &weatherHistory); err != nil {
			http.Error(w, "Error parsing weather history response", http.StatusInternalServerError)
			return
		}

		combinedResponses = append(combinedResponses, CombinedPastMatchResponse{
			City:          match.City,
			UID:           match.UID,
			CityName:      weatherHistory.CityName,
			Date:          weatherHistory.Date,
			HourlyWeather: weatherHistory.HourlyWeather,
		})
	}

	// Step 3: Combine the responses and return to the user
	response := struct {
		Weather []CombinedPastMatchResponse `json:"weather_history"`
	}{
		Weather: combinedResponses,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/weather/forward_weather_forecast", getWeatherRequest)
	http.HandleFunc("/weather/get_weather_history", getWeatherHistory)
	http.HandleFunc("/weather/get_current_weather", getCurrentWeather)
	http.HandleFunc("/weather/get_astro", getAstroInfo)

	http.HandleFunc("/matches/upcoming_matches", getUpcomingMatches)
	http.HandleFunc("/matches/get_today_matches", getTodayMatches)
	http.HandleFunc("/matches/past_matches", getPastMatches)
	http.HandleFunc("/matches/team_info", getTeamInfo)

	http.HandleFunc("/meteo_for_future_matches", getMatchesWeatherForecast)
	http.HandleFunc("/meteo_for_today_matches", getTodayMatchesAndWeather)
	http.HandleFunc("/past_matches_meteo", getPastMatchesMeteo)

	fmt.Println("Server is running on http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Error starting the server:", err)
	}
}
