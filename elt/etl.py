import duckdb
import os

def create_database_from_csv_folder(conn, folder_path, db_path):
  """
  Creates a DuckDB database with tables from all CSV files in a given folder.

  Args:
    folder_path: Path to the folder containing CSV files.
    db_path: Path to the output DuckDB database file.
  """

  for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
      filepath = os.path.join(folder_path, filename)
      table_name = filename.replace(".csv", "")  # Use filename as table name
      try:
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv('{filepath}', nullstr='\\N');")
        print(f"Table '{table_name}' created successfully from '{filepath}'.")
      except Exception as e:
        print(f"Error creating table '{table_name}' from '{filepath}': {e}")


# Example usage:
folder_path = "data"  # Replace with the actual folder path
db_path = "f1_results.duckdb"

conn = duckdb.connect(database=db_path)

create_database_from_csv_folder(conn, folder_path, db_path)

create_query = '''
-- Create Elo Table
create or replace table elo as
select distinct
  driverId,
  results.raceId,
  year,
  round,
  1000 as elo,
  0 as elo_change,
from results
  join races on races.raceId = results.raceId
order by driverId, year, round
;
'''

conn.execute(create_query)

conn.close()