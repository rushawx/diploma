CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE user_type_enum AS ENUM (
    'student',
    'researcher',
    'mentor',
    'admin'
);

CREATE TYPE connection_type_enum AS ENUM (
    'owner',
    'participant',
    'observer',
    'applicant'
);

CREATE TYPE rating_enum AS ENUM (
    'like',
    'dislike',
    'star_1',
    'star_2',
    'star_3',
    'star_4',
    'star_5'
);

CREATE TABLE users (
    id            UUID PRIMARY KEY,
    nick_name     VARCHAR(128) NOT NULL UNIQUE,
    first_name    VARCHAR(128) NOT NULL,
    last_name     VARCHAR(128) NOT NULL,
    middle_name   VARCHAR(128) NOT NULL,
    email_address VARCHAR(128) NOT NULL,
    phone_number  VARCHAR(32),
    self_bio      TEXT,
    user_type     user_type_enum NOT NULL,
    embedding     VECTOR(1536) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ,
    deleted_at    TIMESTAMPTZ,
    modified_by   UUID,
    CONSTRAINT users_phone_number_chk CHECK (phone_number ~ '^[0-9+()\-\s]*$')
);

CREATE TABLE users_auth (
    id            UUID PRIMARY KEY,
    user_id       UUID NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ,
    deleted_at    TIMESTAMPTZ,
    modified_by   UUID,
    CONSTRAINT users_auth_user_fk FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT users_auth_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id)
);

CREATE TABLE tags (
    id          UUID PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ
);

CREATE TABLE users_tags (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL,
    tag_id      UUID NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ,
    modified_by UUID,
    CONSTRAINT users_tags_user_fk FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT users_tags_tag_fk FOREIGN KEY (tag_id) REFERENCES tags(id),
    CONSTRAINT users_tags_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id),
    CONSTRAINT users_tags_unique UNIQUE (user_id, tag_id)
);

CREATE TABLE projects (
    id               UUID PRIMARY KEY,
    name             VARCHAR(512) NOT NULL,
    description      TEXT NOT NULL,
    description_url  TEXT,
    start_deadline   TIMESTAMPTZ NOT NULL,
    finish_deadline  TIMESTAMPTZ NOT NULL,
    created_by       UUID,
    approved_by      UUID,
    embedding        VECTOR(1536) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ,
    deleted_at       TIMESTAMPTZ,
    modified_by      UUID,
    CONSTRAINT projects_created_by_fk FOREIGN KEY (created_by) REFERENCES users(id),
    CONSTRAINT projects_approved_by_fk FOREIGN KEY (approved_by) REFERENCES users(id),
    CONSTRAINT projects_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id)
);

CREATE TABLE projects_tags (
    id          UUID PRIMARY KEY,
    project_id  UUID NOT NULL,
    tag_id      UUID NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ,
    modified_by UUID,
    CONSTRAINT projects_tags_project_fk FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT projects_tags_tag_fk FOREIGN KEY (tag_id) REFERENCES tags(id),
    CONSTRAINT projects_tags_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id),
    CONSTRAINT projects_tags_unique UNIQUE (project_id, tag_id)
);

CREATE TABLE users_projects (
    id             UUID PRIMARY KEY,
    user_id        UUID NOT NULL,
    project_id     UUID NOT NULL,
    connection_type connection_type_enum,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ,
    deleted_at     TIMESTAMPTZ,
    modified_by    UUID,
    CONSTRAINT users_projects_user_fk FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT users_projects_project_fk FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT users_projects_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id),
    CONSTRAINT users_projects_unique UNIQUE (user_id, project_id, connection_type)
);

CREATE TABLE interactions (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL,
    project_id      UUID NOT NULL,
    connection_type connection_type_enum,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by     UUID,
    CONSTRAINT interactions_user_fk FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT interactions_project_fk FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT interactions_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id)
);

CREATE TABLE ratings (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL,
    project_id  UUID NOT NULL,
    rating      rating_enum,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ,
    deleted_at  TIMESTAMPTZ,
    modified_by UUID,
    CONSTRAINT ratings_user_fk FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT ratings_project_fk FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT ratings_modified_by_fk FOREIGN KEY (modified_by) REFERENCES users(id),
    CONSTRAINT ratings_unique UNIQUE (user_id, project_id)
);
