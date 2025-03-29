import duckdb

def calculate_new_elo_driver(conn):
  """
  Loops through unique combinations of year and round in the 'races' table 
  and performs some action (replace this with your desired logic).

  Args:
    conn: A DuckDB connection object.
  """
  result = conn.execute("""
      SELECT DISTINCT 
        year, round 
      FROM elo_driver
      where elo is null
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing drivers: year {year}, round: {round_num}") 

    update_query = f"""
    -- Update the drivers' Elo rating after a race
    update elo_driver
        set 
            elo = elo_driver_calc.new_elo,
            elo_change = elo_driver_calc.elo_change,
            R = elo_driver_calc.R,
            E = elo_driver_calc.E
    from elo_driver_calc
    where
        elo_driver.driver_id = elo_driver_calc.driver_id
        and elo_driver.race_id = elo_driver_calc.race_id
        and elo_driver.year = {year} and elo_driver.round = {round_num};
    """

    conn.sql(update_query)

def calculate_new_elo_constructor(conn):
  """
  Loops through unique combinations of year and round in the 'races' table 
  and performs some action (replace this with your desired logic).

  Args:
    conn: A DuckDB connection object.
  """
  result = conn.execute("""
      SELECT DISTINCT 
        year, round 
      FROM elo_constructor
      where elo is null
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing constructors: year {year}, round: {round_num}") 

    update_query = f"""
    -- Update the constructors' Elo rating after a race
    update elo_constructor
        set 
            elo = elo_constructor_calc.new_elo,
            elo_change = elo_constructor_calc.elo_change,
            R = elo_constructor_calc.R,
            E = elo_constructor_calc.E
    from elo_constructor_calc
    where
        elo_constructor.constructor_id = elo_constructor_calc.constructor_id
        and elo_constructor.race_id = elo_constructor_calc.race_id
        and elo_constructor.year = {year} and elo_constructor.round = {round_num};
    """

    conn.sql(update_query)

# Example usage:
conn = duckdb.connect(database="f1db_local.duckdb") 
print("Calculating ELO for new races")
calculate_new_elo_driver(conn)
calculate_new_elo_constructor(conn)
conn.close()