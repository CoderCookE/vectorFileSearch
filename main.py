
import os
import argparse
import psycopg2
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "file_vector"
DB_USER = "ericcook"
DB_PASSWORD = ""


# Generate the embedding for the file
def generate_embedding(input_data):
    if isinstance(input_data, str):
        content = input_data
    else:
        content = input_data.read()

    # Initialize the HuggingFace embeddings model
    embeddings_model = HuggingFaceEmbeddings()

    # Generate the embeddings for the content
    embedding = embeddings_model.embed_documents([content])

    return embedding[0]  # Return the first (and only) embedding


# Check if a file already exists in the database
def file_already_registered(file_path):
    try:
        with psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
                ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                        "SELECT COUNT(*) FROM embeddings_table WHERE file_path = %s",
                        (file_path,),
                        )
                result = cursor.fetchone()
                return result[0] > 0  # Returns True if file exists, False otherwise
    except psycopg2.Error as e:
        print(f"Database error during duplicate check: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during duplicate check: {e}")
        return False


# Save or update the embedding and file contents in the database
def save_embedding_to_db(file_path, embedding):
    try:
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        with psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
                ) as conn:
            with conn.cursor() as cursor:
                # Normalize the embedding before storing
                embedding_norm = embedding / np.linalg.norm(embedding)
                embedding_list = embedding_norm.tolist()  # Convert numpy array to a list

                if file_already_registered(file_path):
                    # Update existing embedding
                    cursor.execute(
                            """
                        UPDATE embeddings_table 
                        SET embedding = %s 
                        WHERE file_path = %s
                        """,
                        (embedding_list, file_path),
                        )
                    print(f"Updated embedding for file: {file_path}")
                else:
                    # Insert new embedding
                    cursor.execute(
                            """
                        INSERT INTO embeddings_table (file_path, embedding) 
                        VALUES (%s, %s)
                        """,
                        (file_path, embedding_list),
                        )
                    print(f"Inserted embedding for file: {file_path}")

                conn.commit()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Get all file paths from a directory
def get_file_paths(directory):
    return [
            os.path.abspath(os.path.join(directory, f))
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
            ]


# Function to walk down directory and process files, while ignoring paths in ignore_set
def walk_down_directories(start_path, ignore_set):
    processed_dirs = set()
    current_dir = os.path.abspath(start_path)  # Normalize the path

    print(ignore_set)
    print("Starting at:", current_dir)

    for root, dirs, files in os.walk(current_dir):
        # Filter out directories and files that are in the ignore_set
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_set and not d.startswith('.')]
        files = [f for f in files if os.path.join(root, f) not in ignore_set and not f.startswith('.')]

        # Process the directory if it hasn't been processed yet
        if root not in processed_dirs:
            print(f"Processing directory: {root}")
            process_directory(root, files)  # Pass the filtered list of files
            processed_dirs.add(root)


# Function to process the files in the directory
def process_directory(directory, files):
    for file in files:
        file_path = os.path.join(directory, file)
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
                embedding = generate_embedding(file_content)
                save_embedding_to_db(file_path, embedding)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Failed to process file {file_path}: {e}")


# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Generate embeddings for files in a specified directory and recursively walk down directories."
    )

    # Argument for the starting directory
    parser.add_argument(
            "--path",
            type=str,
            required=True,
            help="Starting directory containing the files to process",
    )

    # Argument for the file containing paths/files to ignore
    parser.add_argument(
            "--ignore-list",
            type=str,
            required=False,
            help="Path to a file containing newline-separated list of directories and files to ignore",
    )

    args = parser.parse_args()

    # Read the ignore list file into a set
    ignore_set = set()
    if args.ignore_list:
        if os.path.exists(args.ignore_list):
            with open(args.ignore_list, "r") as f:
                ignore_set = set(f.read().splitlines())  # Each line is a path or file to ignore
        else:
            print(f"Error: The ignore list file '{args.ignore_list}' does not exist.")

    # Ensure the path is valid
    if not os.path.isdir(args.path):
        print(f"Error: The path '{args.path}' is not a valid directory.")
    else:
        # Start walking down the directory structure
        walk_down_directories(args.path, ignore_set)

