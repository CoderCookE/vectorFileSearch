# File Embedding Processor

This project allows you to generate embeddings for files in a specified directory, store them in a PostgreSQL database, and later search the database based on a query to retrieve relevant file paths and their corresponding embeddings. The project uses HuggingFace and PyTorch for generating embeddings and `psycopg2` for database interaction.

## Features
- **Embedding Generation**: Generates file embeddings using HuggingFace's transformer models or a custom embedding generation function.
- **Database Storage**: Embeddings are stored in a PostgreSQL database, allowing for fast retrieval.
- **Search**: Query the database using a user-defined question, retrieve the most relevant file embeddings, and display the corresponding file paths.

## Prerequisites

- **Python 3.7+**: This project uses Python for scripting.
- **PostgreSQL**: You will need a running PostgreSQL instance to store embeddings.
- **CUDA (optional)**: If you have a GPU, PyTorch will automatically use it for faster embedding generation.

## Requirements

### Python Dependencies

The following Python packages are required:

- `psycopg2`: PostgreSQL database adapter for Python.
- `numpy`: Package for numerical operations (used for embedding normalization).
- `torch`: PyTorch, used for running HuggingFace models.
- `transformers`: HuggingFace library for pretrained transformer models.
- `argparse`: Command-line argument parser.
- `langchain`: For embedding models (if using the HuggingFaceEmbeddings class from `langchain`).

Install these packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Setup

### Step 1: Set up PostgreSQL Database

1. Install PostgreSQL on your machine, if it's not already installed.
2. Create a new database (`file_vector`) to store the embeddings.
3. Run the following SQL to create the required table:

```sql
CREATE TABLE embeddings_table (
    file_path TEXT PRIMARY KEY,
    embedding FLOAT8[]
);
```

Alternatively, you can use the provided `setup_database.sh` script to automatically set up the database:

```bash
sh setup_database.sh
```

### Step 2: Set up Virtual Environment

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Configuration

- Update the database connection parameters in both `main.py` and `question.py` to match your PostgreSQL setup:

```python
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "file_vector"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"
```

### Step 4: Prepare Ignore List (Optional)

If you want to exclude certain files or directories from processing, create a text file (e.g., `ignore_list.txt`) containing newline-separated file or directory paths to ignore.

Example `ignore_list.txt`:
```
path/to/ignore1
file_to_ignore.txt
```

### Step 5: Run the Embedding Generation Script

The `main.py` script processes files in the specified directory, generates embeddings, and stores them in the database. You can pass an optional ignore list file.

To run the embedding generation:

```bash
python main.py --path /path/to/start/directory --ignore-list ignore_list.txt
```

Where:
- `/path/to/start/directory` is the path to the directory you want to process.
- `ignore_list.txt` is an optional file containing a list of files or directories to ignore.

### Step 6: Perform a Search

The `question.py` script allows you to search the database using a query string. It generates an embedding for the query and retrieves the most relevant files based on vector similarity.

To run a query:

```bash
python question.py --question "your search query"
```

This will generate an embedding for the search query and return the top 5 matching files with their embedding values.

## Example Usage

### Generate Embeddings for Files:

```bash
python main.py --path /path/to/files --ignore-list ignore_list.txt
```

### Search for Relevant Files Based on Query:

```bash
python question.py --question "What are the important files related to data processing?"
```

### Database Query Example

If you want to manually query the database, you can use the following SQL query to find the most similar embeddings to a given query embedding:

```sql
SELECT file_path, embedding
FROM embeddings_table
ORDER BY embedding <=> %s::vector  -- Ensure proper cast to vector type
LIMIT 5;
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README includes the steps for setup, configuration, and usage. Let me know if you need more sections or clarification!
