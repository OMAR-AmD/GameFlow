from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Initialize the presentation
prs = Presentation()

# Utility functions
def add_title_slide(prs, title_text, subtitle_text):
    slide_layout = prs.slide_layouts[0] # Title Layout
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = title_text
    subtitle.text = subtitle_text
    return slide

def add_bullet_slide(prs, title_text, bullet_points):
    slide_layout = prs.slide_layouts[1] # Title and Content
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    title.text = title_text
    
    tf = slide.placeholders[1].text_frame
    tf.text = bullet_points[0]
    
    for point in bullet_points[1:]:
        p = tf.add_paragraph()
        p.text = point
        p.level = 0
        if ":" in point and not point.startswith("  "):
            pass
        elif point.startswith("-"):
            p.level = 1
            
    return slide

# Slide 1: Title
add_title_slide(
    prs, 
    "GameFlow AI", 
    "Behavior-Driven Game Recommendation System\n\nPrepared by: Akby Anass & Omar Amdouni\nEHTP - MIG (2025-2026)"
)

# Slide 2: Context & Problem Statement
add_bullet_slide(
    prs,
    "1. Context & Problem Statement",
    [
        "The Discoverability Crisis on Steam: Over 50,000 video games available.",
        "Limitations of Traditional Systems:",
        "- Rely heavily on explicit tags (e.g., RPG, Action) and sparse 5-star ratings.",
        "- Unable to distinguish player psychographics (Completionist vs Explorer).",
        "Our Solution (GameFlow AI):",
        "- Shift from recommending by 'genre' to recommending by 'actual behavior'.",
        "- Leverage implicit feedback (hours played) as the ultimate truth of engagement."
    ]
)

# Slide 3: Data & Feature Engineering
add_bullet_slide(
    prs,
    "2. Data & Feature Engineering",
    [
        "Datasets: Steam-200k (User Interactions) & Steam Metadata (Game Tags).",
        "Transforming raw playtime into Behavioral Proxies:",
        "- Session Intensity: User playtime divided by global median playtime.",
        "- Completion Ratio: % of games beaten based on main campaign length.",
        "- Competitive Index: Affinity for multiplayer/eSports environments.",
        "- Exploration Score & Narrative Affinity.",
        "- Abandonment Rate: % of games dropped before the 1.5-hour mark."
    ]
)

# Slide 4: Unsupervised Behavioral Profiling
add_bullet_slide(
    prs,
    "3. Behavioral Profiling (K-Means)",
    [
        "Applied PCA & K-Means Clustering on the behavioral vectors.",
        "Mathematically extracted 5 distinct Player Personas:",
        "1. The Hardcore Competitor (47%): Extreme session intensity, multiplayer focus.",
        "2. The Versatile Collector (19.5%): Highest genre diversity.",
        "3. The Curious Zapper (17%): High abandonment rate, low commitment.",
        "4. The Passionate Marathoner (8.5%): Massive total hours investment.",
        "5. The Narrative Explorer (8%): High story and open-world affinity."
    ]
)

# Slide 5: The Hybrid Recommendation Engine
add_bullet_slide(
    prs,
    "4. The Hybrid Recommendation Engine",
    [
        "Collaborative Filtering via Matrix Factorization (SVD):",
        "- TruncatedSVD compresses the sparse User-Item matrix.",
        "- Identifies latent play-styles and community trends.",
        "Content-Based Filtering (TF-IDF):",
        "- Cosine similarity applied to game descriptions and tags.",
        "The Hybrid Formula:",
        "- Score = (Alpha * SVD Score) + ((1 - Alpha) * TF-IDF Score).",
        "- Delivers serendipity while ensuring genre relevance."
    ]
)

# Slide 6: Application & Explainable AI
add_bullet_slide(
    prs,
    "5. Full-Stack Deployment & Explainable AI",
    [
        "Architecture: SQLite3 -> FastAPI (Backend) -> React/Vite (Frontend).",
        "Innovative 'Cold Start' Solver:",
        "- Infers Persona instantly from 3 initial game selections.",
        "Explainable AI (XAI) Implementation:",
        "- The UI explicitly justifies every algorithmic decision.",
        "- Example: 'Collaborative Score: 85% | Content Score: 15%'.",
        "Admin Analytics Dashboard: Real-time telemetry via Recharts."
    ]
)

# Slide 7: Conclusion
add_bullet_slide(
    prs,
    "6. Conclusion & Perspectives",
    [
        "Achievement: Built an end-to-end Machine Learning product.",
        "Key Takeaway:",
        "- Implicit behavior (playtime) yields far richer recommendations than static genre tags.",
        "Future Perspectives:",
        "- Deep Sequential Models (RNN/Transformers) for chronologically aware recommendations.",
        "- Cloud deployment via Docker and Kubernetes.",
        "Thank you for your attention. Q&A."
    ]
)

# Save the presentation
output_filename = "GameFlow_Presentation.pptx"
prs.save(output_filename)
print(f"Presentation successfully generated: {output_filename}")
