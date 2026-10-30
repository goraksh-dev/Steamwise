import re
from pathlib import Path
import numpy as np
import pandas as pd

ALIASES = {
    "name": ["name", "title", "game", "app_name", "game_name"],
    "price": ["current_price_usd", "current_price", "price", "final_price", "initial_price", "cost", "game_price"],
    "rating": ["steam_rating_pct", "rating", "positive_rating", "review_score", "user_score", "percent_positive", "positive_percent"],
    "reviews": ["reviews", "review_count", "total_reviews", "recommendations", "number_of_reviews", "positive", "owners_reviews"],
    "genres": ["genres", "genre", "category", "categories"],
    "tags": ["tags", "steamspy_tags", "popular_tags"],
    "release_year": ["release_year", "year", "release_date", "released"],
    "app_id": ["appid", "app_id", "steam_appid", "steam_app_id"],
    "discount": ["discount", "discount_percent", "discount_pct"],
}

def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")

def _find_col(df, candidates):
    norm_map = {_norm(c): c for c in df.columns}
    for cand in candidates:
        if _norm(cand) in norm_map:
            return norm_map[_norm(cand)]
    # Common variants by partial match
    for col in df.columns:
        c = _norm(col)
        if any(_norm(x) in c for x in candidates if len(_norm(x)) > 4):
            return col
    return None

def _number(series):
    return pd.to_numeric(series.astype(str).str.replace(r"[$€,£,\s]", "", regex=True).str.replace("%","", regex=False), errors="coerce")


def load_games(source, usd_to_inr=88.0):
    df = pd.read_csv(source, low_memory=False)
    if df.empty:
        return pd.DataFrame()
    out = pd.DataFrame(index=df.index)
    # Map the main columns, avoiding positive-only counts as total review counts.
    for target, aliases in ALIASES.items():
        if target == "reviews":
            aliases = ["reviews", "review_count", "total_reviews", "number_of_reviews", "recommendations"]
        col = _find_col(df, aliases)
        if col is not None:
            out[target] = df[col]

    # Derive a percentage rating and total review count when raw positive/negative
    # rating counts are supplied by common Steam datasets.
    positive_col = _find_col(df, ["positive_ratings", "positive_reviews", "positive_rating_count"])
    negative_col = _find_col(df, ["negative_ratings", "negative_reviews", "negative_rating_count"])
    if positive_col is not None and negative_col is not None:
        positive = _number(df[positive_col]).clip(lower=0)
        negative = _number(df[negative_col]).clip(lower=0)
        total = positive + negative
        derived_rating = (positive / total.replace(0, np.nan)) * 100
        if "rating" not in out or out["rating"].isna().all():
            out["rating"] = derived_rating
        if "reviews" not in out or out["reviews"].isna().all():
            out["reviews"] = total

    if "name" not in out:
        obj = df.select_dtypes(include=["object"]).columns
        if len(obj):
            out["name"] = df[obj[0]].astype(str)
        else:
            out["name"] = "Unknown game"
    out["name"] = out["name"].fillna("").astype(str).str.strip()
    out = out[out["name"].ne("") & out["name"].str.lower().ne("nan")].copy()
    for col in ["price","rating","reviews","app_id","discount"]:
        if col in out:
            out[col] = _number(out[col])
    if "price" not in out:
        out["price"] = np.nan
    # The supplied Steam dataset stores prices in USD. Preserve the source value
    # and use INR as the app-wide price field for filters, charts and recommendations.
    out["price_usd"] = out["price"]
    out["price"] = out["price_usd"] * float(usd_to_inr)
    if "rating" in out and out["rating"].dropna().size:
        q = out["rating"].dropna().quantile(.95)
        if q <= 1.0:
            out["rating"] = out["rating"] * 100
        out["rating"] = out["rating"].clip(0,100)
    else:
        out["rating"] = np.nan
    if "reviews" not in out:
        out["reviews"] = np.nan
    out["reviews"] = out["reviews"].clip(lower=0)
    if "genres" not in out:
        out["genres"] = ""
    if "tags" not in out:
        out["tags"] = ""
    out["genres"] = out["genres"].fillna("").astype(str)
    out["tags"] = out["tags"].fillna("").astype(str)
    if "release_year" in out:
        raw_year = out["release_year"]
        extracted = pd.to_numeric(raw_year, errors="coerce")
        from_dates = pd.to_datetime(raw_year, errors="coerce").dt.year
        out["release_year"] = extracted.fillna(from_dates)
    else:
        out["release_year"] = np.nan
    if "app_id" not in out:
        out["app_id"] = np.nan
    out["app_id"] = pd.to_numeric(out["app_id"], errors="coerce")
    out = out.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)
    return out

def summarize_games(df):
    return {
        "count": int(len(df)),
        "avg_price": df["price"].mean() if "price" in df else np.nan,
        "free_count": int((df["price"].fillna(-1) == 0).sum()) if "price" in df else 0,
        "avg_rating": df["rating"].mean() if "rating" in df else np.nan,
    }

def _split_values(series):
    vals = set()
    for raw in series.fillna("").astype(str):
        for item in re.split(r"[;,|/]", raw):
            item = item.strip()
            if item and item.lower() not in {"nan","none","null"}:
                vals.add(item)
    return sorted(vals, key=str.casefold)

def available_genres(df):
    return _split_values(df["genres"]) if "genres" in df else []

def available_tags(df):
    return _split_values(df["tags"]) if "tags" in df else []
