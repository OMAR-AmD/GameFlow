# 🎮 GameFlow AI : Behavior-Driven Game Recommendation System

![GameFlow AI Banner](dashboard/public/bg.png)

> **Ecole Hassania des Travaux Publics (EHTP)**  
> **Module :** AI & Data Science Basics  
> **Instructeur :** Dr. Rym Nassih  
> **Département :** MIG - EHTP (2025–2026)  
> **Équipe :** Akby Anass | Omar Amdouni

---

## 📖 À propos du projet

**GameFlow AI** est un moteur de recommandation de jeux vidéo conçu pour les utilisateurs de Steam. Contrairement aux systèmes conventionnels qui se basent uniquement sur les "tags" ou les genres déclarés, GameFlow recommande des jeux en se basant sur le **profil comportemental** du joueur (intensité des sessions, taux de complétion, tendances compétitives, affinité narrative).

L'objectif est de résoudre le problème de découvrabilité dans un catalogue massif de plus de 50 000 jeux, en distinguant par exemple deux joueurs de RPG : l'un qui termine scrupuleusement toutes les quêtes (complétionniste) et l'autre qui explore librement avant de passer à autre chose (zappeur).

## ✨ Fonctionnalités Principales (Dépassant la proposition initiale)

Nous avons transformé la proposition de modèle ML statique en un véritable **produit complet (Full-Stack Data Application)** :

1. **🧠 IA Comportementale (Unsupervised Learning)**
   - Utilisation de **K-Means Clustering** pour extraire 5 *Personas* réelles à partir des données comportementales : *Zappeur Curieux*, *Explorateur Narratif*, *Compétiteur Hardcore*, *Marathonien Passionné*, *Collectionneur Versatile*.
2. **⚙️ Moteur Hybride (SVD + Content-Based)**
   - Algorithme hybride combinant la factorisation de matrice (Singular Value Decomposition) pour le filtrage collaboratif, et le TF-IDF pour l'analyse de contenu (genres).
3. **🧊 Interface "Explainable AI" (React + Vite)**
   - Un tableau de bord interactif au design premium (*Glassmorphism*). L'IA **justifie** chaque recommandation en affichant le pourcentage d'influence du score collaboratif vs contenu.
4. **🚀 Résolution du "Cold Start"**
   - Les nouveaux utilisateurs sélectionnent leurs jeux favoris initiaux. L'algorithme déduit instantanément leur *Persona* comportementale et recommande des jeux basés sur les tendances de ce cluster.
5. **📊 Dashboard Analytique Administrateur**
   - Statistiques en temps réel connectées à la base **SQLite** : répartition des Personas (Pie Chart), temps de jeu par cluster, et Top 10 des genres basés sur le *vrai temps de jeu cumulé* (et non la simple taille du catalogue).

## 🛠️ Stack Technique

- **Data Engineering & ML** : `Python 3.10`, `pandas`, `numpy`, `scikit-learn` (PCA, TF-IDF, K-Means, TruncatedSVD).
- **Base de données** : `SQLite3` (Obligatoire Phase 3, utilisée en production locale).
- **Backend API** : `FastAPI`, `Uvicorn`, `Pydantic`.
- **Frontend Web** : `React`, `Vite`, `Axios`, `Recharts` (pour les graphiques analytiques), `Vanilla CSS`.

## 🚀 Installation & Lancement

L'application est conçue pour être lancée facilement en local.

### Prérequis
- Python 3.10+
- Node.js & npm (pour le frontend)

### Méthode 1 : Lancement Rapide (Windows)
Double-cliquez simplement sur le fichier batch à la racine du projet :
```bash
./start_dashboard.bat
```
Cela démarrera automatiquement le serveur Backend (port 8000) et le serveur Frontend (port 5173/5174), puis ouvrira votre navigateur.

### Méthode 2 : Lancement Manuel
1. **Démarrer l'API Backend :**
```bash
# Depuis la racine du projet
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

2. **Démarrer le Frontend React :**
```bash
# Dans un nouveau terminal
cd dashboard
npm install
npm run dev
```
Accédez ensuite à l'URL locale fournie par Vite (ex: `http://localhost:5173`).

---
*Ce projet est une création originale de l'équipe dans le cadre académique de l'EHTP.*
