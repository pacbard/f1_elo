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
      FROM elo_driver
      where elo is null
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing race: year {year}, round: {round_num}") 

    update_query = f"""
    -- Update the drivers' Elo rating after a race
    update elo_driver
        set 
            elo = elo_data.new_driver_elo,
            elo_change = elo_data.change,
            R = elo_data.R,
            E = elo_data.E
    from (
      select 
        race_id, driver_id, 
        R, 
        E, 
        avg(driver_elo) as driver_elo, 
        avg(change) as change,
        avg(driver_elo + change) as new_driver_elo
      from  elo_calc
      where
          elo_calc.year = {year} and elo_calc.round = {round_num}
      group by all
    ) as elo_data
    where
        elo_driver.driver_id = elo_data.driver_id
        and elo_driver.race_id = elo_data.race_id
        and elo_driver.year = {year} and elo_driver.round = {round_num};

    -- Update the constructors' Elo rating after a race
    update elo_constructor
        set 
            elo = elo_data.new_constructor_elo,
            elo_change = elo_data.change,
            R = elo_data.R,
            E = elo_data.E
    from (
      select 
        race_id, constructor_id, 
        avg(R) as R, 
        avg(E) as E, 
        avg(constructor_elo) as constructor_elo, 
        avg(change) as change,
        avg(constructor_elo + change) as new_constructor_elo
      from  elo_calc
      where
          elo_calc.year = {year} and elo_calc.round = {round_num}
      group by race_id, constructor_id, constructor_elo
    ) as elo_data
    where
          elo_data.constructor_id = elo_constructor.constructor_id
          and elo_data.race_id = elo_constructor.race_id
          and elo_constructor.year = {year} and elo_constructor.round = {round_num};
    """

    conn.sql(update_query)

# Example usage:
conn = duckdb.connect(database="f1db_local.duckdb") 
print("Calculating ELO for new races")
calculate_new_elo(conn)
conn.close()