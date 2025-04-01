```sql constructor
select
  constructor.*,
  constructor.name as constructor_name,
  row_number() over (order by elo_constructor.year, elo_constructor.round) as race_order,
  elo_constructor.year,
  elo_constructor.round,
  race.date,
  race.official_name,
  race.short_name,
  race.grand_prix_id,
  elo_constructor.constructor_id,
  elo_constructor.elo,
  elo_constructor.elo_change,
  elo_constructor.R,
  elo_constructor.E,
  '/race/' || race.year::int || '/' || race.round::int as race_link
  from f1_results.constructor
  join f1_results.elo_constructor on constructor.id = elo_constructor.constructor_id
  join f1_results.race on race.id = elo_constructor.race_id
where
    constructor.id = '${params.id}'
order by race.year desc, race.round desc
```

# Stats for <Value data={constructor} column=constructor_name/>

```sql stats
select
  max(elo) as max_elo,
  min(elo) as min_elo,
from ${constructor}
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
select * from ${constructor} 
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
  series=constructor_name
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

<DataTable data={constructor}>
  <Column id=short_name/>
  <Column id=year/>
  <Column id=round/>
  <Column id=R title="HtH Result"/>
  <Column id=E title="HtH Expectation"/>
  <Column id=elo/>
  <Column id=elo_change contentType=delta/>
  <Column id=race_link contentType=link linkLabel="Race Details"/>
</DataTable>

# Drivers

```sql drivers
select distinct 
  race_result.driver_id, driver.name 
from race_result 
  join driver on driver.id = race_result.driver_id 
where constructor_id = '${params.id}' 
```

<Dropdown data={drivers} name=driver_filter value=driver_id label=name multiple=true selectAllByDefault=true />

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
  join f1_results.race_result on race_result.race_id = elo.race_id and race_result.driver_id = driver.id
where
    race_result.constructor_id = '${params.id}'
    and
    driver.id in ${inputs.driver_filter.value}
order by race.year desc, race.round desc
```

```sql driver_stats
select
  max(elo) as max_elo,
  min(elo) as min_elo,
from ${driver}
```

```sql driver_timeline
select * from ${driver} 
```

```sql driver_chart
select
  floor(min(elo) / 20) * 20 as yMin,
  ceiling(max(elo) / 20) * 20 as yMax
from ${driver_timeline}
```

<LineChart
  data={driver_timeline}
  x=date
  y=elo
  series=driver_name
  step=true
  chartAreaHeight=500
  yMin={driver_chart[0].yMin}
  yMax={driver_chart[0].yMax}
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
