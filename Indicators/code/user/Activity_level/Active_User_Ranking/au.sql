-- au
select
	user_id,
    count(behavior_type) num_behavior_type
from data_min
group by user_id
order by num_behavior_type desc
limit 100
