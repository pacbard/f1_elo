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
      FROM races
      where year <> 1950 and round <> 1
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing year: {year}, round: {round_num}") 

    print("Calculating new Elo Scores")

    update_query = f"""
    -- Calculate new Elo with view
    create or replace temporary table new_elo as
    WITH
    res as (
    select
        results.raceId,
        races.year,
        races.round,
        races.name,
        drivers.driverId,
        drivers.driverRef,
        case
            when position is null then 99999
            else position::int 
        end as position,
        constructors.constructorRef
    from results
        join races on races.raceId = results.raceId
        join drivers on drivers.driverId = results.driverId
        join constructors on constructors.constructorId = results.constructorId
    ),
    race_performance as (
    select
        res.driverId,
        res.raceId,
        res.year,
        res.round,
        res.position,
        res2.driverId as opponentId,
        res2.position as opponentPosition
        from res
        join res as res2 on res2.raceId = res.raceId and res2.driverId <> res.driverId
    )
    select 
        race_performance.raceId, race_performance.year, race_performance.round, race_performance.driverId,
        avg(coalesce(elo_opp.elo, 1000)) as elo_opponents,
        avg(case 
                when position < opponentPosition then 400
                when position = opponentPosition and elo_dri.elo >= elo_opp.elo then 200
                when position = opponentPosition and elo_dri.elo < elo_opp.elo then -200
                else -400 
            end) as elo_change,
        cast((elo_opponents + elo_change) as int) as new_elo,
        case
        when race_performance.round = (select max(round) from races where races.year = race_performance.year) 
            then race_performance.year + 1
        else race_performance.year 
        end as next_year,
        case
        when race_performance.round = (select max(round) from races where races.year = race_performance.year) 
            then 1
        else race_performance.round + 1 
    end as next_round
    from race_performance
        left join elo as elo_dri on elo_dri.driverId = race_performance.driverId and elo_dri.year = race_performance.year and elo_dri.round = race_performance.round
        left join elo as elo_opp on elo_opp.driverId = race_performance.opponentId and elo_opp.year = race_performance.year and elo_opp.round = race_performance.round
    where
        elo.year = {year} and elo.round = {round}
    group by all
    order by race_performance.year, race_performance.round, race_performance.driverId
    ;
    """

    print(update_query)

    conn.execute(update_query)

# Example usage:
conn = duckdb.connect(database="f1_results.duckdb") 
calculate_new_elo(conn)
conn.close()