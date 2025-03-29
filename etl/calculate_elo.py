import duckdb

def calculate_new_elo(conn):
  """
  Loops through unique combinations of year and round in the 'races' table 
  and performs some action (replace this with your desired logic).

  Args:
    conn: A DuckDB connection object.
  """
  result = conn.execute("""
      SELECT DISTINCT 
        year, round 
      FROM elo
      where elo is null
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing year: {year}, round: {round_num}") 

    update_query = f"""
    -- Update the drivers' Elo rating after a race
    update elo
        set 
            elo = elo_calc.new_elo,
            elo_change = elo_calc.elo_change,
            R = elo_calc.R,
            E = elo_calc.E
    from elo_calc
    where
        elo.driver_id = elo_calc.driver_id
        and elo.race_id = elo_calc.race_id
        and elo.year = {year} and elo.round = {round_num};
    """

    conn.sql(update_query)

# Example usage:
conn = duckdb.connect(database="f1_results.duckdb") 
calculate_new_elo(conn)
conn.close()