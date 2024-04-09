-- Creating the DIM_user table
CREATE TABLE dim_users (
    id INT PRIMARY KEY,
    user_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Creating the DIM_Plans table
CREATE TABLE dim_plans (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Creating the Activity table
CREATE TABLE activity (
    session_id SERIAL PRIMARY KEY,
    user_id INT,
    plan_id INT,
    Event_type VARCHAR(255) CHECK (Event_type = 'add new task'), -- Assuming only 'add new task' is supported
    task_content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES dim_users(id),
    FOREIGN KEY (plan_id) REFERENCES dim_plans(id)
);

INSERT INTO dim_users (id, user_name, created_at) VALUES (2009, 'Alleria', NOW());
SELECT * FROM dim_users;

-- drop table activity;
-- drop table dim_plans;
-- drop table dim_users;

-- SELECT * FROM dim_plans;