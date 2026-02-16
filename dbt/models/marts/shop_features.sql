SELECT
  shop_id,
  name,
  category,
  city,
  state,
  postal_code,
  latitude,
  longitude,
  price_tier,
  rating,
  review_count,
  source_count,
  traffic_proxy,
  price_score,
  overall_score
FROM {{ ref('stg_shops') }}
