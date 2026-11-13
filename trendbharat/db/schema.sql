CREATE TABLE IF NOT EXISTS daily_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT NOT NULL,
    post_index INTEGER DEFAULT 1,
    topic TEXT NOT NULL,
    category TEXT,
    headline TEXT,
    image_url TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(run_date, post_index)
);
