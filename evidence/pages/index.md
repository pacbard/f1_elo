---
title: F1 Elo Ratings 🏎️
---

Inspired by this [YouTube Video](https://www.youtube.com/watch?v=U16a8tdrbII), I calculate the [Elo ratings](https://en.wikipedia.org/wiki/Elo_rating_system) for all F1 drivers.

Unlike the linked video, where Elo ratings were based on within-team matches, I calculate Elo ratings by race. 

In this model, a race acts as a single event, where all drivers go head-to-head against each other and play a "match". The final Elo ratings are based on the average Elo results for all head-to-head matches for a race. 

For example, if a driver ends the race in 5th position out of 12 drivers, they have lost 4 matches with drivers who placed ahead of them and won 7 matches against drivers who placed behind them.

Elo ratings are calculated at the end of each race, and Elo ratings are pushed forward to the following races.

The dataset is available on [Motherduck](https://motherduck.com). Download it using this share:

```Code
-- Run this snippet to attach database
ATTACH 'md:_share/F1_Results/2c252e3d-f9a1-4ab1-93e1-328d84b6347b';
```

# Greatest Of All Time 🐐

```sql goat
select
  driver.*,
  driver.name as driver_name,
  elo.elo as max_elo, 
  race.short_name as race_name,
  race.date as race_date,
  '/driver/' || driver.id as driver_link
from f1_results.driver
  join f1_results.elo on elo.driver_id = driver.id
  join f1_results.race on race.id = elo.race_id
qualify row_number() OVER (partition by elo.driver_id ORDER BY elo.elo DESC) = 1; 
order by max_elo desc
```

<DataTable data={goat} wrapTitles=true link=driver_link>
  <Column id=last_name/>
  <Column id=first_name/>
  <Column id=max_elo/>
  <Column id=race_name/>
  <Column id=race_date/>
</DataTable>

# Change over Time 📈

<Dropdown data={goat} name=driver_filter value=id label=driver_name multiple=true defaultValue={['lewis-hamilton', 'max-verstappen']}/>

```sql timeline
select
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  race.date,
  race.official_name,
  elo.driver_id,
  elo.elo,
  driver.name as driver_name,
from f1_results.driver
  join f1_results.elo on driver.id = elo.driver_id
  join f1_results.race on race.id = elo.race_id
where
  driver.id in ${inputs.driver_filter.value}
```

<LineChart
  data={timeline}
  x=date
  y=elo
  series=driver_name
  step=true
  chartAreaHeight=500
  yMin=850
  yMax=1500
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

