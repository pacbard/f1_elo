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
  <Column id=elo/>
  <Column id=elo_change contentType=delta/>
</DataTable>