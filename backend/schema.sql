
-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Machines Table
CREATE TABLE IF NOT EXISTS machines (
    id SERIAL PRIMARY KEY,
    machine_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    price_per_page FLOAT DEFAULT 5.0,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Admin Machine Map (Relation)
CREATE TABLE IF NOT EXISTS admin_machine_map (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER UNIQUE NOT NULL,
    machine_id INTEGER UNIQUE NOT NULL,
    CONSTRAINT fk_admin FOREIGN KEY (admin_id) REFERENCES admins(id),
    CONSTRAINT fk_machine FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- 4. Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    machine_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'CREATED',
    file_url VARCHAR(500),
    file_name VARCHAR(255),
    page_count INTEGER DEFAULT 0,
    price_per_page FLOAT,
    total_amount FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_machine FOREIGN KEY (machine_id) REFERENCES machines(id)
);

-- 5. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    session_id INTEGER UNIQUE NOT NULL,
    amount FLOAT NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'PENDING',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_session FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- 6. Print Jobs Table
CREATE TABLE IF NOT EXISTS print_jobs (
    id SERIAL PRIMARY KEY,
    session_id INTEGER UNIQUE NOT NULL,
    file_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'PENDING',
    lp_job_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_print_session FOREIGN KEY (session_id) REFERENCES sessions(id)
);
