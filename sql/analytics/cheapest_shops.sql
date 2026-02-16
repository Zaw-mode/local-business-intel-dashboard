CREATE OR REPLACE TABLE analytics_cheapest_shops AS
SELECT
  shop_id,
  name,
  category,
  address,
  city,
  state,
  latitude,
  longitude,
  price_tier,
  rating,
  review_count,
  traffic_proxy,
  overall_score,
  ROW_NUMBER() OVER (
    ORDER BY price_tier ASC, traffic_proxy DESC, overall_score DESC
  ) AS cheap_rank
FROM shops_master
WHERE price_tier IS NOT NULL
ORDER BY cheap_rank;
