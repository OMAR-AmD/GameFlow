from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import sqlite3
import pandas as pd

# Add the parent directory to sys.path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.recommender import GameRecommender

app = FastAPI(title="GameFlow AI API")

# Setup CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Recommender
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'gameflow.db'))
recommender = GameRecommender(DB_PATH)

class ColdStartRequest(BaseModel):
    games: list[str]

class WarmStartRequest(BaseModel):
    user_id: int

@app.get("/api/games")
def get_games():
    """Return list of all games for the frontend dropdown."""
    conn = sqlite3.connect(DB_PATH)
    games_df = pd.read_sql("SELECT name FROM games ORDER BY name", conn)
    conn.close()
    return {"games": games_df["name"].tolist()}

@app.get("/api/users")
def get_users():
    """Return top 200 active users for the frontend dropdown."""
    conn = sqlite3.connect(DB_PATH)
    users_df = pd.read_sql("""
        SELECT user_id, COUNT(name) as play_count 
        FROM interactions 
        GROUP BY user_id 
        HAVING play_count >= 10
        ORDER BY play_count DESC
        LIMIT 200
    """, conn)
    conn.close()
    return {"users": users_df["user_id"].astype(str).tolist()}

PERSONA_NAMES = {
    0: "Zappeur Curieux",
    1: "Explorateur Narratif",
    2: "Compétiteur Hardcore",
    3: "Marathonien Passionné",
    4: "Collectionneur Versatile"
}

def enrich_game(name):
    """Lookup game metadata from DB."""
    matching = recommender.games_df[recommender.games_df['name'] == name]
    if matching.empty:
        return {"name": name, "image": None, "genres": "", "developer": "", "publisher": ""}
    row = matching.iloc[0]
    appid = int(row['appid'])
    return {
        "name": name,
        "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
        "genres": row.get('genres', ''),
        "developer": row.get('developer', ''),
        "publisher": row.get('publisher', '')
    }

@app.post("/api/recommend/cold-start")
def recommend_cold_start(req: ColdStartRequest):
    if len(req.games) == 0:
        raise HTTPException(status_code=400, detail="At least one game is required.")
    try:
        result = recommender.recommend_cold_start(req.games, top_n=20, explain=True)
        game_names = result["games"]
        persona = result["persona"]
        method = result["method"]
        persona_label = PERSONA_NAMES.get(persona, f"Profil #{persona}")
        
        enriched = []
        for i, name in enumerate(game_names):
            info = enrich_game(name)
            if method == "persona":
                reason = f"🧠 Votre sélection correspond à la Persona \"{persona_label}\". Ce jeu est le #{i+1} le plus joué par les joueurs de ce groupe comportemental."
            else:
                reason = f"🔗 Recommandé par similarité de genres avec \"{req.games[0]}\"."
            info["reason"] = reason
            enriched.append(info)
        
        return {"recommendations": enriched, "persona": persona_label}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/hybrid")
def recommend_hybrid(req: WarmStartRequest):
    try:
        results = recommender.recommend_hybrid(req.user_id, top_n=20, explain=True)
        if not results:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable ou historique insuffisant pour la matrice SVD.")
        
        top_played = results[0].get("top_played", [])
        top_played_str = ", ".join(top_played[:3]) if top_played else "N/A"
        
        enriched = []
        for r in results:
            info = enrich_game(r["name"])
            collab_pct = round(r["collab_score"] * 100)
            content_pct = round(r["content_score"] * 100)
            
            if content_pct > 0:
                reason = f"📊 Score Collaboratif (SVD): {collab_pct}% · Score Contenu (Genres): {content_pct}% — Similaire à vos favoris ({top_played_str})."
            else:
                reason = f"📊 Score Collaboratif (SVD): {collab_pct}% — Des joueurs ayant un profil similaire au vôtre adorent ce jeu."
            info["reason"] = reason
            enriched.append(info)
        
        return {"recommendations": enriched}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics():
    """Return analytics data for the Admin dashboard."""
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Persona Distribution (users per cluster)
    profiles = pd.read_sql("SELECT cluster, COUNT(*) as count FROM user_profiles_clustered GROUP BY cluster ORDER BY cluster", conn)
    persona_distribution = []
    for _, row in profiles.iterrows():
        cluster_id = int(row['cluster'])
        persona_distribution.append({
            "name": PERSONA_NAMES.get(cluster_id, f"Cluster {cluster_id}"),
            "count": int(row['count']),
            "cluster": cluster_id
        })
    
    # 2. Average playtime per Persona
    avg_playtime = pd.read_sql("""
        SELECT p.cluster, ROUND(AVG(i.hours_played), 1) as avg_hours
        FROM interactions i
        JOIN user_profiles_clustered p ON i.user_id = p.user_id
        GROUP BY p.cluster
        ORDER BY p.cluster
    """, conn)
    playtime_by_persona = []
    for _, row in avg_playtime.iterrows():
        cluster_id = int(row['cluster'])
        playtime_by_persona.append({
            "name": PERSONA_NAMES.get(cluster_id, f"Cluster {cluster_id}"),
            "hours": float(row['avg_hours'])
        })
    
    # 3. Top 10 Genres (Basé sur le temps de jeu réel)
    df_genres = pd.read_sql("""
        SELECT g.genres, i.hours_played 
        FROM interactions i
        JOIN games g ON i.appid = g.appid
        WHERE g.genres IS NOT NULL AND g.genres != ''
    """, conn)
    
    genre_popularity = {}
    for _, row in df_genres.iterrows():
        for genre in str(row['genres']).split(';'):
            genre = genre.strip()
            if genre:
                genre_popularity[genre] = genre_popularity.get(genre, 0) + row['hours_played']
                
    top_genres = sorted(genre_popularity.items(), key=lambda x: x[1], reverse=True)[:10]
    genres_data = [{"name": g, "count": int(c)} for g, c in top_genres]
    
    # 4. Summary stats
    total_users = int(pd.read_sql("SELECT COUNT(DISTINCT user_id) as c FROM interactions", conn).iloc[0]['c'])
    total_games = int(pd.read_sql("SELECT COUNT(*) as c FROM games", conn).iloc[0]['c'])
    total_interactions = int(pd.read_sql("SELECT COUNT(*) as c FROM interactions", conn).iloc[0]['c'])
    
    conn.close()
    
    return {
        "persona_distribution": persona_distribution,
        "playtime_by_persona": playtime_by_persona,
        "top_genres": genres_data,
        "stats": {
            "total_users": total_users,
            "total_games": total_games,
            "total_interactions": total_interactions
        }
    }
