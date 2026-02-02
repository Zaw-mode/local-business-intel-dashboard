from __future__ import annotations

import json
from collections import Counter

from textblob import TextBlob

THEMES = {
    "parking": ["parking", "park", "garage"],
    "service": ["service", "staff", "rude", "friendly"],
    "price": ["price", "expensive", "cheap", "cost"],
    "wait_time": ["wait", "line", "queue", "slow"],
    "cleanliness": ["clean", "dirty"],
    "quality": ["quality", "fresh", "stale"],
}


def extract_themes(reviews: list[dict]) -> list[dict]:
    texts = [(((r.get("text") or {}).get("text")) or "") for r in reviews]
    joined = "\n".join(texts).lower()

    theme_counts: dict[str, int] = {}
    samples: dict[str, str] = {}

    for theme, keywords in THEMES.items():
        count = 0
        sample = ""
        for t in texts:
            tl = t.lower()
            if any(k in tl for k in keywords):
                count += 1
                if not sample:
                    sample = t[:240]
        if count:
            theme_counts[theme] = count
            samples[theme] = sample

    # sentiment: average polarity across all reviews (rough)
    sentiments = []
    for t in texts:
        if t.strip():
            try:
                sentiments.append(TextBlob(t).sentiment.polarity)
            except Exception:
                pass
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None

    out = []
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        out.append({"theme": theme, "count": count, "sentiment": avg_sentiment, "sample": samples.get(theme, "")})
    return out
