from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .places_client import PlacesClient, polite_sleep
from .storage import connect
from .text_analytics import extract_themes
from .scoring import competitor_score
from .geocode import geocode_nominatim
from .brave_enrich import brave_search


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", required=True, help="Business category/keyword (e.g. 'coffee shop')")

    # Option A: direct lat/lng
    ap.add_argument("--lat", type=float, help="Latitude")
    ap.add_argument("--lng", type=float, help="Longitude")

    # Option B: area string
    ap.add_argument("--area", help="Area string to geocode (e.g. 'Austin, TX' or '78617')")

    ap.add_argument("--radius-m", type=int, required=True, help="Search radius in meters")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--enrich-brave", action="store_true", help="Optional: enrich each place with a Brave Search snippet (requires BRAVE_API_KEY)")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    db_path = root / "data" / "bi.sqlite"
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve center point
    if args.area and (args.lat is None or args.lng is None):
        gp = geocode_nominatim(args.area)
        lat, lng = gp.lat, gp.lng
    elif args.lat is not None and args.lng is not None:
        lat, lng = args.lat, args.lng
    else:
        raise SystemExit("Provide either (--lat and --lng) OR --area")

    client = PlacesClient()
    con = connect(db_path)

    run_ts = datetime.now().isoformat(timespec="seconds")
    con.execute(
        "INSERT INTO runs(created_at, keyword, lat, lng, radius_m, limit_n) VALUES (?,?,?,?,?,?)",
        (run_ts, args.keyword, lat, lng, args.radius_m, args.limit),
    )
    con.commit()

    places = client.search_text(args.keyword, lat, lng, args.radius_m, limit=args.limit)

    all_places = []
    all_reviews = []
    all_themes = []

    for i, p in enumerate(places):
        pid = p.get("id")
        if not pid:
            continue
        details = client.place_details(pid)

        loc = details.get("location") or {}
        name = ((details.get("displayName") or {}).get("text"))
        address = details.get("formattedAddress")
        rating = details.get("rating")
        urc = details.get("userRatingCount")
        types = ",".join(details.get("types") or [])

        reviews = details.get("reviews") or []
        themes = extract_themes(reviews)

        con.execute(
            "INSERT OR REPLACE INTO places(place_id,name,address,lat,lng,rating,user_rating_count,types,website,phone,price_level,business_status,raw_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                pid,
                name,
                address,
                loc.get("latitude"),
                loc.get("longitude"),
                rating,
                urc,
                types,
                details.get("websiteUri"),
                details.get("nationalPhoneNumber"),
                details.get("priceLevel"),
                details.get("businessStatus"),
                json.dumps(details, ensure_ascii=False),
            ),
        )

        # reviews
        for r in reviews:
            rid = r.get("name") or f"{pid}:{r.get('publishTime','')}:{r.get('relativePublishTimeDescription','')}"
            text = ((r.get("text") or {}).get("text"))
            con.execute(
                "INSERT OR REPLACE INTO reviews(review_id,place_id,rating,relative_publish_time,publish_time,text,language_code,author_name,raw_json) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    rid,
                    pid,
                    r.get("rating"),
                    r.get("relativePublishTimeDescription"),
                    r.get("publishTime"),
                    text,
                    (r.get("text") or {}).get("languageCode"),
                    (r.get("authorAttribution") or {}).get("displayName"),
                    json.dumps(r, ensure_ascii=False),
                ),
            )

        # themes
        con.execute("DELETE FROM themes WHERE place_id=?", (pid,))
        for t in themes:
            con.execute(
                "INSERT INTO themes(place_id,theme,count,sentiment,sample) VALUES (?,?,?,?,?)",
                (pid, t["theme"], t["count"], t.get("sentiment"), t.get("sample")),
            )

        con.commit()
        score = competitor_score(rating, urc)

        enrich = []
        if args.enrich_brave and name:
            try:
                enrich = brave_search(f"{name} {address or ''}", count=2)
            except Exception:
                enrich = []

        all_places.append({
            "place_id": pid,
            "name": name,
            "address": address,
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
            "rating": rating,
            "user_rating_count": urc,
            "score": score,
            "types": types,
            "brave_top_result_url": (enrich[0].get("url") if enrich else None),
            "brave_top_result_title": (enrich[0].get("title") if enrich else None),
        })

        for r in reviews:
            all_reviews.append({
                "place_id": pid,
                "rating": r.get("rating"),
                "publishTime": r.get("publishTime"),
                "relative": r.get("relativePublishTimeDescription"),
                "text": ((r.get("text") or {}).get("text")),
            })

        for t in themes:
            all_themes.append({"place_id": pid, **t})

        polite_sleep(i)

    df_places = pd.DataFrame(all_places)
    df_places.to_csv(out_dir / "places.csv", index=False)

    # competitor ranking (Tableau-friendly)
    if not df_places.empty:
        df_comp = df_places.sort_values(["score", "rating", "user_rating_count"], ascending=False)
        df_comp.to_csv(out_dir / "competitors.csv", index=False)

    pd.DataFrame(all_reviews).to_csv(out_dir / "reviews.csv", index=False)
    pd.DataFrame(all_themes).to_csv(out_dir / "themes.csv", index=False)

    print(f"OK. Wrote {db_path}")
    print(f"OK. Wrote {out_dir / 'places.csv'}")
    if not df_places.empty:
        print(f"OK. Wrote {out_dir / 'competitors.csv'}")


if __name__ == "__main__":
    main()
