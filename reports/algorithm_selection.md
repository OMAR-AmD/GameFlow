# Phase 4: Algorithm Selection & Justification

## 1. Candidate Algorithms Comparison
For our Recommendation System domain, we evaluated four primary algorithmic approaches before implementation:

| Algorithm | How it Works | Assumptions | Strengths | Weaknesses |
|-----------|--------------|-------------|-----------|------------|
| **User-Based KNN** | Computes cosine similarity between user behavioral vectors to find "neighbors". | Assumes users with similar past behavior will have similar future preferences. | Highly interpretable. Easy to implement as a baseline. | Poor scalability ($O(N^2)$). Suffers massively from the Cold Start problem. |
| **Matrix Factorization (SVD)** | Decomposes the sparse user-item interaction matrix into lower-dimensional latent factors. | Assumes a small number of latent features (e.g., "play-styles") explain the variance in user preferences. | Excellent at handling extreme sparsity. Uncovers hidden serendipitous connections. | Black-box nature (low interpretability without XAI wrappers). |
| **Content-Based Filtering (TF-IDF)** | Vectorizes game descriptions/tags into TF-IDF scores, computing item-item cosine similarity. | Assumes users will enjoy games structurally similar (same tags/genres) to what they already play. | Completely immune to the Cold Start problem for new users. | "Filter Bubble" effect. Zero serendipity (will only recommend what the user already knows). |
| **K-Means Clustering** | Unsupervised algorithm partitioning users into $k$ distinct clusters based on behavioral features. | Assumes spherical clusters of similar variance. | Allows macro-level user segmentation. Solves "Cold Start" by grouping new users instantly. | Requires predefined $k$. Sensitive to outliers in continuous playtime data. |

## 2. Justified Selection
We selected a **Hybrid Engine combining SVD, TF-IDF, and K-Means**:
1. **SVD (TruncatedSVD):** Selected as the core collaborative filter because Steam interaction data is over 99% sparse. KNN would collapse, but SVD thrives by finding latent features (e.g., "likes competitive shooters").
2. **TF-IDF:** Selected as the secondary layer to ground the SVD recommendations in reality, ensuring that if a user asks for RPGs, the collaborative anomalies don't accidentally recommend a racing game.
3. **K-Means:** Selected specifically to solve the "Cold Start" problem. Instead of blindly using TF-IDF for new users, we use K-Means to instantly map their first 3 game choices to a behavioral Persona, unlocking collaborative data immediately.
*Rejected:* User-Based KNN was implemented purely as a baseline but rejected for production due to high memory overhead and poor NDCG performance.

## 3. Evaluation Metrics
For an implicit feedback recommendation system (hours played), traditional classification metrics (Accuracy, F1) are meaningless. We selected:
- **NDCG@K (Normalized Discounted Cumulative Gain):** Chosen because the order of recommendations matters. We want the absolute best games at the top of the UI list. NDCG penalizes the model if a highly relevant game is ranked 10th instead of 1st.
- **Silhouette Score:** Chosen to validate our K-Means clustering, ensuring our 5 Personas are mathematically distinct.
