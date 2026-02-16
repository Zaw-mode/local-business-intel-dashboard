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
FROM {{ ref('stg_shops') }}
WHERE price_tier IS NOT NULL
