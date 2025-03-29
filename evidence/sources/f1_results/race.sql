select 
    race.*,
    grand_prix.short_name 
from race
    join grand_prix on grand_prix.id = race.grand_prix_id