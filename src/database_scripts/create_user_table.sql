CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL,
                key_type TEXT NOT NULL,
                recovery_phrase TEXT,
                created_at TEXT NOT NULL
            )