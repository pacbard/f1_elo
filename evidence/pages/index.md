---
title: F1 Elo Ratings
---

Inspired by this [YouTube Video](https://www.youtube.com/watch?v=U16a8tdrbII), I calculate the Elo ratings for all F1 drivers.

Unlike the linked video, where Elo ratings were based on within-team matches, I calculate Elo ratings by race. 

In this model, a race acts as a single event, where all drivers go head-to-head against each other and play a "match". The final Elo ratings are based on the average Elo results for all head-to-head matches for a race. 

For example, if a driver ends the race in 5th position out of 12 drivers, they have lost 4 matches with drivers who placed ahead of them and won 7 matches against drivers who placed behind them.

Elo ratings are calculated at the end of each race, and Elo ratings are pushed forward to the following races.

# Greatest Of All Time 

```sql goat
select
  drivers.*,
  case
    when code is not null then surname || ', ' || left(forename, 1) || ' (' || code || ')'
    else surname || ', ' || left(forename, 1)
  end as driver_name,
  max(elo.elo) as max_elo
from f1_results.drivers
  join f1_results.elo on elo.driverId = drivers.driverId
group by all
order by max_elo desc
```

<DataTable data={goat}>
  <Column id=surname/>
  <Column id=forename/>
  <Column id=max_elo/>
</DataTable>

# Change over Time

<Dropdown data={goat} name=driver_filter value=driverId label=driver_name multiple=true defaultValue={[1]}/>

```sql timeline
select
  row_number() over (order by elo.year, elo.round) as race_order,
  elo.year,
  elo.round,
  races.date,
  elo.driverId,
  elo.elo,
  case
    when code is not null then surname || ', ' || left(forename, 1) || ' (' || code || ')'
    else surname || ', ' || left(forename, 1)
  end as driver_name,
from f1_results.drivers
  join f1_results.elo on elo.driverId = drivers.driverId
  join f1_results.races on races.raceId = elo.raceId
where
  drivers.driverId in ${inputs.driver_filter.value}
```

<LineChart
  data={timeline}
  x=date
  y=elo
  series=driver_name
  step=true
  chartAreaHeight=500
  yMin=800
  yMax=1600
/>

