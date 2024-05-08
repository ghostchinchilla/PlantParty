User
can you help me build a create-react-app based on this .sql file? \c plantparty_db;


CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(100) UNIQUE,
  password VARCHAR(100),  -- Should be hashed and stored securely
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




CREATE TABLE plant_types (
  id SERIAL PRIMARY KEY,
  common_name VARCHAR(100),
  scientific_name VARCHAR(100),
  description TEXT,
  sunlight_requirements VARCHAR(50),  -- e.g., Full Sun, Partial Shade, etc.
  watering_frequency VARCHAR(50),     -- e.g., Daily, Weekly, etc.
);






CREATE TABLE plants (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),  -- Foreign key linking to Users
  plant_type_id INTEGER REFERENCES plant_types(id),  -- Link to Plant Types
  last_watered DATE,                     -- Last time the plant was watered
  notes TEXT  
  poisonous TEXT
  edible TEXT                          
);






CREATE TABLE care_instructions (
  id SERIAL PRIMARY KEY,
  plant_type_id INTEGER REFERENCES plant_types(id),  -- Which plant type this applies to
  care_task VARCHAR(50),                             -- e.g., Watering, Pruning, etc.
  frequency VARCHAR(50),                             -- e.g., Daily, Weekly, etc.
  details TEXT                                       -- Additional care details
);






CREATE TABLE plant_care_schedules (
  id SERIAL PRIMARY KEY,
  plant_id INTEGER REFERENCES plants(id),  -- Which plant this schedule is for
  care_instruction_id INTEGER REFERENCES care_instructions(id),  -- Linked care task
  next_due DATE,                           -- When the next care task is due
  completed BOOLEAN DEFAULT FALSE          -- Whether the task is completed
);






CREATE TABLE plant_diseases (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE,           -- Unique name for the disease
  description TEXT,                   -- Description of the disease
  symptoms TEXT,                      -- Common symptoms
  treatment TEXT                      -- Suggested treatment
);






CREATE TABLE plant_type_diseases (
  id SERIAL PRIMARY KEY,
  plant_type_id INTEGER REFERENCES plant_types(id),  -- Foreign key to plant types
  plant_disease_id INTEGER REFERENCES plant_diseases(id),  -- Foreign key to plant diseases
  UNIQUE(plant_type_id, plant_disease_id)  -- Ensures unique combinations
);








CREATE TABLE user_reports (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  plant_id INTEGER REFERENCES plants(id),
  plant_disease_id INTEGER REFERENCES plant_diseases(id),
  report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  comments TEXT
);