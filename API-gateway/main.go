package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// Response struct for JSON response
type Response struct {
	Message string `json:"message"`
}

func main() {
	// Define the endpoint handler function
	handleTestEndpoint := func(w http.ResponseWriter, r *http.Request) {
		// Create a Response struct
		response := Response{
			Message: "Hello, this is the test endpoint!",
		}

		// Convert the struct to JSON
		jsonResponse, err := json.Marshal(response)
		if err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}

		// Set the content type and write the JSON response
		w.Header().Set("Content-Type", "application/json")
		w.Write(jsonResponse)
	}

	// Set up the server with the endpoint handler
	http.HandleFunc("/test", handleTestEndpoint)

	// Start the server on port 8080
	fmt.Println("Server is running on http://localhost:8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Error starting the server:", err)
	}
}
