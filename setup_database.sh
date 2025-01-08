
#!/bin/bash

# Variables
DB_SUPERUSER="ericcook"  # Replace with your actual superuser
DB_NAME="file_vector"
DB_USER="ericcook"
DB_PASSWORD=""  # Change this to your desired password
TABLE_NAME="embeddings_table"
VECTOR_DIM=768  # Adjust based on your embedding dimensions

# Ensure PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it before proceeding."
    exit 1
fi

# Install pgvector if not already installed
echo "Ensuring pgvector extension is enabled..."
psql -U $DB_SUPERUSER -c "CREATE EXTENSION IF NOT EXISTS vector;" || {
    echo "Failed to enable pgvector. Ensure it's installed correctly and PostgreSQL is restarted."
    exit 1
}

# Create PostgreSQL database if it doesn't exist
echo "Checking if database $DB_NAME exists..."
DB_EXISTS=$(psql -U $DB_SUPERUSER -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';")

if [ "$DB_EXISTS" == "1" ]; then
    echo "Database $DB_NAME already exists. Skipping creation."
else
    echo "Creating database $DB_NAME..."
    psql -U $DB_SUPERUSER -c "CREATE DATABASE $DB_NAME;" || {
        echo "Failed to create database $DB_NAME."
        exit 1
    }
fi

# Create the user with a password if it doesn't exist
echo "Checking if user $DB_USER exists..."
USER_EXISTS=$(psql -U $DB_SUPERUSER -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';")

if [ "$USER_EXISTS" == "1" ]; then
    echo "User $DB_USER already exists. Skipping creation."
else
    echo "Creating user $DB_USER..."
    psql -U $DB_SUPERUSER -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || {
        echo "Failed to create user $DB_USER."
        exit 1
    }
fi

# Grant privileges to the user on the database
echo "Granting privileges to user $DB_USER on database $DB_NAME..."
psql -U $DB_SUPERUSER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" || {
    echo "Failed to grant privileges to user $DB_USER."
    exit 1
}

# Connect to the database and create the embeddings table
echo "Ensuring table $TABLE_NAME exists in database $DB_NAME..."

psql -U $DB_SUPERUSER -d $DB_NAME -c "
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS $TABLE_NAME (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    embedding VECTOR($VECTOR_DIM) NOT NULL  -- Adjust the dimension based on your embeddings
);
" || {
    echo "Failed to create table $TABLE_NAME."
    exit 1
}

echo "Database and table setup complete."

