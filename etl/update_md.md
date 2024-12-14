# Update Motherduck

```
duckdb 'md:F1_Results';

attach 'f1_results.duckdb' as f1_local;
drop table F1_Results.elo;
create table f1_results.elo as select * from f1_local.elo;
```