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
  NULL::float as elo_change,
  NULL::float as elo,
  NULL::float as R, NULL::float as E
from results
  join races on races.raceId = results.raceId
order by driverId, year, round
;

create or replace view elo_calc as
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
        end as headToHead,
        count(distinct res2.driverId) as nOpponents
    from res
    join res as res2 on res2.raceId = res.raceId 
        and res2.driverId != res.driverId
    group by all
),
elo_start as (
    select
        driverId,
        raceId,
        year,
        round,
        coalesce(lag(elo, 1) over (partition by driverId order by year, round), 1000) as elo,
    from elo
),
elo_setup as (
    select 
        race_performance.raceId, 
        race_performance.year, 
        race_performance.round, 
        race_performance.driverId,
        elo_dri.elo,
        race_performance.headToHead as R,
        -- Odds of winning: pow(10, (elo_dri.elo - elo_opp.elo)
        -- Probability of the expected outcome: odds / (odds + 1)
        pow(10, (elo_dri.elo - elo_opp.elo) / 400) / (pow(10, (elo_dri.elo - elo_opp.elo) / 400) + 1) as E,
    from race_performance
        left join elo_start as elo_dri on elo_dri.driverId = race_performance.driverId
            and elo_dri.raceId = race_performance.raceId
        left join elo_start as elo_opp on elo_opp.driverId = race_performance.opponentId
            and elo_opp.raceId = race_performance.raceId
    order by race_performance.raceId, race_performance.driverId
),
elo_sum as (
    select
        raceId,
        year,
        round,
        driverId,
        sum(R)::float as R,
        sum(E)::float as E,
        -- K * (Result - Expected)
        1::float * (sum(R)::float - sum(E)::float) as change,
        elo as driverElo
    from elo_setup
    group by all
)
select 
    raceId, year, round, driverId, R, E, driverElo as elo, change as elo_change, driverElo + change as new_elo,
from elo_sum 
group by all 
order by year, round, driverId
;
'''

conn.execute(create_query)

conn.close()