```sql driver
select
  driver.*,
  driver.name as driver_name,
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  race.date,
  race.official_name,
  race.short_name,
  race.grand_prix_id,
  elo.driver_id,
  elo.elo,
  elo.elo_change,
  elo.R,
  elo.E,
  from f1_results.driver
  join f1_results.elo_driver as elo on driver.id = elo.driver_id
  join f1_results.race on race.id = elo.race_id
where
    driver.id = '${params.id}'
order by race.year desc, race.round desc
```

# Stats for <Value data={driver} column=driver_name/>

```sql stats
select
  max(elo) as max_elo,
  min(elo) as min_elo,
from ${driver}
```
<BigValue
  data={stats}
  value=max_elo
/>

<BigValue
  data={stats}
  value=min_elo
/>

```sql timeline
select * from ${driver} 
```

```sql chart
select
  floor(min(elo) / 20) * 20 as yMin,
  ceiling(max(elo) / 20) * 20 as yMax
from ${timeline}
```

<LineChart
  data={timeline}
  x=date
  y=elo
  series=driver_name
  step=true
  chartAreaHeight=500
  yMin={chart[0].yMin}
  yMax={chart[0].yMax}
  echartsOptions={{
      dataZoom: {
          show: true,
          bottom: 10
      },
      grid: {
          bottom: 50
      }
  }}
/>

<DataTable data={driver}>
  <Column id=short_name/>
  <Column id=year/>
  <Column id=round/>
  <Column id=elo/>
  <Column id=elo_change contentType=delta/>
</DataTable>

# Teams

```sql teams
select distinct 
  race_result.constructor_id, constructor.name
from race_result 
  join constructor on constructor.id = race_result.constructor_id 
where driver_id = '${params.id}' 
```

<Dropdown data={teams} name=team_filter value=constructor_id label=name multiple=true selectAllByDefault=true />

```sql constructor
select
  constructor.*,
  constructor.name as constructor_name,
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  race.date,
  race.official_name,
  race.short_name,
  race.grand_prix_id,
  elo.constructor_id,
  elo.elo,
  elo.elo_change,
  elo.R,
  elo.E,
  from f1_results.constructor
  join f1_results.elo_constructor as elo on constructor.id = elo.constructor_id
  join f1_results.race on race.id = elo.race_id
  join f1_results.race_result on race_result.race_id = elo.race_id and race_result.constructor_id = constructor.id
where
    race_result.driver_id = '${params.id}'
    and
    constructor.id in ${inputs.team_filter.value}
order by race.year desc, race.round desc
```

```sql constructor_stats
select
  max(elo) as max_elo,
  min(elo) as min_elo,
from ${constructor}
```

```sql constructor_timeline
select * from ${constructor} 
```

```sql constructor_chart
select
  floor(min(elo) / 20) * 20 as yMin,
  ceiling(max(elo) / 20) * 20 as yMax
from ${constructor_timeline}
```

<LineChart
  data={constructor_timeline}
  x=date
  y=elo
  series=constructor_name
  step=true
  chartAreaHeight=500
  yMin={constructor_chart[0].yMin}
  yMax={constructor_chart[0].yMax}
  echartsOptions={{
      dataZoom: {
          show: true,
          bottom: 10
      },
      grid: {
          bottom: 50
      }
  }}
/>
