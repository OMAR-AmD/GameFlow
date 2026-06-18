# Phase 1: Problem Framing & Data Acquisition

## 1. Problem Statement
**Domain:** Recommendation System

The digital video game market is saturated. Platforms like Steam host over 50,000 distinct titles, creating a massive discoverability crisis. Consumers suffer from the paradox of choice, frequently experiencing "choice paralysis" when deciding what to play next. Simultaneously, independent developers struggle to reach their target audience due to the sheer volume of competing titles.

Traditional recommendation engines typically rely on explicit feedback (e.g., user ratings, thumbs up/down) and Content-Based Filtering using genre tags (e.g., "Action", "RPG"). This approach is fundamentally flawed for two reasons:
1. **Explicit Feedback is Sparse and Biased:** Most players do not review games unless they have extremely positive or negative experiences.
2. **Genre Homogenization:** The "Action RPG" tag is too broad. It fails to distinguish between a player who plays *The Witcher 3* as a completionist (doing every side quest for 200 hours) and a player who rushes the main story in 30 hours and abandons it.

**GameFlow AI** proposes a solution by abandoning explicit feedback in favor of pure, implicit behavioral telemetry: **playtime**. By analyzing *how* a player engages with their library (Session Intensity, Completion Ratio, Competitive Index, Narrative Affinity), GameFlow clusters users into distinct psychographic Personas and recommends games based on deep behavioral similarity rather than superficial genre tags.

### Business & Social Motivation
- **Business Value (Platforms):** Highly personalized recommendations increase user retention, session length, and ultimately, platform revenue through higher game sales.
- **Business Value (Developers):** Niche games find their exact target audience based on playstyle, not marketing budget.
- **Social Value:** Reduces consumer frustration and choice paralysis, leading to a more satisfying entertainment experience.

### Success Criteria
The project will be considered successful if:
1. The K-Means clustering algorithm produces mathematically distinct and logically interpretable Personas (validated by a Silhouette Score > 0.5).
2. The Hybrid Recommendation Engine (SVD + Content-Based) outperforms a baseline User-Based KNN and pure Content-Based model in ranking accuracy, achieving an NDCG@10 of at least 0.80.
3. The system successfully solves the "Cold Start" problem for new users without interaction history.

## 2. AI Context Note (Course 2 Connection)
*Relevant Concept from Course 2 (Ch. 1-3): The Shift from Symbolic AI to Statistical Machine Learning paradigms.*

Historically, early Recommendation Systems attempted to use **Symbolic AI (Expert Systems)** paradigms. They relied on hard-coded, rule-based logic (e.g., `IF User likes RPG AND Game is RPG THEN Recommend`). This early AI limitation failed spectacularly in the context of entertainment because human taste is abstract, highly non-linear, and cannot be captured by rigid logic trees. 

GameFlow AI contextualizes the historical milestone of shifting toward **Statistical Machine Learning** (specifically Matrix Factorization and Unsupervised Clustering). Instead of relying on human experts to categorize games and players, we allow the latent patterns in large-scale interaction data (Matrix Factorization/SVD) to dynamically define what makes two games or two players similar. This transition from "reasoning via rules" to "reasoning via statistical probability" is the core paradigm shift that makes GameFlow scalable and effective.

## 3. Data Acquisition
The foundational data comprises the **Steam-200k** dataset (interactions) and the **Steam Store Games Metadata** dataset (tags and genres), both publicly available via Kaggle.
The data pipeline script successfully ingests these datasets, performs fuzzy joining, handles missing values, and calculates the necessary behavioral proxies (detailed extensively in the Phase 2 EDA and Phase 3 Feature Engineering reports).
