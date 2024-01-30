package main

import (
	"fmt"
	"io"
	"net/http"
	"sync"
)

var (
	weatherHostnames = []string{"http://weather-hostname.pad:5001", "http://weather-hostname-2.pad:5001"}
	currentIndex     = 0
	mu               sync.Mutex
)

// RoundRobinBalancer returns the next available weather microservice endpoint
func RoundRobinBalancer() string {
	mu.Lock()
	defer mu.Unlock()

	endpoint := weatherHostnames[currentIndex]
	currentIndex = (currentIndex + 1) % len(weatherHostnames)
	return endpoint
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

func main() {
	http.HandleFunc("/weather/forward_weather_forecast", getWeatherRequest)
	http.HandleFunc("/weather/get_weather_history", getWeatherHistory)
	http.HandleFunc("/weather/get_current_weather", getCurrentWeather)
	http.HandleFunc("/weather/get_astro", getAstroInfo)

	fmt.Println("Server is running on http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Error starting the server:", err)
	}
}
