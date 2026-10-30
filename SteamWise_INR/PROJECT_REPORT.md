# SteamWise — Project Report

## Abstract
SteamWise is a Python-based game discovery and price analysis application. It processes a Steam games CSV dataset and provides a dashboard, filters, visual analytics, and a weighted content-based recommendation list.

## Problem statement
A large game catalogue can make it difficult for users to discover suitable games and compare titles against a budget. SteamWise organizes the catalogue and ranks options according to user-selected preferences.

## Objectives
1. Load and preprocess Steam game data.
2. Summarize price, rating, and genre information.
3. Recommend games based on budget and selected preferences.
4. Visualize catalogue patterns.
5. Provide search, sorting, and CSV export.

## Dataset
The supplied dataset contains 308 game records and 17 columns. Key fields include game name and Steam app ID, genres and tags, release year, current/base/all-time-low prices converted from USD to INR, Steam rating percentage, playtime, multiplayer status, discount history, and free-game status. It does not provide a total review count.

## Tools
Python, Pandas, NumPy, Streamlit, Plotly.

## Methodology
The CSV is loaded and column names are mapped to standard fields. Numeric fields are cleaned; missing text values are normalized; duplicate titles are removed. Dashboard metrics and charts are calculated from available data. The recommender applies budget and budget and minimum-rating filters (review-count filtering is unavailable when the source has no review-count field), then computes a weighted score.

## Recommendation score
Score = 0.45 × preference score + 0.30 × rating score + 0.15 × review strength + 0.10 × price-fit score.

Preference score combines selected genres and tags. Review strength uses a logarithmic transformation when review counts exist; this dataset has no review-count field, so that signal is unavailable and should be explained as a limitation during the presentation. The result is a heuristic score from 0 to 100, not model accuracy.

## Limitations
Data freshness depends on the selected dataset. The app does not automatically retrieve current Steam sale prices or user play history. Recommendations depend on available columns and the quality of the dataset.

## Conclusion
SteamWise demonstrates data preprocessing, exploratory analysis, visualization, and a transparent recommendation algorithm in an interactive Python application.
