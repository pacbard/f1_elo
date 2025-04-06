---
title: Greatest Of All Time 🐐
---

```sql goat
select
  driver.*,
  driver.name as driver_name,
  elo_driver.elo as max_elo, 
  race.short_name as race_name,
  race.date as race_date,
  '/driver/' || driver.id as driver_link,
  '/race/' || race.year::int || '/' || race.round::int as race_link
from f1_results.driver
  join f1_results.elo_driver on elo_driver.driver_id = driver.id
  join f1_results.race on race.id = elo_driver.race_id
qualify row_number() OVER (partition by elo_driver.driver_id ORDER BY elo_driver.elo DESC) = 1; 
order by max_elo desc
```

<DataTable data={goat} wrapTitles=true link=driver_link>
  <Column id=last_name/>
  <Column id=first_name/>
  <Column id=max_elo/>
  <Column id=race_name/>
  <Column id=race_date/>
  <Column id=race_link contentType=link linkLabel="Race Details" />
</DataTable>

# Change over Time 📈

<Dropdown data={goat} name=driver_filter value=id label=driver_name multiple=true defaultValue={['lewis-hamilton', 'max-verstappen']}/>

```sql timeline
select
  row_number() over (order by elo_driver.year, elo_driver.round) as race_order,
  elo_driver.year,
  elo_driver.round,
  race.date,
  race.official_name,
  elo_driver.driver_id,
  elo_driver.elo,
  driver.name as driver_name,
from f1_results.driver
  join f1_results.elo_driver on driver.id = elo_driver.driver_id
  join f1_results.race on race.id = elo_driver.race_id
where
  driver.id in ${inputs.driver_filter.value}
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

