```sql driver
select
  driver.*,
  driver.name as driver_name,
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  race.date,
  race.official_name,
  race.grand_prix_id,
  elo.driver_id,
  elo.elo,
  elo.elo_change,
  from f1_results.driver
  join f1_results.elo on driver.id = elo.driver_id
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
  <Column id=official_name/>
  <Column id=year/>
  <Column id=round/>
  <Column id=elo/>
  <Column id=elo_change contentType=delta/>
</DataTable>