CREATE TABLE matches (
  uid VARCHAR (50) PRIMARY KEY,
  match_date DATE NOT NULL,
  match_name VARCHAR (200) NOT NULL,
  venue VARCHAR (100) NOT NULL,
  city VARCHAR (100) NOT NULL,
  state VARCHAR (50) NOT NULL,
  country VARCHAR (100) NOT NULL
);
