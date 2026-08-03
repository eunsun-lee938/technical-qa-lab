CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,

    event_type VARCHAR(30) NOT NULL
        CHECK (
            event_type IN (
                'LOGIN_SUCCESS',
                'LOGIN_FAILED',
                'ACCESS_DENIED'
            )
        ),

    username VARCHAR(50),

    endpoint VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);