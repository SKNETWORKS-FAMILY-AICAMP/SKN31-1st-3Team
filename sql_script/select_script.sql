use mysql;
use vehicle_db;

-- (년도, 지역, 전기자동차 수) query
select year,region, sum(count) as "total count"
from electric_vehicle_count
group by year, region;

-- (년도, 총 자동차 수) query
select * from car_total;

-- ([년도,월->6월,12월], 지역, 총 충전소 수)
SELECT 
    month,
    region,
    SUM(count) AS total_count
FROM ev_charger
WHERE RIGHT(month, 2) IN ('06', '12')
GROUP BY month, region
ORDER BY month, region;