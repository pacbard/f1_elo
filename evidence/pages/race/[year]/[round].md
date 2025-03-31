```sql race
select * from race where race.year = ${params.year} and race.round = ${params.round}
```

# Race Results for the <Value data={race} column=year/> <Value data={race} column=short_name/>

## Driver Results

```sql race_driver
select
    *,
    elo_driver.R as position,
    elo_driver.E as expected
from race_result
    join elo_driver on elo_driver.race_id = race_result.race_id and elo_driver.driver_id = race_result.driver_id
    join elo_constructor on elo_constructor.race_id = race_result.race_id and elo_constructor.constructor_id = race_result.constructor_id
    join driver on driver.id = elo_driver.driver_id
    join constructor on constructor.id = elo_constructor.constructor_id
where elo_driver.year = ${params.year} and elo_driver.round = ${params.round}
order by position desc
```

<DataTable data={race_driver} rows=all>
    <Column id=name/>
    <Column id=elo_change contentType=delta/>
    <Column id=elo/>
    <Column id=position title="HtH Wins" fmt=num/>
    <Column id=expected title="HtH Expected" fmt=num1/>
</DataTable>

## Constructor Results

```sql race_constructor
select
    *,
    R as position,
    E as expected
from elo_constructor
    join constructor on constructor.id = elo_constructor.constructor_id
where elo_constructor.year = ${params.year} and elo_constructor.round = ${params.round}
order by position desc
```

<DataTable data={race_constructor} rows=all>
    <Column id=name/>
    <Column id=elo_change contentType=delta fmt=num1/>
    <Column id=elo fmt=num0/>
    <Column id=position title="HtH Wins" fmt=num/>
    <Column id=expected title="HtH Expected" fmt=num1/>
</DataTable>