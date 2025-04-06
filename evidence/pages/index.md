---
title: F1 Elo Ratings 🏎️
---

```sql seasons
select distinct year from race order by year desc
```

<Dropdown data={seasons} name=season value=year defaultValue={[2025]} title=Season/>

# Driver Standings

```sql driver_standings
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
  elo_change,
  elo.R,
  elo.E,
  '/race/' || cast(race.year as int) || '/' || cast(race.round as int) as race_link,
  dense_rank() over (order by race_id desc) as season_standings
from f1_results.driver
  join f1_results.elo_driver as elo on driver.id = elo.driver_id
  join f1_results.race on race.id = elo.race_id
where
    race.year = ${inputs.season.value}
order by race.year desc, race.round desc
```

<DataTable data={driver_standings} link=race_link sort="elo desc" rows=all groupBy=driver_name groupsOpen=false subtotals=true>
  <Column id=short_name/>
  <Column id=elo totalAgg=mean fmt=num0/>
  <Column id=elo_change totalAgg=sum contentType=delta fmt=num1/>
  <Column id=R totalAgg=sum title="HtH Wins" fmt=num0/>
  <Column id=E totalAgg=sum title="HtH Expected" fmt=num1/>
</DataTable>

<Details title='Progress Chart'>

```sql timeline
select * from ${driver_standings} 
```

```sql chart
select
  floor(min(elo) / 20) * 20 as yMin,
  ceiling(max(elo) / 20) * 20 as yMax
from ${timeline}
```

<LineChart
  data={timeline}
  x=round
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

</Details>

# Constructor Standings

```sql team_standings
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
  elo_change,
  elo.R,
  elo.E,
  '/race/' || race.year || '/' || race.round as race_link,
  dense_rank() over (order by race_id desc) as season_standings
  from f1_results.constructor
  join f1_results.elo_constructor as elo on constructor.id = elo.constructor_id
  join f1_results.race on race.id = elo.race_id
where
    race.year = ${inputs.season.value}
order by race.year desc, race.round desc
```

<DataTable data={team_standings} link=race_link sort="elo desc" rows=all groupBy=constructor_name groupsOpen=false subtotals=true>
  <Column id=short_name/>
  <Column id=elo totalAgg=mean fmt=num0/>
  <Column id=elo_change totalAgg=sum contentType=delta fmt=num1/>
  <Column id=R totalAgg=sum title="HtH Wins" fmt=num0/>
  <Column id=E totalAgg=sum title="HtH Expected" fmt=num1/>
</DataTable>

<Details title='Progress Chart'>

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
where
    race.year = ${inputs.season.value}
order by race.year desc, race.round desc
```

```sql constructor_chart
select
  floor(min(elo) / 20) * 20 as yMin,
  ceiling(max(elo) / 20) * 20 as yMax
from ${constructor}
```

<LineChart
  data={constructor}
  x=round
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

</Details>
