from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.big_query import BigQueryHelper
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from utils.db_conn import execute_query
from dotenv import load_dotenv
import pandas as pd
import logging
import config
import json
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

# Set environment variables
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
    logging.info('Environment variables set')
else:
    logging.error('GOOGLE_APPLICATION_CREDENTIALS not found in environment variables')
    exit(1)  # Exit if credentials are not set

# Initialize BigQueryHelper with project_id
bq_helper = BigQueryHelper(config.PROJECT_ID)

# Default arguments for the DAG
default_args = {
    'owner': 'Ebun',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 10),
    'email': ['tyebunoluwa@gmail.com'],
    'email_on_retry': False,
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    description='Extract data from PostgreSQL and load it into BigQuery',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def extract_postgres_load_bq():

    @task
    def extract_data_from_postgres(tables_queries):
        """
        Extract data from PostgreSQL in parallel.

        Parameters:
        - tables_queries: Dictionary with table IDs and their corresponding SQL queries.

        Returns:
        - data: A dictionary with table IDs as keys and extracted data as DataFrames.
        """
        logging.info("Starting parallel data extraction from PostgreSQL")
        data = {}

        # Use ThreadPoolExecutor for parallel query execution
        with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your database and system capacity
            future_to_table = {
                executor.submit(execute_query, query): table_id for table_id, query in tables_queries.items()
            }

            for future in as_completed(future_to_table):
                table_id = future_to_table[future]
                try:
                    result = future.result()  # Get query result
                    if result:
                        data[table_id] = pd.DataFrame(result)  # Convert to DataFrame
                        logging.info(f"Data extracted for table {table_id}")
                    else:
                        logging.warning(f"No data returned for table {table_id}")
                except Exception as e:
                    logging.error(f"Error extracting data for table {table_id}: {e}")

        return data

    @task
    def load_postgres_data_to_bq(dataset_id, data):
        """
        Load data from PostgreSQL to BigQuery.

        Parameters:
        - dataset_id: The ID of the BigQuery dataset.
        - data: A dictionary with table IDs as keys and extracted data as DataFrames.
        """ 
        logging.info("Starting data load to BigQuery")
        try:
            # Create dataset if not exists
            bq_helper.create_dataset(dataset_id)
        except Exception as e:
            logging.error(f"Error creating BigQuery dataset {dataset_id}: {e}")
            return

        # Load schema from schema folder to create the tables in BigQuery
        with open(config.SCHEMA_FILE, 'r') as f:
            schemas = json.load(f)

        # Function to load a single table to BigQuery
        def load_single_table(table_id, df, schema):
            try:
                bq_helper.create_table(dataset_id, table_id, schema)  # Create table if not exists
                if not df.empty:
                    bq_helper.load_data_to_bq(dataset_id, table_id, df, 'dataframe')  # Load data to BigQuery
                    logging.info(f"Data loaded to BigQuery table {table_id} successfully")
                else:
                    logging.warning(f"Skipping empty DataFrame for table {table_id}")
            except Exception as e:
                logging.error(f"Error loading data to BigQuery for table {table_id}: {e}")

        # Create a thread pool to load tables in parallel
        with ThreadPoolExecutor() as executor:
            futures = []
            for table_id, df in data.items():
                schema = schemas.get(table_id)
                if schema:
                    futures.append(executor.submit(load_single_table, table_id, df, schema))
                else:
                    logging.error(f"Schema for table {table_id} not found. Skipping.")

            # Wait for all tasks to complete
            for future in as_completed(futures):
                future.result()  # Ensure all threads complete

        logging.info("Finished loading data to BigQuery.")

    # List of tables and queries
    tables_queries = {
        config.PRODUCTS_TABLE_ID: 'SELECT * FROM raw.products',
        config.ORDERS_TABLE_ID: 'SELECT * FROM raw.orders',
        config.CUSTOMERS_TABLE_ID: 'SELECT * FROM raw.customers',
        config.ORDER_ITEMS_TABLE_ID: 'SELECT * FROM raw.order_items',
        config.SELLERS_TABLE_ID: 'SELECT * FROM raw.sellers',
        config.PRODUCT_CATEGORY_NAME_TRANSLATION_TABLE_ID: 'SELECT * FROM raw.product_category_name_translation',
        config.GEOLOCATIONS_TABLE_ID: 'SELECT * FROM raw.geolocation',
        config.ORDER_REVIEWS_TABLE_ID: 'SELECT * FROM raw.order_reviews',
        config.ORDER_PAYMENTS_TABLE_ID: 'SELECT * FROM raw.order_payments'
    }

    data_from_postgres = extract_data_from_postgres(tables_queries)
    load_data_task = load_postgres_data_to_bq(config.DATASET_ID, data_from_postgres)

    # Set task dependencies
    data_from_postgres >> load_data_task

# Instantiate the DAG
extract_postgres_load_bq_dag = extract_postgres_load_bq()