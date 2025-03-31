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

