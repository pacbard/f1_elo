import duckdb

def update_motherduck_tables(conn, local_db_path, schema_name):
    """
    Updates the MotherDuck database tables with data from a local DuckDB database.

    Args:
        conn: A DuckDB connection object to the MotherDuck database.
        local_db_path: The path to the local DuckDB database file.
        schema_name: The schema name in the MotherDuck database to use.
    """
    print("Updating MotherDuck database with new data")
    conn.execute(f"""
        ATTACH '{local_db_path}' AS f1_local;
        USE {schema_name};

        CREATE OR REPLACE TABLE constructor AS SELECT * FROM f1_local.constructor;
        CREATE OR REPLACE TABLE driver AS SELECT * FROM f1_local.driver;
        CREATE OR REPLACE TABLE race AS SELECT * FROM f1_local.race;
        CREATE OR REPLACE TABLE grand_prix AS SELECT * FROM f1_local.grand_prix;
        CREATE OR REPLACE TABLE race_result AS SELECT * FROM f1_local.race_result;

        CREATE OR REPLACE TABLE elo_driver AS SELECT * FROM f1_local.elo_driver;
        CREATE OR REPLACE TABLE elo_constructor AS SELECT * FROM f1_local.elo_constructor;
    """)

conn = duckdb.connect('md:F1_Results')
local_db_path = 'f1db_local.duckdb'
update_motherduck_tables(conn, local_db_path, 'F1_Results')
