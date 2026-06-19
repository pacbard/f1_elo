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
url: str = "https://github.com/f1db/f1db/releases/latest/download/f1db-sqlite.zip"

download_and_unzip(url, extract_path=".")

db_path = "f1db_local.duckdb"

conn = duckdb.connect(db_path)

constructor_weight = 0.5  # 0 = pure driver Elo, 1 = equal driver/constructor blend

create_query = f"""
attach 'f1db.db' as f1db (type sqlite, READ_ONLY);

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
select distinct
	race_result.driver_id, 
	race_result.race_id,
	race.year,
	race.round,
	NULL as elo_change,
	NULL as elo,
	NULL as R, 
	NULL as E
from race_result
	join race on race.id = race_result.race_id
order by race_result.driver_id, race.year, race.round
;

-- Create Elo Constructor Table
create or replace table elo_constructor as
select distinct
	race_result.constructor_id, 
	race_result.race_id,
	race.year,
	race.round,
	NULL as elo_change,
	NULL as elo,
	NULL as R, 
	NULL as E
from race_result
	join race on race.id = race_result.race_id
order by race_result.constructor_id, race.year, race.round
;

-- Elo calculation
create or replace view elo_calc as
WITH
res as (
    select
        race_result.race_id,
        race.year,
        race.round,
        race.official_name as race_name,
        driver.id as driver_id,
        driver.abbreviation as driver_ref,
        constructor.id as constructor_id,
        case
            when race_result.position_number is null then (select max(rr.position_number) + 1 from race_result as rr where rr.race_id = race.id)
            else race_result.position_number::int 
        end as position,
        constructor.name as constructor_name,
    from race_result
        join race on race.id = race_result.race_id
        join driver on driver.id = race_result.driver_id
        join constructor on constructor.id = race_result.constructor_id
    where
        race_result.shared_car = 0
),
race_performance as (
    select
        res.driver_id,
        res.constructor_id,
        res.race_id,
        res.year,
        res.round,
        res.position,
        res2.driver_id as opponentId,
        res2.constructor_id as opponentConstructorId,
        res2.position as opponentPosition,
        case
            when res.position::int < res2.position::int then 1
            when res.position::int = res2.position::int then 0.5
            when res.position::int > res2.position::int then 0
        end as headToHead,
    from res
    join res as res2 on res2.race_id = res.race_id
        and res2.driver_id != res.driver_id
),
elo_driver_start as (
    select
        driver_id,
        race_id,
        year,
        round,
        coalesce(lag(elo, 1) over (partition by driver_id order by year, round), 1000) as elo,
    from elo_driver
),
elo_constructor_start as (
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
        race_performance.driver_id,
        race_performance.constructor_id,
        elo_dri.elo as driver_elo,
        elo_cons.elo as constructor_elo,
        race_performance.headToHead as R,
        pow(10, (
            (elo_dri.elo + {constructor_weight} * elo_cons.elo) / {1 + constructor_weight}
            - (elo_opp.elo + {constructor_weight} * elo_copp.elo) / {1 + constructor_weight}
        ) / 400) / (pow(10, (
            (elo_dri.elo + {constructor_weight} * elo_cons.elo) / {1 + constructor_weight}
            - (elo_opp.elo + {constructor_weight} * elo_copp.elo) / {1 + constructor_weight}
        ) / 400) + 1) as E_driver,
        pow(10, (elo_cons.elo - elo_copp.elo) / 400)
        / (pow(10, (elo_cons.elo - elo_copp.elo) / 400) + 1) as E_constructor,
    from race_performance
        -- Driver Elo
        left join elo_driver_start as elo_dri on elo_dri.driver_id = race_performance.driver_id
            and elo_dri.race_id = race_performance.race_id
        left join elo_driver_start as elo_opp on elo_opp.driver_id = race_performance.opponentId
            and elo_opp.race_id = race_performance.race_id
        -- Constructor Elo
        left join elo_constructor_start as elo_cons on elo_cons.constructor_id = race_performance.constructor_id
            and elo_cons.race_id = race_performance.race_id
        left join elo_constructor_start as elo_copp on elo_copp.constructor_id = race_performance.opponentConstructorId
            and elo_copp.race_id = race_performance.race_id
    order by race_performance.race_id, race_performance.driver_id
),
elo_summary as (
    select
        race_id,
        year,
        round,
        driver_id,
        constructor_id,
        driver_elo,
        constructor_elo,
        sum(R)::float as R,
        sum(E_driver)::float as E_driver,
        sum(E_constructor)::float as E_constructor,
        count(*) as nOpponents,
        32::float * (sum(R)::float - sum(E_driver)::float) / count(*) as driver_change,
        32::float * (sum(R)::float - sum(E_constructor)::float) / count(*) as constructor_change,
    from elo_setup
    group by race_id, year, round, driver_id, constructor_id, driver_elo, constructor_elo
)
select
    race_id, year, round, driver_id, constructor_id,
    R, E_driver, E_constructor, driver_change, constructor_change,
    driver_elo, driver_elo + driver_change as new_driver_elo,
    constructor_elo, constructor_elo + constructor_change as new_constructor_elo,
from elo_summary
order by year, round, driver_id
;
"""

print("Updating the local database")
conn.execute(create_query)

conn.close()
