import pandas as pd
import plotly.express as px

LAYOUT = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=15,r=15,t=55,b=15))

def make_price_chart(df):
    data = df["price"].dropna() if "price" in df else pd.Series(dtype=float)
    if data.empty:
        return px.bar(title="Price distribution unavailable").update_layout(**LAYOUT)
    plot = pd.DataFrame({"Price": data.clip(upper=data.quantile(.99))})
    fig = px.histogram(plot, x="Price", nbins=30, title="Game price distribution (INR)", labels={"count":"Number of games", "Price":"Price (₹ INR)"})
    fig.update_layout(**LAYOUT, xaxis_title="Price (₹ INR)", yaxis_tickprefix="₹")
    return fig

def make_genre_chart(df):
    counts = {}
    if "genres" in df:
        for value in df["genres"].fillna("").astype(str):
            for genre in value.replace("|",";").replace(",", ";").split(";"):
                genre = genre.strip()
                if genre and genre.lower() not in {"nan","none"}:
                    counts[genre] = counts.get(genre,0)+1
    if not counts:
        return px.bar(title="Genre data unavailable").update_layout(**LAYOUT)
    top = pd.DataFrame(sorted(counts.items(), key=lambda x:x[1], reverse=True)[:12], columns=["Genre","Games"])
    fig = px.bar(top.sort_values("Games"), x="Games", y="Genre", orientation="h", title="Most common genres")
    fig.update_layout(**LAYOUT)
    return fig

def make_rating_chart(df):
    data = df["rating"].dropna() if "rating" in df else pd.Series(dtype=float)
    if data.empty:
        return px.histogram(title="Rating data unavailable").update_layout(**LAYOUT)
    fig = px.histogram(pd.DataFrame({"Rating (%)":data}), x="Rating (%)", nbins=20, title="User rating distribution")
    fig.update_layout(**LAYOUT)
    return fig
