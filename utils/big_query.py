from google.api_core.exceptions import Conflict
from google.cloud import bigquery
import pandas as pd
import logging

class BigQueryHelper:
    def __init__(self, project_id) -> None:
        self.project_id = project_id
        self.client = bigquery.Client(project=self.project_id)
    
    def create_dataset(self, dataset_id: str) -> None:
        """
        Create a new dataset in BigQuery.

        Parameters:
        - dataset_id: The ID of the dataset to create.
        """
        try:
            dataset_ref = self.client.dataset(dataset_id)
            self.client.create_dataset(dataset_ref)
            logging.info(f'Dataset {dataset_id} created successfully')
        except Conflict:
            logging.info(f'Dataset {dataset_id} already exists')
        except Exception as e:
            logging.error(f"Encountered issues creating the Dataset {dataset_id}: {e}")
    
    def create_table(self, dataset_id:str, table_id:str, schema:str):
        """
        Create a new table in BigQuery.

        Parameters:
        - dataset_id: The ID of the dataset.
        - table_id: The ID of the table to create.
        - schema: The schema of the table (as a list of bigquery.SchemaField).
        """
        try:
            dataset_ref = self.client.dataset(dataset_id)
            table_ref = dataset_ref.table(table_id)
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logging.info(f'{table_id} table created')
        except Conflict:
            logging.info(f'{table_id} table already exists')
        except Exception as e:
            logging.error(f"Encountered issues creating the Table {table_id}: {e}")

    def load_data_to_bq(self, dataset_id: str, table_id: str, source, source_format: str, schema=None) -> None:
        """
        Load data into BigQuery table from a source (local file, GCS URI, or DataFrame).

        Parameters:
        - dataset_id: The ID of the BigQuery dataset.
        - table_id: The ID of the BigQuery table.
        - source: The path to the source file, GCS URI, or a DataFrame.
        - source_format: The format of the source file or 'dataframe'.
        - schema: Optional; The schema of the table (as a list of bigquery.SchemaField).
        """
        try:
            dataset_ref = self.client.dataset(dataset_id)
            table_ref = dataset_ref.table(table_id)
            
            # Fetch job configuration
            job_config = self.fetch_job_config(
                source_format if source_format != 'dataframe' else 'dataframe',
                schema,
                autodetect=(schema is None)
            )
            
            if source_format == 'dataframe' and isinstance(source, pd.DataFrame):
                logging.info(f"Loading data from {table_id} DataFrame to {table_id} table on BigQuery")
                job = self.client.load_table_from_dataframe(source, table_ref, job_config=job_config)
            else:
                if source.startswith('gs://'):
                    logging.info(f"Loading data from GCS URI to {table_id}")
                    job = self.client.load_table_from_uri(source, table_ref, job_config=job_config)
                else:
                    logging.info(f"Loading data from local file to {table_id}")
                    with open(source, 'rb') as source_file:
                        job = self.client.load_table_from_file(source_file, table_ref, job_config=job_config)

            job.result()  # Wait for the job to complete
            logging.info(f"Data loaded to {table_id} table from source: {source}")
        except Exception as e:
            logging.error(f"Encountered issues loading data from source to the {table_id} table on BigQuery: {e}")

    def fetch_job_config(self, file_format, schema=None, autodetect=False, create_disposition='CREATE_IF_NEEDED', write_disposition='WRITE_TRUNCATE') -> bigquery.LoadJobConfig:
        """
        Fetch the job configuration for loading data into BigQuery.

        Parameters:
        - file_format: The format of the source file (e.g., 'CSV', 'NEWLINE_DELIMITED_JSON').
        - schema: Optional; The schema of the table (as a list of bigquery.SchemaField).
        - autodetect: Whether to automatically detect the schema of the data.
        - create_disposition: The create disposition of the job.
        - write_disposition: The write disposition of the job (e.g., 'WRITE_TRUNCATE', 'WRITE_APPEND').
            To maintain idempotence, use 'WRITE_TRUNCATE' to overwrite the table each time.
        """
        config_dict = {
            "dataframe": bigquery.LoadJobConfig(
                schema=schema,
                autodetect=autodetect,
                create_disposition=create_disposition,
                write_disposition=write_disposition
            ),
            "json": bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                schema=schema,
                autodetect=autodetect,
                create_disposition=create_disposition,
                write_disposition=write_disposition
            ),
            "avro": bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.AVRO,
                schema=schema,
                autodetect=autodetect,
                use_avro_logical_types=True,
                create_disposition=create_disposition,
                write_disposition=write_disposition
            ),
            "csv": bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                field_delimiter=",",
                quote_character="\"",
                schema=schema,
                autodetect=autodetect,
                write_disposition=write_disposition
            ),
            "parquet": bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                schema=schema,
                autodetect=autodetect,
                create_disposition=create_disposition,
                write_disposition=write_disposition
            )
        }
        return config_dict[file_format]