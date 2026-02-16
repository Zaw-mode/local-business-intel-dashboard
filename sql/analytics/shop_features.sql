CREATE OR REPLACE TABLE analytics_shop_features AS
SELECT
  shop_id,
  name,
  category,
  city,
  state,
  postal_code,
  latitude,
  longitude,
  COALESCE(price_tier, 2.5) AS price_tier,
  COALESCE(rating, 3.5) AS rating,
  COALESCE(review_count, 0) AS review_count,
  COALESCE(source_count, 1) AS source_count,
  COALESCE(traffic_proxy, 0.4) AS traffic_proxy,
  COALESCE(price_score, 0.5) AS price_score,
  COALESCE(overall_score, 50.0) AS overall_score
FROM shops_master;
