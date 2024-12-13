from dotenv import load_dotenv
import psycopg2
import logging
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_db():
    """
    Establish a connection to the PostgreSQL database.

    Returns:
    - conn: The connection object.
    """
    logging.info("Establishing a connection to the PostgreSQL database......")
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        logging.info("Connection established successfully!")
        return conn
    except psycopg2.Error as e:
        logging.error("Error connecting to the database:", e)
        return None

def execute_query(query):
    """
    Execute a query on the PostgreSQL database.
    
    Parameters:
    - query: The query to execute.
    
    Returns:
    - json_data: The result of the query as a list of dictionaries.

    """
    # Connect to the database
    conn = connect_to_db()
    if conn is None:
        logging.error("Database connection failed. Exiting the function.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()  # Fetch the result of the query
        columns = [desc[0] for desc in cursor.description]  # Fetch the column names
        json_data = [dict(zip(columns, row)) for row in data] # Combine columns and data into a list of dictionaries
        conn.commit()
        logging.info("Query executed successfully!")
        return json_data
    except psycopg2.Error as e:
        # Handle database-specific errors
        logging.error("Error executing query: %s", e)

    except Exception as e:
        # Handle any other unexpected errors
        logging.error("An unexpected error occurred: %s", e)

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()