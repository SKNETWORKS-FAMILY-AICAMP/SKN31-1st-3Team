use mysql;
use vehicle_db;

select * from electric_vehicle_count;
-- (년도, 지역, 전기자동차 수) query
select year,region, sum(count) as "total count"
from electric_vehicle_count
group by year, region;


-- (년도, 총 자동차 수) query
select * from car_total;

-- (전기자동차, 총 자동차 합계)query
SELECT 
    e.year,
    e.ev_count,
    c.total as "total_count"
FROM (
    SELECT 
        year,
        SUM(count) AS ev_count
    FROM electric_vehicle_count
    GROUP BY year
) e
JOIN car_total c
ON e.year = c.year;

-- ([년도,월->6월,12월], 지역, 총 충전소 수)
SELECT 
    month,
    region,
    SUM(count) AS total_countev_chargercar_total
FROM ev_charger
WHERE RIGHT(month, 2) IN ('06', '12')
GROUP BY month, region
ORDER BY month, region;