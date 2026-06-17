# Feature Engineering Log - Phase 3

## Contexte
Le dataset `steam-200k` utilisé pour la recommandation ne possède pas de données granulaires sur les sessions de jeu (heures de connexion, durée des sessions individuelles, événements en jeu). Il ne contient que le total des heures jouées (`hours_played`) par chaque utilisateur pour chaque jeu. 

Pour construire les **7 métriques comportementales** demandées, nous avons dû élaborer des "proxys mathématiques" en fusionnant ces données avec le dataset `steam_metadata` (qui contient la `median_playtime`, `average_playtime`, et les `genres`/`tags`).

Voici le log des formules appliquées dans `notebooks/03_feature_engineering.ipynb`.

---

## 1. Completion Ratio (`completion_ratio`)
- **Définition** : La proportion moyenne d'achèvement des jeux par rapport au reste de la communauté.
- **Proxy (Formule)** : `hours_played / median_playtime_hr`
- **Logique** : Si le joueur médian passe 10 heures sur un jeu pour le "finir" (ou en faire le tour), et que l'utilisateur y a passé 8 heures, son ratio est de 0.8. Le résultat est plafonné à 1.0 par jeu pour éviter qu'un seul jeu multi-joueurs de 2000 heures ne déséquilibre la moyenne.

## 2. Session Intensity (`session_intensity`)
- **Définition** : L'intensité de l'engagement global d'un joueur.
- **Proxy (Formule)** : `hours_played / average_playtime_hr`
- **Logique** : Faute de connaître la durée de la session, nous mesurons l'intensité par rapport à la moyenne globale du jeu. L'utilisation de l'average (au lieu de la médiane) permet de comparer le joueur aux joueurs très engagés ("hardcore"). Plus la moyenne par jeu est élevée, plus l'utilisateur a une session "intense" comparée aux autres.

## 3. Diversity Score (`diversity_score`)
- **Définition** : La variété des genres explorés par l'utilisateur.
- **Proxy (Formule)** : `Nombre de genres uniques joués / Nombre total de genres sur la plateforme`
- **Logique** : Basé sur les tags extraits via `.explode()`. Un joueur qui ne joue qu'à des jeux "Action" aura un score très bas (proche de 0), tandis qu'un joueur explorant "Action", "RPG", "Puzzle" et "Strategy" aura un score élevé.

## 4. Abandonment Rate (`abandonment_rate`)
- **Définition** : La propension d'un joueur à essayer un jeu et à l'abandonner très vite.
- **Proxy (Formule)** : `(hours_played < 0.10 * median_playtime_hr)`
- **Logique** : Si un joueur a joué à un jeu moins de 10% du temps médian de la communauté (ou moins de 30 minutes au total si la donnée médiane manque), on considère que le jeu est "abandonné". Le score de l'utilisateur est le pourcentage de ses jeux qui tombent dans cette catégorie.

## 5. Competitive Index (`competitive_index`)
- **Définition** : L'appétence de l'utilisateur pour l'affrontement en ligne et les jeux e-sports.
- **Proxy (Formule)** : `Total hours_played sur les jeux ("Multiplayer", "e-sports", "Action", "FPS", "MOBA") / Total hours_played global`
- **Logique** : Plus un joueur passe son temps total sur des titres compétitifs, plus il est classé comme compétitif. L'utilisation des tags SteamSpy garantit une grande précision.

## 6. Exploration Score (`exploration_score`)
- **Définition** : L'attrait du joueur pour les mondes ouverts et la liberté d'exploration.
- **Proxy (Formule)** : `Total hours_played sur les jeux ("Open World", "Exploration", "Adventure") / Total hours_played global`
- **Logique** : Similaire à l'index compétitif, mais centré sur les tags d'aventure et de monde ouvert, souvent synonymes de longues balades solitaires.

## 7. Narrative Affinity (`narrative_affinity`)
- **Définition** : Le penchant du joueur pour les jeux scénarisés.
- **Proxy (Formule)** : `Total hours_played sur les jeux ("Story Rich", "RPG", "Visual Novel") / Total hours_played global`
- **Logique** : Permet de distinguer les joueurs qui recherchent une histoire immersive de ceux qui ne s'intéressent qu'aux mécaniques de gameplay pures.

---

## Données de Sortie
Toutes ces features ont été moyennées par `user_id` et exportées sous forme de **11 350 profils utilisateurs uniques** dans `data/processed/user_profiles.csv` et dans la table `user_profiles` de `data/processed/gameflow.db`.
