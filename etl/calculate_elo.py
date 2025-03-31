import duckdb

def update_elo(conn, table_name, calc_table_name, id_column):
    """
    Updates the Elo rating for a given table based on calculated values.

    Args:
        conn: A DuckDB connection object.
        table_name: The name of the table to update (e.g., 'elo_driver').
        calc_table_name: The name of the table with calculated Elo values (e.g., 'elo_driver_calc').
        id_column: The name of the ID column in both tables (e.g., 'driver_id').
    """
    result = conn.execute(f"""
        SELECT DISTINCT year, round FROM {table_name} WHERE elo IS NULL ORDER BY year, round
    """).fetchall()

    for year, round_num in result:
        print(f"Processing {table_name}: year {year}, round: {round_num}")
        update_query = f"""
            UPDATE {table_name} 
            SET 
              elo = {calc_table_name}.new_elo, 
              elo_change = {calc_table_name}.elo_change, 
              R = {calc_table_name}.R, 
              E = {calc_table_name}.E
            FROM {calc_table_name} 
            WHERE 
              {table_name}.{id_column} = {calc_table_name}.{id_column} 
              AND {table_name}.race_id = {calc_table_name}.race_id 
              AND {table_name}.year = {year} 
              AND {table_name}.round = {round_num};
        """
        conn.sql(update_query)

conn = duckdb.connect(database="f1db_local.duckdb") 
print("Calculating ELO for new races")
update_elo(conn, 'elo_driver', 'elo_driver_calc', 'driver_id')
update_elo(conn, 'elo_constructor', 'elo_constructor_calc', 'constructor_id')
conn.close()
