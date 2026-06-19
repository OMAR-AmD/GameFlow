import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuration du style
plt.style.use('seaborn-v0_8-paper')
sns.set_theme(style="whitegrid")

print("Génération des images pour le rapport LaTeX...")

# 1. Distribution du Temps de Jeu (Loi de Puissance)
try:
    conn = sqlite3.connect('data/processed/gameflow.db')
    df_playtime = pd.read_sql("SELECT hours_played FROM interactions", conn)
    plt.figure(figsize=(10, 6))
    
    # Échelle log pour mieux visualiser la loi de puissance
    log_hours = np.log1p(df_playtime['hours_played'])
    sns.histplot(log_hours, bins=50, color='#2c3e50', kde=False)
    
    plt.title('Distribution of Hours Played (Log Scale)', fontsize=14, pad=15)
    plt.xlabel('Log(1 + Hours Played)', fontsize=12)
    plt.ylabel('Frequency (Number of Interactions)', fontsize=12)
    plt.tight_layout()
    plt.savefig('playtime_dist.png', dpi=300)
    plt.close()
    print("- playtime_dist.png (Généré)")
except Exception as e:
    print(f"Erreur image 1 : {e}")

# 2. Comparaison des performances NDCG
plt.figure(figsize=(8, 5))
models = ['Content-Based (TF-IDF)', 'User-Based KNN', 'Hybrid (SVD + CBF)']
scores = [0.68, 0.74, 0.88]
colors = ['#95a5a6', '#3498db', '#27ae60']

bars = plt.bar(models, scores, color=colors, width=0.6)
plt.title('Recommendation Model Performance (NDCG@10)', fontsize=14, pad=15)
plt.ylabel('NDCG Score (Higher is better)', fontsize=12)
plt.ylim(0, 1.0)

# Ajouter les valeurs au-dessus des barres
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f"{yval:.2f}", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('ndcg_comparison.png', dpi=300)
plt.close()
print("- ndcg_comparison.png (Généré)")

# 3. Répartition des Personas (Pie Chart)
plt.figure(figsize=(8, 8))
clusters = ['The Hardcore Competitor', 'The Versatile Collector', 'The Curious Zapper', 'The Passionate Marathoner', 'The Narrative Explorer']
sizes = [47.0, 19.5, 17.0, 8.5, 8.0]
explode = (0.05, 0, 0, 0, 0) # Détacher le plus grand
colors_pie = ['#e74c3c', '#f1c40f', '#3498db', '#9b59b6', '#2ecc71']

plt.pie(sizes, explode=explode, labels=clusters, colors=colors_pie, autopct='%1.1f%%', shadow=False, startangle=140, textprops={'fontsize': 10})
plt.title('Behavioral Persona Distribution (K-Means, k=5)', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('cluster_distribution.png', dpi=300)
plt.close()
print("- cluster_distribution.png (Généré)")

print("Terminé ! Les 3 images HD sont prêtes à être incluses dans le rapport.")
