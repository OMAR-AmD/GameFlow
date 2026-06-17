import nbformat as nbf

nb = nbf.v4.new_notebook()

markdown_intro = """\
# Phase 5: Hybrid Recommendation System
In this notebook, we test the `GameRecommender` class which provides 3 types of recommendations:
1. **Cold-Start Persona Recommendation** (for new users who just chose a Persona)
2. **Content-Based Filtering** (for users looking for games similar to a specific game)
3. **Collaborative Filtering** (for existing users based on their play history, optimized with TruncatedSVD)
"""

code_init = """\
import sys
sys.path.append('../src')
from recommender import GameRecommender

# Initialize the engine (this will load SQLite data, build Genre matrix and SVD Latent User Matrix)
print("Initializing GameRecommender...")
recommender = GameRecommender()
print("Engine successfully loaded!")
"""

code_persona = """\
# 1. PERSONA-BASED RECOMMENDATION (Cold Start)
# Let's say a new user registers and their quiz places them in Cluster 1: The Narrative Completionist
print("--- Persona 1: The Narrative Completionist ---")
recs = recommender.recommend_by_persona(cluster_id=1, top_n=5)
for i, game in enumerate(recs, 1):
    print(f"{i}. {game}")
    
print("\\n--- Persona 2: The Standard Competitor ---")
recs_comp = recommender.recommend_by_persona(cluster_id=2, top_n=5)
for i, game in enumerate(recs_comp, 1):
    print(f"{i}. {game}")
"""

code_content = """\
# 2. CONTENT-BASED RECOMMENDATION (Similar Games)
# Let's say a user loves 'The Elder Scrolls V: Skyrim'
target_game = "The Elder Scrolls V: Skyrim"
print(f"--- Games similar to '{target_game}' ---")

recs = recommender.recommend_similar_games(target_game, top_n=5)
for i, game in enumerate(recs, 1):
    print(f"{i}. {game}")
"""

code_collab = """\
# 3. COLLABORATIVE FILTERING (User-to-User via TruncatedSVD)
# Let's pick a random active user from our dataset
sample_user = recommender.interactions_df['user_id'].value_counts().index[0] # The most active user
print(f"--- Recommendations for User ID: {sample_user} ---")

# First, what are they currently playing?
current_games = recommender.interactions_df[recommender.interactions_df['user_id'] == sample_user]
print("Already Plays (Top 3):")
for game in current_games.sort_values(by='hours_played', ascending=False)['name'].head(3):
    print(f"- {game}")

print("\\nRecommended via Collaborative Filtering:")
recs = recommender.recommend_for_user(sample_user, top_n=5)
for i, game in enumerate(recs, 1):
    print(f"{i}. {game}")
"""

nb.cells = [
    nbf.v4.new_markdown_cell(markdown_intro),
    nbf.v4.new_code_cell(code_init),
    nbf.v4.new_code_cell(code_persona),
    nbf.v4.new_code_cell(code_content),
    nbf.v4.new_code_cell(code_collab)
]

with open('notebooks/05_recommender_testing.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook created at notebooks/05_recommender_testing.ipynb")
