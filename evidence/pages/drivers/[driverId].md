```sql driver
select
  drivers.*,
  case
    when code is not null then surname || ', ' || forename
    else surname || ', ' || left(forename, 1)
  end as driver_name,
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  races.date,
  races.name,
  elo.driverId,
  elo.elo,
  case
    when code is not null then surname || ', ' || forename
    else surname || ', ' || forename
  end as driver_name,
from f1_results.drivers
  join f1_results.elo on elo.driverId = drivers.driverId
  join f1_results.races on races.raceId = elo.raceId
where
    drivers.driverId = ${params.driverId}
order by races.year, races.round desc
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

```sql year_filter
select distinct year from ${driver}
```

<Dropdown multiple=true selectAllByDefault=true data={year_filter} name=year_filter value=year/>

```sql timeline
select * from ${driver} where year in ${inputs.year_filter.value}
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