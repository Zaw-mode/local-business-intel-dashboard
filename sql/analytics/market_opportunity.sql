CREATE OR REPLACE TABLE analytics_market_opportunity AS
WITH area_rollup AS (
  SELECT
    ROUND(latitude, 2) AS area_lat,
    ROUND(longitude, 2) AS area_lon,
    COUNT(*) AS shop_count,
    AVG(COALESCE(price_tier, 2.5)) AS avg_price_tier,
    AVG(COALESCE(traffic_proxy, 0.4)) AS avg_traffic_proxy,
    AVG(COALESCE(rating, 3.5)) AS avg_rating,
    SUM(COALESCE(review_count, 0)) AS total_reviews
  FROM shops_master
  GROUP BY 1, 2
)
SELECT
  area_lat,
  area_lon,
  shop_count,
  avg_price_tier,
  avg_traffic_proxy,
  avg_rating,
  total_reviews,
  (
    (avg_traffic_proxy * 100)
    + (avg_rating * 8)
    + (LN(total_reviews + 1) * 10)
    - (shop_count * 12)
    - (avg_price_tier * 4)
  ) AS opportunity_score
FROM area_rollup
ORDER BY opportunity_score DESC;
