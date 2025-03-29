# Constructor Elo Ratings 🏁

```sql goat
select
  constructor.*,
  constructor.name as constructor_name,
  elo_constructor.elo as max_elo, 
  race.short_name as race_name,
  race.date as race_date,
  '/constr/' || constructor.id as constructor_link
from f1_results.constructor
  join f1_results.elo_constructor on elo_constructor.constructor_id = constructor.id
  join f1_results.race on race.id = elo_constructor.race_id
qualify row_number() OVER (partition by elo_constructor.constructor_id ORDER BY elo_constructor.elo DESC) = 1; 
order by max_elo desc
```

<DataTable data={goat} wrapTitles=true link=constructor_link>
  <Column id=constructor_name/>
  <Column id=max_elo/>
  <Column id=race_name/>
  <Column id=race_date/>
</DataTable>

# Change over Time 📈

<Dropdown data={goat} name=constructor_filter value=id label=constructor_name multiple=true defaultValue={['Ferrari', 'Mercedes', 'Red Bull']}/>

```sql timeline
select
  row_number() over (order by elo_constructor.year, elo_constructor.round) as race_order,
  elo_constructor.year,
  elo_constructor.round,
  race.date,
  race.official_name,
  elo_constructor.constructor_id,
  elo_constructor.elo,
  constructor.name as constructor_name,
from f1_results.constructor
  join f1_results.elo_constructor on constructor.id = elo_constructor.constructor_id
  join f1_results.race on race.id = elo_constructor.race_id
where
  constructor.id in ${inputs.constructor_filter.value}
```

<LineChart
  data={timeline}
  x=date
  y=elo
  series=constructor_name
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

