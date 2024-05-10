 \c plantparty_db;


CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(100) UNIQUE,
  password VARCHAR(100),  -- Should be hashed and stored securely
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE plants (
  id SERIAL PRIMARY KEY,
  common_name VARCHAR(100),
  scientific_name VARCHAR(100),
  description TEXT,
  sunlight_requirements VARCHAR(50),  -- e.g., Full Sun, Partial Shade, etc.
  watering_frequency VARCHAR(50),     -- e.g., Daily, Weekly, etc.
  plant_type_id INTEGER,  -- Foreign key to the plant_type table
  FOREIGN KEY (plant_type_id) REFERENCES plant_type(id)  -- Set the foreign key relationship
);


CREATE TABLE plant_type (
  id SERIAL PRIMARY KEY,
  common_name VARCHAR(100) NOT NULL,
  scientific_name VARCHAR(100),
  description TEXT,
  sunlight_requirements VARCHAR(50),  -- e.g., "Full Sun," "Partial Shade"
  watering_frequency VARCHAR(50),    -- e.g., "Daily," "Weekly"
  growth_rate VARCHAR(50),           -- e.g., "Fast," "Slow"
  soil_type VARCHAR(50)              -- e.g., "Loamy," "Sandy"
);




CREATE TABLE favorites (
  id SERIAL PRIMARY KEY,  -- Unique identifier for each favorite record
  user_id INTEGER REFERENCES users(id),  -- Foreign key linking to the user
  plant_type_id INTEGER REFERENCES plants(id),  -- Link to Plant Types
  last_watered DATE,                     -- Last time the plant was watered
  notes TEXT  
  poisonous TEXT
  edible TEXT 
)



CREATE TABLE plant_care_guides (
  id SERIAL PRIMARY KEY,
  plant_id INTEGER REFERENCES plants(id),  -- Which plant this schedule is for
  care_instruction_id INTEGER REFERENCES care_instructions(id),  -- Linked care task
  next_due DATE,                           -- When the next care task is due
  completed BOOLEAN DEFAULT FALSE          -- Whether the task is completed
);


CREATE TABLE care_instructions (
  id SERIAL PRIMARY KEY,
  plant_type_id INTEGER,  -- Reference to the plant_type table
  care_task VARCHAR(100),  -- E.g., "Watering," "Pruning"
  frequency VARCHAR(50),  -- E.g., "Daily," "Weekly"
  details TEXT,  -- Additional details for the care instruction
  FOREIGN KEY (plant_type_id) REFERENCES plant_type(id)  -- Ensure data integrity
);





CREATE TABLE plant_diseases (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,           -- Unique name for the disease
  description TEXT,                   -- Description of the disease
  symptoms TEXT,                      -- Common symptoms
  treatment TEXT                      -- Suggested treatment
);