# Phase 6: Model Card & Ethical Reflection

## Model Overview
- **Name:** GameFlow Hybrid Recommender (GF-HR v1.0)
- **Type:** Hybrid Recommendation Engine (TruncatedSVD + TF-IDF) combined with K-Means Behavioral Profiling.
- **Task:** Rank and recommend video games based on implicit user behavior (playtime) rather than explicit ratings.
- **Date:** June 2026

## Intended Use
- **Who is it for?** Digital distribution platforms (like Steam, Epic Games, PlayStation) and end-users seeking game discovery.
- **What decisions does it support?** It supports automated content curation, helping users discover niche titles that match their actual playstyle rather than just searching by genre tags.

## Training Data
- **Source:** Steam-200k dataset (Kaggle) and Steam Store Games Metadata (Kaggle).
- **Size:** ~200,000 interactions covering over 5,000 games, augmented with metadata.
- **Features Used:** `hours_played`, derived behavioral features (`session_intensity`, `competitive_index`, `completion_ratio`, `exploration_score`, `narrative_affinity`, `abandonment_rate`), and textual game tags/genres.
- **Preprocessing Summary:** Dropped "purchase-only" rows (0 hours). Handled extreme outliers via robust scaling. Implemented fuzzy matching to join interaction data with metadata.

## Performance Summary
- **Evaluation Metric:** NDCG@10 (Normalized Discounted Cumulative Gain).
- **Test Set Performance:** 
  - Baseline (Content-Based TF-IDF): 0.68
  - Baseline (User-Based KNN): 0.74
  - **GF-HR v1.0 (Hybrid SVD + CBF): 0.88**
- **Clustering:** K-Means achieved a Silhouette Score of 0.62 with k=5.

## Limitations
- **What the model cannot do well:** The SVD matrix is highly sensitive to extreme outliers; if a user leaves a game running in the background for 5,000 hours, it skews their behavioral profile.
- **Distributional Assumptions:** Assumes that past playtime is indicative of future enjoyment, which ignores sudden shifts in a user's taste.

## Ethical Considerations
- **Potential Biases:** The model exhibits "Popularity Bias" inherent to collaborative filtering; massive multiplayer games (like *Dota 2* or *CS:GO*) can disproportionately dominate recommendations because they accumulate the most raw hours.
- **Fairness & Privacy:** The dataset relies on anonymized `user_id` integers. No Personally Identifiable Information (PII) such as names, ages, or locations was used.
- **Risk of Misuse:** If deployed aggressively, hyper-personalized recommendation engines can create "Filter Bubbles" or encourage video game addiction by constantly serving highly engaging content to vulnerable "Zapper" profiles.

## Recommendations
- **Human Oversight:** The system should not enforce auto-play or auto-purchase. The user must always have the agency to manually search the catalog.
- **Usage Recommendation:** The Explainable AI (XAI) UI implemented in the dashboard should be kept active, ensuring users understand exactly *why* a game is recommended, allowing them to spot algorithmic biases themselves.
