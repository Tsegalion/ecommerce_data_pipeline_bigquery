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
        Extract data from PostgreSQL.

        Parameters:
        - tables_queries: Dictionary with table IDs and their corresponding SQL queries.

        Returns:
        - data: A dictionary with table IDs as keys and extracted data as DataFrames.
        """
        data = {}
        for table_id, query in tables_queries.items():
            # Execute query to fetch data from PostgreSQL
            result = execute_query(query)
            if result:
                # Convert result to DataFrame
                df = pd.DataFrame(result)
                data[table_id] = df
            else:
                logging.error(f"No data returned from PostgreSQL for table {table_id}")
        return data

    @task
    def load_postgres_data_to_bq(dataset_id, data):
        """
        Load data from PostgreSQL to BigQuery.

        Parameters:
        - dataset_id: The ID of the BigQuery dataset.
        - data: A dictionary with table IDs as keys and extracted data as DataFrames.
        """
        # Create dataset if not exists
        bq_helper.create_dataset(dataset_id)

        for table_id, df in data.items():
            # Load schema from schema folder to create the tables in BigQuery
            with open(config.SCHEMA_FILE, 'r') as f:
                schema = json.load(f)[table_id]  # Load schema for specific table
            bq_helper.create_table(dataset_id, table_id, schema)  # Create table if not exists

            if df is not None:
                bq_helper.load_data_to_bq(dataset_id, table_id, df, 'dataframe')  # Load data to BigQuery
                logging.info(f"Data loaded to BigQuery table {table_id} successfully")
            else:
                logging.error(f"No data to load to BigQuery for table {table_id}")

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