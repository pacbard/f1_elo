import dlt
from typing import Any

def upload_pipeline_to_motherduck():
    # Attach to the source pipeline
    source_pipeline = dlt.attach(pipeline_name="f1_data")
    
    # Retrieve the DuckDB file path from the source pipeline
    duckdb_path = source_pipeline.sql_client.credentials["database"]  # Access the DuckDB database path
    
    # List of tables to upload
    tables = source_pipeline.default_schema.tables.keys()

    # Create a pipeline for uploading to MotherDuck
    motherduck_pipeline = dlt.pipeline(
        pipeline_name="f1_to_motherduck",
        destination="motherduck",  # MotherDuck as the destination
        dataset_name="F1_test",  # Dataset name in MotherDuck
    )

    # Upload each table
    for table_name in tables:
        @dlt.resource(name=table_name, write_disposition="append")
        def duckdb_table_resource():
            import duckdb

            # Connect to the DuckDB database
            conn = duckdb.connect(duckdb_path)
            
            # Fetch data from the table
            data = conn.execute(f"SELECT * FROM {table_name}").fetchall()
            columns = [desc[0] for desc in conn.description]
            for row in data:
                yield dict(zip(columns, row))

        # Run the pipeline to upload the table
        load_info = motherduck_pipeline.run(duckdb_table_resource())
        print(f"Uploaded table '{table_name}' to MotherDuck.")
        print(load_info)

if __name__ == "__main__":
    # Run the upload pipeline
    upload_pipeline_to_motherduck()