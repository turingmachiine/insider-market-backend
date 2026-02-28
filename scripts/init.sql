-- Football Research Database Initialization
-- Этот скрипт создает только расширения и типы, необходимые для миграций
-- Индексы создаются автоматически через Alembic миграции

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum for positions (если используется в миграциях)
DO $$ BEGIN
    CREATE TYPE player_position AS ENUM (
        'goalkeeper',
        'center_back',
        'left_back',
        'right_back',
        'defensive_midfielder',
        'central_midfielder',
        'attacking_midfielder',
        'left_winger',
        'right_winger',
        'striker',
        'unknown'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
