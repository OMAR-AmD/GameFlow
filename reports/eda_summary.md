# Exploratory Data Analysis & Data Wrangling Summary

This document summarizes the findings from Phase 2: Data Wrangling and Exploratory Data Analysis. 
The complete code and visualizations can be found in `notebooks/02_eda_and_wrangling.ipynb`.

## 1. Data Audit & Cleaning
- **Behavior Filter**: The `steam-200k` dataset contains both "purchase" and "play" behaviors. We filtered the dataset to include **only "play"** events, as purchasing alone does not yield any meaningful behavioral hours played data for our recommendation engine. The `0` column was also dropped as it provided no information.
- **Null Values**: The `steam-200k` data had no null values. The metadata had a few null values in the `developer` and `publisher` columns, which we filled with the string `'Unknown'`.
- **Duplicates**: Duplicate "play" records for the same user and game were identified and removed.

## 2. Outlier Detection
We performed outlier detection on the `hours_played` column:
- **IQR Method**: Detected extreme values beyond 1.5 * IQR above the third quartile.
- **Z-Score Method**: Detected outliers with a standard score greater than 3.
- **Cleaning Decision**: Since some players have immense passion for a single game, outright dropping players with 10,000+ hours would hurt the behavioral integrity of the recommendation engine. Instead, we **capped the hours played at the 99th percentile**. This removes the distortion of extreme outliers (which could be bots or AFK players) while keeping the relative interaction strength high for dedicated players.

## 3. Visualization Findings
1. **Distribution of Hours Played**: Highly right-skewed. Most games are played for under 10 hours, while a long tail exists for competitive/multiplayer games.
2. **Boxplot (Outlier View)**: Visualized the heavy tail even after capping, confirming that power users exist in our platform.
3. **Top 10 Most Played Games**: `Dota 2`, `CS:GO`, and `Team Fortress 2` dominate total hours played.
4. **Top 10 Most Popular Games**: The same games top the charts for unique players, showing a correlation between popularity and total engagement.
5. **Distribution of Game Prices**: The vast majority of games are priced under $20, with a significant spike at $0 (Free to Play), matching the most popular titles.
6. **Correlation Heatmap**: Positive ratings and negative ratings are highly correlated, reflecting overall popularity. Achievements do not strongly correlate with playtime.
7. **Positive vs Negative Ratings**: A log-scale scatter plot shows a linear relationship for most games; games lying far above the diagonal are overwhelmingly well-received.
8. **Average Playtime by Top Genres**: "Action" and "Indie" dominate the platform, but RPG and MMOs tend to have a higher variance in average playtime. 
   - **Correction Appliquée (Graphe 8)**: Pour régler le problème de distribution écrasée sur ce graphique sans corrompre les données, deux changements majeurs ont été appliqués :
     1. *Filtrage des temps nuls* (`average_playtime > 0`) : Les jeux qui n'ont jamais enregistré une seule minute de jeu (0 minute) créaient une accumulation massive sur l'origine. Les exclure a permis de nettoyer le bruit de fond.
     2. *Passage à l'échelle logarithmique* (`axes[1].set_xscale('log')`) : Une échelle logarithmique transforme l'affichage des données en se basant sur des ordres de grandeur, ce qui permet de visualiser correctement la variance extrême des temps de jeu.

## 4. Output
The cleaned data has been saved to the `data/interim/` directory:
- `steam200k_cleaned.csv`
- `steam_metadata_cleaned.csv`

These datasets are now ready for Phase 3: Feature Engineering.
