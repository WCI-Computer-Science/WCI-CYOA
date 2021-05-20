CREATE TABLE test_users (
    email TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    clicks INT DEFAULT 0
);
