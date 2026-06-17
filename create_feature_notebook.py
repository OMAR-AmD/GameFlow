import nbformat as nbf

nb = nbf.v4.new_notebook()

# Initial Markdown
markdown_intro = """\
# Phase 3: Feature Engineering & Data Management
This notebook performs the following:
1. Fuzzy matching game titles between the two datasets.
2. Feature engineering 7 behavioral proxies for each user.
3. Exporting the final profiles to CSV and SQLite.
"""

# Cell 1: Imports
code_imports = """\
import pandas as pd
import numpy as np
import sqlite3
from rapidfuzz import process, fuzz
import re
import warnings
warnings.filterwarnings('ignore')
"""

# Cell 2: Load Data
code_load = """\
# Load cleaned datasets
df_play = pd.read_csv('../data/interim/steam200k_cleaned.csv')
df_meta = pd.read_csv('../data/interim/steam_metadata_cleaned.csv')

print(f"Play data shape: {df_play.shape}")
print(f"Meta data shape: {df_meta.shape}")
"""

# Cell 3: Fuzzy Matching
code_fuzzy = """\
# 1. Fuzzy Matching Game Titles
unique_play_titles = df_play['game_title'].unique()
meta_titles = df_meta['name'].dropna().unique()

print(f"Unique games in 200k dataset: {len(unique_play_titles)}")
print(f"Unique games in metadata: {len(meta_titles)}")

# Clean titles for better matching
def clean_title(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

meta_dict = {clean_title(title): title for title in meta_titles}
meta_clean_list = list(meta_dict.keys())

title_mapping = {}
for title in unique_play_titles:
    clean_t = clean_title(title)
    # Direct match first
    if clean_t in meta_dict:
        title_mapping[title] = meta_dict[clean_t]
    else:
        # Fuzzy match
        match = process.extractOne(clean_t, meta_clean_list, scorer=fuzz.WRatio)
        if match and match[1] >= 85: # 85% confidence threshold
            title_mapping[title] = meta_dict[match[0]]
        else:
            title_mapping[title] = None # No confident match

# Map titles
df_play['meta_name'] = df_play['game_title'].map(title_mapping)
matched_ratio = df_play['meta_name'].notnull().mean()
print(f"Successfully matched {matched_ratio*100:.2f}% of play interactions to metadata.")

# Drop interactions that couldn't be matched
df_merged = df_play.dropna(subset=['meta_name']).merge(df_meta, left_on='meta_name', right_on='name', how='inner')
print(f"Merged dataset shape: {df_merged.shape}")
"""

# Cell 4: Feature Engineering logic
code_fe = """\
# 2. Feature Engineering
print("Computing behavioral features...")

# Ensure types
df_merged['hours_played'] = pd.to_numeric(df_merged['hours_played'], errors='coerce')
df_merged['median_playtime'] = pd.to_numeric(df_merged['median_playtime'], errors='coerce').fillna(0)
df_merged['average_playtime'] = pd.to_numeric(df_merged['average_playtime'], errors='coerce').fillna(0)

# Convert metadata playtimes from minutes to hours for comparison
df_merged['median_playtime_hr'] = df_merged['median_playtime'] / 60.0
df_merged['average_playtime_hr'] = df_merged['average_playtime'] / 60.0

# Base calculations per interaction
# 1. Completion Ratio (capped at 1.0)
df_merged['comp_ratio'] = np.where(
    df_merged['median_playtime_hr'] > 0,
    np.minimum(df_merged['hours_played'] / df_merged['median_playtime_hr'], 1.0),
    np.minimum(df_merged['hours_played'] / 2.0, 1.0) # Assume 2 hours if no median data
)

# 2. Session Intensity Proxy
df_merged['intensity'] = np.where(
    df_merged['average_playtime_hr'] > 0,
    df_merged['hours_played'] / df_merged['average_playtime_hr'],
    df_merged['hours_played'] / 5.0 # Assume 5 hours average if no data
)

# 3. Abandonment Flag
df_merged['is_abandoned'] = np.where(
    df_merged['median_playtime_hr'] > 0,
    (df_merged['hours_played'] < (0.10 * df_merged['median_playtime_hr'])).astype(int),
    (df_merged['hours_played'] < 0.5).astype(int) # Abandoned if played less than 30 mins
)

# Tags & Genres parsing
df_merged['all_tags'] = (df_merged['genres'].fillna('') + ';' + df_merged['steamspy_tags'].fillna('')).str.lower()

df_merged['is_competitive'] = df_merged['all_tags'].str.contains('multi-player|multiplayer|e-sports|action|fps|moba', na=False)
df_merged['is_exploration'] = df_merged['all_tags'].str.contains('open world|exploration|adventure', na=False)
df_merged['is_narrative'] = df_merged['all_tags'].str.contains('story rich|rpg|visual novel', na=False)

# Extract unique genres per game
df_merged['genre_list'] = df_merged['genres'].str.split(r'[;,]')
total_platform_genres = len(set(g.strip() for l in df_merged['genre_list'].dropna() for g in l if g.strip() != ''))

print("Base interaction features computed.")
"""

# Cell 5: Aggregation per user
code_agg = """\
# Aggregate to User Level
user_groups = df_merged.groupby('user_id')

# 1, 2, 4
user_profiles = user_groups.agg({
    'comp_ratio': 'mean',
    'intensity': 'mean',
    'is_abandoned': 'mean',
    'game_title': 'count', # Total games played
    'hours_played': 'sum' # Total hours played
}).rename(columns={
    'comp_ratio': 'completion_ratio',
    'intensity': 'session_intensity',
    'is_abandoned': 'abandonment_rate',
    'game_title': 'total_games'
})

# 3. Diversity Score
def get_unique_genres(series):
    genres = set()
    for g_list in series.dropna():
        for g in g_list:
            if g.strip() != '':
                genres.add(g.strip())
    return len(genres)

user_profiles['diversity_score'] = user_groups['genre_list'].apply(get_unique_genres) / total_platform_genres

# 5, 6, 7: Time-weighted affinity
user_playtime = df_merged.groupby('user_id')['hours_played'].sum()

competitive_time = df_merged[df_merged['is_competitive']].groupby('user_id')['hours_played'].sum()
exploration_time = df_merged[df_merged['is_exploration']].groupby('user_id')['hours_played'].sum()
narrative_time = df_merged[df_merged['is_narrative']].groupby('user_id')['hours_played'].sum()

user_profiles['competitive_index'] = (competitive_time / user_playtime).fillna(0)
user_profiles['exploration_score'] = (exploration_time / user_playtime).fillna(0)
user_profiles['narrative_affinity'] = (narrative_time / user_playtime).fillna(0)

# Final formatting
user_profiles = user_profiles.reset_index()
print(f"Generated profiles for {len(user_profiles)} unique users.")
display(user_profiles.head())
"""

# Cell 6: SQLite Export
code_export = """\
# 3. Export to SQLite
import os

# Create processed dir if not exists
os.makedirs('../data/processed', exist_ok=True)
db_path = '../data/processed/gameflow.db'

# Remove existing db if running again
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)

# Export User Profiles
user_profiles.to_sql('user_profiles', conn, if_exists='replace', index=False)

# Export Raw Interactions (just the essential columns for querying)
interactions_clean = df_merged[['user_id', 'appid', 'name', 'hours_played']]
interactions_clean.to_sql('interactions', conn, if_exists='replace', index=False)

# Export Metadata (essential columns)
meta_clean = df_meta[['appid', 'name', 'developer', 'publisher', 'genres']]
meta_clean.to_sql('games', conn, if_exists='replace', index=False)

conn.close()

# Also save CSV for backup/easy loading
user_profiles.to_csv('../data/processed/user_profiles.csv', index=False)
print("Data successfully exported to SQLite and CSV.")
"""

nb.cells = [
    nbf.v4.new_markdown_cell(markdown_intro),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_code_cell(code_load),
    nbf.v4.new_code_cell(code_fuzzy),
    nbf.v4.new_code_cell(code_fe),
    nbf.v4.new_code_cell(code_agg),
    nbf.v4.new_code_cell(code_export)
]

with open('notebooks/03_feature_engineering.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook created at notebooks/03_feature_engineering.ipynb")
