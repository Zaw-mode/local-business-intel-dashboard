WITH area_rollup AS (
  SELECT
    ROUND(latitude, 2) AS area_lat,
    ROUND(longitude, 2) AS area_lon,
    COUNT(*) AS shop_count,
    AVG(price_tier) AS avg_price_tier,
    AVG(traffic_proxy) AS avg_traffic_proxy,
    AVG(rating) AS avg_rating,
    SUM(review_count) AS total_reviews
  FROM {{ ref('stg_shops') }}
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
