import sqlite3
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

class GameRecommender:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, 'data', 'processed', 'gameflow.db')
        else:
            self.db_path = db_path
            
        self._load_data()
        self._build_content_matrix()
        self._build_collaborative_matrix()
        
    def _load_data(self):
        """Load required tables from SQLite."""
        conn = sqlite3.connect(self.db_path)
        self.games_df = pd.read_sql('SELECT * FROM games', conn)
        self.interactions_df = pd.read_sql('SELECT * FROM interactions', conn)
        self.profiles_df = pd.read_sql('SELECT * FROM user_profiles_clustered', conn)
        conn.close()
        
    def _build_content_matrix(self):
        """Prepare Content-Based filtering using genres."""
        self.games_df['genres'] = self.games_df['genres'].fillna('')
        self.vectorizer = CountVectorizer(tokenizer=lambda x: x.split(';'))
        self.genre_matrix = self.vectorizer.fit_transform(self.games_df['genres'])
        self.game_indices = pd.Series(self.games_df.index, index=self.games_df['name']).drop_duplicates()
        
    def _build_collaborative_matrix(self):
        """Prepare Collaborative filtering using TruncatedSVD."""
        self.user_item_matrix = self.interactions_df.pivot_table(
            index='user_id', 
            columns='name', 
            values='hours_played', 
            fill_value=0
        )
        
        n_components = min(50, self.user_item_matrix.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_latent_matrix = self.svd.fit_transform(self.user_item_matrix)
        
    def recommend_by_persona(self, cluster_id, top_n=5):
        """COLD START: Recommend games based on a specific Persona."""
        cluster_users = self.profiles_df[self.profiles_df['cluster'] == cluster_id]['user_id']
        cluster_interactions = self.interactions_df[self.interactions_df['user_id'].isin(cluster_users)]
        top_games = cluster_interactions.groupby('name')['hours_played'].sum().sort_values(ascending=False)
        return top_games.head(top_n).index.tolist()

    def recommend_cold_start(self, selected_games, top_n=10, explain=False):
        """COLD START: Guess Persona from selected games and recommend."""
        # 1. Find which cluster plays these games the most
        game_interactions = self.interactions_df[self.interactions_df['name'].isin(selected_games)]
        if game_interactions.empty:
            recs = self.recommend_similar_games(selected_games[0], top_n=top_n)
            if explain:
                return {"games": recs, "persona": -1, "method": "content-based"}
            return recs
            
        # 2. Merge with profiles to get clusters of the users who play these games
        merged = game_interactions.merge(self.profiles_df, on='user_id')
        if merged.empty:
            recs = self.recommend_similar_games(selected_games[0], top_n=top_n)
            if explain:
                return {"games": recs, "persona": -1, "method": "content-based"}
            return recs
            
        # 3. The cluster with the most interactions for these games is our guessed Persona
        guessed_cluster = int(merged['cluster'].mode()[0])
        
        # 4. Recommend top games from this Persona
        recs = self.recommend_by_persona(guessed_cluster, top_n=top_n + len(selected_games))
        
        # 5. Filter out the games the user already selected
        final_recs = [g for g in recs if g not in selected_games][:top_n]
        
        if explain:
            return {"games": final_recs, "persona": guessed_cluster, "method": "persona"}
        return final_recs

    def recommend_similar_games(self, game_name, top_n=5):
        """CONTENT-BASED: Recommend games similar to a given game based on genres."""
        if game_name not in self.game_indices:
            return []
            
        idx = self.game_indices[game_name]
        sim_scores = cosine_similarity(self.genre_matrix[idx], self.genre_matrix).flatten()
        similar_indices = sim_scores.argsort()[-(top_n+1):-1][::-1]
        
        return self.games_df['name'].iloc[similar_indices].tolist()

    def recommend_for_user(self, user_id, top_n=5, return_scores=False):
        """COLLABORATIVE FILTERING: Recommend games for an existing user."""
        if user_id not in self.user_item_matrix.index:
            return []
            
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_vector = self.user_latent_matrix[user_idx].reshape(1, -1)
        
        sim_scores = cosine_similarity(user_vector, self.user_latent_matrix).flatten()
        similar_user_indices = sim_scores.argsort()[-6:-1][::-1]
        
        recommended_games = {}
        games_played_by_target = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        
        for sim_idx in similar_user_indices:
            sim_user_id = self.user_item_matrix.index[sim_idx]
            sim_user_games = self.interactions_df[self.interactions_df['user_id'] == sim_user_id]
            
            for _, row in sim_user_games.iterrows():
                game = row['name']
                if game not in games_played_by_target:
                    recommended_games[game] = recommended_games.get(game, 0) + row['hours_played']
                    
        # Normalize scores between 0 and 1
        if recommended_games:
            max_score = max(recommended_games.values())
            recommended_games = {k: v / max_score for k, v in recommended_games.items()}
            
        sorted_recs = sorted(recommended_games.items(), key=lambda x: x[1], reverse=True)
        
        if return_scores:
            return sorted_recs[:top_n]
        return [game for game, score in sorted_recs[:top_n]]

    def recommend_hybrid(self, user_id, top_n=5, collab_weight=0.7, content_weight=0.3, explain=False):
        """
        HYBRID: Combines Collaborative Filtering with Content-Based Filtering.
        Finds a large candidate pool using Collaborative Filtering, then boosts scores
        of games that are mathematically similar to the user's top played games.
        """
        if user_id not in self.user_item_matrix.index:
            return []
            
        # 1. Get top 50 candidates from Collaborative Filtering
        collab_candidates = self.recommend_for_user(user_id, top_n=50, return_scores=True)
        if not collab_candidates:
            return []
            
        candidate_dict = dict(collab_candidates)
        
        # 2. Find user's top 3 most played games for Content-Based boosting
        user_games = self.interactions_df[self.interactions_df['user_id'] == user_id]
        top_played = user_games.sort_values(by='hours_played', ascending=False).head(3)['name'].tolist()
        
        final_scores = {}
        collab_scores_map = {}
        content_scores_map = {}
        
        for candidate_game, collab_score in candidate_dict.items():
            content_score = 0
            
            # 3. Calculate how similar the candidate is to the user's favorite games
            if candidate_game in self.game_indices:
                idx_candidate = self.game_indices[candidate_game]
                for fav_game in top_played:
                    if fav_game in self.game_indices:
                        idx_fav = self.game_indices[fav_game]
                        # Cosine similarity between genre vectors
                        sim = cosine_similarity(self.genre_matrix[idx_candidate], self.genre_matrix[idx_fav]).flatten()[0]
                        content_score = max(content_score, sim) # Take the highest similarity
            
            # 4. Weighted Mix
            collab_scores_map[candidate_game] = collab_score
            content_scores_map[candidate_game] = content_score
            final_scores[candidate_game] = (collab_weight * collab_score) + (content_weight * content_score)
            
        # Sort by final hybrid score
        sorted_hybrid = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        if explain:
            results = []
            for game, score in sorted_hybrid[:top_n]:
                results.append({
                    "name": game,
                    "collab_score": round(collab_scores_map.get(game, 0), 3),
                    "content_score": round(content_scores_map.get(game, 0), 3),
                    "final_score": round(score, 3),
                    "top_played": top_played
                })
            return results
        return [game for game, score in sorted_hybrid[:top_n]]

if __name__ == "__main__":
    print("Initializing GameRecommender Engine...")
    recommender = GameRecommender()
    print("Engine Ready!")
    
    sample_user = recommender.interactions_df['user_id'].value_counts().index[0]
    print(f"\\n--- Test Hybrid Recommendation for User: {sample_user} ---")
    recs = recommender.recommend_hybrid(sample_user, top_n=5)
    for i, game in enumerate(recs, 1):
        print(f"{i}. {game}")
