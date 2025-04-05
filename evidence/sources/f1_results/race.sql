select 
    race.* exclude (pre_qualifying_date, free_practice_4_date, qualifying_1_date, qualifying_2_date, warming_up_date),
    grand_prix.short_name 
from race
    join grand_prix on grand_prix.id = race.grand_prix_id