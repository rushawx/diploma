-- Database Initialization Script
-- This script sets up the database schema and initial data

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nick_name VARCHAR(128) NOT NULL UNIQUE,
    first_name VARCHAR(128),
    middle_name VARCHAR(128),
    last_name VARCHAR(128),
    email_address VARCHAR(128) UNIQUE,
    phone_number VARCHAR(32) UNIQUE,
    self_bio TEXT,
    user_type VARCHAR(50) DEFAULT 'student',
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    modified_by UUID
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_rus VARCHAR(512) NOT NULL,
    title_eng VARCHAR(512),
    annotation TEXT,
    description TEXT,
    embedding VECTOR(384),
    tags VECTOR(1914),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    modified_by UUID
);
