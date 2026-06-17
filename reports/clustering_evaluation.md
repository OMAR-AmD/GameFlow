# Clustering Evaluation & Persona Profiling - Phase 4

Nous avons appliqué l'algorithme de Machine Learning non-supervisé **K-Means** sur les 7 features comportementales de nos 11 350 utilisateurs. L'algorithme a segmenté la base en **5 clusters distincts**.

Voici l'analyse métier et la définition des "Personas" extraits par le modèle :

## 1. Persona 0 : "Le Touriste / L'Acheteur Compulsif" (The Casual Abandoner)
* **Profil (Z-scores)** : `abandonment_rate` extrêmement élevé (+2.0), `completion_ratio` très faible (-1.4), et `session_intensity` basse (-0.67).
* **Analyse** : Ce joueur lance énormément de jeux mais n'y passe que quelques minutes avant de les abandonner. Il accumule probablement des jeux gratuits ou des bundles sans s'y investir.

## 2. Persona 1 : "Le Conteur Patient" (The Narrative Completionist)
* **Profil (Z-scores)** : `narrative_affinity` immense (+3.0), forte `exploration_score` (+1.45), très faible attrait compétitif (-0.65).
* **Analyse** : Ce joueur déteste les jeux multijoueurs compétitifs. Il préfère s'immerger profondément dans des expériences solo (RPG, Histoire, Monde Ouvert).

## 3. Persona 2 : "Le Compétiteur Standard" (The Standard Competitor)
* **Profil (Z-scores)** : `competitive_index` au-dessus de la moyenne (+0.44), faible taux d'abandon (-0.51), peu d'exploration/narration.
* **Analyse** : Le profil classique de la plateforme. Il joue principalement à des jeux multijoueurs/action (CS:GO, Dota 2). Il est fidèle à ses jeux compétitifs et ne cherche pas la diversité.

## 4. Persona 4 : "L'Explorateur Éclectique" (The Diverse Explorer)
* **Profil (Z-scores)** : `diversity_score` très élevé (+1.39), forte `exploration_score` (+0.88), bonne intensité de session.
* **Analyse** : Ce joueur touche à tout. Il a une curiosité insatiable pour de multiples genres (Action, Stratégie, Indés, Puzzles). C'est le profil idéal pour des recommandations "hors des sentiers battus".

## 5. Persona 3 : "Le Spécialiste Hardcore" (The Dedicated Specialist)
* **Profil (Z-scores)** : `session_intensity` très élevée (+1.0), mais `competitive_index` drastiquement bas (-2.43).
* **Analyse** : Un joueur qui dédie un temps monumental à un petit groupe de jeux non compétitifs (ex: jeux de gestion complexes comme *Factorio*, bacs à sable comme *Terraria* ou des simulateurs). 

---
**Conclusion** : Grâce à la transformation logarithmique (`np.log1p`), les outliers de temps de jeu ont été lissés. La méthode du coude et les scores de Silhouette ont confirmé une segmentation robuste. Les modèles mathématiques ont été sauvegardés (`models/`) pour la Phase 6, et chaque utilisateur a reçu son tag de persona dans `user_profiles_clustered.csv`.
