
import os
import argparse
import psycopg2
import torch

from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np

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


# Function to perform a vector search and retrieve relevant files and their embeddings
def vector_search(query_embedding):
    # Convert the numpy.ndarray to a list before passing it to the SQL query
    # Normalize the query embedding (use the same method as during insertion)
    query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)
    query_embedding_list = query_embedding_norm.tolist()  # Convert to list

    with psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT file_path, embedding
                FROM embeddings_table
                ORDER BY embedding <=> %s::vector  -- Ensure proper cast to vector type
                LIMIT 5
                """,
                (query_embedding_list,),  # Pass the list of embedding
            )

            results = cursor.fetchall()

    return results

# Function to handle the search and show the matching embedding values
def run_vector_search_and_answer(question):
    # Generate the embedding for the user question
    question_embedding = generate_embedding(question)
    
    # Perform the vector search to find relevant files and their embeddings
    search_results = vector_search(question_embedding)
    
    # Generate the answer including both file names and corresponding matching embedding values
    answer = "The most relevant files and their matching embedding values are:\n"
    for file_path, embedding in search_results:
        answer += f"\nFile: {file_path}\n"  # Show first 10 values of the embedding
    
    return answer

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find files based on their content")

    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="search string",
    )
    args = parser.parse_args()

    # Use the question to search the vector database and generate an answer
    question = args.question
    answer = run_vector_search_and_answer(question)

    print("file contents:", answer)

