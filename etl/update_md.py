import duckdb

conn = duckdb.connect('md:F1_Results')

print("Update MotherDuck database with new data")
conn.execute("""
attach 'f1db_local.duckdb' as f1_local;

use F1_Results;

create or replace table constructor as select * from f1_local.constructor;
create or replace table driver as select * from f1_local.driver;
create or replace table elo as select * from f1_local.elo;
create or replace table race as select * from f1_local.race;
create or replace table grand_prix as select * from f1_local.grand_prix;
create or replace table race_result as select * from f1_local.race_result;
""")