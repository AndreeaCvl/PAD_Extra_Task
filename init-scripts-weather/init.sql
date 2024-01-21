CREATE TABLE weather (
  id VARCHAR(50) PRIMARY KEY,
  match_date DATE NOT NULL,
  location VARCHAR(100) NOT NULL,
  match_name VARCHAR(200) NOT NULL,
  hourly_weather JSONB
);
