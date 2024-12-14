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
      order by year, round
  """).fetchall()

  for year, round_num in result:
    print(f"Processing year: {year}, round: {round_num}") 

    update_query = f"""
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
            constructors.constructorRef,
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
            res2.position as opponentPosition,
            case
                when res.position::int < res2.position::int then 1
                when res.position::int = res2.position::int then 0.5
                when res.position::int > res2.position::int then 0
            end as headToHead
        from res
        join res as res2 on res2.raceId = res.raceId 
            and res2.driverId != res.driverId
        group by all
    ),
    elo_calc as (
        select 
            race_performance.raceId, race_performance.year, race_performance.round, race_performance.driverId, race_performance.opponentId,
            -- update formula: old_rating + (k_factor * (score - expected_score))
            elo_dri.elo as driverElo, elo_opp.elo as opponentElo, race_performance.headToHead,
            32 * (race_performance.headToHead - (1.0 / (1.0 + POWER(10.0, (elo_opp.elo - elo_dri.elo) / 400.0)))) as change_elo
        from race_performance
            left join elo as elo_dri on elo_dri.driverId = race_performance.driverId 
                and elo_dri.year = race_performance.year 
                and elo_dri.round = race_performance.round
            left join elo as elo_opp on elo_opp.driverId = race_performance.opponentId 
                and elo_opp.year = race_performance.year 
                and elo_opp.round = race_performance.round
        order by race_performance.year, race_performance.round, race_performance.driverId
    )
    select raceId, year, round, driverId, avg(driverElo) + sum(change_elo) as new_elo 
    from elo_calc 
    group by all 
    order by year, round, driverId
    ;

    update elo
        set 
            elo = new_elo.new_elo
    from new_elo
    where 
        new_elo.new_elo is not null 
        and elo.driverId = new_elo.driverId 
        and new_elo.year = {year} and new_elo.round = {round_num}
        and ((elo.year = {year} and elo.round >= {round_num}) or elo.year > {year})
    """

    conn.sql(update_query)

# Example usage:
conn = duckdb.connect(database="f1_results.duckdb") 
calculate_new_elo(conn)
conn.close()