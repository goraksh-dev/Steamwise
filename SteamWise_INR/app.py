from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from data_processing import load_games, summarize_games, available_genres, available_tags
from recommender import recommend_games
from analytics import make_price_chart, make_genre_chart, make_rating_chart

st.set_page_config(page_title="SteamWise", page_icon="🎮", layout="wide")
st.markdown("""
<style>
.stApp {background: #0b1020; color: #edf2ff;}
[data-testid="stSidebar"] {background: #11182b;}
div[data-testid="stMetric"] {background:#141e34; border:1px solid #263452; padding:16px; border-radius:14px;}
.sw-title {font-size:2.45rem;font-weight:800;letter-spacing:-1px;margin-bottom:0}
.sw-sub {color:#a9b7d0;margin-top:0.15rem}
div.stButton > button {border-radius:10px;font-weight:650}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "steam_games.csv"

@st.cache_data(show_spinner=False)
def get_data(uploaded_file, local_path, usd_to_inr):
    if uploaded_file is not None:
        return load_games(uploaded_file, usd_to_inr)
    if Path(local_path).exists():
        return load_games(local_path, usd_to_inr)
    return pd.DataFrame()

with st.sidebar:
    st.markdown("## 🎮 SteamWise")
    st.caption("Discover smarter. Play better.")
    page = st.radio("NAVIGATION", ["Dashboard", "Game Recommender", "Price Analysis", "Game Explorer", "About Project"])
    st.divider()
    st.markdown("### Dataset")
    uploaded = st.file_uploader("Upload Steam CSV", type=["csv"])
    st.caption("Loaded dataset: your 308-game CSV • prices converted from USD to INR.")
    usd_to_inr = st.number_input("USD to INR exchange rate (₹ per $1)", min_value=1.0, max_value=200.0, value=88.0, step=0.5, help="Editable approximate conversion rate. Change this to match the rate you want to use.")
    st.markdown("---")
    st.caption("Python • Pandas • Streamlit • Plotly")

try:
    games = get_data(uploaded, str(DATA_PATH), usd_to_inr)
except Exception as exc:
    games = pd.DataFrame()
    st.error(f"Could not read the dataset: {exc}. Check that it is a valid CSV file.")

if games.empty:
    st.markdown('<p class="sw-title">SteamWise</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-sub">Your personal Steam discovery and price intelligence dashboard.</p>', unsafe_allow_html=True)
    st.info("Upload your Kaggle Steam Games CSV in the sidebar, or place it at `data/steam_games.csv` to activate the full dashboard.")
    demo = pd.DataFrame([
        {"name":"Hollow Knight","price":14.99,"rating":96,"genres":"Action; Indie; Adventure","reviews":120000,"release_year":2017,"tags":"Metroidvania; Souls-like","app_id":367520},
        {"name":"Stardew Valley","price":14.99,"rating":98,"genres":"Indie; RPG; Simulation","reviews":250000,"release_year":2016,"tags":"Farming Sim; Relaxing","app_id":413150},
        {"name":"Portal 2","price":9.99,"rating":98,"genres":"Puzzle; Adventure","reviews":180000,"release_year":2011,"tags":"Puzzle; Comedy","app_id":620},
        {"name":"Terraria","price":9.99,"rating":97,"genres":"Action; Adventure; Indie","reviews":220000,"release_year":2011,"tags":"Sandbox; Survival","app_id":105600},
        {"name":"The Witcher 3: Wild Hunt","price":39.99,"rating":96,"genres":"RPG; Adventure","reviews":500000,"release_year":2015,"tags":"Open World; Story Rich","app_id":292030},
        {"name":"A Short Hike","price":7.99,"rating":99,"genres":"Adventure; Indie","reviews":22000,"release_year":2019,"tags":"Exploration; Relaxing","app_id":1055540},
    ])
    st.markdown("### Preview mode")
    st.caption("Sample titles below demonstrate the interface only. They are not loaded from your Kaggle dataset.")
    c1,c2,c3 = st.columns(3)
    c1.metric("Sample titles", len(demo))
    c2.metric("Average sample price", f"₹{demo.price.mean() * usd_to_inr:,.0f}")
    c3.metric("Average sample rating", f"{demo.rating.mean():.1f}%")
    demo_display = demo[["name","price","rating","genres"]].copy()
    demo_display["price"] = demo_display["price"].map(lambda v: f"₹{v * usd_to_inr:,.0f}")
    demo_display = demo_display.rename(columns={"price":"Price (INR)"})
    st.dataframe(demo_display, use_container_width=True, hide_index=True)
    st.stop()

stats = summarize_games(games)
st.markdown('<p class="sw-title">SteamWise <span style="color:#7c9cff">/</span></p>', unsafe_allow_html=True)
st.markdown('<p class="sw-sub">Discover smarter. Play better. Find your next favourite game.</p>', unsafe_allow_html=True)

if page == "Dashboard":
    st.subheader("Your gaming market at a glance")
    a,b,c,d = st.columns(4)
    a.metric("Games indexed", f"{stats['count']:,}")
    b.metric("Average price (INR)", f"₹{stats['avg_price']:,.0f}" if pd.notna(stats["avg_price"]) else "N/A")
    c.metric("Free games", f"{stats['free_count']:,}")
    d.metric("Average rating", f"{stats['avg_rating']:.1f}%" if pd.notna(stats["avg_rating"]) else "N/A")
    st.markdown("### Market overview")
    left,right = st.columns(2)
    with left:
        st.plotly_chart(make_price_chart(games), use_container_width=True)
    with right:
        st.plotly_chart(make_genre_chart(games), use_container_width=True)
    st.plotly_chart(make_rating_chart(games), use_container_width=True)
    st.caption("Statistics are calculated from the dataset columns that were successfully detected.")

elif page == "Game Recommender":
    st.subheader("Find games that fit your taste")
    st.write("Choose your budget and preferences. SteamWise ranks matching titles using a transparent weighted score.")
    genres = available_genres(games)
    tags = available_tags(games)
    with st.form("recommend_form"):
        c1,c2,c3 = st.columns(3)
        with c1:
            budget = st.number_input("Maximum price (INR)", min_value=0.0, value=3000.0, step=250.0)
            min_rating = st.slider("Minimum rating", 0, 100, 70)
        with c2:
            chosen_genres = st.multiselect("Preferred genres", genres[:80])
            chosen_tags = st.multiselect("Preferred tags", tags[:100])
        with c3:
            min_reviews = st.number_input("Minimum review count", min_value=0, value=0, step=100)
            free_only = st.checkbox("Free games only")
        submitted = st.form_submit_button("✨ Find my games", use_container_width=True)
    if submitted:
        results = recommend_games(games, budget, chosen_genres, chosen_tags, min_rating, min_reviews, free_only)
        if results.empty:
            st.warning("No games matched these filters. Try increasing your budget or lowering the rating/review limits.")
        else:
            st.success(f"Found {len(results):,} matching games. Showing the top 50.")
            show_cols = [c for c in ["name","price","rating","reviews","genres","tags","score","app_id"] if c in results.columns]
            result_display = results[show_cols].head(50).copy()
            if "price" in result_display:
                result_display["price"] = result_display["price"].map(lambda v: f"₹{v:,.0f}" if pd.notna(v) else "N/A")
                result_display = result_display.rename(columns={"price":"Price (INR)"})
            st.dataframe(result_display, use_container_width=True, hide_index=True)
            for _, row in results.head(6).iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['name']}**")
                    x,y,z = st.columns(3)
                    x.write(f"Price: **₹{row['price']:,.0f} INR**" if pd.notna(row['price']) else "Price: N/A")
                    y.write(f"Rating: **{row['rating']:.1f}%**" if pd.notna(row['rating']) else "Rating: N/A")
                    z.write(f"Match score: **{row['score']:.1f}/100**")
                    if pd.notna(row.get("app_id")):
                        st.markdown(f"[Open Steam store page](https://store.steampowered.com/app/{int(row['app_id'])}/)")
elif page == "Price Analysis":
    st.subheader("Price intelligence")
    c1,c2 = st.columns(2)
    with c1:
        low = st.number_input("Minimum price (INR)", min_value=0.0, value=0.0, step=250.0)
    with c2:
        high = st.number_input("Maximum price (INR)", min_value=0.0, value=10000.0, step=250.0)
    filtered = games[(games["price"].fillna(-1) >= low) & (games["price"].fillna(10**12) <= high)]
    st.metric("Games in selected price range", f"{len(filtered):,}")
    st.plotly_chart(make_price_chart(filtered), use_container_width=True)
    price_display = filtered[["name","price","rating","genres"]].sort_values("price").head(100).copy()
    price_display["price"] = price_display["price"].map(lambda v: f"₹{v:,.0f}" if pd.notna(v) else "N/A")
    price_display = price_display.rename(columns={"price":"Price (INR)"})
    st.dataframe(price_display, use_container_width=True, hide_index=True)
    st.caption(f"Prices are converted from the USD values in your CSV using ₹{usd_to_inr:.2f} per US$1. This is a static dataset, not a live Steam price feed.")
elif page == "Game Explorer":
    st.subheader("Explore the catalogue")
    query = st.text_input("Search game title", placeholder="e.g. Portal, Stardew Valley...")
    c1,c2 = st.columns(2)
    with c1:
        max_price = st.number_input("Maximum price (INR)", min_value=0.0, value=10000.0, step=250.0)
    with c2:
        sort_by = st.selectbox("Sort results by", ["Rating (high to low)","Price (low to high)","Reviews (high to low)","Title (A–Z)"])
    view = games[games["price"].fillna(0) <= max_price].copy()
    if query.strip():
        view = view[view["name"].str.contains(query.strip(), case=False, na=False)]
    sort_map = {"Rating (high to low)":"rating","Price (low to high)":"price","Reviews (high to low)":"reviews","Title (A–Z)":"name"}
    col = sort_map[sort_by]
    view = view.sort_values(col, ascending=(sort_by in ["Price (low to high)","Title (A–Z)"]), na_position="last")
    st.caption(f"{len(view):,} games match your search and price filter.")
    explorer_display = view[[c for c in ["name","price","rating","reviews","genres","tags","release_year","app_id"] if c in view.columns]].head(500).copy()
    if "price" in explorer_display:
        explorer_display["price"] = explorer_display["price"].map(lambda v: f"₹{v:,.0f}" if pd.notna(v) else "N/A")
        explorer_display = explorer_display.rename(columns={"price":"Price (INR)"})
    st.dataframe(explorer_display, use_container_width=True, hide_index=True)
    st.download_button("Download filtered results as CSV", view.to_csv(index=False).encode("utf-8"), "steamwise_filtered_games.csv", "text/csv")
elif page == "About Project":
    st.subheader("About SteamWise")
    st.markdown("""
**Objective:** Help users explore a large Steam game catalogue and find titles that fit their interests and budget.

**Workflow**
1. Load the CSV dataset.
2. Normalize column names and clean prices, ratings, review counts, genres, and tags.
3. Calculate summary statistics and visualizations.
4. Apply user-selected filters.
5. Rank matching games using a weighted content-based score.

**Recommendation score (0–100)**
- Genre match: 45%
- Rating: 30%
- Review strength: 15%
- Price fit: 10%

The score is a heuristic ranking, not a trained model's accuracy. Missing columns are handled gracefully; unavailable signals are not fabricated.

**Dataset used:** Your supplied CSV contains 308 games and 17 columns, including current/base price, all-time-low price, Steam rating percentage, genres, tags, discount fields, multiplayer, and free-game status. It does not include total review counts, so review-count filtering/strength is unavailable for this dataset.

**Limitations:** INR prices are conversions of the USD values in the supplied dataset, not verified Indian Steam store prices. The exchange rate is manually adjustable and not fetched live. Dataset prices and ratings can be historical or incomplete. Live Steam prices, current discounts, ownership, and personalised play history are not retrieved automatically.
""")
    st.markdown("### Data and privacy")
    st.write("The app processes the CSV locally in your Python environment. It does not require a Steam login or collect personal account information.")
