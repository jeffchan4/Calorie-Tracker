CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL
);

CREATE TABLE cart (
	id INTEGER PRIMARY KEY,
  user_id TEXT,  -- Changed to TEXT to match user table's id data type
  FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE calendar (
  date DATE PRIMARY KEY
);

CREATE TABLE food(
  id INTEGER PRIMARY KEY,
  name TEXT,
  serving INTEGER,
  cart_id INTEGER,
  date DATE,
  FOREIGN KEY (cart_id) REFERENCES cart(id),
  FOREIGN KEY (date) REFERENCES calendar(date)  -- Corrected the reference to calendar table
);
