/*user table*/
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('client','professional','admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


  /*2. Professionals Table (with skills for AI)*/
CREATE TABLE professionals (
    professional_id SERIAL PRIMARY KEY,
	full_name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    profession VARCHAR(100) NOT NULL,
    skills TEXT[], -- used by AI model for matching
    experience_years INT,
    rating DECIMAL(3,2) DEFAULT 0.0,
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- for geo-location search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* 3. Jobs Table */
CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) CHECK (status IN ('open','assigned','completed','cancelled')) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* 4. AI Suggestions Table */
CREATE TABLE ai_suggestions (
    suggestion_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    professional_id INT NOT NULL REFERENCES professionals(professional_id) ON DELETE CASCADE,
    confidence_score DECIMAL(4,3) NOT NULL, -- AI ranking score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* 5. Payments Table (with M-Pesa) */
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    client_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    professional_id INT NOT NULL REFERENCES professionals(professional_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(20) CHECK (method IN ('mpesa','card','paypal')) DEFAULT 'mpesa',
    transaction_id VARCHAR(100) UNIQUE,
    status VARCHAR(20) CHECK (status IN ('pending','paid','failed','refunded')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS professionals;
                                                                                                                                     
DROP TABLE professionals CASCADE;

 /* 2. Professionals Table (with skills for AI) */
CREATE TABLE professionals (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    profession VARCHAR(100) NOT NULL,
    skills TEXT[], -- used by AI model for matching
    experience_years INT,
    rating DECIMAL(3,2) DEFAULT 0.0,
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- for geo-location search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO professionals (full_name, profession, location, experience_years, rating)
VALUES
('John Doe', 'Plumber', ST_SetSRID(ST_MakePoint(36.8219, -1.2921), 4326)::geography, 5, 4.5),
('Mary Wanjiku', 'Electrician', ST_SetSRID(ST_MakePoint(36.8075, -1.3032), 4326)::geography, 3, 4.2),
('Ali Yusuf', 'Chef', ST_SetSRID(ST_MakePoint(36.8210, -1.3000), 4326)::geography, 7, 4.8);

INSERT INTO professionals (full_name, user_id, profession, skills, experience_years, location)
VALUES (
    'Jane Doe',
    1,
    'Software Engineer',
    ARRAY['Python', 'Django', 'PostgreSQL'],
    5,
    ST_SetSRID(ST_MakePoint(36.8219, -1.2921), 4326) -- Nairobi coords
);
