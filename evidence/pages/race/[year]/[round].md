```sql race
select * from race where race.year = ${params.year} and race.round = ${params.round}
```

# Race Results for the <Value data={race} column=year/> <Value data={race} column=short_name/>

## Driver Results

```sql race_driver
select
    *,
    max(R) over (partition by elo_driver.year, elo_driver.round) - R + 1 as position,
    max(E) over (partition by elo_driver.year, elo_driver.round) - E + 1 as expected
from elo_driver
    join driver on driver.id = elo_driver.driver_id
where elo_driver.year = ${params.year} and elo_driver.round = ${params.round}
order by position 
```

<DataTable data={race_driver} rows=all>
    <Column id=name/>
    <Column id=elo_change contentType=delta/>
    <Column id=elo/>
    <Column id=position/>
    <Column id=expected/>
</DataTable>

## Constructor Results

```sql race_constructor
select
    *,
    max(R) over (partition by elo_constructor.year, elo_constructor.round) - R + 1 as position,
    max(E) over (partition by elo_constructor.year, elo_constructor.round) - E + 1 as expected
from elo_constructor
    join constructor on constructor.id = elo_constructor.constructor_id
where elo_constructor.year = ${params.year} and elo_constructor.round = ${params.round}
order by position 
```

<DataTable data={race_constructor} rows=all>
    <Column id=name/>
    <Column id=elo_change contentType=delta fmt=num1/>
    <Column id=elo fmt=num0/>
    <Column id=position fmt=num/>
    <Column id=expected fmt=num1/>
</DataTable>