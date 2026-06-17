import sqlite3
import pandas as pd

import os

def run_queries():
    # Use absolute path to ensure it runs from anywhere
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'processed', 'gameflow.db')
    conn = sqlite3.connect(db_path)
    
    print("==========================================================")
    print(" GAMEFLOW - PHASE 3: SQL ANALYTICAL QUERIES")
    print("==========================================================\n")
    
    # Query 1: Top 10 Hardcore Gamers
    print("--- Query 1: Top 10 Users by Session Intensity (Min 5 games) ---")
    q1 = """
    SELECT user_id, session_intensity, total_games, hours_played
    FROM user_profiles
    WHERE total_games >= 5
    ORDER BY session_intensity DESC
    LIMIT 10;
    """
    df1 = pd.read_sql_query(q1, conn)
    print(df1.to_string(index=False))
    print("\n")
    
    # Query 2: Abandonment Rate vs Competitive Nature
    print("--- Query 2: Avg Abandonment Rate for Competitive vs Non-Competitive Users ---")
    q2 = """
    SELECT 
        CASE WHEN competitive_index >= 0.5 THEN 'Competitive (>=50%)' ELSE 'Casual/Other (<50%)' END as player_type,
        COUNT(*) as num_users,
        ROUND(AVG(abandonment_rate), 4) as avg_abandonment_rate,
        ROUND(AVG(diversity_score), 4) as avg_diversity
    FROM user_profiles
    GROUP BY player_type;
    """
    df2 = pd.read_sql_query(q2, conn)
    print(df2.to_string(index=False))
    print("\n")
    
    # Query 3: Favorite Games of Narrative Lovers
    print("--- Query 3: Top 5 Games Played by Users with High Narrative Affinity (>0.5) ---")
    q3 = """
    SELECT g.name, COUNT(DISTINCT i.user_id) as narrative_players, ROUND(SUM(i.hours_played), 0) as total_hours
    FROM interactions i
    JOIN user_profiles u ON i.user_id = u.user_id
    JOIN games g ON i.appid = g.appid
    WHERE u.narrative_affinity > 0.5
    GROUP BY g.name
    ORDER BY total_hours DESC
    LIMIT 5;
    """
    df3 = pd.read_sql_query(q3, conn)
    print(df3.to_string(index=False))
    print("\n")
    
    # Query 4: Completion Ratio by Diversity Score Brackets
    print("--- Query 4: Completion Ratio & Intensity grouped by Diversity Score ---")
    q4 = """
    SELECT 
        ROUND(diversity_score, 1) as diversity_bracket,
        COUNT(*) as num_users,
        ROUND(AVG(completion_ratio), 4) as avg_completion,
        ROUND(AVG(session_intensity), 4) as avg_intensity
    FROM user_profiles
    GROUP BY diversity_bracket
    ORDER BY diversity_bracket ASC;
    """
    df4 = pd.read_sql_query(q4, conn)
    print(df4.to_string(index=False))
    print("\n")

    conn.close()

if __name__ == "__main__":
    run_queries()
