import re
import numpy as np
import pandas as pd

def _contains_any(text, selections):
    if not selections:
        return None
    text = str(text).casefold()
    return any(str(s).casefold() in text for s in selections)

def recommend_games(df, budget, genres=None, tags=None, min_rating=0, min_reviews=0, free_only=False):
    if df.empty:
        return df.copy()
    result = df.copy()
    # Apply explicit constraints first.
    if "price" in result:
        result = result[result["price"].notna() & (result["price"] <= float(budget))]
    if free_only:
        result = result[result["price"].fillna(-1) == 0]
    result = result[result["rating"].fillna(0) >= float(min_rating)]
    if "reviews" in result and result["reviews"].notna().any():
        result = result[result["reviews"].fillna(0) >= float(min_reviews)]
    if result.empty:
        return result.assign(score=pd.Series(dtype=float))
    # Weighted content-based heuristic: genre 45%, rating 30%, review strength 15%, price fit 10%.
    genre_score = result["genres"].apply(lambda x: 100 if _contains_any(x, genres) else 0) if genres else pd.Series(50.0, index=result.index)
    tag_score = result["tags"].apply(lambda x: 100 if _contains_any(x, tags) else 0) if tags else pd.Series(50.0, index=result.index)
    preference_score = (genre_score * 0.75) + (tag_score * 0.25)
    rating_score = result["rating"].fillna(50).clip(0,100)
    reviews = result["reviews"].fillna(0).clip(lower=0)
    max_log = np.log1p(reviews.max()) if len(reviews) else 0
    review_score = (np.log1p(reviews) / max_log * 100) if max_log > 0 else pd.Series(50.0, index=result.index)
    price = result["price"].fillna(float(budget))
    price_score = (100 - (price / max(float(budget), 1) * 100)).clip(0,100)
    # With no genre/tag preference, give neutral preference contribution.
    result["score"] = (preference_score * 0.45) + (rating_score * 0.30) + (review_score * 0.15) + (price_score * 0.10)
    return result.sort_values(["score","rating","reviews"], ascending=False, na_position="last").reset_index(drop=True)
