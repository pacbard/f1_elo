import duckdb
import requests
import zipfile
import tempfile
import os

def download_and_unzip(url: str, extract_path: str = ".") -> None:
    """
    Downloads a zip file to a temporary location, extracts its contents, and then deletes the zip file.

    Args:
        url (str): The URL of the zip file.
        extract_path (str, optional): The path to extract the zip file to. Defaults to the current directory.

    Raises:
        requests.exceptions.RequestException: If there is an error downloading the file.
        zipfile.BadZipFile: If the downloaded file is not a valid zip file.
        Exception: For any other unexpected error.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False) as temp_zip:  # create temporary file
            for chunk in response.iter_content(chunk_size=8192):
                temp_zip.write(chunk)
            temp_zip_path: str = temp_zip.name

        with zipfile.ZipFile(temp_zip_path) as zf:
            zf.extractall(extract_path)

        os.remove(temp_zip_path)  # Delete the temporary zip file

        print(f"Successfully downloaded and extracted from {url} to {extract_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid zip file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Download and unzip the SQLite database
db_version = "v2025.2.0"

url: str = f"https://github.com/f1db/f1db/releases/latest/download/f1db-sqlite.zip"

download_and_unzip(url, extract_path=".")

db_path = "f1db_local.duckdb"

conn = duckdb.connect(db_path)

create_query = f"""
attach 'f1db.db' as f1db (type sqlite, READ_ONLY);
attach 'md:F1_Results' as F1_Results;

-- Copy over the tables from the SQLite database
create or replace table driver as
select * from f1db.driver;

create or replace table race as
select * from f1db.race;

create or replace table grand_prix as
select * from f1db.grand_prix;

create or replace table constructor as
select * from f1db.constructor;

create or replace table race_result as
select * from f1db.race_result;

-- Create Elo Driver Table
create or replace table elo_driver as
select 
	race_result.driver_id, 
	race_result.race_id,
	race.year,
	race.round,
	md_elo.elo_change::float as elo_change,
	md_elo.elo::float as elo,
	md_elo.R::float as R, 
	md_elo.E::float as E
from race_result
    left join F1_Results.elo_driver as md_elo on md_elo.driver_id = race_result.driver_id and md_elo.race_id = race_result.race_id
	join race on race.id = race_result.race_id
order by race_result.driver_id, race.year, race.round
;

create or replace view elo_driver_calc as
WITH
res as (
    select
        race_result.race_id,
        race.year,
        race.round,
        race.official_name as race_name,
        driver.id as driver_id,
        driver.abbreviation as driver_ref,
        case
            when race_result.position_number is null then (select max(rr.position_number) from race_result as rr where rr.race_id = race.id) + 1
            else race_result.position_number::int 
        end as position,
        constructor.name as constructor_name,
    from race_result
        join race on race.id = race_result.race_id
        join driver on driver.id = race_result.driver_id
        join constructor on constructor.id = race_result.constructor_id
),
race_performance as (
    select
        res.driver_id,
        res.race_id,
        res.year,
        res.round,
        res.position,
        res2.driver_id as opponentId,
        res2.position as opponentPosition,
        case
            when res.position::int < res2.position::int then 1
            when res.position::int = res2.position::int then 0.5
            when res.position::int > res2.position::int then 0
        end as headToHead,
        count(distinct res2.driver_id) as nOpponents
    from res
    join res as res2 on res2.race_id = res.race_id 
        and res2.driver_id != res.driver_id
    group by all
),
elo_start as (
    select
        driver_id,
        race_id,
        year,
        round,
        coalesce(lag(elo, 1) over (partition by driver_id order by year, round), 1000) as elo,
    from elo_driver
),
elo_setup as (
    select 
        race_performance.race_id, 
        race_performance.year, 
        race_performance.round, 
        race_performance.driver_id,
        elo_dri.elo,
        race_performance.headToHead as R,
        -- Odds of winning: pow(10, (elo_dri.elo - elo_opp.elo)
        -- Probability of the expected outcome: odds / (odds + 1)
        pow(10, (elo_dri.elo - elo_opp.elo) / 400) / (pow(10, (elo_dri.elo - elo_opp.elo) / 400) + 1) as E,
    from race_performance
        left join elo_start as elo_dri on elo_dri.driver_id = race_performance.driver_id
            and elo_dri.race_id = race_performance.race_id
        left join elo_start as elo_opp on elo_opp.driver_id = race_performance.opponentId
            and elo_opp.race_id = race_performance.race_id
    order by race_performance.race_id, race_performance.driver_id
),
elo_sum as (
    select
        race_id,
        year,
        round,
        driver_id,
        sum(R)::float as R,
        sum(E)::float as E,
        -- K * (Result - Expected)
        1::float * (sum(R)::float - sum(E)::float) as change,
        elo as driverElo
    from elo_setup
    group by all
)
select 
    race_id, year, round, driver_id, R, E, driverElo as elo, change as elo_change, driverElo + change as new_elo,
from elo_sum 
group by all 
order by year, round, driver_id
;

-- Create Elo Constructor Table
create or replace table elo_constructor as
select 
	race_result.constructor_id, 
	race_result.race_id,
	race.year,
	race.round,
	md_elo.elo_change::float as elo_change,
	md_elo.elo::float as elo,
	md_elo.R::float as R, 
	md_elo.E::float as E
from race_result
    left join F1_Results.elo_constructor as md_elo on md_elo.constructor_id = race_result.constructor_id and md_elo.race_id = race_result.race_id
	join race on race.id = race_result.race_id
order by race_result.constructor_id, race.year, race.round
;

create or replace view elo_constructor_calc as
WITH
res_long as (
    select
        race_result.race_id,
        race.year,
        race.round,
        race.official_name as race_name,
        constructor.id as constructor_id,
        case
            when race_result.position_number is null then (select max(rr.position_number) from race_result as rr where rr.race_id = race.id) + 1
            else race_result.position_number::int 
        end as position,
        constructor.name as constructor_name,
    from race_result
        join race on race.id = race_result.race_id
        join constructor on constructor.id = race_result.constructor_id
),
res as (
    select
        race_id,
        year,
        round,
        race_name,
        constructor_id,
        avg(position) as position,
        constructor_name,
    from res_long
    group by all
),
race_performance as (
    select
        res.constructor_id,
        res.race_id,
        res.year,
        res.round,
        res.position,
        res2.constructor_id as opponentId,
        res2.position as opponentPosition,
        case
            when res.position::int < res2.position::int then 1
            when res.position::int = res2.position::int then 0.5
            when res.position::int > res2.position::int then 0
        end as headToHead,
        count(distinct res2.constructor_id) as nOpponents
    from res
    join res as res2 on res2.race_id = res.race_id 
        and res2.constructor_id != res.constructor_id
    group by all
),
elo_start as (
    select
        constructor_id,
        race_id,
        year,
        round,
        coalesce(lag(elo, 1) over (partition by constructor_id order by year, round), 1000) as elo,
    from elo_constructor
),
elo_setup as (
    select 
        race_performance.race_id, 
        race_performance.year, 
        race_performance.round, 
        race_performance.constructor_id,
        elo_cons.elo,
        race_performance.headToHead as R,
        -- Odds of winning: pow(10, (elo_cons.elo - elo_opp.elo)
        -- Probability of the expected outcome: odds / (odds + 1)
        pow(10, (elo_cons.elo - elo_opp.elo) / 400) / (pow(10, (elo_cons.elo - elo_opp.elo) / 400) + 1) as E,
    from race_performance
        left join elo_start as elo_cons on elo_cons.constructor_id = race_performance.constructor_id
            and elo_cons.race_id = race_performance.race_id
        left join elo_start as elo_opp on elo_opp.constructor_id = race_performance.opponentId
            and elo_opp.race_id = race_performance.race_id
    order by race_performance.race_id, race_performance.constructor_id
),
elo_sum as (
    select
        race_id,
        year,
        round,
        constructor_id,
        sum(R)::float as R,
        sum(E)::float as E,
        -- K * (Result - Expected)
        15::float * (sum(R)::float - sum(E)::float) as change,
        elo as constructorElo
    from elo_setup
    group by all
)
select 
    race_id, year, round, constructor_id, R, E, constructorElo as elo, change as elo_change, constructorElo + change as new_elo,
from elo_sum 
group by all 
order by year, round, constructor_id
;
"""

print("Updating the local database")
conn.execute(create_query)

conn.close()
